import { useState } from "react";
import { getCSVFile, getNearestGridLocation } from "../services/api";
import { downloadWindDataCSV } from "../services/download";
import { DataModel } from "../types";

export const useDownload = () => {

  const [isDownloading, setIsDownloading] = useState(false);

  const fetchNearestGridLocation = async ({
    lat,
    lng,
    dataModel,
  }: {
    lat: number;
    lng: number;
    dataModel: DataModel;
  }) => {
    try {
      // Fetch nearest grid location
      const nearestLocationData = await getNearestGridLocation({
        lat,
        lng,
        n_neighbors: 1,
        dataModel,
      });
      
      if (nearestLocationData?.locations?.[0]) {
        return {
          latitude: nearestLocationData.locations[0].latitude,
          longitude: nearestLocationData.locations[0].longitude,
        };
      }
      return null;
    } catch (error) {
      console.error('Failed to fetch nearest location:', error);
      return null;
    }
  };

  const downloadFile = async ({
    lat,
    lng,
    dataModel,
    gridLat,
    gridLng,
  }: {
    lat: number;
    lng: number;
    dataModel: DataModel;
    gridLat: number;
    gridLng: number;
  }) => {
    try {
      setIsDownloading(true);
      const response = await getCSVFile({
        lat,
        lng,
        n_neighbors: 1,
        dataModel,
      });
      await downloadWindDataCSV(response, gridLat, gridLng);
      return { success: true };
    } catch (error) {
      console.error('Download failed:', error);
      return { success: false, error };
    } finally {
      setIsDownloading(false);
    }
  };

  return {
    isDownloading,
    fetchNearestGridLocation,
    downloadFile,
  };
};