import numpy as np
import pandas as pd
from invalid_usage import InvalidUsage

def validated_params_v2(request):
    try:
        # Entire request is passed
        args = request.args
    except:
        # Request's args are passed
        args = request

    if 'height' in args:
        height_str = args['height']
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

    if 'lat' in args:
        try:
            lat = float(args['lat'])
        except ValueError:
            raise InvalidUsage(("Lat (latitude) provided is invalid."
                                "Needs to be a number."))
    else:
        raise InvalidUsage("Lat (latitude) is not provided.")

    if 'lon' in args:
        try:
            lon = float(args['lon'])
        except ValueError:
            raise InvalidUsage(("Lon (longitude) provided is invalid."
                                "Needs to be a number."))
    else:
        raise InvalidUsage("Lon (longitude) is not provided.")

    return height, lat, lon


def validated_params_v2_w_year(request):
    try:
        # Entire request is passed
        args = request.args
    except:
        # Request's args are passed
        args = request

    height, lat, lon = validated_params_v2(request)


    if 'year' in args:
        year_raw = args['year']
        try:
            # Works for a list of years and also for a single year
            year_list = [int(yr) for yr in year_raw.split(",")]
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

    # Last value: list of years even if one was specified
    return height, lat, lon, year_list
