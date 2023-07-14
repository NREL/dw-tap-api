import numpy as np
import pandas as pd
from invalid_usage import InvalidUsage

def validated_params_v2(request):

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

    return height, lat, lon
