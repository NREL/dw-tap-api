# -*- coding: utf-8 -*-
"""HSDS Interface.

This file includes functions that allow interacting with HSDS:
connect to it using specified credentials, extract available heights,
extract various timeseries, etc.
"""

import h5pyd
from invalid_usage import InvalidUsage
from timing import timeit
from pyproj import Proj
import pandas as pd
import numpy as np
import cartopy.crs as ccrs
import dateutil
import concurrent.futures
import time
from rex.resource_extraction import MultiYearWindX


@timeit
def connected_hsds_file(request, config):
    """ Return a file object that corresponds to the HSDS resource
    specified in the request (using domain, endpoint, username, password,
    and api_key parameters).

    This function processes request parameters, uses default values for
    'domain' and 'endpoint' if they aren't specified,
    and uses demo API key (rate-limited)
    if none of the relevant parameters is specified; it uses read-only mode.
    """
    # if 'domain' in request.args:
    #     domain = request.args['domain']
    # else:
    #     domain = config["hsds"]["domain"]
    #
    # if 'endpoint' in request.args:
    #     endpoint = request.args['endpoint']
    # else:
    #     endpoint = config["hsds"]["endpoint"]
    #
    # if ('username' not in request.args) and ('password' not in request.args)\
    #    and ('api_key' not in request.args):
    #
    #     username = config["hsds"]["username"]
    #     password = config["hsds"]["password"]
    #     api_key = config["hsds"]["api_key"]
    # else:
    #     if 'username' in request.args:
    #         username = request.args['username']
    #     else:
    #         raise InvalidUsage(("HSDS username is not specified. "
    #                             "Specify all three--username, password, "
    #                             "and api_key--or remove all three from "
    #                             "request to use demo credentials."))
    #
    #     if 'password' in request.args:
    #         password = request.args['password']
    #     else:
    #         raise InvalidUsage(("HSDS password is not specified. "
    #                             "Specify all three--username, password, "
    #                             "and api_key--or remove all three from "
    #                             "request to use demo credentials."))
    #
    #     if 'api_key' in request.args:
    #         api_key = request.args['api_key']
    #     else:
    #         raise InvalidUsage(("HSDS api_key is not specified. "
    #                             "Specify all three--username, password, "
    #                             "and api_key--or remove all three from "
    #                             "request to use demo credentials."))

    try:
        # This worked for public HSDS instance
        # f = h5pyd.File(domain=domain,
        #                endpoint=endpoint,
        #                username=username,
        #                password=password,
        #                api_key=api_key,
        #                mode='r')

        # This works for dedicated HSDS instance
        # f = h5pyd.File(domain=domain,
        #                endpoint=endpoint,
        #                mode='r')
        # return f

        domain = config["hsds"]["domain"]
        myr = MultiYearWindX(domain, hsds=True)
        return myr

    except OSError:
        # raise InvalidUsage(("Failed to access specified HSDS resource. "
        #                     "Check credentials: "
        #                     "domain, endpoint, username, password, api_key. "
        #                     "It could be a transient HSDS connection issue. "
        #                     "Try again later."),
        #                    status_code=403)
        raise InvalidUsage(("Failed to access specified HSDS resource (using MultiYearWindX class)."),
                           status_code=403)


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


# This function finds the nearest x/y indices for a given lat/lon.
# Rather than fetching the entire coordinates database, which is 500+ MB, this
# uses the Proj4 library to find a nearby point and converts to x/y indices
def indicesForCoord(f, coords_df, lat_index, lon_index):

    # TODO: refactor; coords_df might be making f unnecessary here
    #dset_coords = f['coordinates']
    dset_coords = coords_df

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
def find_tile_optimized(f, lat, lon, gridpoint_count=1):
    """ Return dataframe with information about gridpoints in resource f that
    are neighboring (lat, lon).

    This is the NEW version; old one below should be eventually DEPRECATED!
    """
    dd,ii = f.tree.query((lat, lon), gridpoint_count)
    if gridpoint_count == 1:
        dd = [dd]
        ii = [ii]

    gridpoints_latlon = f.coordinates[ii]

    res = pd.DataFrame(columns=["lat", "lon", "index", "x_centered", "y_centered", "d"])

    for i in range(len(ii)):
        res.loc[len(res)] = [gridpoints_latlon[i][0], gridpoints_latlon[i][1], ii[i], \
                             gridpoints_latlon[i][0] - lat, gridpoints_latlon[i][1] - lon, \
                             dd[i]]

    res["index"] = pd.to_numeric(res["index"], downcast='integer')

    # Returned dataframe will be sorted by d because tree.query() returns points sorted by distance
    return res

