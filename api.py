import flask
from flask import request, jsonify
import datetime
import h5pyd
import json
from pyproj import Proj
import numpy as np
import pandas as pd
import cartopy.crs as ccrs

app = flask.Flask(__name__)
app.config["DEBUG"] = True

with open('config.json', 'r') as f:
    config = json.load(f)

# Appropriate for lat/lon pairs
crs_from = ccrs.PlateCarree()

# This projection uses USA_Contiguous_Albers_Equal_Area_Conic_USGS_version --
# typical projection for historical USGS maps of the lower 48
# Reference: https://spatialreference.org/ref/sr-org/usa_contiguous_/
# albers_equal_area_conic_usgs_version-2/
crs_to = ccrs.AlbersEqualArea(central_longitude=-96.0,
                              central_latitude=23.0,
                              false_easting=0.0,
                              false_northing=0.0,
                              standard_parallels=(29.5, 45.5), globe=None)


def coordXform(orig_crs, target_crs, x, y):
    return target_crs.transform_points(orig_crs, x, y)


class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv


@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


def validated_dt(date_str):
    """ Create and return a datetime object based on the given string.
    If the string is inappropriate, raise an error with helpful message.
    """
    try:
        return datetime.datetime.strptime(date_str, '%Y%m%d')
    except ValueError:
        raise InvalidUsage("Incorrect date format, should be: YYYYMMDD")


def connected_hsds_file(request):
    """ Return a file object that corresponds to the HSDS resource
    specified in the request (using domain, endpoint, username, password,
    and api_key parameters).

    This function processes request parameters, uses default values for
    'domain' and 'endpoint' if they aren't specified,
    and uses demo API key (rate-limited)
    if none of the relevant parameters is specified; it uses read-only mode.
    """
    if 'domain' in request.args:
        domain = request.args['domain']
    else:
        domain = config["hsds"]["domain"]

    if 'endpoint' in request.args:
        endpoint = request.args['endpoint']
    else:
        endpoint = config["hsds"]["endpoint"]

    if ('username' not in request.args) and ('password' not in request.args)\
       and ('api_key' not in request.args):

        username = config["hsds"]["username"]
        password = config["hsds"]["password"]
        api_key = config["hsds"]["api_key"]
    else:
        if 'username' in request.args:
            username = request.args['username']
        else:
            raise InvalidUsage(("HSDS username is not specified. "
                                "Specify all three--username, password, "
                                "and api_key--or remove all three from "
                                "request to use demo credentials."))

        if 'password' in request.args:
            password = request.args['password']
        else:
            raise InvalidUsage(("HSDS password is not specified. "
                                "Specify all three--username, password, "
                                "and api_key--or remove all three from "
                                "request to use demo credentials."))

        if 'api_key' in request.args:
            api_key = request.args['api_key']
        else:
            raise InvalidUsage(("HSDS api_key is not specified. "
                                "Specify all three--username, password, "
                                "and api_key--or remove all three from "
                                "request to use demo credentials."))

    try:
        f = h5pyd.File(domain=domain,
                       endpoint=endpoint,
                       username=username,
                       password=password,
                       api_key=api_key,
                       mode='r')
        return f
    except OSError:
        raise InvalidUsage(("Failed to access specfied HSDS resource. "
                            "Check credentials: "
                            "domain, endpoint, username, password, api_key"),
                           status_code=403)


def validated_params(request):
    """ Returns extracted, processed, and validated
    required request parameters.
    """
    if 'height' in request.args:
        height_str = request.args['height']
        if len(height_str) > 0 and height_str[-1] == "m":
            try:
                height = float(height_str.rstrip("m"))
            except ValueError:
                raise InvalidUsage(("Height provided is malformed. "
                                    "Please use the notation: 'XXm' "
                                    "(where 'm' is for meters and XX is a "
                                    "positive number; it doesn't need to be "
                                    "an integer)."))
            if height < 0:
                raise InvalidUsage("Height should be a positive number.")
        else:
            raise InvalidUsage(("Height provided is malformed. "
                                "Please use the notation: 'XXm' "
                                "(where 'm' is for meters and XX is a "
                                "positive number; it doesn't need to be "
                                "an integer)."))

    if 'lat' in request.args:
        try:
            lat = float(request.args['lat'])
        except ValueError:
            raise InvalidUsage(("Lat (latitude) provided is invalid."
                                "Needs to be a number."))
    else:
        raise InvalidUsage("Lat (latitude) is not provided.")

    if 'lon' in request.args:
        try:
            lon = float(request.args['lon'])
        except ValueError:
            raise InvalidUsage(("Lon (longitude) provided is invalid."
                                "Needs to be a number."))
    else:
        raise InvalidUsage("Lon (longitude) is not provided.")

    if 'start_date' in request.args:
        start_date = validated_dt(request.args['start_date'])
    else:
        raise InvalidUsage(("Error: No start_date field provided. "
                            "Please specify start_date."))

    if 'stop_date' in request.args:
        stop_date = validated_dt(request.args['stop_date'])
    else:
        raise InvalidUsage(("Error: No stop_date field provided. "
                            "Please specify stop_date."))

    return height, lat, lon, start_date, stop_date


