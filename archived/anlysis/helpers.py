# -*- coding: utf-8 -*-
"""Helpers module.

This file includes functions for data manipulation tasks,
either windspeed/winddirection-specific or
related to handling Pandas dataframes.
"""

import datetime
from invalid_usage import InvalidUsage
import numpy as np
import pandas as pd


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
        #return datetime.datetime.strptime(date_str, '%Y%m%d')
        return pd.to_datetime(date_str, format='%Y%m%d').tz_localize('UTC')
    except ValueError:
        raise InvalidUsage("Incorrect date format, should be: YYYYMMDD")


def windrose_from_df(df):
    # count per timestamp windspeed and direction class
    a = df[['timestamp', 'windspeed_class',
            'direction_class']].groupby(
                ['windspeed_class', 'direction_class']).count()
    a = a.reset_index()

    # count per direction class
    b = df[['timestamp',
            'direction_class']].groupby(['direction_class']).count()
    b = b.reset_index()

    # combine and calculate percentages
    c = a.reset_index().merge(b.reset_index(),
                              on='direction_class',
                              suffixes=('_a', '_b'), how='left')
    c["pct"] = 100.0*c['timestamp_a']/c['timestamp_b']
    c = c[['windspeed_class',
           'direction_class',
           'pct']].set_index(['windspeed_class', 'direction_class'])

    # calculate percentage for each wind class within each direction
    ret = {}
    for i in ['<5 m/s', '5-10 m/s', '10-20 m/s', '>20 m/s']:
        r = []
        for j in ['N', 'NE', 'E', 'SE', 'S', 'W', 'NW']:
            try:
                r.append(c.loc[i, j]["pct"])
            except KeyError:
                r.append(0.0)
        ret[i] = r

    # calculate the percentage for each direction
    b = b.set_index('direction_class')
    bs = b["timestamp"].sum()
    r = []
    for j in ['N', 'NE', 'E', 'SE', 'S', 'W', 'NW']:
        try:
            r.append(100*b.loc[j]["timestamp"]/bs)
        except KeyError:
            r.append(0.0)
    ret["Any"] = r

    return ret


def windspeed_class(x):
    if x < 5:
        return "<5 m/s"
    elif x < 10:
        return "5-10 m/s"
    elif x <= 20:
        return "10-20 m/s"
    else:
        return ">20 m/s"


def direction_class(x):
    if (x >= (360.0-45.0/2)) or (x < (45.0/2)):
        return "N"
    elif x < 22.5+45:
        return "NE"
    elif x < 90+22.5:
        return "E"
    elif x < 135+22.5:
        return "SE"
    elif x < 180+22.5:
        return "S"
    elif x < 225+22.5:
        return "SW"
    elif x < 270+22.5:
        return "W"
    else:
        return "NW"
