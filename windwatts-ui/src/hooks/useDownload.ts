import { useState } from "react";
import { downloadCSV, getNearestGridLocation } from "../services/api";

export const useDownload = () => {

  const [isDownloading, setIsDownloading] = useState(false);
  const [showDownloadDialog, setShowDownloadDialog] = useState(false);
  const [nearestGridLocation, setNearestGridLocation] = useState<{
    latitude: number;
    longitude: number;
  } | null>(null);

  const handleDownloadClick = async ({
    lat,
    lng,
    dataModel,
  }: {
    lat: number;
    lng: number;
    dataModel?: string;
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
        setNearestGridLocation({
          latitude: nearestLocationData.locations[0].latitude,
          longitude: nearestLocationData.locations[0].longitude,
        });
      }
    } catch (error) {
      console.error('Failed to fetch nearest location:', error);
      // Still show dialog even if nearest location fetch fails
      setNearestGridLocation(null);
    }
    
    setShowDownloadDialog(true);
  };

  const handleDownloadConfirm = async ({
    lat,
    lng,
    dataModel,
  }: {
    lat: number;
    lng: number;
    dataModel?: string;
  }) => {
    setShowDownloadDialog(false);
    
    try {
      setIsDownloading(true);
      await downloadCSV({
        lat,
        lng,
        n_neighbors: 1,
        dataModel,
      });
    } catch (error) {
      console.error('Download failed:', error);
      alert('Download failed. Please try again.');
    } finally {
      setIsDownloading(false);
      setNearestGridLocation(null);
    }
  };

  const handleDownloadCancel = () => {
    setShowDownloadDialog(false);
    setNearestGridLocation(null);
  };

  return {
    isDownloading,
    showDownloadDialog,
    nearestGridLocation,
    handleDownloadClick,
    handleDownloadConfirm,
    handleDownloadCancel,
  };
};