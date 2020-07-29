"""
The purpose of this module is to define a class which will associate a set of model points with a desired point to be interpolated.
The class will keep the state of interpolation in the attribute called model points.

For example:

If a point needs both vertical and spatial interpolation, but vertical interpolation is done first, then, the set model points will first contain the set of all TS (x,y,z)and then be reduced to a set (x,y,z_desired). Then, spatial interpolation can be performed on the set to reduce it further to (x_desired, y_desired, z_desired)

"""

import pandas as pd
import timeseries
import points
import vertical_interpolation as vif
import numpy as np

class interpolation():
    _desired_point = None #Should refer a desired point object
    _model_points = None #Should refer to a set of model points which will be acted on in the process of interpolation
    _model_transformed = None
    _to_vertically_interpolate = None
    _vertical_interpolation_techniques = None

    def __init__(self,desired_point,model_points, vertically_interpolate, spatially_interpolate,vertical_interpolation_techniques):
        self._desired_point = desired_point
        self._model_points = [model_points] if type(model_points) is not list else model_points
        self._to_vertically_interpolate = vertically_interpolate
        self._to_spatially_interpolate = spatially_interpolate
        self._vertical_interpolation_techniques = vertical_interpolation_techniques
        self._model_transformed = []

    def interpolate(self,save_path = None):

        if self._to_vertically_interpolate:
            self._vertically_interpolate(save_path)

    def _vertically_interpolate(self,save_path):
        for xy_point in self._model_points:
            vertically_interpolated_timeseries = []
            heights = [poynt.height for poynt in xy_point._xyz_points]

            #Ensure sorted assumption is satisfied
            assert np.array_equal(heights, np.sort(heights))

            if 'polynomial' in self._vertical_interpolation_techniques:
                for degree in range(1, len(xy_point._xyz_points)):
                    polynomial_interpolated_series = vif.polynomial(self._desired_point, xy_point._xyz_points,degree = degree)
                    if polynomial_interpolated_series is not None:
                        polynomial_interpolated_series.name = 'vert_poly_deg{0}'.format(str(degree))
                        #polynomial_interpolated_series = pd.Series([x[0] for x in polynomial_interpolated_series.values])
                        print("poly branch")
                        #polynomial_interpolated_series = pd.to_numeric(polynomial_interpolated_series)
                        print(polynomial_interpolated_series)
                        #polynomial_interpolated_series = pd.Series(polynomial_interpolated_series.values)
                        vertically_interpolated_timeseries.append(timeseries.timeseries(polynomial_interpolated_series))

            if 'nn' in self._vertical_interpolation_techniques:
                nn_interpolated_series = vif.nearest_neighbor(self._desired_point, xy_point._xyz_points)
                if nn_interpolated_series is not None:
                    nn_interpolated_series.name = 'vert_nn'
                    vertically_interpolated_timeseries.append(timeseries.timeseries(nn_interpolated_series))

            if 'stability_adjusted_log_law' in self._vertical_interpolation_techniques:
                stability_corrected_log_law_series = vif.stability_corrected_log_law(self._desired_point, xy_point._xyz_points, xy_point.get_timeseries_with_attribute('stability'), xy_point.surface_roughness, xy_point.displacement_height)
                if stability_corrected_log_law_series is not None:
                    stability_corrected_log_law_series.name = 'stability_corrected_log_law_series'
                    vertically_interpolated_timeseries.append(timeseries.timeseries(stability_corrected_log_law_series))

            if 'neutral_log_law' in self._vertical_interpolation_techniques:
                neutral_log_law_series = vif.neutral_log_law(self._desired_point, xy_point._xyz_points, xy_point.surface_roughness, xy_point.displacement_height)
                if neutral_log_law_series is not None:
                    neutral_log_law_series.name = 'neutral_log_law_series'
                    vertically_interpolated_timeseries.append(timeseries.timeseries(neutral_log_law_series))

            if 'stability_adjusted_power_law' in self._vertical_interpolation_techniques:
                stability_corrected_power_law_series = vif.stability_corrected_power_law(self._desired_point, xy_point._xyz_points)
                if stability_corrected_power_law_series is not None:
                    stability_corrected_power_law_series.name = 'stability_corrected_power_law_series'
                    vertically_interpolated_timeseries.append(timeseries.timeseries(stability_corrected_power_law_series))

            if 'neutral_power_law' in self._vertical_interpolation_techniques:
                neutral_power_law_series = vif.neutral_power_law(self._desired_point, xy_point._xyz_points)
                if neutral_power_law_series is not None:
                    neutral_power_law_series.name = 'neutral_power_law_series'
                    vertically_interpolated_timeseries.append(timeseries.timeseries(neutral_power_law_series))

            ground_truth = self._desired_point.get_timeseries_with_attribute('ws')
            if ground_truth is not None:
                ground_truth.name = "ground_truth"
                vertically_interpolated_timeseries.append(ground_truth)

            #Create a new XY Point that will contain the time series associated with the vertical interpolation
            model_transform_point = points.XYPoint(xy_point.lat,xy_point.lon,'model')
            model_transform_point.xyz_points = points.XYZPoint(xy_point.lat, xy_point.lon,self._desired_point.height,'model', gid = self._desired_point._gid)
            model_transform_point.xyz_points.set_timeseries(vertically_interpolated_timeseries)

            #model_transform_point.xyz_points.save_timeseries(save_path,identifier = 'Z=' + str(model_transform_point.xyz_points.height) + '&vertical_interpolation', timeseries_set = 'all',concat_axis = 1)

            self._model_transformed.append(model_transform_point)

        #Signal that the vertical interpolation has been completed
        self._to_vertically_interpolate = False
        return

    @property
    def interpolation_finished(self):
        return len(self._model_transformed) == 1
