import { EnergyProductionRequest, WindspeedByLatLngRequest } from "../types";

export const fetchWrapper = async (url: string, options: RequestInit) => {
  const response = await fetch(url, options);
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  return response.json();
};
// time_period = "global" is default for windspeed in the era5_controller. But have to include "source" param as "athena_ensemble" for ensemble model result and "athena_era5" for regular era5 result which is default anyway.
export const getWindspeedByLatLong = async ({
  lat,
  lng,
  hubHeight,
  dataModel,
  ensemble,
}: WindspeedByLatLngRequest) => {
  const url = `/api/${dataModel}/windspeed?lat=${lat}&lng=${lng}&height=${hubHeight}${ensemble ? "&ensemble=true" : ""}`;
  const options = {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
  };
  return fetchWrapper(url, options);
};

// time_period = "all" works for era5 but have to add source param as "athena_era5" ("athena_era5" is default in era5_data_controller as source)
// time_period = "global" works for the ensemble model to fetch single global production value but have to add source as "athena_ensemble". Key is "energy_production" to get value.
export const getEnergyProduction = async ({
  lat,
  lng,
  hubHeight,
  powerCurve,
  dataModel,
  time_period = "all",
  ensemble,
}: EnergyProductionRequest) => {
  const url = `/api/${dataModel}/energy-production?lat=${lat}&lng=${lng}&height=${hubHeight}&selected_powercurve=${powerCurve}&time_period=${time_period}${ensemble ? "&ensemble=true" : ""}`;
  const options = {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
  };
  return fetchWrapper(url, options);
};

// export const getAvailablePowerCurves = async ({
//   dataModel,
// }: { dataModel: DataModel }) => {
//   const url = `/api/${dataModel}/available-powercurves`;
//   const options = {
//     method: "GET",
//     headers: {
//       "Content-Type": "application/json",
//     },
//   };
//   return fetchWrapper(url, options);
// };

export const getAvailablePowerCurves = async () => {
  const url = `/api/era5/available-powercurves`; // if fetching from era5, replace the wtk with era5
  const options = {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
  };
  return fetchWrapper(url, options);
};

export const getNearestGridLocation = async ({
  lat,
  lng,
  n_neighbors = 1,
  dataModel
}: {
  lat: number;
  lng: number;
  n_neighbors?: number;
  dataModel?: string;
}) => {
  const url = `/api/${dataModel}/nearest-locations?lat=${lat}&lng=${lng}&n_neighbors=${n_neighbors}`;
  const options = {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
  };
  return fetchWrapper(url, options);
};

export const downloadCSV = async ({
  lat,
  lng,
  n_neighbors = 1,
  dataModel
}: {
  lat: number;
  lng: number;
  n_neighbors?: number;
  source?: string;
  dataModel?: string;
}) => {
  const nearestLocationData = await getNearestGridLocation({
      lat,
      lng,
      n_neighbors: 1,
      dataModel,
    });

  let gridLat = lat;
  let gridLng = lng;

  if (nearestLocationData?.locations?.[0]) {
      gridLat = nearestLocationData.locations[0].latitude;
      gridLng = nearestLocationData.locations[0].longitude;
  }

  const url = `/api/${dataModel}/download-csv?lat=${lat}&lng=${lng}&n_neighbors=${n_neighbors}`;
  
  const options = {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
  };

  try {

    const response = await fetch(url, options);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    // Handling the file blob and trigger the download
    const blob = await response.blob();
    const downloadUrl = window.URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = downloadUrl;
    
    // Generating the filename with grid coordinates
    const filename = `wind_data_${gridLat.toFixed(3)}_${gridLng.toFixed(3)}.csv`;
    link.download = filename;
    
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(downloadUrl);
    
    return { success: true, filename };
  } catch (error) {
    console.error('Download failed:', error);
    throw error;
  }
};
