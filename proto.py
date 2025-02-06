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
import boto3
matplotlib.use('agg')

from dw_tap.data_fetching import getData
from dw_tap.observations import locate_nearest_obs_sites
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
from invalid_usage import InvalidUsage
from flask import send_file

import xarray as xr
import s3fs

# ERA5 Hourly setup with zarr file in S3
era5_hourly_s3_path = "s3://windwatts-era5/hourly/conus-2023-hourly.zarr"
s3 = s3fs.S3FileSystem()
store = s3fs.S3Map(root=era5_hourly_s3_path, s3=s3, check=False)
era5_hourly = xr.open_zarr(store=store, consolidated=True)

def power_law(ws10, ws100, height):
    # Use default alpha if ws10 and ws100 are opposite directions
    alpha = np.where(
        np.isnan(ws10) | np.isnan(ws100) | (ws10 <= 0) | (ws100 <= 0),
        1/7.0,
        np.log(ws10/ws100) / np.log(10/100)
    )
    ws = ws100 * ((height / 100) ** alpha)
    return ws

def convert_to_ws(u, v):
    """ Converts u and v vector to wind speed """
    return np.sqrt(u**2 + v**2)

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

# Get index once when the app starts (rather than as part of every request)
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

# Turn mohr values into separate month and hour values
def parse_mohr(mohr):
    s = str(mohr)
    m, h = s[:-2], s[-2:]
    return int(m), int(h)

# Fetch a single year of WTK-LED 12x24 data
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

# Fetch all 20 years of WTK-LED 12x24 data
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

# Process a dataframe with 20 years of WTK-LED 12x24 data, turning it into a dataframe with lowest, average, highest years
def df2yearly_avg(df, ws_column, kw_column):
    tmp = df.drop(columns=["mohr", "month", "h"] + [x for x in df.columns if "winddirection" in x])
    #res = tmp.groupby("year").agg("mean")
    res = tmp.groupby("year").agg(avg_ws=(ws_column, "mean"), kwh_total=(kw_column, "sum")) # kwh_total will sum for all months and all hours

    res["kwh_total"] = res["kwh_total"] * 30 # Coarse estimation: 30 days in every month; no need to /20.0 for individual years
    res.rename(columns={"avg_ws": "Average wind speed, m/s", "kwh_total": "kWh produced"}, inplace=True)

    res = res.sort_values("Average wind speed, m/s")

    res_avg = pd.DataFrame(res.mean()).T
    res_avg.index=["Average year"]

    res_3years = pd.concat([res.iloc[[0]], res_avg, res.iloc[[-1]]])
    res_3years["kWh produced"] = res_3years["kWh produced"].astype(float).map('{:,.0f}'.format)
    res_3years["Average wind speed, m/s"] = res_3years["Average wind speed, m/s"].astype(float).map('{:,.2f}'.format)

    res_3years.index = ["Lowest year (%s)" % str(res_3years.index[0]), \
                        res_3years.index[1], \
                        "Highest year (%s)" % str(res_3years.index[2])]

    return res_3years

# Process a dataframe with 20 years of WTK-LED 12x24 data, turning it into a dataframe with monthly averages
def df2monthly_avg(df, ws_column, kw_column):
    tmp = df.drop(columns=["year", "mohr", "h"] + [x for x in df.columns if "winddirection" in x])
    res = tmp.groupby("month").agg(avg_ws=(ws_column, "mean"), kwh_total=(kw_column, "sum")) # kwh_total will sum for all hours and all years

    res["kwh_total"] = res["kwh_total"] * 30 / 20.0 # Coarse estimation: 30 days in every month & 20 years
    res.rename(columns={"avg_ws": "Average wind speed, m/s", "kwh_total": "kWh produced"}, inplace=True)
    res.index = pd.Series(res.index).apply(lambda x: calendar.month_abbr[x])

    res["kWh produced"] = res["kWh produced"].astype(float).map('{:,.0f}'.format)
    res["Average wind speed, m/s"] = res["Average wind speed, m/s"].astype(float).map('{:,.2f}'.format)

    return res

# Given a 20-year dataframe with columns for different heights and a user-specified height, return closest heights and corresponding column names
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

# Function for fetching WTK-LED uncertainty data
def get_uncertainty_dataframe(location,height=40):
    # For sample:
    #base_url = "https://wtk-csv-testing-dav-sandbox.s3.us-west-2.amazonaws.com/uncertainty"
    base_url = "https://wtk-led.s3.us-west-2.amazonaws.com/uncertainty"
    file_path = f"/height={height}/index={location}/{location}_{height}m.csv.gz"
    return pd.read_csv(base_url+file_path)

