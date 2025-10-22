export const getDownloadInfo = (dataModel: string) => {
  const modelInfo = {
    era5: {
      description: "ERA5 (ECMWF Reanalysis v5) Dataset",
      yearRange: "2020-2023",
      windspeed_heights: ["10m", "30m", "40m", "50m", "60m", "80m", "100m"],
      winddirection_heights: ["10m", "100m"],
    }
  };
  
  return modelInfo[dataModel as keyof typeof modelInfo];
};