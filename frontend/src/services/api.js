export const delay = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

export const fetchWrapper = async (url, options) => {
  const response = await fetch(url, options);
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  return response.json();
};

export const getWindResourceData = async (windResource) => {
  // example implementation
  // const url = `api/wind-resource/${windResource}`;
  // const options = {
  //   method: "GET",
  //   headers: {
  //     "Content-Type": "application/json",
  //   },
  // };
  // return fetchWrapper(url, options);
  console.log("getWindResourceData for " + windResource);
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

export const getWindResourceDataByCoordinates = async ({ lat, lng }) => {
  // example implementation
  // const url = `api/wind-resource/coordinates?lat=${lat}&lng=${lng}`;
  // const options = {
  //   method: "GET",
  //   headers: {
  //     "Content-Type": "application/json",
  //   },
  // };
  // return fetchWrapper(url, options);
  // throw new Error("Not implemented");
  console.log("getWindResourceDataByCoordinates for " + lat + ", " + lng);
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
