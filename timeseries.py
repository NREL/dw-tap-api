# -*- coding: utf-8 -*-
"""Class representing a Timeseries.

This class is a light encapsulation of a Pandas Series
object with a datetime index. Metadata on the variable
and unit is also added.

Written by: Sagi Zisman (sagi.zisman@nrel.gov) and Caleb Phillips (caleb.phillips@nrel.gov)
in collaboration with the National Renewable Energy Laboratories.

"""


class timeseries():

    """This class represents a Timeseries class"""

    # This represents a Pandas Series Object with the time as the index
    _timeseries = None

    # This reperesents the type of variable that represents the time series
    _var = None

    # This represents the unit of the variable
    _unit = None

    def __init__(self, timeseries, var=None, unit=None):
        self._timeseries = timeseries
        self._var = var
        self._unit = unit
