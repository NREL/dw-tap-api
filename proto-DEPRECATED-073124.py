from flask import Flask, render_template, request, jsonify, Response
from flask_cors import CORS
from threading import Thread
from time import sleep
import time
import datetime
import json
import pandas as pd
import argparse
import asyncio
import calendar
import hashlib
import shutil
import os
import requests
import urllib
import glob
import calendar
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('agg')

from dw_tap.data_fetching import getData
from v2 import validated_params_v2_w_year
from v2 import validated_params_v2
from v2 import validated_latlon
from hsds_helpers import connected_hsds_file
from bc import bc_for_point
from infomap import get_infomap_script
from windrose import WindroseAxes
from powercurve import PowerCurve
from shapely.geometry import Point
import geopandas as gpd
import heapq
import scipy.interpolate
import numpy as np
from html_maker import *
import flask

# Start of WTK-LED fucntions
# Code below is copied from the uncertainty notebook by Caleb Phillips
# This function fetches the grid point index and returns as an indexed geodataframe
def get_index():
    # For sample:
    #base_url = "https://wtk-csv-testing-dav-sandbox.s3.us-west-2.amazonaws.com"
    base_url = "https://wtk-led.s3.us-west-2.amazonaws.com"
    file_path = f"/location_index.csv.gz"
    index = gpd.GeoDataFrame(pd.read_csv(base_url+file_path))
    index['location'] = gpd.GeoSeries(gpd.points_from_xy(index.longitude, index.latitude))
    return index
wtkled_index = get_index()

# This function finds the closest grid point to the given lat/lon
# Note that a faster method might use index.location.sindex, the STRTree optimized
# spatial index, but support is not universal and depends on specific versions of Geos and PyGeos:
# https://pygeos.readthedocs.io/en/latest/strtree.html
# Hence, we're doing the more universally supported, but less optimized thing here
def closest_grid_point(index,lat,lon):
    p = Point(lon,lat)
    r = index.iloc[index.location.distance(p).argmin()].copy()
    r['distance_degrees'] = Point(r['longitude'],r['latitude']).distance(p)
    return r

def parse_mohr(mohr):
    s = str(mohr)
    m, h = s[:-2], s[-2:]
    return int(m), int(h)

def get_1224(idx, year=2020, add_year_col=False):
    # For sample:
    #base_url = "https://wtk-csv-testing-dav-sandbox.s3.us-west-2.amazonaws.com/1224"
    base_url = "https://wtk-led.s3.us-west-2.amazonaws.com/1224"
    file_path = f"/year={year}/varset=all/index={idx}/{idx}_{year}_all.csv.gz"
    res = pd.read_csv(base_url + file_path)
    res["m"], res["h"] = zip(*res["mohr"].apply(parse_mohr))
    if add_year_col:
        res["year"] = year
    return res

def get_1224_20yrs(idx, ws_col_for_estimating_power, selected_powercurve, relevant_columns_only=True):
   # Example of the dataframe returned by this func (wtih relevant_columns_only=True):
   #
   # year  mohr month  h  windspeed_40m  windspeed_40m_kw  winddirection_40m
   # 0  2001   101   Jan  1           4.31         10.765848             334.29
   # 1  2001   102   Jan  2           5.07         17.058348             323.40
   # 2  2001   103   Jan  3           5.38         20.721432             302.85

    df = pd.concat([get_1224(idx, year=yr, add_year_col=True) for yr in range(2001, 2021)])

    df.rename(columns={"m": "month"}, inplace=True)
    # df.month = df.month.apply(lambda x: calendar.month_abbr[x]) -- converting months to Jan, Feb, etc. should happen last to avoid messing up the other of months

    if ws_col_for_estimating_power in df.columns:
        df[ws_col_for_estimating_power + "_kw"] = selected_powercurve.windspeed_to_kw(df, ws_col_for_estimating_power)
    if relevant_columns_only:
        wd_col = ws_col_for_estimating_power.replace("speed", "direction")
        relevant_columns = ["year", "mohr", "month", "h", ws_col_for_estimating_power, ws_col_for_estimating_power + "_kw", wd_col]
        return df[relevant_columns]
    else:
        return df

def df2yearly_avg(df, ws_column, kw_column):
    tmp = df.drop(columns=["mohr", "month", "h"] + [x for x in df.columns if "winddirection" in x])
    #res = tmp.groupby("year").agg("mean")
    res = tmp.groupby("year").agg(avg_ws=(ws_column, "mean"), kwh_total=(kw_column, "sum")) # kwh_total will sum for all months and all hours

    res["kwh_total"] = res["kwh_total"] * 30 # Coarse estimation: 30 days in every month; no need to /20.0 for individual years
    res.rename(columns={"avg_ws": "Average wind speed, m/s", "kwh_total": "kWh produced"}, inplace=True)

    # res["kWh produced"] = res["kWh produced"].astype(float).map('{:,.0f}'.format)
    # res["Average wind speed, m/s"] = res["Average wind speed, m/s"].astype(float).map('{:,.2f}'.format)

    # Return entired dataframe, with all years
    # return res

    # Create df with low, avg, high year

    res = res.sort_values("Average wind speed, m/s")
    #return res

    res_avg = pd.DataFrame(res.mean()).T
    res_avg.index=["Average year"]
    #return res_avg

    res_3years = pd.concat([res.iloc[[0]], res_avg, res.iloc[[-1]]])
    res_3years["kWh produced"] = res_3years["kWh produced"].astype(float).map('{:,.0f}'.format)
    res_3years["Average wind speed, m/s"] = res_3years["Average wind speed, m/s"].astype(float).map('{:,.2f}'.format)

    res_3years.index = ["Lowest year (%s)" % str(res_3years.index[0]), \
                        res_3years.index[1], \
                        "Highest year (%s)" % str(res_3years.index[2])]

    return res_3years

def df2monthly_avg(df, ws_column, kw_column):
    tmp = df.drop(columns=["year", "mohr", "h"] + [x for x in df.columns if "winddirection" in x])
    #res = tmp.groupby("month").agg("mean")
    res = tmp.groupby("month").agg(avg_ws=(ws_column, "mean"), kwh_total=(kw_column, "sum")) # kwh_total will sum for all hours and all years

    res["kwh_total"] = res["kwh_total"] * 30 / 20.0 # Coarse estimation: 30 days in every month & 20 years
    res.rename(columns={"avg_ws": "Average wind speed, m/s", "kwh_total": "kWh produced"}, inplace=True)
    res.index = pd.Series(res.index).apply(lambda x: calendar.month_abbr[x])

    res["kWh produced"] = res["kWh produced"].astype(float).map('{:,.0f}'.format)
    res["Average wind speed, m/s"] = res["Average wind speed, m/s"].astype(float).map('{:,.2f}'.format)

    return res

def yearly_avg_df_to_closest_heights(yearly_avg, selected_height, heights_count=1):
    # Use columns that are of format: windspeed_XYZm where XYZ are integers
    all_cols = yearly_avg.columns
    heights = [int(c.split("_")[1].rstrip("m")) for c in yearly_avg.columns if "windspeed" in c]
    #return heights

    closest_heights = heapq.nsmallest(heights_count, heights, key=lambda x: abs(x-selected_height))

    closest_heights_columns = []
    for h in closest_heights:
        c = "windspeed_%dm" % h
        if c in all_cols:
            closest_heights_columns.append(c)
        # Leave out winddirection columns for now
        # c = "winddirection_%dm" % h
        # if c in all_cols:
        #     closest_heights_columns.append(c)

    return closest_heights, closest_heights_columns

def get_uncertainty_dataframe(location,height=40):
    # For sample:
    #base_url = "https://wtk-csv-testing-dav-sandbox.s3.us-west-2.amazonaws.com/uncertainty"
    base_url = "https://wtk-led.s3.us-west-2.amazonaws.com/uncertainty"
    file_path = f"/height={height}/index={location}/{location}_{height}m.csv.gz"
    return pd.read_csv(base_url+file_path)

# End of WTK-LED fucntions


def feasibility_thresh_by_height(h):
    """
    From literature (shared by Heidi):
        For a small wind turbine hub height of 30 m, 4.0 m/s (9 mph)
        is typically cited as the minimum annual average wind speed
        required for a feasible project.
        For a large wind turbine hub height of 80 m,
        a minimum annual average wind speed of 6.5 m/s (14.5 mph) is typically needed.
    """
    y_interp = scipy.interpolate.interp1d([30, 80], [4.0, 6.5], fill_value="extrapolate")
    return y_interp(h)

server_started_at = datetime.datetime.now()

if "GOOGLE_MAPS_API_KEY" in os.environ:
    given_google_maps_api_key = os.environ.get('GOOGLE_MAPS_API_KEY')
else:
    given_google_maps_api_key = ""

# Necessary directories: create if not there
outputs_dir = "outputs"
if not os.path.exists(outputs_dir):
  os.mkdir(outputs_dir)

