# -*- coding: utf-8 -*-
"""Main API module.

This file includes all components needed to run a Flask app with several
endpoints, serving windspeed, winddirection, and windrose data.

Getting Started:
    $ conda env create -f environment.yml
    $ conda activate dw-tap-api
Examples:
    - Run a development instance (on port 8080, as specified in config.json):
    $ python api.py
    or
    $ python api.py -d
    or
    # python api.py --development
    - Run a production instance
        (on port 80; again, refer to config.json for details):
    $ python api.py -p
    or
    # python api.py --production

Additional info about running the app is in README.md.

Written by: Dmitry Duplyakin (dmitry.duplyakin@nrel.gov) and Caleb Phillips (caleb.phillips@nrel.gov)
in collaboration with the National Renewable Energy Laboratories.
"""

import flask
from flask import request, jsonify
from flask_cors import CORS
import random
import json
import argparse
import threading
import queue
import matplotlib
matplotlib.use('agg')
import os
import xarray as xr
import traceback

from windspeed import *
from winddirection import *
from hsds_helpers import *
from invalid_usage import InvalidUsage
from helpers import *
from v2 import validated_params_v2
from v2 import validated_params_v2_w_year

import h5pyd
from dw_tap.data_fetching import getData
from dw_tap.vis import plot_monthly_avg

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

app = flask.Flask(__name__)
app.config["DEBUG"] = False
# Note: may consider limiting CORS for production deployment
#       this opens up to AJAX calls from any domain
cors = CORS(app)

# Switch from desired json output to debug info and intemediate dataframes
DEBUG_OUTPUT = False

# Undo for actual fetching
#f = h5pyd.File("/nrel/wtk-us.h5", 'r', bucket="nrel-pds-hsds")
#f = connected_hsds_file(request, config)

# To recreate saving of the time index, uncomment:
# def _getDateTime(f):
#     """ Retrieves and parses date and time from data returning dt["datetime"] """
#     dt = f["datetime"]
#     dt = pd.DataFrame({"datetime": dt[:]},index=range(0,dt.shape[0]))
#     dt['datetime'] = dt['datetime'].apply(dateutil.parser.parse)
#     dt["datetime"] = pd.to_datetime(dt['datetime'])
#     return dt["datetime"]
#
# dt=_getDateTime(f)
# dt.to_csv("wtk-dt.csv")
dt = pd.read_csv("wtk-dt.csv")

@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

# Home/documentation route
@app.route('/', methods=['GET'])
def home():
    # Serve documentation produced by apiDoc
    return flask.send_file('docs/index.html')

# This helps serve files that are part of the apiDoc output (in /docs)
@app.route('/<foldername>/<path:filename>')
def docs_folder_file(foldername, filename):
    return flask.send_from_directory("docs/" + foldername, filename)

# This helps serve files that are part of the apiDoc output (in /docs)
@app.route('/<path:filename>')
def docs_file(filename):
    if filename.endswith(".js") or filename.endswith(".json"):
        return flask.send_from_directory("docs", filename)
    elif filename == "favicon.ico":
        return flask.send_from_directory("docs/img", filename)