# This function finds the nearest x/y indices for a given lat/lon.
# Rather than fetching the entire coordinates database, which is 500+ MB, this
# uses the Proj4 library to find a nearby point and converts to x/y indices
def indicesForCoord(f, lat_index, lon_index):
    dset_coords = f['coordinates']
    projstring = """+proj=lcc +lat_1=30 +lat_2=60
                    +lat_0=38.47240422490422 +lon_0=-96.0
                    +x_0=0 +y_0=0 +ellps=sphere
                    +units=m +no_defs """
    projectLcc = Proj(projstring)
    origin_ll = reversed(dset_coords[0][0])  # Grab origin directly from db
    origin = projectLcc(*origin_ll)

    coords = (lon_index, lat_index)
    coords = projectLcc(*coords)
    delta = np.subtract(coords, origin)
    ij = [int(round(x/2000)) for x in delta]
    return tuple(reversed(ij))


def find_tile(f, lat, lon, radius=3, trim=16):
    """ Return dataframe with information about gridpoints in resource f that
    are neighboring (lat, lon). At first, there will be (radius*2) ^ 2
    entries/neighbors. The dataframe will be sorted by the distance (in meters)
    from (lat, lon); the first row -- nearest neighbor. Finally,
    the function will return N=trim first/nearest rows.
    """
    point_idx = indicesForCoord(f, lat, lon)
    point_xy = coordXform(crs_from, crs_to,
                          np.array([lon]), np.array([lat]))[0]

    # # TODO: Edge cases (around boundaries) need to be handled differently
    neighbors_to_check = []
    for x_idx in range(point_idx[0] - radius, point_idx[0] + radius + 1):
        for y_idx in range(point_idx[1] - radius, point_idx[1] + radius + 1):
            neighbors_to_check.append([x_idx, y_idx])

    # Get lat/lon pairs for all neighbors (faster than one-at-a-time)
    neighbors_latlon = [list(p) for p in f["coordinates"][neighbors_to_check]]

    # Convert all neighbors' lat/lon pairs to x/y
    neighbors_xy = coordXform(crs_from, crs_to,
                              np.array(neighbors_latlon).reshape(-1, 2)[:, 1],
                              np.array(neighbors_latlon).reshape(-1, 2)[:, 0])

    res = pd.DataFrame(columns=["x_idx", "y_idx", "lat", "lon", "d"])
    for idx, latlon, xy in zip(neighbors_to_check,
                               neighbors_latlon, neighbors_xy):

        # Distance in meters calculated after applying projections
        d = np.sqrt((xy[0] - point_xy[0]) ** 2 + (xy[1] - point_xy[1]) ** 2)
        res.loc[len(res)] = [idx[0], idx[1], latlon[0], latlon[1], d]

    return res.sort_values("d")[:trim]

# "About" route
@app.route('/', methods=['GET'])
def home():
    return config["html_home"]

# Fully functional route (currently only prints validated parameters)
@app.route('/v1/timeseries/windspeed', methods=['GET'])
def v1_ws():
    height, lat, lon, start_date, stop_date = validated_params(request)
    hsds_f = connected_hsds_file(request)

    result = []
    result.append("Specified height: %f" % height)
    result.append("Specified lat: %f" % lat)
    result.append("Specified lon: %f" % lon)
    result.append("Specified start_date: %s" % str(start_date))
    result.append("Specified stop_date: %s" % str(stop_date))

    # # DEBUG:
    NewYorkCity_idx = indicesForCoord(hsds_f, lat, lon)
    result.append(("y,x indices for New York City: "
                   "\t\t {}".format(NewYorkCity_idx)))
    result.append("Coordinates of New York City: \t {}".format((lat, lon)))
    result.append(("Coordinates of nearest point: "
                   "\t {}".format(hsds_f["coordinates"][NewYorkCity_idx])))

    tile_df = find_tile(hsds_f, lat, lon)
    # # DEBUG:
    for idx, row in tile_df.iterrows():
        result.append(str(row))

    return "".join([s + "<br>" for s in result])


app.run()
