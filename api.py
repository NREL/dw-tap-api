import flask
from flask import request, jsonify
from flask_cors import CORS
import datetime
import h5pyd
import json
from pyproj import Proj
import numpy as np
import pandas as pd
import cartopy.crs as ccrs
import dateutil
from scipy.interpolate import griddata
import time
import concurrent.futures
import points
import timeseries
import interpolation

app = flask.Flask(__name__)
app.config["DEBUG"] = False
# Note: may consider limiting CORS for production deployment
#       this opens up to AJAX calls from any domain
cors = CORS(app)

# Switch from desired json output to debug info and intemediate dataframes
DEBUG_OUTPUT = False

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


def timeit(method):
    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()
        if 'log_time' in kw:
            name = kw.get('log_name', method.__name__.upper())
            kw['log_time'][name] = int((te - ts) * 1000)
        else:
            print("%r  %2.2f ms" % (method.__name__, (te - ts) * 1000))
        return result
    return timed


def validated_dt(date_str):
    """ Create and return a datetime object based on the given string.
    If the string is inappropriate, raise an error with helpful message.
    """
    try:
        return datetime.datetime.strptime(date_str, '%Y%m%d')
    except ValueError:
        raise InvalidUsage("Incorrect date format, should be: YYYYMMDD")


@timeit
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
        raise InvalidUsage(("Failed to access specified HSDS resource. "
                            "Check credentials: "
                            "domain, endpoint, username, password, api_key. "
                            "It could be a transient HSDS connection issue. "
                            "Try again later."),
                           status_code=403)


@timeit
def validated_params_windspeed(request):
    """ Returns extracted, processed, and validated
    required request parameters. This version is desiged for windspeed queries.
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

    if 'spatial_interpolation' in request.args:
        si = request.args['spatial_interpolation']
        si_allowed = ["nearest", "linear", "cubic", "idw"]
        if si not in si_allowed:
            raise InvalidUsage(("Error: invalid spatial_interpolation. "
                                "Choose one of: " + str(si_allowed)))
    else:
        raise InvalidUsage(("Error: No spatial_interpolation field provided. "
                            "Please specify spatial_interpolation."))

    if 'vertical_interpolation' in request.args:
        vi = request.args['vertical_interpolation']
        vi_allowed = ["nearest", "linear", "neutral_power", "stability_power"]
        if vi not in vi_allowed:
            raise InvalidUsage(("Error: invalid vertical_interpolation. "
                                "Choose one of: " + str(vi_allowed)))

        # Map the name from the request to name that have been used in
        # vertical interpolation code
        vi_name_map = {"nearest": "nn",
                       "linear": "polynomial",
                       "neutral_power": "neutral_power_law",
                       "stability_power": "stability_adjusted_power_law"}
        if vi in vi_name_map.keys():
            vi = vi_name_map[vi]
    else:
        raise InvalidUsage(("Error: No vertical_interpolation field provided. "
                            "Please specify vertical_interpolation."))

    return height, lat, lon, start_date, stop_date, si, vi


@timeit
def validated_params_winddirection(request):
    """ Returns extracted, processed, and validated
    required request parameters.
    This version is desiged for winddirection queries.
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


@timeit
def find_tile(f, lat, lon, radius=3, trim=4):
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

    res = pd.DataFrame(columns=["x_idx", "y_idx", "lat", "lon",
                                "x_centered", "y_centered", "d"])
    for idx, latlon, xy in zip(neighbors_to_check,
                               neighbors_latlon, neighbors_xy):

        # Distance in meters calculated after applying projections
        dx = xy[0] - point_xy[0]
        dy = xy[1] - point_xy[1]
        d = np.sqrt(dx ** 2 + dy ** 2)
        res.loc[len(res)] = [idx[0], idx[1],
                             latlon[0], latlon[1], dx, dy, d]

    res["x_idx"] = pd.to_numeric(res["x_idx"], downcast='integer')
    res["y_idx"] = pd.to_numeric(res["y_idx"], downcast='integer')
    return res.sort_values("d")[:trim].reset_index(drop=True)


def available_heights(f, prefix="windspeed"):
    """ Return list of all heights available in resource f --
    datasets named "<prefix>_XXm", where XX is a number.
    """
    prefix = prefix.rstrip("_") + "_"
    try:
        heights = sorted([int(attr.replace(prefix, "").rstrip("m"))
                         for attr in
                         list(f) if prefix in attr])
    except ValueError:
        raise InvalidUsage("Problem with processing WTK heights.")
    return heights


