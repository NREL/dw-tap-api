import { useState, useMemo, useContext } from "react";
import useSWR from "swr";
import { getCSVFile, getNearestGridLocation } from "../services/api";
import { downloadWindDataCSV } from "../services/download";
import { SettingsContext } from "../providers/SettingsContext";

export const useDownloadCSVFile = () => {
  const [isDownloading, setIsDownloading] = useState(false);
  const { currentPosition, preferredModel: dataModel } = useContext(SettingsContext);
  const { lat, lng } = currentPosition || {};

  const canDownload = !!(lat && lng && dataModel);

  const downloadFile = async (gridLat: number, gridLng: number) => {
    try {
      setIsDownloading(true);
      const response = await getCSVFile({
        lat: lat!,
        lng: lng!,
        n_neighbors: 1,
        dataModel: dataModel!,
      });
      await downloadWindDataCSV(response, gridLat, gridLng);
      return { success: true };
    } catch (error) {
      console.error("Download failed:", error);
      return { success: false, error };
    } finally {
      setIsDownloading(false);
    }
  };

  return {
    canDownload,
    isDownloading,
    downloadFile,
  };
};

export const useNearestGridLocation = () => {
  const { currentPosition, preferredModel: dataModel } =
    useContext(SettingsContext);
  const { lat, lng } = currentPosition || {};

  const shouldFetch = lat && lng && dataModel;

  // Memoize the SWR key to prevent unnecessary re-renders
  const swrKey = useMemo(() => {
    if (!shouldFetch) return null;
    return JSON.stringify({ lat, lng, dataModel, type: "nearest-grid" });
  }, [shouldFetch, lat, lng, dataModel]);

  const { isLoading, data, error } = useSWR(
    swrKey,
    () =>
      getNearestGridLocation({
        lat: lat!,
        lng: lng!,
        n_neighbors: 1,
        dataModel: dataModel!,
      }),
    {
      revalidateOnFocus: false,
      revalidateOnReconnect: false,
      revalidateIfStale: false,
      dedupingInterval: 60000, // Cache for 1 minute
    }
  );

  const gridLocation = data?.locations?.[0]
    ? {
        latitude: data.locations[0].latitude,
        longitude: data.locations[0].longitude,
      }
    : null;

  return {
    gridLocation,
    isLoading,
    error,
    hasData: !!gridLocation,
  };
};
