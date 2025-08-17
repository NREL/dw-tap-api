# Summary of Datasets and Analysis in WindWatts

## ERA5 

Source: https://www.ecmwf.int/en/forecasts/dataset/ecmwf-reanalysis-v5

ERA5 is produced by the Copernicus Climate Change Service (C3S) at the European Centre for Medium-Range Weather Forecasts (ECMWF).

ERA5 comes with wind data for 10 meters and 100 meters above ground, with both wind speeds and wind directions. 

WindWatts uses 10-meter and 100-meter ERA5 data at hourly resolution to estimate power law exponents for the vertical interpolation and then estimates wind speeds at: 40 meters, 60 meters, and 80 meters, complementing the original 10 and 100.

Hourly timeseries for each year (approx. 8760 data points) for each of these heights get summarized statistically using: 0th percentile (minimum for the year), 
10th percentile, 20th percentile, ..., 90th percentile, and 100th percentile (maximum for the year) -- 11 values in total. 
This data aggregation reduces the time needed for data fetching in WindWatts but, at the same time, preserves statistical properties of wind speed distributions (much better compared to storing only average values).

These percentiles are calculated and saved for 5 heights and 42,375 gridpoints covering the continental United States.

When a WindWatts user clicks on the map to study a particular location, WindWatts fetches those percentiles for the grid point that is closest to the selected 
location and uses them to estimate the global wind speed average (i.e. average across all yearly distributions) and average yearly energy production amount for a selected power curve. 
For the latter, each percentile is run through the power curve, resulting in the estimates that are much more accurate than the energy estimates obtained using glabal wind speed averages.   

Currently, WindWatts uses ERA5 data for 2013--2023.