# End of WTK-LED fucntions

# ERA5 functions

def get_era5_index():
    s3 = boto3.resource('s3')
    my_bucket = s3.Bucket('windwatts-era5')
    my_bucket.download_file("location_index.csv", "location_index.csv")
    index = gpd.GeoDataFrame(pd.read_csv("location_index.csv"))

    #base_url = "https://windwatts-era5.s3.us-west-2.amazonaws.com"
    #file_path = f"/location_index.csv"
    #index = gpd.GeoDataFrame(pd.read_csv(base_url+file_path))

    index['location'] = gpd.GeoSeries(gpd.points_from_xy(index.longitude, index.latitude))
    index["index"] = index["index"].apply(lambda x: str(x).zfill(6))
    return index

era5_index = get_era5_index()

def closest_grid_point_era5(index,lat,lon):
    p = Point(lon,lat)
    r = index.iloc[index.location.distance(p).argmin()].copy()
    r['distance_degrees'] = Point(r['longitude'],r['latitude']).distance(p)
    return r

def get_era5(idx, year=2021, add_year_col=False, add_avg_row=True):
    #base_url = "https://wtk-led.s3.us-west-2.amazonaws.com/1224"
    #file_path = f"/year={year}/varset=all/index={idx}/{idx}_{year}_all.csv.gz"
    #res = pd.read_csv(base_url + file_path)

    s3 = boto3.resource('s3')
    my_bucket = s3.Bucket('windwatts-era5')
    file_path = f"initial_era5_csv_test_files/year={year}/varset=quantiles/index={idx}/{idx}_{year}_quantiles.csv.gz"
    #print(file_path)
    my_bucket.download_file(file_path, "data.csv.gz")
    res = pd.read_csv("data.csv.gz")

    res["quantile"] = res["quantile"].apply(lambda x: "q%.2f" % x)
    res.rename(columns={"quantile": "measure"}, inplace=True)

    if add_avg_row:
        new_row = []
        for c in res.columns:
            if c == "measure":
                new_row.append("avg")
            else:
                # For each column, add: sum(x*f(x)) where f(x) is estimated density -- easy to calcuate for uniformly spaced quantiles
                new_row.append(np.sum(res[c] * 0.1))
        res.loc[len(res)] = new_row

    if add_year_col:
        res["year"] = year
    return res

def get_era5_all_yrs(idx, ws_col_for_estimating_power=None, selected_powercurve=None, relevant_columns_only=True):

    df = pd.concat([get_era5(idx, year=yr, add_year_col=True, add_avg_row=True) for yr in range(2013, 2024)])
    return df

def era5_analysis(df, height, pc):
    all_heights = [int(el.replace("ws", "")) for el in df.columns if "ws" in el]
    closest_height_idx = (np.abs(np.array(all_heights) - height)).argmin()
    closest_height_column = "ws" + str(all_heights[closest_height_idx])

    avgs = df[df["measure"] == "avg"].mean(axis=0, numeric_only=True)
    #all_heights = [int(el.replace("ws", "")) for el in avgs.index if "ws" in el]

    global_avg = df[closest_height_column].mean()

    df["pwr"] = pc.windspeed_to_kw(df, closest_height_column)

    # Estimate energy using yearly average windspeed converted to power
    df_yearly_avg = df[df["measure"] == "avg"][["pwr", "year"]]
    df_yearly_avg["kWh"] = df_yearly_avg["pwr"] * 8760

    # Estimate energy using quantiles turned to power estimates
    df_quantiles = df[df["measure"] != "avg"][["pwr", "year"]]
    df_quantiles["kWh"] = df_quantiles["pwr"] * (8760 / 10.0)  # Assume 10 quantiles being used in describing distributions
    df_yearly_quantiles = df_quantiles.groupby("year").agg(kWh_yearly = ("kWh", "sum"))

    df_avg_yearly_production = df_yearly_quantiles["kWh_yearly"].mean()

    return global_avg, closest_height_column, df_avg_yearly_production


# End of ERA5 functions

