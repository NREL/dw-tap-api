# -*- coding: utf-8 -*-
"""Windspeed data preparation.

This file includes the code involved in preparing windspeed timeseries:
parameter validaton (specific to windspeed requests),
spatial interpolation, and overall procedure for preparing windspeed datasets
(which includes calling vertical interpolation routines).
"""

import points
import timeseries
import interpolation
from invalid_usage import InvalidUsage
from hsds_helpers import *
import numpy as np
from scipy.interpolate import griddata
from helpers import *

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

def single_height_spatial_interpolation(args):
    """ Function run in its own thread when multiple heights are processed.
    """
    height, hsds_f, tile_df, tidx, spatial_interpolation, timestamps = args

    dset = hsds_f["windspeed_%dm" % height]
    neighbor_ts_df = extract_ts_for_neighbors(tile_df, tidx, dset)
    interpolated_df = interpolate_spatially(tile_df, neighbor_ts_df,
                                            method=spatial_interpolation,
                                            neighbors_number=4)
    interpolated_df["timestamp"] = timestamps

    return interpolated_df

def prepare_windpseed(height, lat, lon,
                      start_date, stop_date, spatial_interpolation,
                      vertical_interpolation,
                      hsds_f, debug=False):
    debug_info = []

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

    if debug:
        debug_info.append("Specified height: %f" % height)
        debug_info.append("Specified lat: %f" % lat)
        debug_info.append("Specified lon: %f" % lon)
        debug_info.append("Specified start_date: %s" % str(start_date))
        debug_info.append("Specified stop_date: %s" % str(stop_date))
        debug_info.append("Available heights: %s" % str(heights))
        debug_info.append("Time indices: %s" % str(tidx))
        debug_info.append("Available datasets: %s" % str(datasets))

    tile_df = find_tile(hsds_f, lat, lon)

    if debug:
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

        if debug:
            debug_info += df2strings(imol_df)

        height_below, height_above = heights_below_and_above(heights, height)

        # Process two heights in parallel, in separate threads
        tasks = [(height, hsds_f, tile_df, tidx, spatial_interpolation, timestamps)
                 for height in [height_below, height_above]]
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [executor.submit(single_height_spatial_interpolation, t) for t in tasks]
            interpolated = [f.result() for f in futures]

        p_below = points.XYZPoint(lat, lon, height_below, 'model',
                                  timeseries=[timeseries.timeseries(
                                      interpolated[0]["spatially_interpolated"],
                                      var="ws")])
        p_above = points.XYZPoint(lat, lon, height_above, 'model',
                                  timeseries=[timeseries.timeseries(
                                      interpolated[1]["spatially_interpolated"],
                                      var="ws")])
        xyz_points = [p_below, p_above]

        interpolated_df = pd.DataFrame({"height_below": interpolated[0]["spatially_interpolated"],
                                        "height_above": interpolated[1]["spatially_interpolated"],
                                        "timestamp": interpolated[0]["timestamp"]})

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

        finalized_df = interpolated_df[["timestamp", "windspeed"]].reset_index(drop=True)

    else:
        xyz_points = []

        dset = hsds_f["windspeed_%dm" % height]
        neighbor_ts_df = extract_ts_for_neighbors(tile_df, tidx, dset)
        interpolated_df = interpolate_spatially(tile_df, neighbor_ts_df,
                                                method=spatial_interpolation,
                                                neighbors_number=4)
        interpolated_df["timestamp"] = timestamps
        if debug:
            debug_info += df2strings(interpolated_df)

        interpolated_df["timestamp"] = interpolated_df["timestamp"].astype(str)
        finalized_df = interpolated_df[["timestamp",
                                        "spatially_interpolated"]
                                       ].reset_index(drop=True).rename(
                                       columns={"spatially_interpolated":
                                                "windspeed"})

    return (finalized_df, debug_info)


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