# pending_dir = "static/pending/"
# if not os.path.exists(pending_dir):
#   os.mkdir(pending_dir)
completed_dir = "static/completed/"
if not os.path.exists(completed_dir):
  os.mkdir(completed_dir)

templates_dir = "templates"
if not os.path.exists("%s/served" % templates_dir):
  os.mkdir("%s/served" % templates_dir)

# Csv and png outputs will be saved in the following dirs;
# Having them live inside static is important becuase it makes them accessible to the outside
csv_dir = "static/raw"
if not os.path.exists(csv_dir):
  os.mkdir(csv_dir)

plot_dir = "static/plots/"
if not os.path.exists(plot_dir):
  os.mkdir(plot_dir)

powercurves_dir = "powercurves"
# Create dict with keys being names of all available power curves (without extensions)
# and values being the corresponding PowerCurve objects
powercurves = {}
powercurve_default = ""
for fname in glob.glob(powercurves_dir + '/*.csv'):
    powercurve_name = os.path.basename(fname).replace(".csv", "")
    powercurves[powercurve_name] = PowerCurve(fname)
    if powercurve_name == "nrel-reference-100kW":
        powercurve_default = powercurve_name
if not powercurve_default:
    powercurve_default = powercurves.keys()[0]

# def instantiate_from_template(src, dest, old_text, new_text):
#     """ Copy src file to dest with replacement of old_text with new_text """
#     # This version performs single substring replacement: old_text -> new_text
#
#     fin = open(src)
#     fout = open(dest, "wt")
#     for line in fin:
#         fout.write(line.replace(old_text, new_text))
#     fin.close()
#     fout.close()

def instantiate_from_template(src, dest, replacements):
    """ Copy src file to dest with replacement of old_text with new_text """

    # This version performs multiple substring replacement, using each tuple provided in the replacements list
    # Each element there is: old_text -> new_text
    fin = open(src)
    fout = open(dest, "wt")
    for line in fin:
        updated_line = line
        for r in replacements:
            old_text, new_text = r[0], r[1]
            updated_line = updated_line.replace(old_text, new_text)
        fout.write(updated_line)
    fin.close()
    fout.close()

def plot_monthly_avg(atmospheric_df, ws_column="ws", datetime_column="datetime",
                     title="Windspeed monthly averages",
                     show_avg_across_years=True,
                     label_avg_across_years=True,
                     save_to_file=True,
                     show_overall_avg=True,
                     show=True):

    if ws_column not in atmospheric_df.columns:
        raise ValueError("Can't find %s column in dataframe. Skipping plotting" % ws_column)
    if datetime_column not in atmospheric_df.columns:
        raise ValueError("Can't find %s column in dataframe. Skipping plotting" % datetime_column)

    df = atmospheric_df[[datetime_column, ws_column]].copy()

    year_month = pd.Series(pd.PeriodIndex(df[datetime_column], freq="M"))
    df["month"] = year_month.apply(lambda x: x.month)
    df["year"] = year_month.apply(lambda x: x.year)
    #display(df)

    fig, ax = plt.subplots(figsize=(10, 3))
    xvals = list(range(1, 13)) # for showing monthly data

    nyears = df["year"].nunique()
    if nyears > 1:
        for year, grp in df.groupby("year"):
            monthly_avg = grp[[ws_column, "month"]].groupby("month").agg("mean")
            ax.plot(monthly_avg, label=str(year), linestyle="--", alpha=0.4)

        if show_avg_across_years:
            monthly_avg_across_years = df.groupby("month")[ws_column].agg("mean")
            ax.plot(monthly_avg_across_years, label="Avg across years (labeled)", marker="o")
            if label_avg_across_years:
                ylim0 = ax.get_ylim()[0]
                ylim1 = ax.get_ylim()[1]
                yoffset = ylim1 / 20  # express offest as a fraction of height
                yvals = pd.Series(monthly_avg_across_years.tolist())
                a = pd.concat({'x': pd.Series(xvals),
                               'y': yvals,
                               'val': yvals}, axis=1)
                for i, point in a.iterrows():
                    t = ax.text(point['x'], point['y'] + yoffset, "%.2f" % point['val'], fontsize=7)
                    t.set_bbox(dict(facecolor='lightgray', alpha=0.75, edgecolor='red'))
                ax.set_ylim([ylim0, ylim1*1.25])
    else:
        single_year = df["year"].tolist()[0]
        monthly_avg_across_years = df.groupby("month")[ws_column].agg("mean")
        ax.plot(monthly_avg_across_years, linestyle="--", label="Year: " + str(single_year), marker="o")
        if label_avg_across_years:
            ylim0 = ax.get_ylim()[0]
            ylim1 = ax.get_ylim()[1]
            yoffset = ylim1 / 20  # express offest as a fraction of height
            yvals = pd.Series(monthly_avg_across_years.tolist())
            a = pd.concat({'x': pd.Series(xvals),
                           'y': yvals,
                           'val': yvals}, axis=1)
            for i, point in a.iterrows():
                t = ax.text(point['x'], point['y'] + yoffset, "%.2f" % point['val'], fontsize=7)
                t.set_bbox(dict(facecolor='lightgray', alpha=0.75, edgecolor='red'))
            ax.set_ylim([ylim0, ylim1*1.25])

    ax.set_xticks(xvals)
    ax.set_xticklabels(["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"])

    ax.set_ylabel("Monthly avg windspeed, m/s")
    ax.set_title(title)

    # plt.figtext(0.1, -0.05,
    #             "Code used to produce this figure is developed under NREL's TAP project "
    #             "(https://www.nrel.gov/wind/tools-assessing-performance.html)",
    #             ha="left", fontsize=6)

    # Shrink current axis by 20%
    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])

    # Put a legend to the right of the current axis
    ax.legend(loc='center left', bbox_to_anchor=(1, 0.5));

    if show_overall_avg:
        ax.set_xlim([0, 16])
        overall_avg = df[ws_column].mean()
        ax.axhline(y=overall_avg,linestyle="dotted", color="orange", linewidth=2.0)
        t = ax.text(13.0, overall_avg + yoffset, "Overall avg=%.2f" % overall_avg, fontsize=8)
        t.set_bbox(dict(facecolor='orange', alpha=0.3, edgecolor='black'))

    if save_to_file == True:
        plt.savefig('%s.png' % title, dpi=300)
    elif type(save_to_file) == str:
        plt.savefig(save_to_file, dpi=300)

    if show:
        plt.show()

def plot_windrose(df, ws_column="ws", wd_column="wd", save_to_file=True):
    ax = WindroseAxes.from_ax()
    ax.bar(df[wd_column], df[ws_column], normed=True, opening=0.8, edgecolor='white')
    ax.set_legend()
    if save_to_file == True:
        plt.savefig('%s.png' % title, dpi=300)
    elif type(save_to_file) == str:
        plt.savefig(save_to_file, dpi=300)

def timeseries_to_12_by_24(df, styling=True, format="html"):
    res = df

    res["datetime"] = pd.to_datetime(res["datetime"])
    res["hour"] = res["datetime"].apply(lambda x: x.hour)
    res["month"] = res["datetime"].apply(lambda x: x.month)
    res = res.groupby(["hour", "month"]).agg(ws_avg=("ws", "mean"))
    res = res.stack().unstack(level=1)
    res.index = ["Hour " + str(el[0]) for el in res.index] # range(len(res))
    res.columns.name = ""
    res.rename(columns={c:calendar.month_name[c][:3] for c in res.columns}, inplace=True)

    min_ws = res.min().min()
    max_ws = res.max().max()
    overall_mean = res.mean().mean()

    if styling:
        res = res.style.background_gradient("BuPu", axis=1).format(precision=3).set_caption("Overall average: <strong>%.3f</strong>" % overall_mean)
    if format=="dataframe":
        return res
    elif format=="html":
        #html = res.to_html(classes='12_by_24')
        # Add colormap image
        #html += "<div id=\"colormap_wrapper\"><p id=\"colormap_min\">Min=%.3f</p><img id=\"colormap\" src=\"static/colormap.png\"/></div>" % (min_ws)

        html = "<div class=\"centered\">%s</div>" % (res.to_html(table_id='12_by_24'))

        # <tr>
        #   <td id="colormap_min_cell">Min=%.3f</td>
        #   <td id="colormap_max_cell">Max=%.3f</td>
        # </tr>
        # <tr>
        #   <td colspan=2><img id=\"colormap\" src=\"static/colormap.png\"/></td>
        # </tr>

        # """ % (min_ws, max_ws)


        return html
    else:
        return res

with open('config.json', 'r') as f:
    config = json.load(f)

parser = argparse.ArgumentParser()
parser.add_argument('-p', '--production', action='store_true')
parser.add_argument('-d', '--development', action='store_true')
args = parser.parse_args()

# Make development the default mode
development_mode = True
# Switch it if: "-p" and no "-d"
if (not args.development) and (args.production):
    development_mode = False

# Use parameters that are appropriate for the selected mode
if development_mode:
    host = config["development"]["host"]
    port = config["development"]["port"]
