import flask
from flask import request, jsonify
import datetime

app = flask.Flask(__name__)
app.config["DEBUG"] = True


def validated_dt(date_str):
    try:
        return datetime.datetime.strptime(date_str, '%Y%m%d')
    except ValueError:
        raise ValueError("Incorrect date format, should be: YYYYMMDD")

# "About" route
@app.route('/', methods=['GET'])
def home():
    return """<h1>DW-TAP Project's API Endpoint</h1>
    <p> This endpoint supports the following requests:<br>
    GET /v1/timeseries/windspeed?height=50m&start_date=20100302&\
    stop_date=20120101&vertical_interpolation=poly2&\
    spatial_interpolation=idw&bias_correction=default&unit=m/s</p>"""


# Fully functional route (currently only prints validated parameters)
@app.route('/v1/timeseries/windspeed', methods=['GET'])
def v1_ws():
    result = []

    if 'height' in request.args:
        height_str = request.args['height']
        if len(height_str) > 0 and height_str[-1] == "m":
            height = float(height_str.rstrip("m"))
            result.append("Specified height: %f" % height)
        else:
            return 'Error: height provided is malformed. \
            Please use the notation: "XXm" \
            (where "m" is for meters and XX is a number, \
            doesn\'t need to be an integer).'

    if 'start_date' in request.args:
        start_date_str = request.args['start_date']
        start_date = validated_dt(start_date_str)
        result.append("Specified start_date: %s" % str(start_date))
    else:
        return "Error: No start_date field provided. \
        Please specify start_date."

    if 'stop_date' in request.args:
        stop_date_str = request.args['stop_date']
        stop_date = validated_dt(stop_date_str)
        result.append("Specified stop_date: %s" % str(stop_date))
    else:
        return "Error: No stop_date field provided. \
        Please specify stop_date."

    return "".join([s + "<br>" for s in result])


app.run()
