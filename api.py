import flask
from flask import request, jsonify
from flask_cors import CORS
import json
import argparse

from windspeed import *
from winddirection import *
from hsds_helpers import *
from invalid_usage import InvalidUsage
from helpers import *

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

@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

# Home/documentation route
@app.route('/', methods=['GET'])
def home():
    # Serve documentation produced by apiDoc
    return flask.send_file('doc/index.html')

# This helps serve files that are part of the apiDoc output (in /doc)
@app.route('/<foldername>/<path:filename>')
def doc_folder_file(foldername, filename):
    return flask.send_from_directory("doc/" + foldername, filename)

# This helps serve files that are part of the apiDoc output (in /doc)
@app.route('/<path:filename>')
def doc_file(filename):
    if filename.endswith(".js") or filename.endswith(".json"):
        return flask.send_from_directory("doc", filename)


# Fully functional route for windspeed
@app.route('/v1/timeseries/windspeed', methods=['GET'])
@timeit
def v1_ws():
    """
    @api {get} /timeseries/windspeed Request windspeed estimates
    @apiVersion 1.0.0
    @apiName GetWindspeed
    @apiGroup Wind Speed

    @apiDescription Request windspeed estimates for a particular site, for a specified height, and corresponding to the given time interval.

    @apiSampleRequest tap-api.nrel.gov/v1/timeseries/windspeed?height=50m&lat=40.7128&lon=-74.0059&start_date=20100302&stop_date=20120101&vertical_interpolation=linear&spatial_interpolation=idw

    @apiSuccess {String} JSON JSON with `timestamp` and `windspeed` series

    @apiSuccessExample Example output on success:
    {"timestamp":{"0":"2011-03-02 00:00:00","1":"2011-03-02 01:00:00","2":"2011-03-02 02:00:00",
    "3":"2011-03-02 03:00:00","4":"2011-03-02 04:00:00","5":"2011-03-02 05:00:00"},
    "windspeed":{"0":3.5925824239,"1":5.440796747,"2":4.8400592119,"3":5.4325136517,"4":4.9044365704,"5":5.2218727909}}

    @apiParam {Float} height Height (in meters) for which the windspeed estimates are requested; notation: `XXm`, where XX is an integer of float
    @apiParam {Float} lat Latitude (in degrees) for a particular site
    @apiParam {Float} lon Longitude (in degrees) for a particular site
    @apiParam {String} start_date Beginning of the time interval in the format: YYYYMMDD
    @apiParam {String} stop_date End of the time interval in the format: YYYYMMDD
    @apiParam {String} vertical_interpolation Method used for vertical interpolation; allowed: `nearest`, `linear`, `neutral_power`, `stability_power`
    @apiParam {String} spatial_interpolation Method used for spatial interpolation; allowed: `nearest`, `linear`, `cubic`, `idw`
    @apiParam {String} [username] Optional attribute of the HSDS credentials
    @apiParam {String} [password] Optional attribute of the HSDS credentials
    @apiParam {String} [api_key] Optional attribute of the HSDS credentials. If one of `username`, `password`, and `api_key` is specified, all three of these attributes should be specified. Alternatively, if none of these is specified, the default values will be use for rate-limited, demo access 
    """

    print("v1_ws")

    height, lat, lon,\
        start_date, stop_date,\
        spatial_interpolation,\
        vertical_interpolation = validated_params_windspeed(request)
    hsds_f = connected_hsds_file(request,config)

    finalized_df, debug_info = prepare_windpseed(height, lat, lon, start_date, stop_date, spatial_interpolation,
                                                 vertical_interpolation, hsds_f, DEBUG_OUTPUT)

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

    @apiDescription Request wind direction estimates for a particular site, for a specified height, and corresponding to the given time interval. `Nearest-neighbor` is used for both spatial and vertical interpolations.

    @apiSampleRequest tap-api.nrel.gov/v1/timeseries/winddirection?height=50m&lat=40.7128&lon=-74.0059&start_date=20100302&stop_date=20120101

    @apiSuccess {String} JSON JSON with `timestamp` and `winddirection` series

    @apiSuccessExample Example output on success:
    {"timestamp":{"0":"2011-03-02 00:00:00","1":"2011-03-02 01:00:00","2":"2011-03-02 02:00:00",
    "3":"2011-03-02 03:00:00","4":"2011-03-02 04:00:00","5":"2011-03-02 05:00:00"},
    "winddirection":{"0":188.9596252441,"1":183.7189788818,"2":193.1125793457,"3":184.4605865479,"4":200.0836181641,"5":215.415512085}}

    @apiParam {Float} height Height (in meters) for which the wind direction estimates are requested; notation: `XXm`, where XX is an integer of float
    @apiParam {Float} lat Latitude (in degrees) for a particular site
    @apiParam {Float} lon Longitude (in degrees) for a particular site
    @apiParam {String} start_date Beginning of the time interval in the format: YYYYMMDD
    @apiParam {String} stop_date End of the time interval in the format: YYYYMMDD
    @apiParam {String} [username] Optional attribute of the HSDS credentials
    @apiParam {String} [password] Optional attribute of the HSDS credentials
    @apiParam {String} [api_key] Optional attribute of the HSDS credentials. If one of `username`, `password`, and `api_key` is specified, all three of these attributes should be specified. Alternatively, if none of these is specified, the default values will be use for rate-limited, demo access
    """

    print("v1_wd")

    height, lat, lon,\
        start_date, stop_date = validated_params_winddirection(request)
    hsds_f = connected_hsds_file(request,config)

    finalized_df, debug_info = prepare_winddirection(height, lat, lon, start_date, stop_date, hsds_f, DEBUG_OUTPUT)

    if DEBUG_OUTPUT:
        return "<br>".join(debug_info)
    else:
        return finalized_df.to_json()

# Fully functional route for winddirection
@app.route('/v1/windrose', methods=['GET'])
def v1_wr():
    """
    @api {get} /windrose Request windrose estimates
    @apiVersion 1.0.0
    @apiName GetWindrose
    @apiGroup Wind Rose

    @apiDescription Convenience function that convolves wind direction and wind speed to create a wind rose as output.

    @apiSampleRequest tap-api.nrel.gov/v1/windrose?height=50m&lat=40.7128&lon=-74.0059&start_date=20100302&stop_date=20120101

    @apiSuccess {String} JSON with percentage observations in each of 8 radial segments (N, NE, E, SE, S, SW, W, NW) and each of 4 wind speed classes (11-14 mps, 8-11 mps, 5-8 mps, less than 5 mps)

    @apiSuccessExample Example output on success:
    {"11-14 m/s": [77.5, 72.5, 70.0, 45.0, 22.5, 42.5, 40.0, 62.5], "8-11 m/s": [57.5, 50.0, 45.0, 35.0, 20.0, 22.5, 37.5, 55.0], "5-8 m/s": [40.0, 30.0, 30.0, 35.0, 7.5, 7.5, 32.5, 40.0], "< 5 m/s": [20.0, 7.5, 15.0, 22.5, 2.5, 2.5, 12.5, 22.5]}

    @apiParam {Float} height Height (in meters) for which the wind direction estimates are requested; notation: `XXm`, where XX is an integer of float
    @apiParam {Float} lat Latitude (in degrees) for a particular site
    @apiParam {Float} lon Longitude (in degrees) for a particular site
    @apiParam {String} start_date Beginning of the time interval in the format: YYYYMMDD
    @apiParam {String} stop_date End of the time interval in the format: YYYYMMDD
    @apiParam {String} [username] Optional attribute of the HSDS credentials
    @apiParam {String} [password] Optional attribute of the HSDS credentials
    @apiParam {String} [api_key] Optional attribute of the HSDS credentials. If one of `username`, `password`, and `api_key` is specified, all three of these attributes should be specified. Alternatively, if none of these is specified, the default values will be use for rate-limited, demo access
    """
    print("v1_wr")
    hsds_f = connected_hsds_file(request,config)

    height, lat, lon, \
    start_date, stop_date, \
    spatial_interpolation, \
    vertical_interpolation = validated_params_windspeed(request)

    wd_df, wd_debug_info = prepare_winddirection(height, lat, lon, start_date, stop_date, hsds_f, DEBUG_OUTPUT)

    ws_df, ws_debug_info = prepare_windpseed(height, lat, lon, start_date, stop_date, spatial_interpolation,
                                                 vertical_interpolation, hsds_f, DEBUG_OUTPUT)

    combined_df = ws_df.merge(wd_df,on='timestamp')
    combined_df["windspeed_class"] = combined_df["windspeed"].apply(windspeed_class)
    combined_df["direction_class"] = combined_df["winddirection"].apply(direction_class)

    ret = windrose_from_df(combined_df)

    if DEBUG_OUTPUT:
        return "<br>".join(ws_debug_info + wd_debug_info)
    else:
        return json.dumps(ret)


@app.route('/check', methods=['GET'])
def check():
    return json.dumps({"Status": "OK!"})


def main():
    app.run(host=host, port=port)


if __name__ == "__main__":
    main()
