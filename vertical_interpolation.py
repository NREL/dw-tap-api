# -*- coding: utf-8 -*-
""" Code implementing vertical interpolation functions.

A collection of vertical interpolation functions used for
estimating the wind speed at arbitrary heights. Functions
include statistical and domain-specific approaches. The
neutral log law method requires surface roughness data
which is associated with (land cover) NLCD tiles.

Functions act on known input heights and wind speeds (called
model points but could be observed data). Both the model and
desired points utilize the Points Class to organize
interpolations.

Implementation of domain-specific approaches is based on
theory developed in the following sources:

* M. C. Holtslag, "Estimating atmospheric stability from observations and correcting wind sheer models accordingly," Journal of Physics: Conference Series, vol. 444, no. 012052, 2014. 
* W. Brutsaert, Evaporation into the Atmosphere, Kluwer Academic Publishers, 1982.
* E. A. M. D. B. G. S. A. Hsu, "Determining the Power-Law Wind-Profile Exponent under Near-Neutral Stability Conditions at Sea," Journal of Applied Meteorology, vol. 33, pp. 757-765, 1994


import pandas as pd
import numpy as np
from scipy.interpolate import BarycentricInterpolator

"""
Vertical Interpolation Functions takes a set of 
model points and a desired point and 
calculates/returns a timeseries object that 
represents the vertically interpolated time series.
"""

#Function 1: Nearest Neighbor Approach
def nearest_neighbor(desired_point, model_points):
    min_idx = _argsort_height_diffs(desired_point, model_points)[0]
    return model_points[min_idx]._time_series[0]._timeseries.copy()

def polynomial(desired_point, model_points, degree):
    idx_points_for_poly_interp =_argsort_height_diffs(desired_point, model_points)[:(degree + 1)]
    points_for_poly_interp = [model_points[idx] for idx in idx_points_for_poly_interp]
    heights = [point.height for point in points_for_poly_interp]
    ts_df = pd.concat([point._time_series[0]._timeseries for point in points_for_poly_interp], axis = 1)
    results = ts_df.T.apply(lambda x: BarycentricInterpolator(heights, x.values)(desired_point.height).reshape(1)[0])
    return results

def stability_corrected_log_law(desired_point, model_points,stability,surface_roughness,displacement_height):
    if stability is None or surface_roughness is None:
        return None

    model_point_heights = [model_point.height for model_point in model_points]
    lower_height, upper_height, nearest_height = _closest_higher_lower_height_ws(desired_point.height, model_point_heights)

    nearest_height_model_point = model_points[model_point_heights.index(nearest_height)]
    scaling_series = (np.log(desired_point.height / surface_roughness).values - stability._timeseries.apply(_psi, z=desired_point.height)) / (np.log(nearest_height / surface_roughness).values - stability._timeseries.apply(_psi, z=nearest_height))

    return nearest_height_model_point.get_timeseries_with_attribute('ws')._timeseries * scaling_series

def neutral_log_law(desired_point, model_points, surface_roughness, displacement_height):
    if surface_roughness is None or displacement_height is None:
        return None

    model_point_heights = [model_point.height for model_point in model_points]
    lower_height, upper_height, nearest_height = _closest_higher_lower_height_ws(desired_point.height, model_point_heights)

    nearest_height_model_point = model_points[model_point_heights.index(nearest_height)]

    scaling_coefficient = (np.log(desired_point.height / surface_roughness) / np.log(nearest_height / surface_roughness))
    return nearest_height_model_point.get_timeseries_with_attribute('ws')._timeseries * scaling_coefficient.values

# Caleb: does not appear to actually use stability?
def stability_corrected_power_law(desired_point, model_points):

    model_point_heights = [model_point.height for model_point in model_points]
    lower_height, upper_height, nearest_height = _closest_higher_lower_height_ws(desired_point.height, model_point_heights)

    nearest_height_model_point  = model_points[model_point_heights.index(nearest_height)]
    lower_height_model_point = model_points[model_point_heights.index(lower_height)]
    upper_height_model_point = model_points[model_point_heights.index(upper_height)]

    alpha = np.log(upper_height_model_point.get_timeseries_with_attribute('ws')._timeseries / lower_height_model_point.get_timeseries_with_attribute('ws')._timeseries) / np.log(upper_height / lower_height)
    return nearest_height_model_point.get_timeseries_with_attribute('ws')._timeseries * alpha.apply(_power_of_alpha, height_ratio = desired_point.height / nearest_height)

def neutral_power_law(desired_point, model_points):

    onshore_alpha = 1/7
    offshore_alpha = .11
    model_point_heights = [model_point.height for model_point in model_points]
    lower_height, upper_height, nearest_height = _closest_higher_lower_height_ws(desired_point.height, model_point_heights)

    nearest_height_model_point  = model_points[model_point_heights.index(nearest_height)]
    return nearest_height_model_point.get_timeseries_with_attribute('ws')._timeseries * (desired_point.height / nearest_height) ** (onshore_alpha)
"""
Helper Function
"""
def _argsort_height_diffs(desired_point, model_points):
    model_heights = np.array([model_point.height for model_point in model_points])
    heigh_diffs = model_heights - desired_point.height
    model_desired_diffs = abs(heigh_diffs)
    return np.argsort(model_desired_diffs)

def _power_of_alpha(x,height_ratio):
        return height_ratio ** x

def _psi(L_inv,z):
    if z*L_inv > 1: #Strongly Stable
        return -4.7*np.log(z*L_inv) - 4.7
    elif z*L_inv > .1:
        return -4.7*z*L_inv
    elif z*L_inv < -.1:
        return 2*np.log((1 + (1 - 15 * z * L_inv) ** (1/4)) /2) + np.log((1 + (1 - 15 * z * L_inv) ** (1/2)) /2) - 2 * np.arctan((1 - 15 * z * L_inv) ** (1/4)) + (np.pi / 2)
    else:
        return 0

def _closest_higher_lower_height_ws(channel_height,model_heights,non_inclusive_height_bounds = False):
    #Edge Cases
    if len(model_heights) == 1:
        lower_height = model_heights[0]
        upper_height = model_heights[0]
        nearest_height = lower_height

    elif channel_height < min(model_heights):
        lower_height = model_heights[0]
        upper_height = model_heights[1]
        nearest_height = lower_height

    elif channel_height > max(model_heights):
        lower_height = model_heights[-2]
        upper_height = model_heights[-1]
        nearest_height = upper_height
    else:
        lower_idx = np.searchsorted(model_heights,channel_height) - 1
        lower_height = model_heights[lower_idx]
        upper_height = model_heights[lower_idx + 1]
        nearest_height = lower_height if abs(lower_height - channel_height) <= abs(upper_height - channel_height) else upper_height
        if non_inclusive_height_bounds:
           if nearest_height > 10 and nearest_height < 200:
              nearest_height_idx = np.argwhere(model_heights == nearest_height)[0,0]
              lower_height = model_heights[nearest_height_idx - 1]
              upper_height = model_heights[nearest_height_idx + 1]
    return lower_height, upper_height, nearest_height