else:
    host = config["production"]["host"]
    port = config["production"]["port"]

# # Identify the current environment
# # URL_prefix should NOT include "/" at the end, otherwise there will be errors
# if os.environ.get('AWS_EXECUTION_ENV') == "AWS_ECS_EC2":
#     running_in_aws = True
#     if port == 80 or port == "80":
#         URL_prefix = "https://dw-tap.nrel.gov"
#     else:
#         URL_prefix = "https://dw-tap.nrel.gov:%s" % str(port)
# else:
#     running_in_aws = False
#     # This case is for running locally (container should be accessed via port 8080 even though inside it the server runs on part 80)
#     URL_prefix = "http://localhost:8080"

# Identify the current environment
# URL_prefix should NOT include "/" at the end, otherwise there will be errors
if os.environ.get('ENV') == "prod":
    running_in_aws = True
    if port == 80 or port == "80":
        URL_prefix = "https://dw-tap.nrel.gov"
    else:
        URL_prefix = "https://dw-tap.nrel.gov:%s" % str(port)
elif os.environ.get('ENV') == "stage":
    running_in_aws = True
    if port == 80 or port == "80":
        URL_prefix = "https://dw-tap-stage.stratus.nrel.gov"
    else:
        URL_prefix = "https://dw-tap-stage.stratus.nrel.gov:%s" % str(port)
elif os.environ.get('ENV') == "dev":
    running_in_aws = True
    if port == 80 or port == "80":
        URL_prefix = "https://dw-tap-dev.stratus.nrel.gov"
    else:
        URL_prefix = "https://dw-tap-dev.stratus.nrel.gov:%s" % str(port)
else:
    running_in_aws = False
    # This case is for running locally (container should be accessed via port 8080 even though inside it the server runs on part 80)
    URL_prefix = "http://localhost:8080"




# Now that URL_prefix is determined for the current env, prepare templates from universal ones
# Universal here means that those template can be used for AWS and non-AWS envs
src_dest_names = [("universal_monthly_index.html", "monthly_index.html"),\
                  ("universal_windrose_index.html", "windrose_index.html"),\
                  ("universal_12x24_index.html", "12x24_index.html"),\
                  ("universal_ts_index.html", "ts_index.html"),\
                  ("universal_bc_index.html", "bc_index.html"),\
                  ("universal_info.html", "info.html"),\
                  ("universal_on_map.html", "on_map.html"),\
                  ("universal_on_map3.html", "on_map3.html"),\
                  ("universal_by_address.html", "by_address.html"),\
                  ("universal_kwh_index.html", "kwh_index.html"),\
                  ("universal_energy.html", "energy.html")]
for src_dest in src_dest_names:
    t_src, t_dest = src_dest[0], src_dest[1]
    t_src = os.path.join(templates_dir, t_src)
    t_dest = os.path.join(templates_dir, t_dest)
    if os.path.exists(t_src):
        instantiate_from_template(t_src,\
                                  t_dest, \
                                  [("URL_PREFIX", URL_prefix)])

app = Flask(__name__)
app.config["DEBUG"] = False
# Note: may consider limiting CORS for production deployment
#       this opens up to AJAX calls from any domain
cors = CORS(app)

output = ""
req_args = {}

def serve_12x24(req_id, req_args):
  output_dest = os.path.join(outputs_dir, req_id)
  try:
      height, lat, lon, year_list = validated_params_v2_w_year(req_args)
      f = connected_hsds_file(req_args, config)

      # Time index can be obtained from f but reading it from a previously saved file is faster
      dt = pd.read_csv("wtk-dt.csv")
      dt["datetime"] = pd.to_datetime(dt["datetime"])
      dt["year"] = dt["datetime"].apply(lambda x: x.year)

      subsets=[]
      for yr in year_list:
          idx = dt[dt["year"] == yr].index
          subsets.append(getData(f, lat, lon, height,
                                  "IDW",
                                  power_estimate=False,
                                  inverse_monin_obukhov_length=False,
                                  start_time_idx=idx[0], end_time_idx=idx[-1], time_stride=1,
                                  saved_dt=dt))
      atmospheric_df = pd.concat(subsets)
      atmospheric_df.index = range(len(atmospheric_df))

  #     output = timeseries_to_12_by_24(atmospheric_df)
  #
  #     output_dest = os.path.join(outputs_dir, req_id)
  #     with open(output_dest, "w") as text_file:
  #         text_file.write(output)
  #     return
  # except Exception as e:
  #     output = "The following error has occurred:<br>" + str(e)
  #     with open(output_dest, "w") as text_file:
  #         text_file.write(output)
  #     return

      output_table = timeseries_to_12_by_24(atmospheric_df)

      output = "Selected location:<br><div id=\"infomap\"></div><br><br>" + \
      """
      <div classes="centered">
      <div>
        <table>
            <tr>
              <td>
              %s
              </td>
            </tr>
        </table>
      </div>
      </div>
      """ % output_table

      info = "Source of data: <a href=\"https://www.nrel.gov/grid/wind-toolkit.html\" target=\"_blank\" rel=\"noopener noreferrer\">NREL's WTK dataset</a>, covering 2007-2013."
      info += "<br><br>The shown subset of the model data includes %d timesteps between %s and %s." % \
        (len(atmospheric_df), atmospheric_df.datetime.tolist()[0], atmospheric_df.datetime.tolist()[-1])
      info += """<br><br>To get the shown point estimates, TAP API performed horizontal and vertical interpolation based on the TAP team's
       previous research published at: <a href=\"https://www.nrel.gov/docs/fy21osti/78412.pdf\" target=\"_blank\" rel=\"noopener noreferrer\">https://www.nrel.gov/docs/fy21osti/78412.pdf</a>.
       Specifically, the Inverse-Distance Weighting was used for horizontal interpolation and linear interpolation between the two adjacent heights in the model data was used for vertical interpolation.
       """
      json_output = {'output': output, "info": info}
      with open(output_dest, 'w') as f:
          json.dump(json_output, f)
      return
  except Exception as e:
      output = "The following error has occurred:<br>" + str(e)
      info = ""
      json_output = {'output': output, "info": info}
      with open(output_dest, 'w') as f:
          json.dump(json_output, f)
      return

def serve_monthly(req_id, req_args):
  output_dest = os.path.join(outputs_dir, req_id)
  try:
      height, lat, lon, year_list = validated_params_v2_w_year(req_args)
      f = connected_hsds_file(req_args, config)
      dt = pd.read_csv("wtk-dt.csv")
      dt["datetime"] = pd.to_datetime(dt["datetime"])
      dt["year"] = dt["datetime"].apply(lambda x: x.year)

      subsets=[]
      for yr in year_list:
          idx = dt[dt["year"] == yr].index
          subsets.append(getData(f, lat, lon, height,
                                 "IDW",
                                 power_estimate=False,
                                 inverse_monin_obukhov_length=False,
                                 start_time_idx=idx[0], end_time_idx=idx[-1], time_stride=1,
                                 saved_dt=dt))
      atmospheric_df = pd.concat(subsets)
      atmospheric_df.index = range(len(atmospheric_df))

      plot_monthly_avg(atmospheric_df, \
                       title="Location: (%f, %f), %.0fm hub height" % (lat, lon, height),\
                       save_to_file='static/saved.png',\
                       show_avg_across_years=True,
                       show_overall_avg=True,
                       show=False)
      #return flask.send_file('saved.png')


      output = "Selected location:<br><div id=\"infomap\"></div><br><br>" + \
      """
      <div classes="centered">
      <div>
        <table>
            <tr>
              <td><img id=\"monthly_plot\" src=\"static/saved.png\"/></td>
            </tr>
        </table>
      </div>
      </div>
      """
      # Adding info map after output
      #output += "<br><br>Selected location:<br><div id=\"infomap\"></div>"

      #info = "The shown dataset includes %d timesteps between %s and %s." % \
      #    (len(atmospheric_df), atmospheric_df.datetime.tolist()[0], atmospheric_df.datetime.tolist()[-1])

      info = "Source of data: <a href=\"https://www.nrel.gov/grid/wind-toolkit.html\" target=\"_blank\" rel=\"noopener noreferrer\">NREL's WTK dataset</a>, covering 2007-2013."
      info += "<br><br>The shown subset of model data includes %d timesteps between %s and %s." % \
        (len(atmospheric_df), atmospheric_df.datetime.tolist()[0], atmospheric_df.datetime.tolist()[-1])
      info += """<br><br>To get the shown point estimates, TAP API performed horizontal and vertical interpolation based on the TAP team's
       previous research published at: <a href=\"https://www.nrel.gov/docs/fy21osti/78412.pdf\" target=\"_blank\" rel=\"noopener noreferrer\">https://www.nrel.gov/docs/fy21osti/78412.pdf</a>.
       Specifically, the Inverse-Distance Weighting was used for horizontal interpolation and linear interpolation between the two adjacent heights in the model data was used for vertical interpolation.
       """

      # Adding info map inside the info collapsable box doesn't quite work; there is a strage display problem where map shows up partially
      #info += "<br><br>Selected location:<br><div id=\"infomap\"></div>"

      json_output = {'output': output, "info": info}
      with open(output_dest, 'w') as f:
          json.dump(json_output, f)
      return
  except Exception as e:
      output = "The following error has occurred:<br>" + str(e)
      info = ""
      json_output = {'output': output, "info": info}
      with open(output_dest, 'w') as f:
          json.dump(json_output, f)
      return