def pd2srw(df, lat, lon, height, year):
# $ head /Applications/SAM_2022.11.21/SAM.app/Contents/wind_resource/WY\ Southern-Flat\ Lands.srw
# loc_id,city??,WY,USA,year??,lat??,lon??,2088,-7,8760
# Southern WY - flat lands (NREL AWS Truepower representative file)
# Temperature,Pressure,Direction,Speed,Temperature,Pressure,Direction,Speed,Temperature,Pressure,Direction,Speed,Temperature,Pressure,Direction,Speed
# C,atm,degrees,m/s,C,atm,degrees,m/s,C,atm,degrees,m/s,C,atm,degrees,m/s
# 50,50,50,50,80,80,80,80,110,110,110,110,140,140,140,140
# -4.479,0.756533925,253,9.897,-4.719,0.753473476,254,10.665,-4.919,0.75041204,254,11.333,-5.069,0.747450284,254,11.989
# -4.279,0.759496669,261,9.659,-4.519,0.756435233,262,10.378,-4.699,0.753374784,264,10.998,-4.869,0.750313348,264,11.53
# -4.079,0.759990131,278,8.062,-4.319,0.756928695,282,8.766,-4.469,0.753966938,285,9.287,-4.569,0.750905502,285,9.749
# -3.639,0.761371823,312,8.447,-3.819,0.758310387,316,9.23,-4.019,0.755348631,318,9.883,-4.269,0.752287195,318,10.496
# -3.679,0.762260054,321,9.84,-3.919,0.759199605,324,10.566,-4.169,0.756039477,325,11.117,-4.369,0.752979028,325,11.626

    # Need to support a single height

    # header = "loc_id,denver,CO,USA,%s,%s,%s,2088,-7,8760\n" % (year,lat, lon) + \
    #          "Somewhere - ? (NREL WTK sample)\n" + \
    #          "Temperature,Pressure,Direction,Speed\n" + \
    #          "C,atm,degrees,m/s\n" + \
    #          "%d,%d,%d,%d\n" % (height,height,height,height)

    header = """SiteID,SOMEID,Site Timezone,SOMETIMEZONE,Data Timezone,SOMETIMEZONE,Longitude,%f,Latitude,%f
Year,Month,Day,Hour,Minute,surface air pressure (Pa),air pressure at 100m (Pa),air pressure at 200m (Pa),wind speed at %dm (m/s),wind direction at %dm (deg),air temperature at %dm (C)\n""" % (lon, lat, int(height), int(height), int(height)) #, height)

    df['timestamp'] = pd.to_datetime(df['time'])
    df['year'] = df['timestamp'].dt.year
    df['month'] = df['timestamp'].dt.month
    df['day'] = df['timestamp'].dt.day
    df['hour'] = df['timestamp'].dt.hour
    df['minute'] = df['timestamp'].dt.minute

    df['surface air pressure (Pa)'] = 101325
    df['air pressure at 100m (Pa)'] = 100325
    df['air pressure at 200m (Pa)'] = 98800
    df['wind speed at 30m (m/s)'] = df["windspeed"]
    df['wind direction at 30m (deg)'] = 0.0
    df['air temperature at 30m (C)'] = 15.0

    print(df.head())

    #return header + df[["temp", "pres", "wd", "ws"]].to_csv(index=False, header=False)
    return header + df[["year", "month" , "day", "hour", "minute",\
    "surface air pressure (Pa)","air pressure at 100m (Pa)","air pressure at 200m (Pa)",\
    "wind speed at 30m (m/s)","wind direction at 30m (deg)", "air temperature at 30m (C)"]].to_csv(index=False, header=False)

# Determine feasibility threshold given the height
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

# Helper function for taking an HTML template (src), making a list of replacements (for different environments), svaing it (to dest)
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

# Create a wind rose plot and save into a specifed file
def plot_windrose(df, ws_column="ws", wd_column="wd", save_to_file=True):
    ax = WindroseAxes.from_ax()
    ax.bar(df[wd_column], df[ws_column], normed=True, opening=0.8, edgecolor='white')
    ax.set_legend()
    if save_to_file == True:
        plt.savefig('%s.png' % title, dpi=300)
    elif type(save_to_file) == str:
        plt.savefig(save_to_file, dpi=300)

# The rest of the server's start-up code
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

# Load and prepare power curve objects put into a dictionary by power curve name
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

with open('config.json', 'r') as f:
    config = json.load(f)

# Command-line args parsing
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

# Identify the current environment -- local or AWS
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