# Fully functional route for windspeed
@app.route('/v1/timeseries/windspeed', methods=['GET'])
def v1_ws():
    """
    @api {get} /timeseries/windspeed Request windspeed estimates
    @apiVersion 1.0.0
    @apiName GetWindspeed
    @apiGroup Wind Speed

    @apiDescription Request windspeed estimates for a particular site,
    for a specified height, and corresponding to the given time interval.

    @apiSampleRequest https://dw-tap.nrel.gov/v1/timeseries/windspeed?height=50m
&lat=40.7128&lon=-74.0059&start_date=20100302&stop_date=20100402
&vertical_interpolation=linear&spatial_interpolation=idw

    @apiSuccess {String} JSON JSON with `timestamp` and `windspeed` series

    @apiSuccessExample Example output on success:
    {"timestamp":{"0":"2011-03-02 00:00:00","1":"2011-03-02 01:00:00",
    "2":"2011-03-02 02:00:00",
    "3":"2011-03-02 03:00:00","4":"2011-03-02 04:00:00",
    "5":"2011-03-02 05:00:00"},
    "windspeed":{"0":3.5925824239,"1":5.440796747,"2":4.8400592119,
    "3":5.4325136517,"4":4.9044365704,"5":5.2218727909}}

    @apiParam {Float} height Height (in meters) for which the windspeed
    estimates are requested; notation: `XXm`, where XX is an integer or float
    @apiParam {Float} lat Latitude (in degrees) for a particular site
    @apiParam {Float} lon Longitude (in degrees) for a particular site
    @apiParam {String} start_date Beginning of the time interval in the format:
    YYYYMMDD
    @apiParam {String} stop_date End of the time interval in the format:
    YYYYMMDD
    @apiParam {String} vertical_interpolation Method used for vertical
    interpolation; allowed: `nearest`, `linear`, `neutral_power`,
    `stability_power`
    @apiParam {String} spatial_interpolation Method used for spatial
    interpolation; allowed: `nearest`, `linear`, `cubic`, `idw`
    @apiParam {String} [username] Optional attribute of the HSDS credentials
    @apiParam {String} [password] Optional attribute of the HSDS credentials
    @apiParam {String} [api_key] Optional attribute of the HSDS credentials.
    If one of `username`, `password`, and `api_key` is specified, all three
    of these attributes should be specified. Alternatively, if none of these
    is specified, the default values will be use for rate-limited, demo access
    """

    print("v1_ws")

    height, lat, lon,\
        start_date, stop_date,\
        spatial_interpolation,\
        vertical_interpolation = validated_params_windspeed(request)
    hsds_f = connected_hsds_file(request, config)

    finalized_df, debug_info = prepare_windpseed(
                                   height, lat, lon,
                                   start_date, stop_date,
                                   spatial_interpolation,
                                   vertical_interpolation,
                                   hsds_f, DEBUG_OUTPUT)

    if DEBUG_OUTPUT:
        return "<br>".join(debug_info)
    else:
        return finalized_df.to_json()

# Fully functional route for winddirection
@app.route('/v1/timeseries/winddirection', methods=['GET'])
def v1_wd():
    """
    @api {get} /timeseries/winddirection Request winddirection estimates
    @apiVersion 1.0.0
    @apiName GetWinddirection
    @apiGroup Wind Direction

    @apiDescription Request wind direction estimates for a particular site,
    for a specified height, and corresponding to the given time interval.
    `Nearest-neighbor` is used for both spatial and vertical interpolations.

    @apiSampleRequest https://dw-tap.nrel.gov/v1/timeseries/winddirection?height=50m
&lat=40.7128&lon=-74.0059&start_date=20100302&stop_date=20100402

    @apiSuccess {String} JSON JSON with `timestamp` and `winddirection` series

    @apiSuccessExample Example output on success:
    {"timestamp":{"0":"2011-03-02 00:00:00","1":"2011-03-02 01:00:00",
    "2":"2011-03-02 02:00:00",
    "3":"2011-03-02 03:00:00","4":"2011-03-02 04:00:00",
    "5":"2011-03-02 05:00:00"},
    "winddirection":{"0":188.9596252441,"1":183.7189788818,"2":193.1125793457,
    "3":184.4605865479,"4":200.0836181641,"5":215.415512085}}

    @apiParam {Float} height Height (in meters) for which the wind direction
    estimates are requested; notation: `XXm`, where XX is an integer or float
    @apiParam {Float} lat Latitude (in degrees) for a particular site
    @apiParam {Float} lon Longitude (in degrees) for a particular site
    @apiParam {String} start_date Beginning of the time interval in the format:
    YYYYMMDD
    @apiParam {String} stop_date End of the time interval in the format:
    YYYYMMDD
    @apiParam {String} [username] Optional attribute of the HSDS credentials
    @apiParam {String} [password] Optional attribute of the HSDS credentials
    @apiParam {String} [api_key] Optional attribute of the HSDS credentials.
    If one of `username`, `password`, and `api_key` is specified,
    all three of these attributes should be specified. Alternatively,
    if none of these is specified, the default values will be use for
    rate-limited, demo access
    """

    print("v1_wd")

    height, lat, lon,\
        start_date, stop_date = validated_params_winddirection(request)
    hsds_f = connected_hsds_file(request, config)

    finalized_df, debug_info = prepare_winddirection(
                                   height, lat, lon,
                                   start_date, stop_date,
                                   hsds_f, DEBUG_OUTPUT)

    if DEBUG_OUTPUT:
        return "<br>".join(debug_info)
    else:
        return finalized_df.to_json()