def serve_windrose(req_id, req_args):
  output_dest = os.path.join(outputs_dir, req_id)
  try:
      height, lat, lon, year_list = validated_params_v2_w_year(req_args)
      f = connected_hsds_file(req_args, config)
      dt = pd.read_csv("wtk-dt.csv")
      dt["datetime"] = pd.to_datetime(dt["datetime"])
      dt["year"] = dt["datetime"].apply(lambda x: x.year)

      subsets=[]
      for yr in year_list:
          idx = dt[dt["year"] == yr].index
          subsets.append(getData(f, lat, lon, height,
                                 "IDW",
                                 power_estimate=False,
                                 inverse_monin_obukhov_length=False,
                                 start_time_idx=idx[0], end_time_idx=idx[-1], time_stride=1,
                                 saved_dt=dt))
      atmospheric_df = pd.concat(subsets)
      atmospheric_df.index = range(len(atmospheric_df))

      plot_name = "%s/windrose_%s.png" % (plot_dir, req_id)
      plot_windrose(atmospheric_df, save_to_file=plot_name)

      output = "Selected location:<br><div id=\"infomap\"></div><br><br>" + \
      """
      <div classes="centered">
      <div>
        <table>
            <tr>
              <td><img id=\"windrose_plot\" src=\"%s\"/></td>
            </tr>
        </table>
      </div>
      </div>
      """ % plot_name

      info = "Source of data: <a href=\"https://www.nrel.gov/grid/wind-toolkit.html\" target=\"_blank\" rel=\"noopener noreferrer\">NREL's WTK dataset</a>, covering 2007-2013."
      info += "<br><br>The shown subset of model data includes %d timesteps between %s and %s." % \
        (len(atmospheric_df), atmospheric_df.datetime.tolist()[0], atmospheric_df.datetime.tolist()[-1])
      info += """<br><br>To get the shown point estimates, TAP API performed horizontal and vertical interpolation based on the TAP team's
       previous research published at: <a href=\"https://www.nrel.gov/docs/fy21osti/78412.pdf\" target=\"_blank\" rel=\"noopener noreferrer\">https://www.nrel.gov/docs/fy21osti/78412.pdf</a>.
       Specifically, the Inverse-Distance Weighting was used for horizontal interpolation and linear interpolation between the two adjacent heights in the model data was used for vertical interpolation.
       """

      # Adding info map inside the info collapsable box doesn't quite work; there is a strage display problem where map shows up partially
      #info += "<br><br>Selected location:<br><div id=\"infomap\"></div>"

      json_output = {'output': output, "info": info}
      with open(output_dest, 'w') as f:
          json.dump(json_output, f)
      return
  except Exception as e:
      output = "The following error has occurred:<br>" + str(e)
      info = ""
      json_output = {'output': output, "info": info}
      with open(output_dest, 'w') as f:
          json.dump(json_output, f)
      return

def serve_ts(req_id, req_args):
  output_dest = os.path.join(outputs_dir, req_id)
  try:
      height, lat, lon, year_list = validated_params_v2_w_year(req_args)
      f = connected_hsds_file(req_args, config)

      # Time index can be obtained from f but reading it from a previously saved file is faster
      dt = pd.read_csv("wtk-dt.csv")
      dt["datetime"] = pd.to_datetime(dt["datetime"])
      dt["year"] = dt["datetime"].apply(lambda x: x.year)

      subsets=[]
      for yr in year_list:
          idx = dt[dt["year"] == yr].index
          subsets.append(getData(f, lat, lon, height,
                                  "IDW",
                                  power_estimate=False,
                                  inverse_monin_obukhov_length=False,
                                  start_time_idx=idx[0], end_time_idx=idx[-1], time_stride=1,
                                  saved_dt=dt))
      atmospheric_df = pd.concat(subsets)
      atmospheric_df.index = range(len(atmospheric_df))
      atmospheric_df = atmospheric_df.round(3)
      if "Unnamed: 0" in atmospheric_df.columns:
          atmospheric_df.drop(columns=["Unnamed: 0"], inplace=True)
      if "year" in atmospheric_df.columns:
          # Year is redundant if datetime is there
          atmospheric_df.drop(columns=["year"], inplace=True)

      # Saving to file
      csv_dest = "%s/ts-%s.csv" % (csv_dir, req_id)
      atmospheric_df.to_csv(csv_dest, index=False)

      output = atmospheric_df.to_csv(index=False).replace("\n", "<br>")
      #info = ""

      info = "Source of data: <a href=\"https://www.nrel.gov/grid/wind-toolkit.html\" target=\"_blank\" rel=\"noopener noreferrer\">NREL's WTK dataset</a>, covering 2007-2013."
      info += "<br><br>The shown subset of model data includes %d timesteps between %s and %s." % \
        (len(atmospheric_df), atmospheric_df.datetime.tolist()[0], atmospheric_df.datetime.tolist()[-1])
      info += """<br><br>To get the shown point estimates, TAP API performed horizontal and vertical interpolation based on the TAP team's
       previous research published at: <a href=\"https://www.nrel.gov/docs/fy21osti/78412.pdf\" target=\"_blank\" rel=\"noopener noreferrer\">https://www.nrel.gov/docs/fy21osti/78412.pdf</a>.
       Specifically, the Inverse-Distance Weighting was used for horizontal interpolation and linear interpolation between the two adjacent heights in the model data was used for vertical interpolation.
       """

      #save = "Download: static/raw/ts-%s.csv" % req_id
      proposed_fname="%.6f_%.6f_%.1f.csv" % (lat, lon, height)
      save = "href=\"%s\" download=\"%s\"" % (csv_dest, proposed_fname)
      # Example: href="static/raw/ts-cd5e6247a3b935d7770bb1657df34715.csv" download="39.7430_-105.1470_65.000000.csv"
      # it will be added inside the  <a> tag

      json_output = {'output': output, "info": info, "save": save}
      with open(output_dest, 'w') as f:
          json.dump(json_output, f)
      return
  except Exception as e:
      output = "The following error has occurred:<br>" + str(e)
      info = ""
      save = ""
      json_output = {'output': output, "info": info, "save": save}
      with open(output_dest, 'w') as f:
          json.dump(json_output, f)
      return

def serve_bc(req_id, req_args):
  output_dest = os.path.join(outputs_dir, req_id)
  try:
      height, lat, lon, year_list = validated_params_v2_w_year(req_args)
      f = connected_hsds_file(req_args, config)
      dt = pd.read_csv("wtk-dt.csv")
      dt["datetime"] = pd.to_datetime(dt["datetime"])
      dt["year"] = dt["datetime"].apply(lambda x: x.year)

      subsets=[]
      for yr in year_list:
          idx = dt[dt["year"] == yr].index
          subsets.append(getData(f, lat, lon, height,
                                 "IDW",
                                 power_estimate=False,
                                 inverse_monin_obukhov_length=False,
                                 start_time_idx=idx[0], end_time_idx=idx[-1], time_stride=1,
                                 saved_dt=dt))
      atmospheric_df = pd.concat(subsets)
      atmospheric_df.index = range(len(atmospheric_df))

      # plot_monthly_avg(atmospheric_df, \
      #                  title="Location: (%f, %f), %.0fm hub height" % (lat, lon, height),\
      #                  save_to_file='static/saved.png',\
      #                  show_avg_across_years=True,
      #                  show_overall_avg=True,
      #                  show=False)
      # #return flask.send_file('saved.png')

      # output = """
      # <div classes="centered">
      # <div>
      #   <table>
      #       <tr>
      #         <td><img id=\"monthly_plot\" src=\"static/saved.png\"/></td>
      #       </tr>
      #   </table>
      # </div>
      # </div>
      # """

      # Ordered list of BC data locations; supports running inside ECS container and locally
      # Code below will find first existing and will proceed to using it
      bc_locs = ["/bc/bc_v4/", "~/OneDrive - NREL/dw-tap-data/bc_development/bc_v4/"]
      selected_bc_loc = None
      for bc_loc in bc_locs:
          d = os.path.expanduser(bc_loc)
          if os.path.isdir(d):
              selected_bc_loc = d
      if not (selected_bc_loc):
          output = """
          <div classes="centered">
          Unable to locate directory with BC data. Checked locations: %s.
          </div>
          """ % str(bc_locs)
          info = ""
      else:
          # Todo: check to make sure that atmospheric_df is not empty

          output, bc_info = bc_for_point(lon=lon, lat=lat, height=height, \
                                      model_data=atmospheric_df, \
                                      bc_dir=selected_bc_loc,\
                                      plot_dest = 'static/bc.png') # plot_dest="outputs/fig-%s.png" % req_id)

          basic_info = "Source of data: <a href=\"https://www.nrel.gov/grid/wind-toolkit.html\" target=\"_blank\" rel=\"noopener noreferrer\">NREL's WTK dataset</a>, covering 2007-2013."
          basic_info += "<br><br>The shown subset of model data includes %d timesteps between %s and %s." % \
                        (len(atmospheric_df), atmospheric_df.datetime.tolist()[0], atmospheric_df.datetime.tolist()[-1])
          basic_info += """<br><br>To get the shown point estimates, TAP API performed horizontal and vertical interpolation based on the TAP team's
                 previous research published at: <a href=\"https://www.nrel.gov/docs/fy21osti/78412.pdf\" target=\"_blank\" rel=\"noopener noreferrer\">https://www.nrel.gov/docs/fy21osti/78412.pdf</a>.
                 Specifically, the Inverse-Distance Weighting was used for horizontal interpolation and linear interpolation between the two adjacent heights in the model data was used for vertical interpolation.
                 """

          info = basic_info + "<br><br> Additionally, <strong>bias correction (BC)</strong> was applied to the point estimates. Details:<br><br>" + bc_info
          #info = "The shown dataset includes %d timesteps between %s and %s." % \
          #    (len(atmospheric_df), atmospheric_df.datetime.tolist()[0], atmospheric_df.datetime.tolist()[-1])

      json_output = {'output': output, "info": info}
      with open(output_dest, 'w') as f:
          json.dump(json_output, f)
      return
  except Exception as e:
      output = "The following error has occurred:<br>" + str(e)
      info = ""
      json_output = {'output': output, "info": info}
      with open(output_dest, 'w') as f:
          json.dump(json_output, f)
      return

