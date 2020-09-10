# -*- coding: utf-8 -*-
"""Class representing a Timeseries.

This class is a light encapsulation of a Pandas Series
object with a datetime index. Metadata on the variable
and unit is also added.

"""

class timeseries():

	"""This class represents a Timeseries class"""

	_timeseries = None #This represents a Pandas Series Object with the time as the index
	_var = None #This reperesents the type of variable that represents the time series
	_unit = None #This represents the unit of the variable

	def __init__(self,timeseries,var=None,unit=None):
		self._timeseries = timeseries
		self._var = var
		self._unit =  unit	
