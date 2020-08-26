from timeit import *
from invalid_usage import InvalidUsage
from helpers import *
from hsds_helpers import *

def prepare_winddirection(height, lat, lon, start_date, stop_date, hsds_f, debug=False):
    debug_info = []
    heights = available_heights(hsds_f, prefix="winddirection")
    datasets = available_datasets(hsds_f)

    if height < np.min(heights) or height > np.max(heights):
        raise InvalidUsage(("Requested height is outside "
                            "of allowed range: [%.2f, %.2f]" %
                            (np.min(heights), np.max(heights))))

    tidx, timestamps = time_indices(hsds_f, start_date, stop_date)

    if debug:
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
    finalized_df = neighbor_ts_df[["timestamp", "winddirection"]].reset_index(drop=True)

    if debug:
        debug_info += df2strings(tile_df)
        debug_info += df2strings(neighbor_ts_df)


    return (finalized_df,debug_info)


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