# Prepare templates from universal ones (URL_prefix is determined for the current env by now and can be used),
# Universal here means that those template can be used for AWS and non-AWS envs
# For making permanent changes, need to use unversal_* templates rather than the copies create based on them
#
# src_dest_names = [("universal_monthly_index.html", "monthly_index.html"),\
#                   ("universal_windrose_index.html", "windrose_index.html"),\
#                   ("universal_12x24_index.html", "12x24_index.html"),\
#                   ("universal_ts_index.html", "ts_index.html"),\
#                   ("universal_bc_index.html", "bc_index.html"),\
#                   ("universal_info.html", "info.html"),\
#                   ("universal_on_map.html", "on_map.html"),\
#                   ("universal_on_map3.html", "on_map3.html"),\
#                   ("universal_by_address.html", "by_address.html"),\
#                   ("universal_kwh_index.html", "kwh_index.html"),\
#                   ("universal_energy.html", "energy.html")]

src_dest_names = [("universal_on_map3.html", "on_map3.html")]

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

# Needed for checking if output is created and ready; checking by the request ID hash
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

# Produce summary for uncertainty data
def daily_udf_to_summary(udf):
    """ Use daily uncertainty to create a summary """
    p50 = udf["percentile_50"].mean()
    p25 = udf["percentile_25"].mean()
    p75 = udf["percentile_75"].mean()

    p25_percent_diff_from_p50 = (p50 - p25) / p50 * 100
    p75_percent_diff_from_p50 = (p75 - p50) / p50 * 100
    #return p25, p50, p75, p25_percent_diff_from_p50, p75_percent_diff_from_p50

    summary = """
                    <!-- <p class="results_disclaimer_text"><span>OLD CONTENT BELOW. TO BE UPDATED.</span></p><br><br> --!>
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

# Convert wind speed to meaningful levels
def ws_to_level(ws, moderate_resource_thresh_ms, high_resource_thresh_ms):
    if ws < moderate_resource_thresh_ms:
        return "Low"
    elif ws >= moderate_resource_thresh_ms and ws < high_resource_thresh_ms:
        return "Moderate"
    else:
        return "High"

# Given a request (in the form of a json), produce output file and save it at: <completed_dir/<request ID> (json as well)
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

        output_dest = os.path.join(completed_dir, id)

        # Fetching WTK-LED
        #point = closest_grid_point(wtkled_index, data["lat"], data["lon"])
        #df_1224_20years = get_1224_20yrs(point['index'], ws_column, selected_powercurve, relevant_columns_only=True)
        #print("obtained df_1224_20years:")
        #print(df_1224_20years.head())

        # ToDo: the following code can eventually be replaces with a simple call to new API built around WTK-LED and other datasets

        # WTK-LED

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

        # ERA5

        attempt_lim = 5
        error_str = ""
        for attempt in range(attempt_lim):
            try:
                error_str = ""
                print("Fetching ERA5 data. Attempt: %d of %d" % (attempt, attempt_lim))
                point_era5 = closest_grid_point_era5(era5_index, data["lat"], data["lon"])
                era5_df = get_era5_all_yrs(point_era5["index"])
                era5_global_avg, era5_closest_height_column, era5_df_avg_yearly_production = \
                    era5_analysis(era5_df, int(data["height"]), selected_powercurve)
                era5_summary = era5_summary_to_html(era5_global_avg, era5_closest_height_column, era5_df_avg_yearly_production)

            except Exception as e:
                print("Error in fetching ERA5 data. Will wait a little and try again")
                print("Exception: %s" % str(e))
                error_str = "An error occurred during fetching ERA5 data. If it is an intermittent, network issue, may need to try again later! To help with troubleshooting, here is the error message: %s" % str(e)
                time.sleep(0.5)
                continue
            else:
                print("Fetching ERA5 data was successful")
                error_str = ""
                break

        if error_str:
            with open(output_dest, 'w') as f:
                json.dump({"error": error_str}, f)
            print("Saved error info to: %s" % output_dest)
            return

        print("era5 analysis results:", era5_global_avg, era5_closest_height_column, era5_df_avg_yearly_production)


        yearly_df = df2yearly_avg(df_1224_20years, ws_column, kw_column)
        kwh_produced_avg_year = yearly_df["kWh produced"].tolist()[1] # Average year comes after the lowest
        monthly_df = df2monthly_avg(df_1224_20years, ws_column, kw_column)

        overall_mean = df_1224_20years[ws_column].mean()

        feasibility_thresh = feasibility_thresh_by_height(float(data["height"]))
        moderate_resource_thresh_ms = feasibility_thresh - 1.0
        high_resource_thresh_ms = feasibility_thresh + 1.0
        ws_level = ws_to_level(overall_mean, moderate_resource_thresh_ms, high_resource_thresh_ms)

        # uncertainty_summary = ""
        udf = get_uncertainty_dataframe(point['index'])
        udf['doy'] = udf.index # assume the day of year is the index, which would be true once all 12 months of data are present
        uncertainty_summary = daily_udf_to_summary(udf)

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

        # new addition: summary of observational data
        observations = locate_nearest_obs_sites(["./obs/met_tower_obs_summary.geojson", "./obs/vendor_obs_summary.geojson"], \
            float(data["lat"]), float(data["lon"]), float(data["height"]))

        print("before with open, saving results")
        with open(output_dest, 'w') as f:
            json.dump({"wtk_led_summary": summary, "wtk_led_windresource": windresource,
                "wtk_led_energyproduction": energyproduction,
                "observations": observations,
                "uncertainty_summary": uncertainty_summary,
                "era5_summary": era5_summary}, f)
                #"uncertainty_data": uncertainty_data},\

        print("Saved output to: %s" % output_dest)

    except Exception as e:
        print("error: " + str(e))
        output = "Error: " + str(e)


# API endpoint -- early version
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

def get_era5_hourly(lat, lon, height):
    point = closest_grid_point_era5(era5_index,lat,lon)
    lat_idx = int(point["index"][:3])
    lon_idx = int(point["index"][3:])

    tt = era5_hourly.time.values
    tt = np.datetime_as_string(tt, unit='s')

    u = dict()
    v = dict()
    ws = dict()
    u[10] = era5_hourly.u10[:,lat_idx,lon_idx].values
    v[10] = era5_hourly.v10[:,lat_idx,lon_idx].values
    u[100] = era5_hourly.u100[:,lat_idx,lon_idx].values
    v[100] = era5_hourly.v100[:,lat_idx,lon_idx].values
    u[height] = power_law(u[10], u[100], height)
    v[height] = power_law(v[10], v[100], height)
    ws[height] = convert_to_ws(u[height], v[height])

    #res = pd.DataFrame({"time": tt, "ws%d" % int(height): ws[height]})
    res = pd.DataFrame({"time": tt, "windspeed": ws[height]})
    return res

#@app.route('/era5-hourly', methods=['GET'])
@app.route('/windspeed-hourly', methods=['GET'])
def serve_era5_hourly():
    """ Endpoint serving ERA5 hourly data.

    Access it at using URLs like: <hostname>:<port>/windspeed-hourly?lat=39.76004&lon=-105.14058&height=30m
    """
    #lat, lon = validated_latlon(request)
    height, lat, lon = validated_params_v2(request)
    height = int(height)

    try:
        # Entire request is passed
        rargs = request.args
    except:
        # Request's args are passed
        rargs = request

    if 'download' in rargs:
        download_fmt = rargs['download']

        if download_fmt.lower() == "csv":
            res = get_era5_hourly(lat, lon, height)

            csv_path = os.path.join(completed_dir, "windwatts-%f-%f-%d.csv" % (lat,lon,height))
            res.to_csv(csv_path, index=False)
            print("Debug: saved csv with era5 hourly, %s" % csv_path)
            return send_file(csv_path, as_attachment=True)
        elif download_fmt.lower() == "srw":
            res = get_era5_hourly(lat, lon, height)

            # srw_path = os.path.join(completed_dir, "windwatts-%f-%f-%d.srw" % (lat,lon,height))
            srw_path = os.path.join(completed_dir, "windwatts-%f-%f-%d.csv" % (lat,lon,height))

            srw_contents = pd2srw(res, lat, lon, height, 2023)

            with open(srw_path, "w") as text_file:
                text_file.write(srw_contents)
            print("Debug: saved srw with era5 hourly, %s" % srw_path)
            return send_file(srw_path, as_attachment=True)
        else:
            raise InvalidUsage("Unsupported download format. Currently supported: csv, srw")
    else:
        res = get_era5_hourly(lat, lon, height)
        return res.to_html(index=False)


#@app.route('/era5-avg', methods=['GET'])
@app.route('/windspeed-avg', methods=['GET'])
def serve_era5_avg():
    """ Endpoint serving ERA5 average windspeed.

    Access it at using URLs like: <hostname>:<port>/windspeed-avg?lat=39.76004&lon=-105.14058&height=30m
    """
    #lat, lon = validated_latlon(request)
    height, lat, lon = validated_params_v2(request)
    height = int(height)
    res = get_era5_hourly(lat, lon, height)
    return "%f" % res["windspeed"].mean()

def serve_windwatts_api_request_windspeed(req):

    if "lon" in req:
        lon = req["lon"]
    else:
        return error2json("'lon', which is a required field of windwatts-api-request-windspeed, is missing.")

    if "lat" in req:
        lat = req["lat"]
    else:
        return error2json("'lat', which is a required field of windwatts-api-request-windspeed, is missing.")

    if "height" in req:
        height = req["height"]
    else:
        return error2json("'height', which is a required field of windwatts-api-request-windspeed, is missing.")
    try:
        height = float(height)
    except ValueError:
        return error2json("Expecting a numeric value provided for 'height'.")

    height_supported_wtkled = [10, 30, 40, 60, 80, 100, 120, 140, 160, 180, 200]
    if height in height_supported_wtkled:
        # May need to support floats better (10.00, 30.00), etc.; right now only ints will work with this if
        pass
    else:
        return error2json("'height' should match exactly one of WTK-LED heights: %s." % str(height_supported_wtkled))

    output_supported = ["avg", "all"]
    if "output" in req:
        if req["output"] in output_supported:
            output = req["output"]
        else:
            return error2json("'output', which is a required field of windwatts-api-request-windspeed, needs to be one of: %s." % str(output_supported))
    else:
        # Default value
        output = "all"

    windspeed_col = "windspeed_" + str(int(height)) + "m"
    cols = ["mohr", windspeed_col]

    try:
        point = closest_grid_point(wtkled_index, lat, lon)
        df_1224_20years = get_1224_20yrs(point['index'],
            ws_col_for_estimating_power="nonexistent_column", # This helps avoid power estimation
            selected_powercurve=None, # No power estimation
            relevant_columns_only=False) # Show all columns/data instead of a subset

        if output == "all":
            res = df_1224_20years[cols].to_csv(index=False)
        elif output == "avg":
            res = round(df_1224_20years[windspeed_col].mean(), 2)

        return json.dumps({'data': res, 'status': 0})

    except Exception as e:
        return error2json("Error in fetching wind data (WTK-LED 12x24). Error: " + str(e))

def serve_windwatts_api_request_windenergy(req):
    return "Serving wind energy: " + str(req)

def error2json(msg, status=1):
    """ Always serve error messages as json with 'message' and (non-zero) 'status' """
    return json.dumps({"message": msg,\
                       "status": status})

# API endpoint for batch requests -- early version
@app.route('/batch', methods=['GET'])
def serve_batch():
    """ Endpoint serving multiple requests passed in a single json.

    Access it at using URL: <hostname>:<port>/batch with attached json via GET method
    """

    if request.method == 'GET':
        if not request.data:
            return error2json("This endpoint is expecting request data wrapped in a JSON object.") # Maybe add link to a page with API doc

        try:
            req_json = json.loads(request.data)
        except Exception as e:
            return error2json("JSON parsing error. Make sure valid JSON is used. Error: " + str(e))

        if ("windwatts-api-request-windspeed" not in req_json) and ("windwatts-api-request-windsenergy" not in req_json):
            return error2json("Supported types of requests: windwatts-api-request-windspeed, windwatts-api-request-windenergy. Neither was selected in the submitted JSON")

        res = []

        # Process windspeed requests first, energy requests second (this will allow caching of results of the windspeed requests)

        if 'windwatts-api-request-windspeed' in req_json:
            for r in req_json["windwatts-api-request-windspeed"]:
                res.append(serve_windwatts_api_request_windspeed(r))

        if 'windwatts-api-request-windenergy' in req_json:
            for r in req_json["windwatts-api-request-windenergy"]:
                res.append(serve_windwatts_api_request_windenergy(r))

        return res
    else:
        return error2json("Use GET method with this endpoint.")


# API/documentation route -- not working now because apiDoc isn't working for buildings docs (deprecated)
@app.route('/api', methods=['GET'])
def api():
    # Serve documentation produced by apiDoc
    return flask.send_file('docs/index.html')

# UI uses this endpoint to make the initial request (with POST) and checking the availability of results (using GET)
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

# Display some server info
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

    output += "WTK-LED index: %d columns, %d rows" % (len(wtkled_index.columns), len(wtkled_index)) + "<br>"
    output += "ERA5 index: %d columns, %d rows" % (len(era5_index.columns), len(era5_index))
    return output

# DO NOT DELETE: /info route is needed for checking the health of the service during deployment
@app.route('/info', methods=['GET'])
def info():
    return status()

if __name__ == '__main__':
    app.run(host=host, port=port, debug=True)