def serve_kwh(req_id, req_args):
  output_dest = os.path.join(outputs_dir, req_id)
  try:

      height, lat, lon, year_list = validated_params_v2_w_year(req_args)
      if 'pc' in req_args:
          pc = req_args['pc']
          if not (pc in powercurves.keys()):
              pc = powercurve_default
      else:
          pc = powercurve_default

      f = connected_hsds_file(req_args, config)

      # Time index can be obtained from f but reading it from a previously saved file is faster
      dt = pd.read_csv("wtk-dt.csv")
      dt["datetime"] = pd.to_datetime(dt["datetime"])
      dt["year"] = dt["datetime"].apply(lambda x: x.year)

      subsets=[]
      for yr in year_list:
          idx = dt[dt["year"] == yr].index
          subsets.append(getData(f, lat, lon, height,
                                  "IDW",
                                  power_estimate=False,
                                  inverse_monin_obukhov_length=False,
                                  start_time_idx=idx[0], end_time_idx=idx[-1], time_stride=1,
                                  saved_dt=dt))
      atmospheric_df = pd.concat(subsets)
      atmospheric_df.index = range(len(atmospheric_df))
      if "Unnamed: 0" in atmospheric_df.columns:
          atmospheric_df.drop(columns=["Unnamed: 0"], inplace=True)
      atmospheric_df['year'] = atmospheric_df['datetime'].dt.year
      atmospheric_df['month'] = atmospheric_df['datetime'].dt.month
      atmospheric_df["Month-Year"] = atmospheric_df['month'].astype(str).apply(lambda x: x.zfill(2)) + "-" + atmospheric_df['year'].astype(str)

      # Add power colum
      atmospheric_df["kw"] = powercurves[pc].windspeed_to_kw(atmospheric_df, 'ws')

      # Calculate the time difference between consecutive rows
      atmospheric_df['interval_hrs'] = atmospheric_df['datetime'].diff().fillna(pd.Timedelta(seconds=0)).dt.components.hours

      # Energy as the power * time product
      atmospheric_df["kwh"] = atmospheric_df["kw"] * atmospheric_df['interval_hrs']

      atmospheric_df_agg = atmospheric_df.groupby("Month-Year").agg(avg_ws=("ws", "mean"), \
      median_ws=("ws", "median"), \
      energy_total=("kwh", "sum"))
      atmospheric_df_agg.rename(columns={"avg_ws": "Avg. wind speed, m/s", "median_ws": "Median wind speed, m/s", "energy_total": "Energy produced, kWh"}, \
      inplace=True)
      atmospheric_df_agg = atmospheric_df_agg.round(3)

      # Add summary row
      atmospheric_df_agg = pd.concat([atmospheric_df_agg,\
      pd.DataFrame([{"Avg. wind speed, m/s": "Overall avg.: %.3f" % (atmospheric_df_agg["Avg. wind speed, m/s"].mean()),\
                     "Median wind speed, m/s": "Overall median: %.3f" % (atmospheric_df["ws"].median()),\
                     "Energy produced, kWh": "Total: %.3f" % (atmospheric_df_agg["Energy produced, kWh"].sum())}], index=["Summary"])])

      output_table = atmospheric_df_agg.to_html(classes='energy_table')

      output = "Selected location:<br><div id=\"infomap\"></div><br><br>" + \
      """
      <div classes="centered">
      <div>
        <table>
            <tr>
              <td>
              %s
              </td>
            </tr>
        </table>
      </div>
      </div>
      """ % output_table

      #output = str(atmospheric_df.head()).replace("\n", "<br>")

      info = "Source of data: <a href=\"https://www.nrel.gov/grid/wind-toolkit.html\" target=\"_blank\" rel=\"noopener noreferrer\">NREL's WTK dataset</a>, covering 2007-2013."
      info += "<br><br>The shown subset of the model data includes %d timesteps between %s and %s." % \
        (len(atmospheric_df), atmospheric_df.datetime.tolist()[0], atmospheric_df.datetime.tolist()[-1])
      info += """<br><br>To get the shown point estimates, TAP API performed horizontal and vertical interpolation based on the TAP team's
       previous research published at: <a href=\"https://www.nrel.gov/docs/fy21osti/78412.pdf\" target=\"_blank\" rel=\"noopener noreferrer\">https://www.nrel.gov/docs/fy21osti/78412.pdf</a>.
       Specifically, the Inverse-Distance Weighting was used for horizontal interpolation and linear interpolation between the two adjacent heights in the model data was used for vertical interpolation.
       """
      info += "<br><br>Selected power curve: %s" % pc

      json_output = {'output': output, "info": info}
      with open(output_dest, 'w') as f:
          json.dump(json_output, f)
      return
  except Exception as e:
      output = "The following error has occurred:<br>" + str(e)
      info = ""
      json_output = {'output': output, "info": info}
      with open(output_dest, 'w') as f:
          json.dump(json_output, f)
      return


@app.route('/output', methods=['GET'])
def get_output():
    """ Check if output file for requested req_id has been cretead and, if so, return its contents as part of a json in the form expected by the js in html page """
    req_args = request.args
    if 'req_id' in req_args:
        req_id = request.args['req_id']
        output_path = os.path.join(outputs_dir, req_id)
        if os.path.exists(output_path):
            output = open(output_path, 'r').read()
        else:
            output = {'output': "", "info": ""}
    else:
        output = {'output': "", "info": ""}
    return output

@app.route('/infomap', methods=['GET'])
def get_infomap():
    req_args = request.args

    if not ('lat' in req_args):
        return ""
    if not ('lon' in req_args):
        return ""

    try:
        lat = float(req_args["lat"])
        lon = float(req_args["lon"])
        #return get_infomap_script(lat, lon)

        # The following should solve the issue "Refused to execite script because "X-Content-Type-Options: nosniff" was given and its Content-Type is not a script MIME type"
        return Response(get_infomap_script(lat, lon), mimetype='text/javascript')
    except Exception as e:
        return ""

@app.route('/addr_to_latlon', methods=['GET'])
def addr_to_latlon():
    """ Translate a request with an address to a lat/lon"""
    req_args = request.args
    if 'addr' in req_args:
        addr = request.args['addr']
        try:
            url = 'https://nominatim.openstreetmap.org/search?q=' + urllib.parse.quote(addr) +'&format=json'
            response = requests.get(url).json()
            return json.dumps({"latlon": "lat=%s&lon=%s" % (response[0]["lat"], response[0]["lon"])})
        except Exception as e:
            # "Error" at the beginning is important; js will be looking for it in the returned string to handle the error cases
            latlon = "Error: OpenStreetMap's API was unable to find lat/lon for the given address.<br>\
            Provide valid address and try again.<br>Keep in mind that OpenStreetMap may not provide info for addresses with special restrictions.<br>\
            If unable to use the desired address, try using <a href=\"%s/on_map\">this interface</a> and choose the location on the map." % URL_prefix
            return json.dumps({"latlon": latlon})
    else:
        return json.dumps({"latlon": ""})

    # address = '1840 Alkire Ct, Golden, CO 80401'
    # url = 'https://nominatim.openstreetmap.org/search?q=' + urllib.parse.quote(address) +'&format=json'
    # response = requests.get(url).json()
    # return response[0]["lat"] + "   " + response[0]["lon"]

