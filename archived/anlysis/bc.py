import pandas as pd
import numpy as np
import shapely
import shapely.geometry
import geopandas as gpd
import os
import datetime
from dw_tap.data_fetching import getData
import h5pyd
import joblib
from collections import OrderedDict
import json
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('agg')

def round3(x):
    return "%.3f" % x

def bc_for_point(lat, lon, height, model_data, bc_dir, plot_dest):
    info = OrderedDict()

    site = shapely.geometry.Point(lon, lat)

    info["<strong>BC: input and closest site with measurements</strong>"] = ""
    info["Point chosen for BC (lon, lat)"] = str(site)
    info["Height chosen for BC, m"] = round3(height)

    src_crs="EPSG:4326"
    dest_crs="EPSG:3857"

    site_projected = gpd.GeoDataFrame(geometry=[site], crs=src_crs).to_crs(dest_crs).geometry[0]

    info["Projection"] = "%s -> %s" % (src_crs, dest_crs)
    info["Point after projection (coords in meters)"] = "("+round3(site_projected.x) + ", " + round3(site_projected.y) + ")"

    #bc_dir = os.path.join(dw_tap_data.path, "bc_development", "bc_v4")

    bc_index = gpd.read_file(os.path.join(bc_dir, "index.json"))
    bc_index.set_crs(src_crs)
    bc_index_wtk = bc_index[bc_index["model"] == "wtk"].reset_index(drop=True)
    bc_index_wtk_projected = bc_index_wtk.to_crs(dest_crs)

    distances_km = bc_index_wtk_projected.distance(site_projected)/1000.0
    closest_idx, closest_bc_site_distance_km = distances_km.argmin(), distances_km.min()

    closest_cid = bc_index_wtk.at[closest_idx, "cid"]

    info["Closest BC site, cid"] = str(closest_cid)
    info["Closest BC site after projection (coords in meters)"] = "("+round3(bc_index_wtk_projected.at[closest_idx, "geometry"].x) + ", " + round3(bc_index_wtk_projected.at[closest_idx, "geometry"].y) + ")"#str(bc_index_wtk_projected.at[closest_idx, "geometry"])

    info["Distance to closest BC site, km"] = "<strong>" + round3(closest_bc_site_distance_km) + "</strong>"

    model_file = bc_index_wtk.at[closest_idx, "model_file"]
    #info["File with closest BC site's fit model"] = str(model_file)

    bc_height = bc_index_wtk.at[closest_idx, "height"]
    info["Height at which the closest BC site's model is fit, m"] = round3(bc_height)
    info["Difference between selected height and the BC height, m"] = "<strong>" + round3(np.abs(bc_height-height)) + "</strong>"

    info["<br> #1"] = "" # Adding empty line
    info["<strong>Site with measurements and its BC model</strong>"] = ""
    info["Wind speed RMSE on test subset (m/s), before BC"] = round3(bc_index_wtk_projected.at[closest_idx, "rmse_test_nobc"])
    info["Wind speed RMSE on test subset (m/s), after BC"] = round3(bc_index_wtk_projected.at[closest_idx, "rmse_test_bc"])
    info["Wind speed RMSE reduction, %"] = round3(bc_index_wtk_projected.at[closest_idx, "rmse_test_percent_reduction"])
    info["Number of time-aligned instances for fitting the model"] = round3(bc_index_wtk_projected.at[closest_idx, "train_set_length"])
    info["Perf factor for wind speeds in the test subset before BC"] = round3(bc_index_wtk_projected.at[closest_idx, "perf_factor_no_bc"])
    info["Perf factor for wind speeds in the test subset after BC"] = round3(bc_index_wtk_projected.at[closest_idx, "perf_factor_bc"])

    fit = joblib.load(os.path.join(bc_dir, model_file))
    info["Closest BC site's model"] = str(fit)
    info["Coefficients of the closest BC site's model"] = str(fit.coef_)

    # f = h5pyd.File("/nrel/wtk-us.h5", 'r', bucket="nrel-pds-hsds")
    # model_data = getData(f, site.y, site.x, height, "IDW",
    #                                        power_estimate=False,
    #                                        inverse_monin_obukhov_length=False,
    #                                        start_time_idx=0, end_time_idx=8760, time_stride=1)

    model_data["datetime"] = pd.to_datetime(model_data["datetime"])
    model_data['hour'] = model_data['datetime'].dt.hour
    model_data['month'] = model_data['datetime'].dt.month
    model_data['year'] = model_data['datetime'].dt.year

    features_list = ["ws", "wd", "hour", "month"]
    model_data["ws_bc"] = fit.predict(model_data[features_list])

    # Simple timeseries plot with no aggregation
    #model_data[["ws", "ws_bc"]].plot();
    #plt.savefig(plot_dest, dpi=300)

    print("before bc_plot_before_and_after")
    bc_plot_before_and_after(model_data, ws_before="ws", ws_after="ws_bc", datetime_column="datetime", \
                                 title="Location: (%f, %f), %.0fm hub height" % (lat, lon, height), \
                                 save_to_file=plot_dest, \
                                 show=False)

    output = """
      <div classes="centered">
      <div>
        <table>
            <tr>
              <td><img id=\"monthly_plot\" src=\"%s\"/></td>
            </tr>
        </table>
      </div>
      </div>
      """ % (plot_dest)

    info["<br> #2"] = "" # Adding empty line
    info["<strong>Before and after BC</strong>"] = ""
    info["Number of timesteps in the model data fetched for Point"] = str(len(model_data))
    info["Min wind speed before BC, m/s"] = round3(model_data["ws"].min())
    info["Avg wind speed before BC, m/s"] = round3(model_data["ws"].mean())
    info["Max wind speed before BC, m/s"] = round3(model_data["ws"].max())

    info["Min wind speed after BC, m/s"] = round3(model_data["ws_bc"].min())
    info["Avg wind speed after BC, m/s"] = round3(model_data["ws_bc"].mean())
    info["Max wind speed after BC, m/s"] = round3(model_data["ws_bc"].max())

    info = "<br>".join(["%s:&nbsp;%s" % (k.lstrip(","), info[k]) if (not (k.startswith("<br>"))) else "<br>" for k in info.keys()])

    #print(json.dumps(bc_info, indent=4))
    #return json.dumps({"output": str(p), "info": info})

    return output, info

