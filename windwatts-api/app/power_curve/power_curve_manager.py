from .powercurve import PowerCurve
import os
import pandas as pd
import calendar
import numpy as np

class PowerCurveManager:
    """
    Manages multiple power curves stored in a directory.
    """
    def __init__(self, power_curve_dir: str, data_type: str):
        """
        Initialize PowerCurveManager to load multiple power curves.

        :param power_curve_dir: Directory containing power curve files.
        """
        self.power_curves = {}
        self.load_power_curves(power_curve_dir)
        self.data_type = data_type
    
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
    
    def fetch_energy_production_df(self, df: pd.DataFrame, height: int, selected_power_curve: str, relevant_columns_only: bool = True) -> pd.DataFrame:
        """
        Computes energy production data using the selected power curve.

        Args:
            df (pd.DataFrame): Dataframe containing wind speed data.
            height (int): Height in meters for which to estimate power production.
            selected_power_curve (str): Name of the selected power curve.
            relevant_columns_only (bool): If True, returns only relevant columns.

        Returns:
            pd.DataFrame: Processed dataframe with estimated power production.
        """
        ws_col = f'windspeed_{height}m'
        power_curve = self.get_curve(selected_power_curve)
        if self.data_type == 'wtk':
            # era5 data doesn't have month and hour columns
            df['month'], df['hour'] = df['mohr'] // 100, df['mohr'] % 100
            df[f"{ws_col}_kw"] = power_curve.windspeed_to_kw(df, ws_col)
            if relevant_columns_only:
                return df[["year", "mohr", "month", "hour", ws_col, f"{ws_col}_kw"]]
        elif self.data_type == 'era5':
            records = []

            for year, group in df.groupby("year"):
                # sorting by probability is important since the records might be shuffled by "groupby" and we are using midpoint method.
                group = group.sort_values("probability").reset_index(drop=True)
                wind_values = group[ws_col]

                # Compute midpoints (32 values from 33 quantiles)
                midpoints = (wind_values.shift(-1) + wind_values) / 2
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
            raise ValueError(f"Invalid data_type: {self.data_type}.")
        return df
    
    def fetch_yearly_avg_energy_production(self, df: pd.DataFrame, height: int, selected_power_curve: str) -> dict:
        """
        Computes yearly average energy production.

        Args:
            df (pd.DataFrame): Dataframe containing data at all heights for a location.
            height (int): Height in meters.

        Returns:
            pd.DataFrame: Dataframe summarizing yearly energy production.
        
        Example:
            {'Lowest year': 
            {'year': 2015, 'Average wind speed, m/s': '3.48', 'kWh produced': '54,395'}, 
            'Average year': 
            {'year': None, 'Average wind speed, m/s': '3.79', 'kWh produced': '72,214'}, 
            'Highest year': 
            {'year': 2014, 'Average wind speed, m/s': '4.00', 'kWh produced': '86,536'}}

            Note: for "Average year" the "year" is "None" as it's the global average production.
        """
        prod_df = self.fetch_energy_production_df(df, height, selected_power_curve)
        ws_column = f'windspeed_{height}m'
        kw_column = f'windspeed_{height}m_kw'

        if self.data_type=='wtk':
            # era5 data doesn't have mohr, month and hour columns
            prod_df = prod_df.drop(columns=["mohr", "month", "hour"] + [col for col in prod_df.columns if "winddirection" in col])
        
        res_list = []
        for year, group in prod_df.groupby("year"):
            avg_ws = group[ws_column].mean()

            if self.data_type == 'wtk':
                kwh = group[kw_column].sum() * 30 # Approximate estimation for 30 days per month
            elif self.data_type == 'era5':
                kwh = group[kw_column].sum() * 8760.0 / len(group) # 8760 hours/year

            res_list.append({
                "year": year,
                "Average wind speed (m/s)": avg_ws,
                "kWh produced": kwh
            })

        res = pd.DataFrame(res_list)
        res.sort_values("Average wind speed (m/s)", inplace=True)
        res_avg = pd.DataFrame(res.drop(columns=['year']).mean()).T
        res_avg.index = ["Average year"]

        # Final formatting
        res_summary = pd.concat([res.iloc[[0]], res_avg, res.iloc[[-1]]])
        res_summary["year"] = res_summary["year"].astype("Int64")
        res_summary["kWh produced"] = round(res_summary["kWh produced"].astype(float))
        res_summary["Average wind speed (m/s)"] = res_summary["Average wind speed (m/s)"].astype(float).map('{:,.2f}'.format)

        res_summary.index = [
            f"Lowest year",
            res_summary.index[1], # Average year
            f"Highest year"
        ]

        return res_summary.to_dict(orient="index")

    def fetch_monthly_avg_energy_production(self, df: pd.DataFrame, height: int, selected_power_curve: str) -> dict:
        """
        Computes monthly average energy production.

        Args:
            df (pd.DataFrame): Dataframe containing data at all heights for a location.
            height (int): Height in meters.po

        Returns:
            pd.DataFrame: Dataframe summarizing monthly energy production.

        Example:
        {'Jan': {'Average wind speed, m/s': '3.80', 'kWh produced': '5,934'}, 
        'Feb': {'Average wind speed, m/s': '3.92', 'kWh produced': '6,357'}, 
        'Mar': {'Average wind speed, m/s': '4.17', 'kWh produced': '7,689'}....}
        """
        prod_df = self.fetch_energy_production_df(df, height, selected_power_curve)
        prod_df = prod_df.drop(columns=["mohr", "year", "hour"] + [col for col in prod_df.columns if "winddirection" in col])
        ws_column = f'windspeed_{height}m'
        kw_column = f'windspeed_{height}m_kw'

        res = prod_df.groupby("month").agg(avg_ws=(ws_column, "mean"), kwh_total=(kw_column, "sum"))
        res["kwh_total"] *= 30 / 20.0  # Approximation: 30 days per month, averaged over 20 years

        res.rename(columns={"avg_ws": "Average wind speed (m/s)", "kwh_total": "kWh produced"}, inplace=True)
        res.index = pd.Series(res.index).apply(lambda x: calendar.month_abbr[x])

        res["kWh produced"] = round(res["kWh produced"].astype(float))
        res["Average wind speed (m/s)"] = res["Average wind speed (m/s)"].astype(float).map('{:,.2f}'.format)

        return res.to_dict(orient="index")