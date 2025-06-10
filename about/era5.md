# ERA5 data

---

The ERA5 reanalysis dataset was rigorously evaluated using wind speed observations from 304 sites across the United States, covering a wide range of geographies and measurement heights. This analysis focused on the period from 2015 to 2023 to assess the dataset's current performance and suitability for distributed wind project assessment in settings where on-site measurements are typically unavailable.

- **High temporal fidelity:** ERA5 demonstrated a strong ability to capture hourly wind speed variability, achieving a Pearson correlation coefficient of 0.775 during the 2015–2023 period.
- **Low error:** The mean absolute error (MAE) for ERA5 was 1.58 m/s, indicating close agreement with observed wind speeds across diverse locations and conditions.
- **Minimal bias:** ERA5 exhibited a small positive bias of 0.09 m/s, with an absolute bias of 0.82 m/s, suggesting that modeled wind speeds slightly overestimate observed values on average but remain within acceptable margins for resource assessment.

Overall, ERA5 provides reliable and well-characterized wind speed estimates for the United States, with strong temporal resolution, low error, and minimal bias demonstrated in recent years. These attributes support its use as a credible and practical resource for distributed wind energy stakeholders seeking to evaluate project opportunities and manage uncertainty in the absence of on-site observational data.


## Spatial Coverage

The official [ERA5 data](https://www.ecmwf.int/en/forecasts/dataset/ecmwf-reanalysis-v5) offers global coverage. For WindWatts, we chose to focus on the continental United States to balance usability with data storage and processing efficiency. As a result, current wind resource estimates are provided only for locations within the highlighted region:

<a href="era5-coverage.png"><img src="era5-coverage.png" width="75%"></a>