@timeit
def find_tile(f, coords_df, lat, lon, radius=3, trim=4):
    """ Return dataframe with information about gridpoints in resource f that
    are neighboring (lat, lon). At first, there will be (radius*2) ^ 2
    entries/neighbors. The dataframe will be sorted by the distance (in meters)
    from (lat, lon); the first row -- nearest neighbor. Finally,
    the function will return N=trim first/nearest rows.

    Should be DEPRECATED!
    """

    # Appropriate for lat/lon pairs
    crs_from = ccrs.PlateCarree()

    # This projection uses USA_Contiguous_Albers_Equal_Area_Conic_USGS_version:
    # typical projection for historical USGS maps of the lower 48
    # Reference: https://spatialreference.org/ref/sr-org/usa_contiguous_/
    # albers_equal_area_conic_usgs_version-2/
    crs_to = ccrs.AlbersEqualArea(central_longitude=-96.0,
                                  central_latitude=23.0,
                                  false_easting=0.0,
                                  false_northing=0.0,
                                  standard_parallels=(29.5, 45.5), globe=None)
    ts = time.time()
    point_idx = indicesForCoord(f, coords_df, lat, lon)
    te = time.time()
    print("***** Timed indicesForCoord, hsds_helpers.py:", te - ts)

    point_xy = coordXform(crs_from, crs_to,
                          np.array([lon]), np.array([lat]))[0]

    # # TODO: Edge cases (around boundaries) need to be handled differently
    neighbors_to_check = []
    for x_idx in range(point_idx[0] - radius, point_idx[0] + radius + 1):
        for y_idx in range(point_idx[1] - radius, point_idx[1] + radius + 1):
            neighbors_to_check.append([x_idx, y_idx])

    # Get lat/lon pairs for all neighbors (faster than one-at-a-time)
    # ts = time.time()
    # neighbors_latlon = [list(p) for p in f["coordinates"][neighbors_to_check]]
    # te = time.time()
    # print("***** Timed getting neighbors_latlon, hsds_helpers.py:", te - ts)
    ts = time.time()
    # neighbors_latlon = [list(p) for p in f["coordinates"][neighbors_to_check]]
    neighbors_latlon = [coords_df[nr[0]][nr[1]] for nr in neighbors_to_check]
    te = time.time()
    print("***** Timed getting neighbors_latlon, hsds_helpers.py:", te - ts)
    print(np.array(neighbors_latlon).shape)
    print([el[1] for el in neighbors_latlon])
    print([el[0] for el in neighbors_latlon])



    # Convert all neighbors' lat/lon pairs to x/y
    # neighbors_xy = coordXform(crs_from, crs_to,
    #                           np.array(neighbors_latlon).reshape(-1, 2)[:, 1],
    #                           np.array(neighbors_latlon).reshape(-1, 2)[:, 0])
    neighbors_xy = coordXform(crs_from, crs_to,
                              np.array([el[1] for el in neighbors_latlon]),
                              np.array([el[0] for el in neighbors_latlon]))

    ts = time.time()
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
    te = time.time()
    print("***** Timed forming res dataframe, hsds_helpers.py:", te - ts)

    res["x_idx"] = pd.to_numeric(res["x_idx"], downcast='integer')
    res["y_idx"] = pd.to_numeric(res["y_idx"], downcast='integer')
    return res.sort_values("d")[:trim].reset_index(drop=True)


def coordXform(orig_crs, target_crs, x, y):
    return target_crs.transform_points(orig_crs, x, y)

def time_indices_all(f):
    """ Returns a dataframe with all processed timestamps from f
    (meant to run once, when the app is first loaded, and reduce overhead)
    """
    dt = f["datetime"]
    dt = pd.DataFrame({"datetime": dt[:]}, index=range(0, dt.shape[0]))
    dt['datetime'] = dt['datetime'].apply(dateutil.parser.parse)
    return dt

def time_indices_select(time_df, start_date, stop_date):
    """ Return lists of time indices and timestamps corresponding to the the
    requested time interval: [start_date, stop_date].
    """
    selected = time_df.loc[(time_df.datetime >= start_date) &
                           (time_df.datetime <= stop_date)]
    return selected.index.tolist(), selected.datetime.tolist()

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
def extract_ts_for_neighbors_sequential(tile_df, tidx, dset):
    """ Sequential (slow) implementation of extract_ts_for_neighbors().
    """
    res_df = pd.DataFrame(index=tidx)

    #tidx_min = np.array(tidx).min()
    #tidx_max = np.array(tidx).max()
    tidx_min = tidx[0]
    tidx_max = tidx[-1]

    for idx, row in tile_df.iterrows():

        ts = time.time()
        neighbor_data = dset[tidx_min:tidx_max+1,
                             row.x_idx, row.y_idx]
        te = time.time()
        print("***!!!** Timed getting neighbor_data, hsds_helpers.py:", te - ts)
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
