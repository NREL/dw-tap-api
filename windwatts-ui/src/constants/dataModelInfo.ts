import { DataModelInfo } from "../types";

export const DATA_MODEL_INFO: Record<string, DataModelInfo> = {
  era5: {
    label: "ERA5",
    source_href:
      "https://www.ecmwf.int/en/forecasts/dataset/ecmwf-reanalysis-v5",
    help_href: "https://github.com/NREL/dw-tap-api/blob/master/about/era5.md",
  },
  wtk: {
    label: "NREL's 20-year WTK-LED dataset",
    source_href:
      "https://www.energy.gov/eere/wind/articles/new-wind-resource-database-includes-updated-wind-toolkit",
    help_href: "",
  },
};
