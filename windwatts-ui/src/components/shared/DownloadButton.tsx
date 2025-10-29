import { useState, useContext } from "react";
import { Button, ButtonProps } from "@mui/material";
import DownloadIcon from "@mui/icons-material/Download";
import { useDownloadCSVFile, useNearestGridLocation } from "../../hooks";
import { DownloadDialog } from "./DownloadDialog";
import { SettingsContext } from "../../providers/SettingsContext";

interface DownloadButtonProps extends Omit<ButtonProps, 'onClick'> {
  buttonText?: string;
  downloadingText?: string;
}

export const DownloadButton = ({
  buttonText = "Download Example Hourly Data",
  downloadingText = "Downloading...",
  variant = "contained",
  size = "small",
  sx,
  ...buttonProps
}: DownloadButtonProps) => {
  const [showDownloadDialog, setShowDownloadDialog] = useState(false);
  const [downloadError, setDownloadError] = useState<string | null>(null);

  const { currentPosition, preferredModel: dataModel } = useContext(SettingsContext);
  const { lat, lng } = currentPosition || {};

  const { canDownload, isDownloading, downloadFile } = useDownloadCSVFile();

  // useNearestGridLocation hook to fetch and cache nearest grid location
  const {
    gridLocation: nearestGridLocation,
    isLoading: isLoadingGridLocation,
    error: gridLocationError,
  } = useNearestGridLocation();

  const handleDownloadClick = () => {
    if (!canDownload) return;
    setDownloadError(null);
    setShowDownloadDialog(true);
  };

  const handleDownloadConfirm = async () => {
    if (!canDownload || !nearestGridLocation) return;

    setDownloadError(null);
    
    try {
      const result = await downloadFile(
        nearestGridLocation.latitude,
        nearestGridLocation.longitude
      );

      if (!result.success) {
        const errorMessage = result.error instanceof Error ? result.error.message : "Download failed";
        setDownloadError(errorMessage);
        return;
      }

      setShowDownloadDialog(false);
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : "Unexpected error occurred";
      setDownloadError(errorMessage);
    }
  };

  const handleDownloadCancel = () => {
    if (isDownloading || isLoadingGridLocation) return;
    setShowDownloadDialog(false);
    setDownloadError(null);
  };

  const handleRetry = () => {
    if (gridLocationError) {
      // Retry is handled by SWR automatically when dialog reopens
      setShowDownloadDialog(false);
      setTimeout(() => setShowDownloadDialog(true), 100);
    } else if (downloadError) {
      handleDownloadConfirm();
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
        lat={lat ?? 0}
        lng={lng ?? 0}
        nearestGridLocation={nearestGridLocation}
        dataModel={dataModel!}
        isLoadingGridLocation={isLoadingGridLocation}
        gridLocationError={gridLocationError}
        downloadError={downloadError}
      />
    </>
  );
};