# Fully functional route for windrose
@app.route('/v1/windrose', methods=['GET'])
@timeit
def v1_wr():
    """
    @api {get} /windrose Request windrose estimates
    @apiVersion 1.0.0
    @apiName GetWindrose
    @apiGroup Wind Rose

    @apiDescription Convenience function that convolves wind direction
    and wind speed to create a wind rose as output.

    @apiSampleRequest https://dw-tap.nrel.gov/v1/windrose?height=50m&
lat=40.7128&lon=-74.0059&start_date=20100302&stop_date=20100402&
vertical_interpolation=linear&spatial_interpolation=idw

    @apiSuccess {String} JSON with percentage observations in each
    of 8 radial segments (N, NE, E, SE, S, SW, W, NW) and each of 4 wind speed
    classes (11-14 mps, 8-11 mps, 5-8 mps, less than 5 mps)
    and all together ("All")

    @apiSuccessExample Example output on success:
    {"11-14 m/s": [77.5, 72.5, 70.0, 45.0, 22.5, 42.5, 40.0, 62.5],
    "8-11 m/s": [57.5, 50.0, 45.0, 35.0, 20.0, 22.5, 37.5, 55.0],
    "5-8 m/s": [40.0, 30.0, 30.0, 35.0, 7.5, 7.5, 32.5, 40.0],
    "< 5 m/s": [20.0, 7.5, 15.0, 22.5, 2.5, 2.5, 12.5, 22.5],
    "All": [5.0,10.0,50.0,35.0,0.0] }

    @apiParam {Float} height Height (in meters) for which the wind
    direction estimates are requested; notation: `XXm`,
    where XX is an integer or float
    @apiParam {Float} lat Latitude (in degrees) for a particular site
    @apiParam {Float} lon Longitude (in degrees) for a particular site
    @apiParam {String} start_date Beginning of the time interval in the format:
    YYYYMMDD
    @apiParam {String} stop_date End of the time interval in the format:
    YYYYMMDD
    @apiParam {String} vertical_interpolation Method used for vertical
    interpolation; allowed: `nearest`, `linear`, `neutral_power`,
    `stability_power`. Currently applied only to the windspeed data (not direction).
    @apiParam {String} spatial_interpolation Method used for spatial
    interpolation; allowed: `nearest`, `linear`, `cubic`, `idw`. Currently
    applied only to the windspeed data (not direction).
    @apiParam {String} [username] Optional attribute of the HSDS credentials
    @apiParam {String} [password] Optional attribute of the HSDS credentials
    @apiParam {String} [api_key] Optional attribute of the HSDS credentials.
    If one of `username`, `password`, and `api_key` is specified, all three
    of these attributes should be specified. Alternatively, if none of these
    is specified, the default values will be use for rate-limited, demo access
    """
    print("v1_wr")
    hsds_f = connected_hsds_file(request, config)

    height, lat, lon, \
        start_date, stop_date, \
        spatial_interpolation, \
        vertical_interpolation = validated_params_windspeed(request)

    # Use different threads to get windspeed and winddirection
    wd_que = queue.Queue()
    ws_que = queue.Queue()
    wd_th = threading.Thread(
        target=lambda q, arglist: q.put(prepare_winddirection(*arglist)),
        args=(wd_que, [height, lat, lon, start_date, stop_date,
                       hsds_f, DEBUG_OUTPUT]),
        daemon=True)
    wd_th.start()

    ws_th = threading.Thread(
        target=lambda q, arglist: q.put(prepare_windpseed(*arglist)),
        args=(ws_que, [height, lat, lon, start_date, stop_date,
                       spatial_interpolation, vertical_interpolation,
                       hsds_f, DEBUG_OUTPUT]),
        daemon=True)
    ws_th.start()

    # Complete calculations, gather results, and assign right variables
    wd_th.join()
    ws_th.join()
    wd_df, wd_debug_info = wd_que.get()
    ws_df, ws_debug_info = ws_que.get()

    combined_df = ws_df.merge(wd_df, on='timestamp')
    combined_df["windspeed_class"] = combined_df["windspeed"].apply(
        windspeed_class)
    combined_df["direction_class"] = combined_df["winddirection"].apply(
        direction_class)

    ret = windrose_from_df(combined_df)

    if DEBUG_OUTPUT:
        return "<br>".join(ws_debug_info + wd_debug_info)
    else:
        return json.dumps(ret)