@app.route('/testing', methods=['GET'])
def testing():
    return render_template("testing.html")


@app.route('/by_address', methods=['GET'])
def by_address():
    return render_template("by_address.html")

@app.route('/on_map', methods=['GET'])
def on_map():
    return render_template("on_map.html")

# Old version: serving WindWatts at /map
#@app.route('/map', methods=['GET'])
#def map():
#    return render_template("on_map3.html", google_maps_api_key=given_google_maps_api_key)

@app.route('/', methods=['GET'])
def map():
   return render_template("on_map3.html", google_maps_api_key=given_google_maps_api_key)

def process_year_input(year_raw):

    if len(year_raw) > 0:
        # Remove spaces
        year_raw = year_raw.replace(" ","")
        try:
            year_list_full = []
            # Works for a list of years and also for a single year
            year_list = year_raw.split(",")
            for el in year_list:
                if "-" in el:
                    # Year range with a dash
                    year_start, year_end = int(el.split("-")[0]), int(el.split("-")[1])
                    for x in range(year_start, year_end + 1):
                        year_list_full.append(x)
                else:
                    # Single year
                    year_list_full.append(int(el))
            year_list = year_list_full

        except ValueError:
            raise InvalidUsage(("Year needs to be an integer or a comma-separated list of integers."))
    else:
        # Use latest year if not specified
        year_list = [2013]

    for yr in year_list:
        if yr < 2007 or yr > 2013:
            raise InvalidUsage("Each selected year needs to be between 2007 and 2013. One of the selected years: %s" % str(yr))

    # unique and sorted
    year_list = sorted(list(set(year_list)))
    return year_list

def feasibility_test(estimate, thresh, result_prefix=True):
    if estimate > thresh:
        sign = ">"
        if result_prefix:
            result = "Result: feasible &#10004;"
        else:
            result = "feasible &#10004;"
    else:
        sign = "<"
        if result_prefix:
            result = "Result: not feasible &#10007;"
        else:
            result = "not feasible &#10007;"
    return sign, result

def daily_udf_to_summary(udf):
    """ Use daily uncertainty to create a summary """
    p50 = udf["percentile_50"].mean()
    p25 = udf["percentile_25"].mean()
    p75 = udf["percentile_75"].mean()

    p25_percent_diff_from_p50 = (p50 - p25) / p50 * 100
    p75_percent_diff_from_p50 = (p75 - p50) / p50 * 100
    #return p25, p50, p75, p25_percent_diff_from_p50, p75_percent_diff_from_p50

    summary = """
                    <p class="results_disclaimer_text"><span>OLD CONTENT BELOW. TO BE UPDATED.</span></p><br><br>
                    <table border="0" cellspacing="10" class="yearly_table">
                    	<tbody>
                    		<tr>
                    			<td><span class="yearly_table_metric">Average daily 25th percentile:</td>
                                <td><span class="yearly_table_metric">Average daily median:</td>
                                <td><span class="yearly_table_metric">Average daily 75th percentile:</td>
                    		</tr>
                    		<tr>
                    			<td><span class="yearly_table_value">%.2f</span></td>
                                <td><span class="yearly_table_value">%.2f</span></td>
                                <td><span class="yearly_table_value">%.2f</span></td>
                    		</tr>
                    		<tr>
                    			<td><span class="yearly_table_value">-%.2f%%</span> from avg. daily median</td>
                                <td></td>
                                <td><span class="yearly_table_value">%.2f%%</span> from avg. daily median</span></td>
                    		</tr>
                    	</tbody>
                    </table>
                """ % (p25, p50, p75, p25_percent_diff_from_p50, p75_percent_diff_from_p50)

    summary += """
        <br><hr><br>
        <table border="0" cellspacing="10" class="feasibility_desc_table">
            <tbody>
                <tr>
                    <td>This analysis is performed using WTK-LED's daily uncertainty data for 2018 at 40 meters [More info to be added].
                    <br><br>The identified range, <span class="yearly_table_value">[-%.2f%%, %.2f%%]</span>, characterizes model uncertainty,
                    and the overall statistics like the all-time wind speed average displayed at the top have at least this much uncertainty.</td>
                </tr>
            </tbody>
        <table>
        """ % (p25_percent_diff_from_p50, p75_percent_diff_from_p50)
    return summary

def ws_to_level(ws, moderate_resource_thresh_ms, high_resource_thresh_ms):
    if ws < moderate_resource_thresh_ms:
        return "Low"
    elif ws >= moderate_resource_thresh_ms and ws < high_resource_thresh_ms:
        return "Moderate"
    else:
        return "High"

