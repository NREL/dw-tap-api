export const delay = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

export const fetchWrapper = async (url, options) => {
  const response = await fetch(url, options);
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  return response.json();
};

export const getWindResourceData = async (windResource) => {
  await delay(1000);
  return {
    winddataexample: [
      {
        title: "Wind Resource 1",
        subheader: "Details about wind resource 1",
        data: "Data for wind resource 1",
        details: ["Detail 1", "Detail 2", "Detail 3"],
      },
      {
        title: "Wind Resource 2",
        subheader: "Details about wind resource 2",
        data: "Data for wind resource 2",
        details: ["Detail 1", "Detail 2", "Detail 3"],
      },
      {
        title: "Wind Resource 3",
        subheader: "Details about wind resource 3",
        data: "Data for wind resource 3",
        details: ["Detail 1", "Detail 2", "Detail 3"],
      },
    ],
  };
};

export const getWindspeedByLatLong = async ({ lat, lng, height }) => {
  const url = `/api/wtk/windspeed?lat=${lat}&lng=${lng}&height=${height}`;
  const options = {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
  };
  return fetchWrapper(url, options);
};

export const getEnergyProduction = async ({ lat, lng, height, powerCurve }) => {
  const url = `/api/wtk/energy-production?lat=${lat}&lng=${lng}&height=${height}&selected_powercurve=${powerCurve}`;
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