@app.route('/check', methods=['GET'])
def check():
    return json.dumps({"Status": "OK!"})

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

    header = "loc_id,denver,CO,USA,%s,%s,%s,2088,-7,8760\n" % (year,lat, lon) + \
             "Somewhere - ? (NREL WTK sample)\n" + \
             "Temperature,Pressure,Direction,Speed\n" + \
             "C,atm,degrees,m/s\n" + \
             "%d,%d,%d,%d\n" % (height,height,height,height)

    return header + df[["temp", "pres", "wd", "ws"]].to_csv(index=False, header=False)

# New endpoint
@app.route('/v2/srw', methods=['GET'])
def v2_srw():
    height, lat, lon, year = validated_params_v2_w_year(request)
    #f = h5pyd.File("/nrel/wtk-us.h5", 'r', bucket="nrel-pds-hsds")
    f = connected_hsds_file(request, config)

    dt = pd.read_csv("wtk-dt.csv")
    dt["datetime"] = pd.to_datetime(dt["datetime"])
    dt["year"] = dt["datetime"].apply(lambda x: x.year)
    idx = dt[dt["year"] == year].index

    atmospheric_df = getData(f, lat, lon, height,
                            "IDW",
                            power_estimate=True,
                            inverse_monin_obukhov_length=False,
                            start_time_idx=idx[0], end_time_idx=idx[-1], time_stride=1,
                            saved_dt=dt,
                            srw=True)
    srw = pd2srw(atmospheric_df, lat, lon, height, year)
    return srw

# New endpoint for displaying plots
@app.route('/v2/plot', methods=['GET'])
def v2_plot():
    height, lat, lon, year = validated_params_v2_w_year(request)
    #f = h5pyd.File("/nrel/wtk-us.h5", 'r', bucket="nrel-pds-hsds")
    f = connected_hsds_file(request, config)

    dt = pd.read_csv("wtk-dt.csv")
    dt["datetime"] = pd.to_datetime(dt["datetime"])
    dt["year"] = dt["datetime"].apply(lambda x: x.year)
    idx = dt[dt["year"] == year].index

    atmospheric_df = getData(f, lat, lon, height,
                            "IDW",
                            power_estimate=True,
                            inverse_monin_obukhov_length=False,
                            start_time_idx=idx[0], end_time_idx=idx[-1], time_stride=1,
                            saved_dt=dt)
    plot_monthly_avg(atmospheric_df, \
                     title="(%f, %f), %.0fm hub height" % (lat, lon, height),\
                     save_to_file='saved.png',\
                     show_avg_across_years=True,
                     show_overall_avg=True)
    return flask.send_file('saved.png')

# New endpoint
@app.route('/v2/ts', methods=['GET'])
def v2_ws():

    #example = pd.DataFrame({"time": [1,2], "value": [2,3]})
    #return example.to_json()

    height, lat, lon = validated_params_v2(request)

    f = h5pyd.File("/nrel/wtk-us.h5", 'r', bucket="nrel-pds-hsds")
    #atmospheric_df = getData(f, lat, lon, height,
    #                         "IDW",
    #                         power_estimate=False,
    #                         inverse_monin_obukhov_length=False,
    #                         start_time_idx=0, end_time_idx=20, time_stride=1)
    #atmospheric_df.to_csv("saved.csv", index=False)
    atmospheric_df = pd.read_csv("saved.csv")
    print(atmospheric_df)

    return atmospheric_df.to_csv()

