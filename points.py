from abc import ABC
import pandas as pd

class Point(ABC):
	"""This class represents a base spatial point"""

	_lat = None
	_lon = None
	_gid = None #If there exists a meaningful identifier for the point

	#meta = None If metadata is needed further down the line

	_point_type = None #Allowable types are 'model' or 'desired'
	_time_series = None #A collection of time series objects

	def __init__(self,lat,lon, point_type, gid = None,timeseries = None):
		self._lat = lat
		self._lon = lon
		self._gid = gid
		self._point_type = point_type
		if timeseries is None:
			self._time_series = []
		else:
			self._time_series = timeseries

	@property
	def lat(self):
		return self._lat

	@lat.setter
	def lat(self, value):
		self._lat = value

	@property
	def lon(self):
		return self._lon
	@lon.setter
	def lon(self, value):
		self._lon = value

	@property
	def gid(self):
		return self._gid

	@property
	def is_model_point(self):
		return _self.is_model_point

	@property
	def point_type(self):
		return self._point_type

	def set_timeseries(self, timeseries):
		"""
		Appends a time series objects that represent valid time series variables associated
		with the point.
		"""
		if type(timeseries) is list:
			self._time_series += timeseries
		else:
			self._time_series.append(timeseries)

	def get_timeseries_with_attribute(self, attribute):
		for timeseries in self._time_series:
			if timeseries._var == attribute:
				return timeseries

		#TODO: Raise AttributeNotFound Error

	#concat_axis is valid if timeseries_set is 'all'
	def save_timeseries(self, filename,identifier = '', timeseries_set = 'all',concat_axis = 1):
		if timeseries_set == 'all':
			concat_timeseries = pd.concat([timeseries._timeseries for timeseries in self._time_series], axis = concat_axis)
			save_path = filename + (self._gid if self._gid else str(self._lat) + str(self._lon)) + '&' + identifier + '.csv'
			concat_timeseries.to_csv(save_path)
		return

class XYPoint(Point):
	""" This class represents a type of horizontal point"""

	_xyz_points  = None
	_surface_roughness = None
	_displacement_height = None

	def __init__(self,lat,lon,point_type,timeseries=None,surface_roughness = None, displacement_height = None):
		self._surface_roughness = surface_roughness
		self._displacement_height = displacement_height
		super().__init__(lat,lon,point_type,timeseries)

	#TODO: Add a raise exception code to signify that incompatible XYZ points were passed into the initializer
	@classmethod
	def from_xyz_points(cls, xyz_points):
		current_point = None
		for xyz_point in xyz_points:
			if current_point is None or (xyz_point._lat == current_point._lat and xyz_point._lon == current_point._lon):
				current_point = xyz_point
			#else:
			#	raise 'INCOMPATIBLE XY POINTS EXCEPTION'

		xy_point = cls(lat = current_point.lat,  lon = current_point.lon, point_type = current_point.point_type)
		xy_point._xyz_points = xyz_points
		return xy_point

	@property
	def xyz_points(self):
		return self._xyz_points

	@xyz_points.setter
	def xyz_points(self,xyz_points):
		self._xyz_points = xyz_points


	@property
	def surface_roughness(self):
		return self._surface_roughness

	@surface_roughness.setter
	def surface_roughness(self, surface_roughness):
		self._surface_roughness = surface_roughness

	@property
	def displacement_height(self):
		return self._displacement_height

	@displacement_height.setter
	def displacement_height(self, displacement_height):
		self._displacement_height = displacement_height

class XYZPoint(Point):
	""" This class represents a unique spatial point"""

	_height = None
	_a_wtk_latlon = True

	def __init__(self,lat,lon,height,point_type,  gid = None,timeseries = None):
		self._height = height
		super().__init__(lat,lon,point_type,gid,timeseries)

	@property
	def height(self):
		return self._height

	@property
	def a_wtk_latlon(self):
		return self._a_wtk_latlon
