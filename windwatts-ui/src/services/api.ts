import {
  EnergyProductionRequest,
  WindspeedByLatLngRequest,
} from "../types/Requests";

export const fetchWrapper = async (url: string, options: RequestInit) => {
  const response = await fetch(url, options);
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  return response.json();
};

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
