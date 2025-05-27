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
}: WindspeedByLatLngRequest) => {
  const url = `/api/wtk/windspeed?lat=${lat}&lng=${lng}&height=${hubHeight}`;
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
}: EnergyProductionRequest) => {
  const url = `/api/wtk/energy-production?lat=${lat}&lng=${lng}&height=${hubHeight}&selected_powercurve=${powerCurve}&time_period=yearly`;
  const options = {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
  };
  return fetchWrapper(url, options);
};

export const getAvailablePowerCurves = async () => {
  const url = `/api/wtk/available-powercurves`;
  const options = {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
  };
  return fetchWrapper(url, options);
};

export const getProductionTable = async ({
  lat,
  lng,
  hubHeight,
  powerCurve,
  time_period,
}: EnergyProductionRequest) => {
  const url = `/api/wtk/energy-production?lat=${lat}&lng=${lng}&height=${hubHeight}&selected_powercurve=${powerCurve}&time_period=${time_period}`;
  if (time_period) {
    console.log("Time period:", time_period);
  }
  const options = {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
  };
  return fetchWrapper(url, options);
}


export const getProductionTables = async (lat: number, lng: number, hubHeight: number, powerCurve: string) => {
  const yearlyProductionRequest: EnergyProductionRequest = {
    lat: lat,
    lng: lng,
    hubHeight: hubHeight,
    powerCurve: powerCurve,
    time_period: "yearly",
  }
  const monthlyProductionRequest: EnergyProductionRequest = {
    lat: lat,
    lng: lng,
    hubHeight: hubHeight,
    powerCurve: powerCurve,
    time_period: "monthly",
  };
  const y = await getProductionTable(yearlyProductionRequest);
  const m = await getProductionTable(monthlyProductionRequest);
  console.log('Yearly Production:', y);
  console.log('Monthly Production:', m);
  return {
    'yearly': y.yearly_avg_energy_production,
    'monthly': m.monthly_avg_energy_production,
  }
}