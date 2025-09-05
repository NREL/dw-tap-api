import { EnergyProductionRequest, WindspeedByLatLngRequest } from "../types";

export const fetchWrapper = async (url: string, options: RequestInit) => {
  const response = await fetch(url, options);
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  return response.json();
};
// time_period = "global" is default for windspeed in the era5_controller. But have to include "source" param as "athena_era5_bc" for bias corrected result and "athena_era5" for non bc result which is default anyway.
export const getWindspeedByLatLong = async ({
  lat,
  lng,
  hubHeight,
  dataModel,
}: WindspeedByLatLngRequest) => {
  const url = `/api/${dataModel}/windspeed?lat=${lat}&lng=${lng}&height=${hubHeight}`;
  const options = {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
  };
  return fetchWrapper(url, options);
};
// time_period = "all" works for era5 but have to add source param as "athena_era5" ("athena_era5" is default in era5_data_controller as source)
// time_period = "global" works for the era5_bc to fetch single global production value but have to add source as "athena_era5_bc". Key is "global_energy_production" to get value.
export const getEnergyProduction = async ({
  lat,
  lng,
  hubHeight,
  powerCurve,
  dataModel,
  time_period = "all",
}: EnergyProductionRequest) => {
  const url = `/api/${dataModel}/energy-production?lat=${lat}&lng=${lng}&height=${hubHeight}&selected_powercurve=${powerCurve}&time_period=${time_period}`;
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