def available_datasets(f):
    """ Return list of all datasets available in resource f.
    """
    try:
        datasets = sorted(list(f))
    except ValueError:
        raise InvalidUsage("Problem with processing WTK datasets.")
    return datasets


def time_indices(f, start_date, stop_date):
    """ Return lists of time indices and timestamps corresponding to the the
    requested time interval: [start_date, stop_date].
    """
    dt = f["datetime"]
    dt = pd.DataFrame({"datetime": dt[:]}, index=range(0, dt.shape[0]))
    dt['datetime'] = dt['datetime'].apply(dateutil.parser.parse)
    selected = dt.loc[(dt.datetime >= start_date) &
                      (dt.datetime <= stop_date)]
    selected_inices = selected.index.tolist()
    selected_timestamps = selected.datetime.tolist()
    return selected_inices, selected_timestamps


@timeit
def extract_ts_for_neighbors_sequential(tile_df, tidx, dset):
    """ Sequential (slow) implementation of extract_ts_for_neighbors().
    """
    res_df = pd.DataFrame(index=tidx)

    tidx_min = np.array(tidx).min()
    tidx_max = np.array(tidx).max()

    for idx, row in tile_df.iterrows():

        neighbor_data = dset[tidx_min:tidx_max+1,
                             row.x_idx, row.y_idx]
        column_name = "%d-%d" % (row.x_idx, row.y_idx)
        res_df[column_name] = neighbor_data

    return res_df


def extract_ts_thread(args):
    """ Function run in its own thread when multiple WTK subsets are extracted.
    """
    dset, tidx, x_idx, y_idx = args

    res_df = pd.DataFrame(index=tidx)

    tidx_min = np.array(tidx).min()
    tidx_max = np.array(tidx).max()

    neighbor_data = dset[tidx_min:tidx_max+1, x_idx, y_idx]
    column_name = "%d-%d" % (x_idx, y_idx)

    res_df[column_name] = neighbor_data

    return res_df


@timeit
def extract_ts_for_neighbors_parallel(tile_df, tidx, dset):
    """ Parallel (fast) implementation of extract_ts_for_neighbors().
    """
    tasks = [(dset, tidx, row.x_idx, row.y_idx)
             for idx, row in tile_df.iterrows()]

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(extract_ts_thread, t) for t in tasks]
        results = [f.result() for f in futures]

    res_df = pd.concat(results, axis=1)

    return res_df


@timeit
def extract_ts_for_neighbors(tile_df, tidx, dset, impl="parallel"):
    """ Extract WTK timeseries for all neighbor points in tile_df dataframe.
    Only extract values for times that correspond to time indices in tidx.
    Extract values from dataset dset corresponding to a specific height.
    Columns in the returned dataframe will match rows in tile_df
    and the *order will be preserved*.

    Behind the scenes, a sequential or a parallel implementation is called.
    """
    if impl == "sequential":
        return extract_ts_for_neighbors_sequential(tile_df, tidx, dset)
    elif impl == "parallel":
        return extract_ts_for_neighbors_parallel(tile_df, tidx, dset)
    else:
        raise ValueError(("Invalid usage of extract_ts_for_neighbors()."
                          "Choose implementation: sequential or parallel."))


def interpolate_spatially_row(row, neighbor_xy_centered, method='nearest'):
    """ This function provides per-row spatial interpolatoin using
    nearest, linear, cubic, and IDW (inverse-distance weighting) methods.
    It is conveninet to use this function with df.apply().
    """
    if method in ["nearest", "linear", "cubic"]:
        result = griddata(neighbor_xy_centered, row.values,
                          ([0], [0]), method=method)[0]
    elif method == "idw":
        numerator = 0
        denominator = 0
        for idx in range(len(row.values)):
            w = 1.0 / np.sqrt(neighbor_xy_centered[idx][0] ** 2 +
                              neighbor_xy_centered[idx][1] ** 2)
            numerator += w * row.values[idx]
            denominator += w
        result = numerator/denominator

    return result


