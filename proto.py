from flask import Flask, render_template, request, jsonify
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
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('agg')

from dw_tap.data_fetching import getData
from v2 import validated_params_v2_w_year
from hsds_helpers import connected_hsds_file
#from dw_tap.vis import plot_monthly_avg

#app = Flask(__name__)
#cors = CORS(app)

outputs_dir = "outputs"
templates_dir = "templates"

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
        res = res.style.background_gradient("BuPu", axis=1).format(precision=3).set_caption("12x24 average wind speeds. Overall average: %.3f" % overall_mean)
    if format=="dataframe":
        return res
    elif format=="html":
        html = res.to_html(classes='12_by_24')
        # Add colormap image
        #html += "<div id=\"colormap_wrapper\"><p id=\"colormap_min\">Min=%.3f</p><img id=\"colormap\" src=\"static/colormap.png\"/></div>" % (min_ws)

        html += """
        <div classes="centered">
        <div id="colormap_wrapper">
          <table id="colormap_table">
              <tr>
                <td id="colormap_min_cell">Min=%.3f</td>
                <td id="colormap_max_cell">Max=%.3f</td>
              </tr>
              <tr>
                <td colspan=2><img id=\"colormap\" src=\"static/colormap.png\"/></td>
              </tr>
          </table>
        </div>
        </div>
        """ % (min_ws, max_ws)

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

      output = timeseries_to_12_by_24(atmospheric_df)
      info = "The shown dataset includes %d timesteps between %s and %s." % \
        (len(atmospheric_df), atmospheric_df.datetime.tolist()[0], atmospheric_df.datetime.tolist()[-1])
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

      output = """
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

  #     output_dest = os.path.join(outputs_dir, req_id)
  #     with open(output_dest, "w") as text_file:
  #         text_file.write(output)
  #     return
  # except Exception as e:
  #     output = "The following error has occurred:<br>" + str(e)
  #     with open(output_dest, "w") as text_file:
  #         text_file.write(output)
  #     return

      info = "The shown dataset includes %d timesteps between %s and %s." % \
        (len(atmospheric_df), atmospheric_df.datetime.tolist()[0], atmospheric_df.datetime.tolist()[-1])
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

      output = atmospheric_df.to_csv(index=False).replace("\n", "<br>")
      info = ""
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

# @app.route('/12x24')
# def endpoint_12x24():
#   global req_args
#   req_args = request.args
#   t1 = Thread(target=serve_12x24)
#   t1.start()
#   return render_template('12x24_index.html')
#
# @app.route('/monthly')
# def endpoint_monthly():
#   global req_args
#   req_args = request.args
#   t1 = Thread(target=serve_monthly)
#   t1.start()
#   return render_template('monthly_index.html')
#
# @app.route('/12x24_output', methods=['GET'])
# def output_12x24():
#   json_output = {'output': output}
#   return json.dumps(json_output)
#
# @app.route('/monthly_output', methods=['GET'])
# def output_monthly():
#   json_output = {'output': output}
#   return json.dumps(json_output)

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
            #output = ""
            output = {'output': "", "info": ""}
    else:
        # output = ""
        output = {'output': "", "info": ""}

    #json_output = {'output': output}
    #return json.dumps(json_output)

    return output

def instantiate_from_template(src, dest, old_text, new_text):
    """ Copy src file to dest with replacement of old_text with new_text """
    fin = open(src)
    fout = open(dest, "wt")
    for line in fin:
        fout.write(line.replace(old_text, new_text))
    fin.close()
    fout.close()

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
            latlon = "Error: OpenStreetMap's API was unable to find lat/lon for the given address.<br>Provide valid address and try again.<br>Keep in mind that OpenStreetMap may not provide info for addresses with special restrictions."
            return json.dumps({"latlon": latlon})
    else:
        return json.dumps({"latlon": ""})

    # address = '1840 Alkire Ct, Golden, CO 80401'
    # url = 'https://nominatim.openstreetmap.org/search?q=' + urllib.parse.quote(address) +'&format=json'
    # response = requests.get(url).json()
    # return response[0]["lat"] + "   " + response[0]["lon"]

@app.route('/by_address', methods=['GET'])
def by_address():
    #return render_template("testing.html")

    # address = '1840 Alkire Ct, Golden, CO 80401'
    # url = 'https://nominatim.openstreetmap.org/search?q=' + urllib.parse.quote(address) +'&format=json'
    # response = requests.get(url).json()
    # return response[0]["lat"] + "   " + response[0]["lon"]

    return render_template("by_address.html")

@app.route('/', methods=['GET'])
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

        # Copy from a template and replace the string that has the endpoint for fetching outputs from
        instantiate_from_template(os.path.join(templates_dir, "12x24_index.html"),\
                                  os.path.join(templates_dir, "served", html_name),
                                  old_text="const FETCH_STR = \"/output?req_id=NEED_SPECIFIC_REQ_ID\";",\
                                  new_text="const FETCH_STR = \"/output?req_id=%s\";" % req_id)

        return render_template(os.path.join("served", html_name))

    elif req_endpoint == "monthly":
        th = Thread(target=serve_monthly, args=(req_id, req_args))
        th.start()

        html_name = "monthly_%s.html" % req_id

        # Copy from a template and replace the string that has the endpoint for fetching outputs from
        instantiate_from_template(os.path.join(templates_dir, "monthly_index.html"),\
                                  os.path.join(templates_dir, "served", html_name),
                                  old_text="const FETCH_STR = \"/output?req_id=NEED_SPECIFIC_REQ_ID\";",\
                                  new_text="const FETCH_STR = \"/output?req_id=%s\";" % req_id)

        return render_template(os.path.join("served", html_name))

    elif req_endpoint == "ts":
        th = Thread(target=serve_ts, args=(req_id, req_args))
        th.start()

        html_name = "ts_%s.html" % req_id

        # Copy from a template and replace the string that has the endpoint for fetching outputs from
        instantiate_from_template(os.path.join(templates_dir, "ts_index.html"),\
                                  os.path.join(templates_dir, "served", html_name),
                                  old_text="const FETCH_STR = \"/output?req_id=NEED_SPECIFIC_REQ_ID\";",\
                                  new_text="const FETCH_STR = \"/output?req_id=%s\";" % req_id)

        return render_template(os.path.join("served", html_name))

    elif req_endpoint == "info":
        return render_template("info.html")
    else:
        return "Unsupported endpoint is selected: %s" % req_endpoint

if __name__ == '__main__':
    app.run(debug=True)