def bc_plot_before_and_after(atmospheric_df, ws_before="ws", ws_after="ws_bc", datetime_column="datetime",
                             title="Windspeed monthly averages, with and without BC",
                             save_to_file=False,
                             show=True):
    print("bc_plot_before_and_after")
    df = atmospheric_df[[datetime_column, ws_before, ws_after]].copy()

    year_month = pd.Series(pd.PeriodIndex(df[datetime_column], freq="M"))
    print("1")
    df["month"] = year_month.apply(lambda x: x.month)
    df["year"] = year_month.apply(lambda x: x.year)
    df["day"] = 15 # For plotting only, middle of the month
    df["moyr"] = [str(el[1]) + "-" + str(el[0]).zfill(2) for el in zip(df["month"], df["year"])]
    df['middle_of_the_month'] = pd.to_datetime(df[['year','month', "day"]])

    fig, ax = plt.subplots(figsize=(10, 3))

    df_averaged = df.groupby("middle_of_the_month").agg(ws_before_avg=(ws_before, "mean"), \
                                                        ws_after_avg=(ws_after, "mean"), \
                                                        count=(ws_after, "count"))
    df_averaged.sort_index(inplace=True)

    ws_before_overall_avg = df_averaged.ws_before_avg.mean()
    ws_after_overall_avg = df_averaged.ws_after_avg.mean()
    ax.plot(df_averaged.index, df_averaged.ws_before_avg, \
            marker="o", label="Model data; avg=%.3f" % (ws_before_overall_avg), linestyle="--", alpha=1.0)
    ax.plot(df_averaged.index, df_averaged.ws_after_avg, \
            marker="d", label="Bias-corrected model data; avg=%.3f" % (ws_after_overall_avg), linestyle="-.", alpha=1.0)

    ax.set_ylabel("Monthly avg wind speed, m/s")
    ax.set_title(title)
    plt.legend()

    if save_to_file == True:
        plt.savefig('%s.png' % title, dpi=300)
    elif type(save_to_file) == str:
        plt.savefig(save_to_file, dpi=300)

    if show:
        plt.show()

    #return df_averaged
