from .powercurve import PowerCurve
import os
import pandas as pd
import calendar

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
        df['month'], df['hour'] = df['mohr'] // 100, df['mohr'] % 100
        power_curve = self.get_curve(selected_power_curve)
        df[f"{ws_col}_kw"] = power_curve.windspeed_to_kw(df, ws_col)

        if relevant_columns_only:
            wd_col = ws_col.replace("speed", "direction")
            return df[["year", "mohr", "month", "hour", ws_col, f"{ws_col}_kw", wd_col]]
        
        return df
    
    def fetch_yearly_avg_energy_production(self, df: pd.DataFrame, height: int, selected_power_curve: str) -> pd.DataFrame:
        """
        Computes yearly average energy production.

        Args:
            df (pd.DataFrame): Dataframe containing data at all heights for a location.
            height (int): Height in meters.

        Returns:
            pd.DataFrame: Dataframe summarizing yearly energy production.
        """
        prod_df = self.fetch_energy_production_df(df, height, selected_power_curve)
        prod_df = prod_df.drop(columns=["mohr", "month", "hour"] + [col for col in prod_df.columns if "winddirection" in col])
        ws_column = f'windspeed_{height}m'
        kw_column = f'windspeed_{height}m_kw'

        res = prod_df.groupby("year").agg(avg_ws=(ws_column, "mean"), kwh_total=(kw_column, "sum"))
        res["kwh_total"] *= 30  # Approximate estimation for 30 days per month

        res.rename(columns={"avg_ws": "Average wind speed (m/s)", "kwh_total": "kWh produced"}, inplace=True)
        res.sort_values("Average wind speed (m/s)", inplace=True)

        res_avg = pd.DataFrame(res.mean()).T
        res_avg.index = ["Average year"]

        res_summary = pd.concat([res.iloc[[0]], res_avg, res.iloc[[-1]]])
        res_summary["kWh produced"] = res_summary["kWh produced"].astype(float).map('{:,.0f}'.format)
        res_summary["Average wind speed (m/s)"] = res_summary["Average wind speed (m/s)"].astype(float).map('{:,.2f}'.format)

        res_summary.index = [
            f"Lowest year ({res_summary.index[0]})",
            res_summary.index[1],
            f"Highest year ({res_summary.index[2]})"
        ]

        return res_summary

    def fetch_monthly_avg_energy_production(self, df: pd.DataFrame, height: int, selected_power_curve: str) -> pd.DataFrame:
        """
        Computes monthly average energy production.

        Args:
            df (pd.DataFrame): Dataframe containing wind speed and power data.
            height (int): Height in meters.

        Returns:
            pd.DataFrame: Dataframe summarizing monthly energy production.
        """
        prod_df = self.fetch_energy_production_df(df, height, selected_power_curve)
        prod_df = prod_df.drop(columns=["mohr", "year", "hour"] + [col for col in prod_df.columns if "winddirection" in col])
        ws_column = f'windspeed_{height}m'
        kw_column = f'windspeed_{height}m_kw'

        res = prod_df.groupby("month").agg(avg_ws=(ws_column, "mean"), kwh_total=(kw_column, "sum"))
        res["kwh_total"] *= 30 / 20.0  # Approximation: 30 days per month, averaged over 20 years

        res.rename(columns={"avg_ws": "Average wind speed (m/s)", "kwh_total": "kWh produced"}, inplace=True)
        res.index = pd.Series(res.index).apply(lambda x: calendar.month_abbr[x])

        res["kWh produced"] = res["kWh produced"].astype(float).map('{:,.0f}'.format)
        res["Average wind speed (m/s)"] = res["Average wind speed (m/s)"].astype(float).map('{:,.2f}'.format)

        return res