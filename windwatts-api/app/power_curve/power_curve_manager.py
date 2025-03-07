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
                print(curve_name)
                self.power_curves[curve_name] = PowerCurve(os.path.join(directory, file))

    def get_curve(self, curve_name: str) -> PowerCurve:
        """
        Retrieve a power curve by name.
        """
        if curve_name not in self.power_curves:
            raise KeyError(f"Power curve '{curve_name}' not found.")
        return self.power_curves[curve_name]
    
    def fetch_energy_production_df(self, df, height, selected_power_curve, relevant_columns_only = True):

        ws_col_for_estimating_power = f'windspeed_{height}m'
        
        df['month'], df['hour'] = df['mohr']//100, df['mohr']%100
        power_curve = self.power_curves[selected_power_curve]
        df[ws_col_for_estimating_power + "_kw"] = power_curve.windspeed_to_kw(df, ws_col_for_estimating_power)
        if relevant_columns_only:
            wd_col = ws_col_for_estimating_power.replace("speed", "direction")
            relevant_columns = ["year", "mohr", "month", "hour", ws_col_for_estimating_power, ws_col_for_estimating_power + "_kw", wd_col]
            return df[relevant_columns]
        else:
            return df
    
    def fetch_yearly_avg_energy_production(self, df, height):

        df = df.drop(columns=["mohr", "month", "hour"] + [x for x in df.columns if "winddirection" in x])
        ws_column = f'windspeed_{height}m'
        kw_column = f'windspeed_{height}m_kw'
        res = df.groupby("year").agg(avg_ws=(ws_column, "mean"), kwh_total=(kw_column, "sum")) # kwh_total will sum for all months and all hours

        res["kwh_total"] = res["kwh_total"] * 30 # Coarse estimation: 30 days in every month; no need to /20.0 for individual years
        res.rename(columns={"avg_ws": "Average wind speed, m/s", "kwh_total": "kWh produced"}, inplace=True)

        res = res.sort_values("Average wind speed, m/s")

        res_avg = pd.DataFrame(res.mean()).T
        res_avg.index=["Average year"]

        res_years = pd.concat([res.iloc[[0]], res_avg, res.iloc[[-1]]])
        res_years["kWh produced"] = res_years["kWh produced"].astype(float).map('{:,.0f}'.format)
        res_years["Average wind speed, m/s"] = res_years["Average wind speed, m/s"].astype(float).map('{:,.2f}'.format)

        res_years.index = ["Lowest year (%s)" % str(res_years.index[0]), \
                            res_years.index[1], \
                            "Highest year (%s)" % str(res_years.index[2])]

        return res_years
    
    def fetch_monthly_avg_energy_production(self, df, height):

        df = df.drop(columns=["mohr", "year", "hour"] + [x for x in df.columns if "winddirection" in x])
        ws_column = f'windspeed_{height}m'
        kw_column = f'windspeed_{height}m_kw'
        res = df.groupby("month").agg(avg_ws=(ws_column, "mean"), kwh_total=(kw_column, "sum")) # kwh_total will sum for all months and all hours

        res["kwh_total"] = res["kwh_total"] * 30 / 20.0 # Coarse estimation: 30 days in every month & 20 years
        res.rename(columns={"avg_ws": "Average wind speed, m/s", "kwh_total": "kWh produced"}, inplace=True)
        res.index = pd.Series(res.index).apply(lambda x: calendar.month_abbr[x])

        res["kWh produced"] = res["kWh produced"].astype(float).map('{:,.0f}'.format)
        res["Average wind speed, m/s"] = res["Average wind speed, m/s"].astype(float).map('{:,.2f}'.format)

        return res