# @app.route('/v2/plot_all', methods=['GET'])
# def v2_plot_all():
#
#
#     height, lat, lon = validated_params_v2(request)
#
#     atmospheric_df = getData(f, lat, lon, height,
#                              "IDW",
#                              power_estimate=False,
#                              inverse_monin_obukhov_length=False,
#                              #start_time_idx=0, end_time_idx=8760, time_stride=1)
#                             )
#
#     #to_plot = atmospheric_df["ws"]
#     #to_plot.index = atmospheric_df["datetime"]
#     #res = to_plot.plot(figsize=(4, 3), fontsize=8).get_figure()
#     #res.savefig('saved.png', dpi=300)
#
#     plot_monthly_avg(atmospheric_df, title="(%f, %f), %.0fm hub height" % (lat, lon, height),
#                            save_to_file='saved.png')
#     return flask.send_file('saved.png')

# @app.route('/v2/plot_year', methods=['GET'])
# def v2_plot_year():
#
#     height, lat, lon = validated_params_v2(request)
#
#     if 'year' in request.args:
#         year_str = request.args['year']
#         try:
#             year = int(year_str)
#         except ValueError:
#             raise InvalidUsage(("Year provided is not a number"))
#
#         # Only support years that are in WTK: 2007-2013
#         if year < 2007 or year > 2013:
#             raise InvalidUsage("Year should be one of: 2007, 2008, 2009, 2010, 2011, 2012, 2013.")
#     else:
#         year = 2013
#
#     start_time_idx = (year - 2007) * 8760
#     end_time_idx = (year - 2007 + 1) * 8760
#     atmospheric_df = getData(f, lat, lon, height,
#                              "IDW",
#                              power_estimate=False,
#                              inverse_monin_obukhov_length=False,
#                              start_time_idx=start_time_idx, end_time_idx=end_time_idx,
#                              time_stride=1)
#     print(atmospheric_df.head())
#     print(atmospheric_df.tail())
#
#
#     plot_monthly_avg(atmospheric_df, title="(%f, %f), %.0fm hub height" % (lat, lon, height),
#                            save_to_file='saved.png')
#     return flask.send_file('saved.png')

@app.route('/v2/stresstest', methods=['GET'])
def v2_stresstest():
    delta = random.random()

    lat, lon, height = 39.0, -90.0 + delta, 40
    atmospheric_df1 = getData(f, lat, lon, height,
                            "IDW",
                            power_estimate=True,
                            inverse_monin_obukhov_length=False,
                            start_time_idx=0, end_time_idx=8760, time_stride=1,
                            saved_dt=dt,
                            srw=True)
    year = 2007
    srw = pd2srw(atmospheric_df1, lat, lon, height, year)
    return srw

    # lat, lon, height = 40.0 + delta, -91.0, 50
    # atmospheric_df2 = getData(f, lat, lon, height,
    #                             "IDW",
    #                             power_estimate=False,
    #                             inverse_monin_obukhov_length=False,
    #                             start_time_idx=0, end_time_idx=8760, time_stride=1,
    #                             saved_dt=dt)
    #
    # lat, lon, height = 38.0 + delta, -89.0 + delta, 60
    # atmospheric_df3 = getData(f, lat, lon, height,
    #                             "IDW",
    #                             power_estimate=False,
    #                             inverse_monin_obukhov_length=False,
    #                             start_time_idx=0, end_time_idx=8760, time_stride=1,
    #                             saved_dt=dt)
    #
    #combined = pd.concat([atmospheric_df1, atmospheric_df2, atmospheric_df3])
    #combined = pd.concat([atmospheric_df1])
    #return "Fetched 3 datasets; Total length: %d<br>Avg. ws=%f" % (len(combined), combined["ws"].mean())

# The following is used to confirm that efs volume was mounted
@app.route('/v2/lsera5', methods=['GET'])
def v2_lsera5():
    if os.path.exists("/era5-conus/"):
        output = os.listdir("/era5-conus/")
        output = "Contents of /era5-conus:<br>" + "<br>".join(output)
    else:
        output = "era5 directory isn't found"
    return output

