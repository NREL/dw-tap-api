import datetime
from invalid_usage import InvalidUsage
import numpy as np

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


def validated_dt(date_str):
    """ Create and return a datetime object based on the given string.
    If the string is inappropriate, raise an error with helpful message.
    """
    try:
        return datetime.datetime.strptime(date_str, '%Y%m%d')
    except ValueError:
        raise InvalidUsage("Incorrect date format, should be: YYYYMMDD")