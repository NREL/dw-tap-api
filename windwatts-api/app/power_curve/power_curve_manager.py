from .powercurve import PowerCurve
import os
import pandas as pd
import calendar
import numpy as np
from scipy.interpolate import CubicSpline
import time

class PowerCurveManager:
    """
    Manages multiple power curves stored in a directory.
    """
    def __init__(self, power_curve_dir: str):
        """
        Initialize PowerCurveManager to load multiple power curves.

        :param power_curve_dir: Directory containing power curve files.
        """
        self.power_curves = {}
        self.load_power_curves(power_curve_dir)
    
    def load_power_curves(self, directory: str):
        """
        Load power curves from the specified directory.
        """
        for file in os.listdir(directory):
            if file.endswith(".csv") or file.endswith(".xlsx"):
                curve_name = os.path.splitext(file)[0]
                self.power_curves[curve_name] = PowerCurve(os.path.join(directory, file))

    def get_curve(self, curve_name: str) -> PowerCurve:
        """
        Retrieves a power curve by name.

        Args:
            curve_name (str): Name of the power curve.

        Returns:
            PowerCurve: Corresponding power curve object.
        """
        if curve_name not in self.power_curves:
            raise KeyError(f"Power curve '{curve_name}' not found.")
        return self.power_curves[curve_name]
    
    def find_inverse(self, x_smooth: np.ndarray, y_smooth: np.ndarray, y_hat: np.ndarray) -> np.ndarray:
        """
        Vectorized inverse mapping: finds the x values corresponding to the closest y values to each y_hat.

        :param x_smooth: Smoothed x values.
        :type x_smooth: numpy.ndarray
        :param y_smooth: Smoothed y values corresponding to x_smooth.
        :type y_smooth: numpy.ndarray
        :param y_hat: Target y values to invert.
        :type y_hat: numpy.ndarray

        :return: Array of x values corresponding to closest y matches.
        :rtype: numpy.ndarray
        """
        # Broadcasting to compute pairwise absolute differences
        diff = np.abs(y_smooth[:, None] - y_hat[None, :])
        closest_indices = np.argmin(diff, axis=0)
        return x_smooth[closest_indices]
    
    def estimation_quantiles_SWI(self, quantiles, probs, M1=1000, M2=501):
        """
        Estimate a smoother quantile function using the Spline With Inversion (SWI) method.

        This method constructs a cubic spline interpolation of the empirical CDF (defined by the 
        provided `quantiles` and corresponding `probs`), and then performs an inversion to generate 
        a smooth estimate of quantiles over a high-resolution, uniformly spaced probability range.

        Assumes that:
            - `quantiles` and `probs` are both sorted in ascending order.
            - `probs` span the interval [0, 1] and are uniformly spaced.

        :param quantiles: Observed quantile values (e.g., from sample data).
        :type quantiles: numpy.ndarray
        :param probs: Corresponding cumulative probabilities for the quantiles.
        :type probs: numpy.ndarray
        :param M1: Number of points for spline interpolation (default: 1000).
        :type M1: int
        :param M2: Number of evenly spaced probability points at which to estimate new quantiles (default: 501).
        :type M2: int

        :return: Tuple containing:
            - quantiles_new (numpy.ndarray): Estimated quantile values corresponding to probs_new.
            - probs_new (numpy.ndarray): Uniformly spaced probabilities in [0, 1] (length M2).
        :rtype: Tuple[numpy.ndarray, numpy.ndarray]
        """

        x = quantiles
        y = probs # interpolate probs w.r.t. quantile values

        # === Compute approximate derivatives at endpoints ===
        dy_start = (y[1] - y[0]) / (x[1] - x[0])  # Forward difference
        dy_end = (y[-1] - y[-2]) / (x[-1] - x[-2])  # Backward difference

        # === Create the cubic spline with clamped boundary conditions ===
        spline = CubicSpline(x, y, bc_type=((1, dy_start), (1, dy_end)))
        
        #=== High-resolution discretization (interp_point_count is large) ===
        x_smooth = np.linspace(x[0], x[-1], M1)
        y_smooth = spline(x_smooth)

        probs_new = np.linspace(0, 1, M2)
        quantiles_new = self.find_inverse(x_smooth, y_smooth, probs_new)

        return quantiles_new,probs_new
    
    def fetch_energy_production_df(self, df: pd.DataFrame, height: int, selected_power_curve: str, data_type : str, relevant_columns_only: bool = True) -> pd.DataFrame:
        """
        Computes energy production data using the selected power curve.

        Args:
            df (pd.DataFrame): Dataframe containing wind speed data.
            height (int): Height in meters for which to estimate power production.
            selected_power_curve (str): Name of the selected power curve.
            data_type (str): data source {wtk or era5}
            relevant_columns_only (bool): If True, returns only relevant columns.

        Returns:
            pd.DataFrame: Processed dataframe with estimated power production.
        """
        ws_col = f'windspeed_{height}m'
        power_curve = self.get_curve(selected_power_curve)
        if data_type == 'wtk':
            # era5 data doesn't have month and hour columns
            df['month'], df['hour'] = df['mohr'] // 100, df['mohr'] % 100
            df[f"{ws_col}_kw"] = power_curve.windspeed_to_kw(df, ws_col)
            if relevant_columns_only:
                return df[["year", "mohr", "month", "hour", ws_col, f"{ws_col}_kw"]]
        elif data_type == 'era5':
            records = []
            for year, group in df.groupby("year"):
                # sorting by probability is important since the records might be shuffled by "groupby" and we are using midpoint method.
                group = group.sort_values("probability").reset_index(drop=True)
                
                quantiles, probs = self.estimation_quantiles_SWI(group[ws_col].values, group['probability'].values)
                
                # Compute midpoints (32 values from 33 quantiles)
                midpoints = (pd.Series(quantiles).shift(-1) + pd.Series(quantiles)) / 2
                midpoints = midpoints.iloc[:-1]  # drop last NaN
            
                # Compute power for each midpoint
                kw_values = power_curve.windspeed_to_kw(pd.DataFrame({"ws": midpoints}), "ws")
                
                for mp, kw in zip(midpoints, kw_values):
                    records.append({
                        "year": year,
                        ws_col: mp, # pass midpoints
                        f"{ws_col}_kw": kw
                    })
            midpoints_df = pd.DataFrame(records)

            if relevant_columns_only:
                return midpoints_df[["year", ws_col, f"{ws_col}_kw"]]
        else:
            raise ValueError(f"Invalid data_type: {data_type}.")
        return df
    
    def prepare_yearly_production_df(self, df: pd.DataFrame, height: int, selected_power_curve: str, data_type: str) -> pd.DataFrame:
        """
        Prepares yearly average energy production and windspeed dataframe for dependent methods.

        Args:
            df (pd.DataFrame): Dataframe containing data at all heights for a location.
            height (int): Height in meters.
            selected_power_curve (str): Power curve
            data_type (str): data source {wtk or era5}

        Returns:
            pd.Dataframe
        """
        prod_df = self.fetch_energy_production_df(df, height, selected_power_curve, data_type)
        ws_column = f'windspeed_{height}m'
        kw_column = f'windspeed_{height}m_kw'

        if data_type=='wtk':
            # era5 data doesn't have mohr, month and hour columns
            prod_df = prod_df.drop(columns=["mohr", "month", "hour"] + [col for col in prod_df.columns if "winddirection" in col])
        
        res_list = []
        for year, group in prod_df.groupby("year"):
            avg_ws = group[ws_column].mean()

            if data_type == 'wtk':
                kwh = group[kw_column].sum() * 30 # Approximate estimation for 30 days per month
            elif data_type == 'era5':
                kwh = group[kw_column].sum() * 8760.0 / len(group) # 8760 hours/year

            res_list.append({
                "year": year,
                "Average wind speed (m/s)": avg_ws,
                "kWh produced": kwh
            })

        res = pd.DataFrame(res_list)
        res.sort_values("Average wind speed (m/s)", inplace=True)

        return res
    
    def fetch_yearly_avg_energy_production(self, df: pd.DataFrame, height: int, selected_power_curve: str, data_type: str) -> dict:
        """
        Computes yearly average energy production and windspeed.

        Args:
            df (pd.DataFrame): Dataframe containing data at all heights for a location.
            height (int): Height in meters.
            selected_power_curve (str): Power curve
            data_type (str): data source {wtk or era5}

        Returns:
            dict
        
        Example:
            {
                "2001": {"Average wind speed (m/s)": "5.65", "kWh produced": 250117},
                "2002": {"Average wind speed (m/s)": "5.72", "kWh produced": 264044},
                ...
            }
        """
        yearly_prod_df = self.prepare_yearly_production_df(df,height,selected_power_curve,data_type)
        
        yearly_prod_df["year"] = yearly_prod_df["year"].astype(str)
        yearly_prod_df["kWh produced"] = round(yearly_prod_df["kWh produced"].astype(float))
        yearly_prod_df["Average wind speed (m/s)"] = yearly_prod_df["Average wind speed (m/s)"].astype(float).map('{:,.2f}'.format)

        return yearly_prod_df.set_index("year").to_dict(orient="index")
    
    def fetch_avg_energy_production_summary(self, df: pd.DataFrame, height: int, selected_power_curve: str, data_type: str) -> dict:
        """
        Computes yearly average energy production and windspeed summary.

        Args:
            df (pd.DataFrame): Dataframe containing data at all heights for a location.
            height (int): Height in meters.
            selected_power_curve (str): Power curve
            data_type (str): data source {wtk or era5}

        Returns:
            dict
        
        Example:
            {
                "Lowest year": {"year": 2015, "Average wind speed (m/s)": "5.36", "kWh produced": 202791},
                "Average year": {"year": None, "Average wind speed (m/s)": "5.86", "kWh produced": 267712},
                "Highest year": {"year": 2014, "Average wind speed (m/s)": "6.32", "kWh produced": 326354}
            }
        """
        yearly_prod_df = self.prepare_yearly_production_df(df,height,selected_power_curve,data_type)
        res_avg = pd.DataFrame(yearly_prod_df.drop(columns=['year']).mean()).T
        res_avg.index = ["Average year"]

        # Final formatting
        res_summary = pd.concat([yearly_prod_df.iloc[[0]], res_avg, yearly_prod_df.iloc[[-1]]])
        res_summary["year"] = res_summary["year"].astype("Int64")
        res_summary["kWh produced"] = round(res_summary["kWh produced"].astype(float))
        res_summary["Average wind speed (m/s)"] = res_summary["Average wind speed (m/s)"].astype(float).map('{:,.2f}'.format)

        res_summary.index = [
            f"Lowest year",
            res_summary.index[1], # Average year
            f"Highest year"
        ]
        return res_summary.to_dict(orient="index")

    def fetch_monthly_avg_energy_production(self, df: pd.DataFrame, height: int, selected_power_curve: str, data_type: str) -> dict:
        """
        Computes monthly average energy production.

        Args:
            df (pd.DataFrame): Dataframe containing data at all heights for a location.
            height (int): Height in meters.
            selected_power_curve (str): Power curve
            data_type (str): data source {wtk or era5}
        Returns:
            dict: dict summarizing monthly energy production and windspeed.

        Example:
        {'Jan': {'Average wind speed, m/s': '3.80', 'kWh produced': '5,934'}, 
        'Feb': {'Average wind speed, m/s': '3.92', 'kWh produced': '6,357'}, 
        'Mar': {'Average wind speed, m/s': '4.17', 'kWh produced': '7,689'}....}
        """
        
        prod_df = self.fetch_energy_production_df(df, height, selected_power_curve, data_type)
       
        ws_column = f'windspeed_{height}m'
        kw_column = f'windspeed_{height}m_kw'

        prod_df = prod_df.drop(columns=["mohr", "year", "hour"] + [col for col in prod_df.columns if "winddirection" in col])
        
        res = prod_df.groupby("month").agg(avg_ws=(ws_column, "mean"), kwh_total=(kw_column, "sum"))
        res["kwh_total"] *= 30 / 20.0  # Approximation: 30 days per month, averaged over 20 years

        res.rename(columns={"avg_ws": "Average wind speed (m/s)", "kwh_total": "kWh produced"}, inplace=True)
        res.index = pd.Series(res.index).apply(lambda x: calendar.month_abbr[x])

        res["kWh produced"] = round(res["kWh produced"].astype(float))
        res["Average wind speed (m/s)"] = res["Average wind speed (m/s)"].astype(float).map('{:,.2f}'.format)

        return res.to_dict(orient="index")