def latlon2era5_idx(ds, lat, lon):
    # The following relies on u100 being one of the variables in the dataset
    lats = ds.u100.latitude.values
    lons = ds.u100.longitude.values
    lat_closest_idx = np.abs(lats - lat).argmin()
    lon_closest_idx = np.abs(lons - lon).argmin()
    return lat_closest_idx, lon_closest_idx

def get_era5_data_100m(ds, lat, lon):

    if type(ds) == type([]) and len(ds) > 1:
        # Support the case where ds is a list of ds/grib files
        idx_for_all_ds = [latlon2era5_idx(ds_indiv, lat, lon) for ds_indiv in ds]

        # Check if all lat_idx, and lon_idx pairs are the same; otherwise, raise an error
        for idx in range(1,len(idx_for_all_ds)):
            if idx_for_all_ds[idx] != idx_for_all_ds[idx-1]:
                raise ValueError("Mismatch detected for lat/lon indices across given files.")

        lat_idx, lon_idx = idx_for_all_ds[0][0], idx_for_all_ds[0][1]

        df_list = []
        for ds_indiv in ds:
            u100 = ds_indiv.u100.values[:,lat_idx,lon_idx]
            v100 = ds_indiv.v100.values[:,lat_idx,lon_idx]
            tt = ds_indiv.u100.time.values
            df = pd.DataFrame({"datetime": tt, "u100": u100.flatten(), "v100": v100.flatten()})
            df["datetime"] = pd.to_datetime(df["datetime"])
            df["ws100"] = np.sqrt(df["u100"]**2 + df["v100"]**2)
            df_list.append(df)
        return pd.concat(df_list).sort_values("datetime").reset_index(drop=True)

    else:
        # Treat ds as a single file
        if type(ds) == type([]):
            ds = ds[0]

        lat_idx, lon_idx = latlon2era5_idx(ds, lat, lon)
        u100 = ds.u100.values[:,lat_idx,lon_idx]
        v100 = ds.v100.values[:,lat_idx,lon_idx]
        tt = ds.u100.time.values
        df = pd.DataFrame({"datetime": tt, "u100": u100.flatten(), "v100": v100.flatten()})
        df["datetime"] = pd.to_datetime(df["datetime"])
        df["ws100"] = np.sqrt(df["u100"]**2 + df["v100"]**2)
        return df

def get_era5_data(ds, lat, lon, height):
    df = get_era5_data_100m(ds, lat, lon)
    if height == 100:
        df["ws"] = df["ws100"]
    else:
        # Power-law vertical interpolation
        df["ws"] = df["ws100"] * ((height/100.0)**(1/7.0))
    return df

@app.route('/v2/era5', methods=['GET'])
def v2_era5():
    try:
        height, lat, lon = validated_params_v2(request)

        era5_dir = "/era5-conus/"

        # Controlling indexpath is important; without it the code tries to write to read-only valume with /era5-conus
        # ds_list = [xr.open_dataset(os.path.join(era5_dir, "conus-%s-hourly.grib" % year), engine="cfgrib", \
        #             backend_kwargs={"indexpath": "/tmp/conus-%s-hourly.grib.idx" % year}) \
        #        for year in ['2020', '2021', '2022', '2023']]

        # One year for now
        ds_list = [xr.open_dataset(os.path.join(era5_dir, "conus-%s-hourly.grib" % year), engine="cfgrib", \
                    backend_kwargs={"indexpath": "/tmp/conus-%s-hourly.grib.idx" % year}) \
               for year in ['2020']]

        atmospheric_df = get_era5_data(ds_list, lat, lon, height=height)

        plot_monthly_avg(atmospheric_df, \
                         title="(%f, %f), %.0fm hub height" % (lat, lon, height),\
                         save_to_file='saved.png',\
                         show_avg_across_years=True,
                         show_overall_avg=True)
        return flask.send_file('saved.png')

    except:
        tb = traceback.format_exc().replace("\n", "<br>")
        return tb


def main():
    app.run(host=host, port=port)


if __name__ == "__main__":
    main()