def serve_data_request(data):
    try:
        id = data["id"]

        # Creates an empty pending file
        # with open(os.path.join(pending_dir, id), 'w') as fp:
        #     pass

        year_list = process_year_input(data["years"])
        #f = connected_hsds_file(req_args, config) # Need for hsds requests (not needed for WTK-LED s3 fetching)

        # Time index can be obtained from f but reading it from a previously saved file is faster
        dt = pd.read_csv("wtk-dt.csv")
        dt["datetime"] = pd.to_datetime(dt["datetime"])
        dt["year"] = dt["datetime"].apply(lambda x: x.year)
        selected_powercurve = powercurves[data["powercurve"]]

        closest_height = float(data["height"])
        ws_column = "windspeed_" + str(int(data["height"])) + "m"
        wd_column = ws_column.replace("windspeed", "winddirection")
        kw_column = "windspeed_" + str(int(data["height"])) + "m" + "_kw"

        # New code for WTK-LED (WTK is a default handled below this if)
        if data["datasource"] == "WTK-LED":
            print("Serving data for WTK-LED request")

            output_dest = os.path.join(completed_dir, id)

            # Fetching WTK-LED
            #point = closest_grid_point(wtkled_index, data["lat"], data["lon"])
            #df_1224_20years = get_1224_20yrs(point['index'], ws_column, selected_powercurve, relevant_columns_only=True)
            #print("obtained df_1224_20years:")
            #print(df_1224_20years.head())

            attempt_lim = 5
            error_str = ""
            for attempt in range(attempt_lim):
                try:
                    error_str = ""
                    print("Fetching WTK-LED data. Attempt: %d of %d" % (attempt, attempt_lim))
                    point = closest_grid_point(wtkled_index, data["lat"], data["lon"])
                    df_1224_20years = get_1224_20yrs(point['index'], ws_column, selected_powercurve, relevant_columns_only=True)
                except Exception as e:
                    print("Error in fetching WTK-LED data. Will wait a little and try again")
                    print("Exception: %s" % str(e))
                    error_str = "An error occurred during fetching WTK-LED data. If it is an intermittent, network issue, may need to try again later! To help with troubleshooting, here is the error message: %s" % str(e)
                    time.sleep(0.5)
                    continue
                else:
                    print("Fetching WTK-LED data was successful")
                    error_str = ""
                    break

            if error_str:
                with open(output_dest, 'w') as f:
                    json.dump({"error": error_str}, f)
                print("Saved error info to: %s" % output_dest)
                return

            yearly_df = df2yearly_avg(df_1224_20years, ws_column, kw_column)
            kwh_produced_avg_year = yearly_df["kWh produced"].tolist()[1] # Average year comes after the lowest
            monthly_df = df2monthly_avg(df_1224_20years, ws_column, kw_column)

            overall_mean = df_1224_20years[ws_column].mean()

            feasibility_thresh = feasibility_thresh_by_height(float(data["height"]))
            moderate_resource_thresh_ms = feasibility_thresh - 1.0
            high_resource_thresh_ms = feasibility_thresh + 1.0
            ws_level = ws_to_level(overall_mean, moderate_resource_thresh_ms, high_resource_thresh_ms)

            #udf = get_uncertainty_dataframe(point['index'])
            #udf['doy'] = udf.index # assume the day of year is the index, which would be true once all 12 months of data are present
            #uncertainty_summary = daily_udf_to_summary(udf)

            #udf['iqr'] = udf['percentile_75'] - df['percentile_25'] # compute inter quartile range
            #udf['uncertainty'] = udf['percentile_95'] - udf['percentile_5'] # compute inter quartile range
            #udf

            summary = summary_to_html(float(data["lat"]), float(data["lon"]), closest_height, data["powercurve"], overall_mean, ws_level, kwh_produced_avg_year)

            windrose_plot_name = "%s/%s_windrose.png" % (plot_dir, id)
            plot_windrose(df_1224_20years, ws_column, wd_column, save_to_file=windrose_plot_name)

            windresource = windresource_to_html(overall_mean, \
                ws_level, \
                moderate_resource_thresh_ms=feasibility_thresh-1.0,\
                high_resource_thresh_ms=feasibility_thresh+1.0,\
                closest_height=closest_height, \
                windrose_plot_name=windrose_plot_name)



            # Rounding
            #yearly_df = yearly_df.round(2)
            #monthly_df = monthly_df.round(2)
            #udf = udf.round(2)

            #data = yearly_avg_closest_heights.to_html(classes="detailed_yearly_table")
            energyproduction = energyproduction_to_html(monthly_df, yearly_df)

            #uncertainty_data = udf.to_html(classes="detailed_yearly_table")

            with open(output_dest, 'w') as f:
                json.dump({"wtk_led_summary": summary, "wtk_led_windresource": windresource,
                    "wtk_led_energyproduction": energyproduction}, #, \
                    #"uncertainty_summary": uncertainty_summary, \
                    #"uncertainty_data": uncertainty_data},\
                f)
            print("Saved output to: %s" % output_dest)

        else: # WTK dataset

            subsets=[]

            for yr in year_list:
                idx = dt[dt["year"] == yr].index
                df = getData(f, float(data["lat"]), float(data["lon"]), float(data["height"]),
                                        "IDW",
                                        power_estimate=False,
                                        inverse_monin_obukhov_length=False,
                                        start_time_idx=idx[0], end_time_idx=idx[-1], time_stride=1,
                                        saved_dt=dt)
                print(df.head())
                subsets.append(df)
            atmospheric_df = pd.concat(subsets)
            atmospheric_df.index = range(len(atmospheric_df))
            atmospheric_df = atmospheric_df.round(3)
            if "Unnamed: 0" in atmospheric_df.columns:
                atmospheric_df.drop(columns=["Unnamed: 0"], inplace=True)
            if "year" in atmospheric_df.columns:
                # Year is redundant if datetime is there
                atmospheric_df.drop(columns=["year"], inplace=True)

            if data["output_type"] == "raw":
                output_dest = os.path.join(completed_dir, id)
                with open(output_dest, 'w') as f:
                    json.dump({"raw": atmospheric_df.to_csv(index=False).replace("\n", "<br>")}, f)
                print("Saved output to: %s" % output_dest)
            else:
                # Assume data["output_type"] == "report" (only 2 options are available now)

                output_dest = os.path.join(completed_dir, id)

                plot_dest = os.path.join(plot_dir, "monthly-%s.png" % id)
                plot_monthly_avg(atmospheric_df, \
                               title="Location: (%f, %f), %.0fm hub height" % (float(data["lat"]), float(data["lon"]), float(data["height"])),\
                               save_to_file=plot_dest,\
                               show_avg_across_years=True,
                               show_overall_avg=True,
                               show=False)
                #return flask.send_file('saved.png')

                output_monthly = """
                <div class="centered">
                <div>
                <table>
                    <tr>
                      <td><img id=\"monthly_plot\" src=\"%s\"/></td>
                    </tr>
                </table>
                </div>
                </div>
                """ % plot_dest

                output_12x24_table = timeseries_to_12_by_24(atmospheric_df)
                output_12x24 = """
                <div class="centered">
                <div>
                <table>
                    <tr>
                      <td>
                      %s
                      </td>
                    </tr>
                </table>
                </div>
                </div>
                """ % output_12x24_table

                plot_dest = os.path.join(plot_dir, "windrose_-%s.png" % id)
                plot_windrose(atmospheric_df, save_to_file=plot_dest)
                output_windrose = """
                <div class="centered">
                    <img id=\"windrose_plot\" src=\"%s\"/></td>
                </div>
                """ % plot_dest

                if data["powercurve"] in powercurves.keys():
                    pc = data["powercurve"]

                    atmospheric_df['year'] = atmospheric_df['datetime'].dt.year
                    atmospheric_df['month'] = atmospheric_df['datetime'].dt.month
                    atmospheric_df["Month-Year"] = atmospheric_df['month'].astype(str).apply(lambda x: x.zfill(2)) + "-" + atmospheric_df['year'].astype(str)
                    # Add power colum
                    atmospheric_df["kw"] = powercurves[pc].windspeed_to_kw(atmospheric_df, 'ws')
                    # Calculate the time difference between consecutive rows
                    atmospheric_df['interval_hrs'] = atmospheric_df['datetime'].diff().fillna(pd.Timedelta(seconds=0)).dt.components.hours

                    # Energy as the power * time product
                    atmospheric_df["kwh"] = atmospheric_df["kw"] * atmospheric_df['interval_hrs']

                    atmospheric_df_agg = atmospheric_df.groupby("Month-Year").agg(avg_ws=("ws", "mean"), \
                        median_ws=("ws", "median"), \
                        energy_total=("kwh", "sum"))
                    atmospheric_df_agg.rename(columns={"avg_ws": "Avg. wind speed, m/s", "median_ws": "Median wind speed, m/s", "energy_total": "Energy produced, kWh"}, \
                        inplace=True)
                    atmospheric_df_agg = atmospheric_df_agg.round(3)

                    # Add summary row
                    atmospheric_df_agg = pd.concat([atmospheric_df_agg,\
                        pd.DataFrame([{"Avg. wind speed, m/s": "Overall avg.: %.3f" % (atmospheric_df_agg["Avg. wind speed, m/s"].mean()),\
                                       "Median wind speed, m/s": "Overall median: %.3f" % (atmospheric_df["ws"].median()),\
                                       "Energy produced, kWh": "Total: %.3f" % (atmospheric_df_agg["Energy produced, kWh"].sum())}], index=["Summary"])])

                    energy_table = atmospheric_df_agg.to_html(classes='energy_table')

                    output_energy = """
                    <div classes="centered">
                    <div>%s</div>
                    </div>
                    """ % energy_table
                else:
                    output_energy = ""

                info = "Source of data: <a href=\"https://www.nrel.gov/grid/wind-toolkit.html\" target=\"_blank\" rel=\"noopener noreferrer\">NREL's WTK dataset</a>, covering 2007-2013."
                info += "<br><br>The shown subset of the model data includes %d timesteps between %s and %s." % \
                    (len(atmospheric_df), atmospheric_df.datetime.tolist()[0], atmospheric_df.datetime.tolist()[-1])
                info += """<br><br>To get the shown point estimates, TAP API performed horizontal and vertical interpolation based on the TAP team's
                previous research published at: <a href=\"https://www.nrel.gov/docs/fy21osti/78412.pdf\" target=\"_blank\" rel=\"noopener noreferrer\">https://www.nrel.gov/docs/fy21osti/78412.pdf</a>.
                Specifically, the Inverse-Distance Weighting was used for horizontal interpolation and linear interpolation between the two adjacent heights in the model data was used for vertical interpolation.
                """

                with open(output_dest, 'w') as f:
                    json.dump({"monthly": output_monthly, "12x24": output_12x24, "windrose": output_windrose, "energy": output_energy, "info": info}, f)

                print("Saved output to: %s" % output_dest)

    except Exception as e:
        print("error: " + str(e))
        output = "Error: " + str(e)


@app.route('/1224', methods=['GET'])
def serve_1224():
    """ Endpoint serving WTK-LED 12x24 data for 20 years.

    Access it at using URLs like: <hostname>:<port>/1224?lat=39.76004&lon=-105.14058
    """

    lat, lon = validated_latlon(request)
    point = closest_grid_point(wtkled_index, lat, lon)
    df_1224_20years = get_1224_20yrs(point['index'],
        ws_col_for_estimating_power="nonexistent_column", # This helps avoid power estimation
        selected_powercurve=None, # No power estimation
        relevant_columns_only=False) # Show all columns/data instead of a subset
    return df_1224_20years.to_csv(index=False)

# API/documentation route
@app.route('/api', methods=['GET'])
def api():
    # Serve documentation produced by apiDoc
    return flask.send_file('docs/index.html')

@app.route('/data_request', methods=['POST', 'GET'])
def data_request():
    if request.method == 'GET':
        # Check if output file for requested req_id has been cretead and,
        # if so, return its contents as part of a json """
        req_args = request.args
        if 'id' in req_args:
            id = request.args['id']
            if id == "":
                output = {}
            else:
                output_path = os.path.join(completed_dir, id)
                if os.path.exists(output_path):
                    output = open(output_path, 'r').read()
                else:
                    output = {}
        else:
            output = {}
        return output

    elif request.method == 'POST':
        # POST is used when the page requests new data
        data = json.loads(request.data)
        serve_data_request(data)
        return data


@app.route('/energy', methods=['GET'])
def energy():
    return render_template("energy.html")

@app.route('/status', methods=['GET'])
def status():
    """ Minimal simple status with env info and check for hsds """
    output = "Server started at: " + str(server_started_at) + "<br>"
    output += "Running in AWS? " + str(running_in_aws) + "<br>"
    output += "Host: " + str(host) + "<br>"
    output += "Port: " + str(port) + "<br>"
    output += "URL_prefix: " + URL_prefix + "<br>"
    output += "Google Maps API key: %s<br>" % ("provided" if given_google_maps_api_key else "not provided")
    req_args = request.args
    try:
        f = connected_hsds_file(req_args, config)
        output += "Successfully connected to HSDS.<br>"
    except Exception as e:
        output += "Can't connect to HSDS. Error:<br>" + str(e)

    output += "WTK-LED index: %d columns, %d rows" % (len(wtkled_index.columns), len(wtkled_index))
    return output

