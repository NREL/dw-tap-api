import { useState } from "react";
import { Button, ButtonProps } from "@mui/material";
import DownloadIcon from "@mui/icons-material/Download";
import { useDownload } from "../../hooks/useDownload";
import { DownloadDialog } from "./DownloadDialog";
import { DataModel } from "../../types";

interface DownloadButtonProps extends Omit<ButtonProps, 'onClick'> {
  lat: number;
  lng: number;
  dataModel: DataModel;
  canDownload: boolean;
  buttonText?: string;
  downloadingText?: string;
}

export const DownloadButton = ({
  lat,
  lng,
  dataModel,
  canDownload,
  buttonText = "Download Example Hourly Data",
  downloadingText = "Downloading...",
  variant = "contained",
  size = "small",
  sx,
  ...buttonProps
}: DownloadButtonProps) => {
  const [showDownloadDialog, setShowDownloadDialog] = useState(false);
  const [nearestGridLocation, setNearestGridLocation] = useState<{
    latitude: number;
    longitude: number;
  } | null>(null);

  const [isLoadingGridLocation, setIsLoadingGridLocation] = useState(false);
  const [gridLocationError, setGridLocationError] = useState<string | null>(null);
  const [downloadError, setDownloadError] = useState<string | null>(null);

  const {
    isDownloading,
    fetchNearestGridLocation,
    downloadFile
  } = useDownload();

  const handleDownloadClick = async () => {
    if (!canDownload) return;

    setGridLocationError(null);
    setDownloadError(null);
    setIsLoadingGridLocation(true);
    setShowDownloadDialog(true);

    try{
        const gridLocation = await fetchNearestGridLocation({
        lat,
        lng,
        dataModel
        });

        setNearestGridLocation(gridLocation);

        if (!gridLocation) {
            setGridLocationError("Unable to find nearest grid location for the selected coordinates.");
        }
    }
    catch(error){
        const errorMessage = error instanceof Error ? error.message : "Unknown error occurred";
        setGridLocationError(errorMessage);
        setNearestGridLocation(null);
    }
    finally{
        setIsLoadingGridLocation(false);
    }
  };

  const handleDownloadConfirm = async () => {
    if (!canDownload || !nearestGridLocation) return;

    setDownloadError(null);
    
    try{
        const result = await downloadFile({
        lat,
        lng,
        dataModel,
        gridLat: nearestGridLocation?.latitude,
        gridLng: nearestGridLocation?.longitude
        });

        if (!result.success) {
            const errorMessage = result.error instanceof Error ? result.error.message : "Download failed";
            setDownloadError(errorMessage);
            return;
        }

        setShowDownloadDialog(false);
        setNearestGridLocation(null);
    }
    catch(error){
        const errorMessage = error instanceof Error ? error.message : "Unexpected error occurred";
        setDownloadError(errorMessage);
    }
  };

  const handleDownloadCancel = () => {
    if (isDownloading || isLoadingGridLocation) return;

    setShowDownloadDialog(false);
    setNearestGridLocation(null);
    setGridLocationError(null);
    setDownloadError(null);
  };

  const handleRetry = async () => {
    if (gridLocationError) {
      await handleDownloadClick();
    } else if (downloadError) {
      await handleDownloadConfirm();
    }
  };

  return (
    <>
      <Button
        variant={variant}
        size={size}
        startIcon={<DownloadIcon />}
        onClick={handleDownloadClick}
        disabled={!canDownload || isDownloading}
        sx={{
          fontSize: "0.9em",
          textTransform: "none",
          borderRadius: 2,
          px: 2,
          py: 0.5,
          backgroundColor: variant === "contained" ? "primary.main" : undefined,
          "&:hover": {
            backgroundColor: variant === "contained" ? "primary.dark" : undefined,
          },
          ...sx,
        }}
        {...buttonProps}
      >
        {isDownloading ? downloadingText : buttonText}
      </Button>

      <DownloadDialog
        open={showDownloadDialog}
        onClose={handleDownloadCancel}
        onConfirm={gridLocationError || downloadError ? handleRetry : handleDownloadConfirm}
        isDownloading={isDownloading}
        lat={lat}
        lng={lng}
        nearestGridLocation={nearestGridLocation}
        dataModel={dataModel}
        isLoadingGridLocation={isLoadingGridLocation}
        gridLocationError={gridLocationError}
        downloadError={downloadError}
      />
    </>
  );
};