@timeit
def interpolate_spatially(tile_df, neighbor_ts_df,
                          method='nearest', neighbors_number=4):
    """ Process a single-height dataframe for
    single location with timeseries for neighboring gridpoints.
    Method should be validated in validated_params_X()."""

    res_df = pd.DataFrame(index=neighbor_ts_df.index)

    # This assumes that tile_df is sorted by distance, which should be
    # handled in find_tile()
    res_df["min_dist"] = tile_df.loc[0]["d"]

    neighbor_xy_centered = [(row.x_centered, row.y_centered)
                            for idx, row in tile_df.iterrows()]

    if method == "nearest":
        # Nearest is the only method for which the results don't change
        # if we change number of neighbors used; no trimming needed
        res_df["spatially_interpolated"] = \
            neighbor_ts_df.apply(interpolate_spatially_row,
                                 args=(neighbor_xy_centered, 'nearest'),
                                 axis=1)
    else:
        # "neighbor_ii[:neighbors_number]" below is used to make sure
        # that first/closest n=neighbors_number points are used;
        # the same with: neighbor_xy_centered[:neighbors_number]
        res_df["spatially_interpolated"] = \
            neighbor_ts_df.apply(interpolate_spatially_row,
                                 args=(neighbor_xy_centered[:neighbors_number],
                                       method),
                                 axis=1)
    return res_df


def heights_below_and_above(all_heights, selected_height):
    """ Out of the given list of all heights, return the two
    that are below and above the specified height.
    Cases where selected_height is exactly one of heights in the all_heights
    list (including edges) are handled outside of this function.
    """
    arr = np.array(all_heights)
    height_below = arr[arr < selected_height].max()
    height_above = arr[arr > selected_height].min()
    return height_below, height_above


def df2strings(df):
    """ Helper function for outputing a dataframe in the form of a list of
    strings (for each row) for debug.
    """
    return [str(row) for idx, row in df.iterrows()]

# "About" route
@app.route('/', methods=['GET'])
def home():
    return config["html_home"]

# Fully functional route for windspeed
@app.route('/v1/timeseries/windspeed', methods=['GET'])
@timeit
def v1_ws():
    debug_info = []

    height, lat, lon,\
        start_date, stop_date,\
        spatial_interpolation,\
        vertical_interpolation = validated_params_windspeed(request)
    hsds_f = connected_hsds_file(request)
    heights = available_heights(hsds_f, prefix="windspeed")
    datasets = available_datasets(hsds_f)

    bypass_vertical_interpolation = False
    if height.is_integer() and int(height) in heights:
        bypass_vertical_interpolation = True

    if height < np.min(heights) or height > np.max(heights):
        raise InvalidUsage(("Requested height is outside "
                            "of allowed range: [%.2f, %.2f]" %
                            (np.min(heights), np.max(heights))))

    if "inversemoninobukhovlength_2m" not in datasets:
        raise InvalidUsage(("WTK does not include one of required datasets: "
                            "inversemoninobukhovlength_2m"))

    tidx, timestamps = time_indices(hsds_f, start_date, stop_date)

    desired_point = points.XYZPoint(lat, lon, height, 'desired')

    if DEBUG_OUTPUT:
        debug_info.append("Specified height: %f" % height)
        debug_info.append("Specified lat: %f" % lat)
        debug_info.append("Specified lon: %f" % lon)
        debug_info.append("Specified start_date: %s" % str(start_date))
        debug_info.append("Specified stop_date: %s" % str(stop_date))
        debug_info.append("Available heights: %s" % str(heights))
        debug_info.append("Time indices: %s" % str(tidx))
        debug_info.append("Available datasets: %s" % str(datasets))

    tile_df = find_tile(hsds_f, lat, lon)

    if DEBUG_OUTPUT:
        debug_info += df2strings(tile_df)

    if not bypass_vertical_interpolation:
        # Use Nearest Neighbor for imol -- inversemoninobukhovlength_2m
        imol_dset = hsds_f["inversemoninobukhovlength_2m"]
        # head(1) is sufficient for nearest neighbor
        imol_neighbor_ts_df = extract_ts_for_neighbors(tile_df.head(1),
                                                       tidx, imol_dset)
        imol_df = interpolate_spatially(tile_df.head(1), imol_neighbor_ts_df,
                                        method="nearest")
        imol_df.rename(columns={"spatially_interpolated": "imol"},
                       inplace=True)

        if DEBUG_OUTPUT:
            debug_info += df2strings(imol_df)

    if bypass_vertical_interpolation:
        selected_heights = [int(height)]
    else:
        height_below, height_above = heights_below_and_above(heights, height)
        selected_heights = [height_below, height_above]

    xyz_points = []
    for h_idx, h in enumerate(selected_heights):
        dset = hsds_f["windspeed_%dm" % h]

        neighbor_ts_df = extract_ts_for_neighbors(tile_df, tidx, dset)

        interpolated_df = interpolate_spatially(tile_df, neighbor_ts_df,
                                                method=spatial_interpolation,
                                                neighbors_number=4)
        interpolated_df["timestamp"] = timestamps

        if DEBUG_OUTPUT:
            debug_info += df2strings(interpolated_df)

        if not bypass_vertical_interpolation:
            p = points.XYZPoint(lat, lon, h, 'model',
                                timeseries=[timeseries.timeseries(
                                    interpolated_df["spatially_interpolated"],
                                    var="ws")])
            xyz_points.append(p)

            # Special handling for processing two heights in this case
            if h_idx == 0:
                interpolated_df_combined = interpolated_df.rename(
                                           columns={"spatially_interpolated":
                                                    "height_below"})
            elif h_idx == 1:
                interpolated_df_combined["height_above"] = \
                    interpolated_df["spatially_interpolated"]
                interpolated_df = interpolated_df_combined
            else:
                raise InvalidUsage(("Height selection should pick "
                                    "only 2 heights in this case, not more."))

    if bypass_vertical_interpolation:
        interpolated_df["timestamp"] = interpolated_df["timestamp"].astype(str)
        finalized_df = interpolated_df[["timestamp",
                                        "spatially_interpolated"]
                                       ].reset_index(drop=True).rename(
                                       columns={"spatially_interpolated":
                                                "windspeed"})
        if DEBUG_OUTPUT:
            return "<br>".join(debug_info)
        else:
            return finalized_df.to_json()
    else:
        xy_point = points.XYPoint.from_xyz_points(xyz_points)
        xy_point.set_timeseries(timeseries.timeseries(imol_df["imol"],
                                var='stability'))
        vi = interpolation.interpolation(
            desired_point,
            xy_point,
            vertically_interpolate=True,
            spatially_interpolate=False,
            vertical_interpolation_techniques=vertical_interpolation)
        vi.interpolate()

        interpolated_df["windspeed"] = vi._model_transformed[0].\
            _xyz_points._time_series[0]._timeseries

        interpolated_df["timestamp"] = interpolated_df["timestamp"].astype(str)
        finalized_df = interpolated_df[["timestamp", "windspeed"]
                                       ].reset_index(drop=True)
        if DEBUG_OUTPUT:
            return "<br>".join(debug_info)
        else:
            return finalized_df.to_json()