#@app.route('/', methods=['GET'])
#def serve_slash():
#    return render_template("info.html")

#@app.route('/', methods=['GET'])
@app.route('/<path:path>')
def root(path):
    """ Main routine that servies multiple endpoints """
    current_time = datetime.datetime.utcnow()

    req_args = request.args

    # Simply using request.endpoint doesn't work; it is set to root (name of this func)
    req_endpoint = request.base_url.split("/")[-1]

    # Prepare request info for hashing
    # For request http://localhost:5000/testing?b=3&a=5
    # string to be hashed is: "2024-02-01 23:05:26.905643testinga5b3"
    hashing_src = str(current_time)
    hashing_src += req_endpoint
    for k in sorted(req_args.keys()):
        hashing_src += str(k)+str(req_args[k])

    # Hash becomes the request ID
    req_id = hashlib.md5(hashing_src.encode()).hexdigest() # example: 5ac99a3648385a2230ade76b3f92df0c (unique ID for a request)

    if req_endpoint == "12x24":
        th = Thread(target=serve_12x24, args=(req_id, req_args))
        th.start()

        html_name = "12x24_%s.html" % req_id
        height, lat, lon, year_list = validated_params_v2_w_year(req_args)

        # Copy from a template and replace the string that has the endpoint for fetching outputs from
        # instantiate_from_template(os.path.join(templates_dir, "12x24_index.html"),\
        #                           os.path.join(templates_dir, "served", html_name),
        #                           old_text="const FETCH_STR = \"/output?req_id=NEED_SPECIFIC_REQ_ID\";",\
        #                           new_text="const FETCH_STR = \"/output?req_id=%s\";" % req_id)
        instantiate_from_template(os.path.join(templates_dir, "12x24_index.html"),\
                                  os.path.join(templates_dir, "served", html_name),\
                                  [("const FETCH_STR = \"/output?req_id=NEED_SPECIFIC_REQ_ID\";", \
                                  "const FETCH_STR = \"/output?req_id=%s\";" % req_id),\
                                  ("const lat = \"NEED_SPECIFIC_LAT\";",\
                                  "const lat = %.6f;" % lat),\
                                  ("const lon = \"NEED_SPECIFIC_LON\";",\
                                  "const lon = %.6f;" % lon)])

        return render_template(os.path.join("served", html_name))

    elif req_endpoint == "monthly":

        # Step 1: spin up a separate thread for processing
        th = Thread(target=serve_monthly, args=(req_id, req_args))
        th.start()

        # Step 2: from monthly_index.html create html inside served/ for specic request, with specifif lat & lon
        # Universal here means that the template can be used for AWS and non-AWS envs
        html_name = "monthly_%s.html" % req_id
        height, lat, lon, year_list = validated_params_v2_w_year(req_args)

        # Copy from a template and replace the string that has the endpoint for fetching outputs from
        # instantiate_from_template(os.path.join(templates_dir, "monthly_index.html"),\
        #                           os.path.join(templates_dir, "served", html_name),
        #                           old_text="const FETCH_STR = \"/output?req_id=NEED_SPECIFIC_REQ_ID\";",\
        #                           new_text="const FETCH_STR = \"/output?req_id=%s\";" % req_id)
        instantiate_from_template(os.path.join(templates_dir, "monthly_index.html"),\
                                  os.path.join(templates_dir, "served", html_name),\
                                  [("const FETCH_STR = \"/output?req_id=NEED_SPECIFIC_REQ_ID\";",\
                                  "const FETCH_STR = \"/output?req_id=%s\";" % req_id),\
                                  ("const lat = \"NEED_SPECIFIC_LAT\";",\
                                  "const lat = %.6f;" % lat),\
                                  ("const lon = \"NEED_SPECIFIC_LON\";",\
                                  "const lon = %.6f;" % lon)])

        # Step 3: Render the final, filled out template
        return render_template(os.path.join("served", html_name))

    elif req_endpoint == "windrose":

        # Step 1: spin up a separate thread for processing
        th = Thread(target=serve_windrose, args=(req_id, req_args))
        th.start()

        # Step 2: from monthly_index.html create html inside served/ for specic request, with specifif lat & lon
        # Universal here means that the template can be used for AWS and non-AWS envs
        html_name = "windrose_%s.html" % req_id
        height, lat, lon, year_list = validated_params_v2_w_year(req_args)

        # Copy from a template and replace the string that has the endpoint for fetching outputs from
        # instantiate_from_template(os.path.join(templates_dir, "monthly_index.html"),\
        #                           os.path.join(templates_dir, "served", html_name),
        #                           old_text="const FETCH_STR = \"/output?req_id=NEED_SPECIFIC_REQ_ID\";",\
        #                           new_text="const FETCH_STR = \"/output?req_id=%s\";" % req_id)
        instantiate_from_template(os.path.join(templates_dir, "windrose_index.html"),\
                                  os.path.join(templates_dir, "served", html_name),\
                                  [("const FETCH_STR = \"/output?req_id=NEED_SPECIFIC_REQ_ID\";",\
                                  "const FETCH_STR = \"/output?req_id=%s\";" % req_id),\
                                  ("const lat = \"NEED_SPECIFIC_LAT\";",\
                                  "const lat = %.6f;" % lat),\
                                  ("const lon = \"NEED_SPECIFIC_LON\";",\
                                  "const lon = %.6f;" % lon)])

        # Step 3: Render the final, filled out template
        return render_template(os.path.join("served", html_name))

    elif req_endpoint == "ts":
        th = Thread(target=serve_ts, args=(req_id, req_args))
        th.start()

        html_name = "ts_%s.html" % req_id

        # Copy from a template and replace the string that has the endpoint for fetching outputs from
        # instantiate_from_template(os.path.join(templates_dir, "ts_index.html"),\
        #                           os.path.join(templates_dir, "served", html_name),
        #                           old_text="const FETCH_STR = \"/output?req_id=NEED_SPECIFIC_REQ_ID\";",\
        #                           new_text="const FETCH_STR = \"/output?req_id=%s\";" % req_id)
        instantiate_from_template(os.path.join(templates_dir, "ts_index.html"),\
                                  os.path.join(templates_dir, "served", html_name),\
                                  [("const FETCH_STR = \"/output?req_id=NEED_SPECIFIC_REQ_ID\";",\
                                  "const FETCH_STR = \"/output?req_id=%s\";" % req_id)])

        return render_template(os.path.join("served", html_name))

    elif req_endpoint == "bc":
            th = Thread(target=serve_bc, args=(req_id, req_args))
            th.start()

            html_name = "bc_%s.html" % req_id

            # Copy from a template and replace the string that has the endpoint for fetching outputs from
            # instantiate_from_template(os.path.join(templates_dir, "bc_index.html"),\
            #                           os.path.join(templates_dir, "served", html_name),
            #                           old_text="const FETCH_STR = \"/output?req_id=NEED_SPECIFIC_REQ_ID\";",\
            #                           new_text="const FETCH_STR = \"/output?req_id=%s\";" % req_id)
            instantiate_from_template(os.path.join(templates_dir, "bc_index.html"),\
                                      os.path.join(templates_dir, "served", html_name),\
                                      [("const FETCH_STR = \"/output?req_id=NEED_SPECIFIC_REQ_ID\";",\
                                      "const FETCH_STR = \"/output?req_id=%s\";" % req_id)])

            return render_template(os.path.join("served", html_name))

    elif req_endpoint == "kwh":
            th = Thread(target=serve_kwh, args=(req_id, req_args))
            th.start()

            html_name = "kwh_%s.html" % req_id
            height, lat, lon, year_list = validated_params_v2_w_year(req_args)

            # Copy from a template and replace the string that has the endpoint for fetching outputs from
            # instantiate_from_template(os.path.join(templates_dir, "bc_index.html"),\
            #                           os.path.join(templates_dir, "served", html_name),
            #                           old_text="const FETCH_STR = \"/output?req_id=NEED_SPECIFIC_REQ_ID\";",\
            #                           new_text="const FETCH_STR = \"/output?req_id=%s\";" % req_id)
            instantiate_from_template(os.path.join(templates_dir, "kwh_index.html"),\
                                      os.path.join(templates_dir, "served", html_name),\
                                      [("const FETCH_STR = \"/output?req_id=NEED_SPECIFIC_REQ_ID\";",\
                                      "const FETCH_STR = \"/output?req_id=%s\";" % req_id),\
                                      ("const lat = \"NEED_SPECIFIC_LAT\";",\
                                      "const lat = %.6f;" % lat),\
                                      ("const lon = \"NEED_SPECIFIC_LON\";",\
                                      "const lon = %.6f;" % lon)])

            return render_template(os.path.join("served", html_name))

    elif req_endpoint == "info":
        return render_template("info.html")
    else:
        return "Unsupported endpoint is selected: %s" % req_endpoint


if __name__ == '__main__':
    app.run(host=host, port=port, debug=True)