# Fully functional route for winddirection
@app.route('/v1/timeseries/winddirection', methods=['GET'])
def v1_wd():

    print("v1_wd")
    debug_info = []

    height, lat, lon,\
        start_date, stop_date = validated_params_winddirection(request)
    hsds_f = connected_hsds_file(request)
    heights = available_heights(hsds_f, prefix="winddirection")
    datasets = available_datasets(hsds_f)

    if height < np.min(heights) or height > np.max(heights):
        raise InvalidUsage(("Requested height is outside "
                            "of allowed range: [%.2f, %.2f]" %
                            (np.min(heights), np.max(heights))))

    tidx, timestamps = time_indices(hsds_f, start_date, stop_date)

    if DEBUG_OUTPUT:
        debug_info.append("Specified height: %f" % height)
        debug_info.append("Specified lat: %f" % lat)
        debug_info.append("Specified lon: %f" % lon)
        debug_info.append("Specified start_date: %s" % str(start_date))
        debug_info.append("Specified stop_date: %s" % str(stop_date))
        debug_info.append("Available heights: %s" % str(heights))
        debug_info.append("Time indices: %s" % str(tidx))
        debug_info.append("Available datasets: %s" % str(datasets))

    tile_df = find_tile(hsds_f, lat, lon, radius=1)

    nearest_h = heights[np.abs(np.array(heights) - height).argmin()]
    wd_dset = hsds_f["winddirection_%dm" % int(nearest_h)]
    neighbor_ts_df = extract_ts_for_neighbors(tile_df.head(1),
                                              tidx, wd_dset)
    neighbor_ts_df.columns = ["winddirection"]
    neighbor_ts_df["timestamp"] = timestamps

    neighbor_ts_df["timestamp"] = neighbor_ts_df["timestamp"].astype(str)
    finalized_df = neighbor_ts_df[["timestamp", "winddirection"]
                                  ].reset_index(drop=True)

    if DEBUG_OUTPUT:
        debug_info += df2strings(tile_df)
        debug_info += df2strings(neighbor_ts_df)
        return "<br>".join(debug_info)
    else:
        return finalized_df.to_json()


@app.route('/check', methods=['GET'])
def check():
    return json.dumps({"Status": "OK!"})


def main():
    app.run(host='0.0.0.0', port=80)


if __name__ == "__main__":
    main()
