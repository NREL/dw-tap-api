import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  DialogContentText,
  Button,
  Box,
  Typography,
} from "@mui/material";
import { getDownloadInfo } from "../../utils/downloadInfo";

interface DownloadDialogProps {
  open: boolean;
  onClose: () => void;
  onConfirm: () => void;
  isDownloading: boolean;
  lat?: number;
  lng?: number;
  nearestGridLocation?: {
    latitude: number;
    longitude: number;
  } | null;
  dataModel: string;
}

export const DownloadDialog = ({
  open,
  onClose,
  onConfirm,
  isDownloading,
  lat,
  lng,
  nearestGridLocation,
  dataModel,
}: DownloadDialogProps) => {
  const downloadInfo = getDownloadInfo(dataModel);

  return (
    <Dialog
      open={open}
      onClose={onClose}
      aria-labelledby="download-dialog-title"
      aria-describedby="download-dialog-description"
      maxWidth="sm"
      fullWidth
    >
      <DialogTitle id="download-dialog-title">
        Download Hourly Wind Data
      </DialogTitle>
      <DialogContent>
        <DialogContentText id="download-dialog-description" component="div">
          <Typography variant="body2" sx={{ mb: 1 }}>
            <strong>Selected Coordinates:</strong> ({lat?.toFixed(3)}, {lng?.toFixed(3)})
          </Typography>
          
          {nearestGridLocation && (
            <Box sx={{ mb: 1 }}>
              <Typography variant="body2">
                <strong>Data Grid Coordinates:</strong> ({nearestGridLocation.latitude.toFixed(3)}, {nearestGridLocation.longitude.toFixed(3)})
              </Typography>
              <Typography 
                variant="body2" 
                sx={{ 
                  fontSize: '0.9em', 
                  color: '#666', 
                  fontStyle: 'italic',
                  mt: 0.5,
                  mb: 1
                }}
              >
                Note: Wind data is available at specific grid points. The download will contain data from the nearest grid point to your selected location.
              </Typography>
            </Box>
          )}

          {downloadInfo && (
            <>
              <Typography variant="body2" sx={{ mb: 1 }}>
                <strong>Data Source:</strong> {downloadInfo.description}
              </Typography>
              
              <Typography variant="body2" sx={{ mb: 1 }}>
                <strong>Year Range:</strong> {downloadInfo.yearRange}
              </Typography>

              {/* Windspeed heights */}
              {downloadInfo.windspeed_heights && (
                <Typography variant="body2" sx={{ mb: 1 }}>
                  <strong>Windspeed Heights:</strong> {downloadInfo.windspeed_heights.join(", ")}
                </Typography>
              )}

              {/* Wind direction heights */}
              {downloadInfo.winddirection_heights && (
                <Typography variant="body2" sx={{ mb: 1 }}>
                  <strong>Wind Direction Heights:</strong> {downloadInfo.winddirection_heights.join(", ")}
                </Typography>
              )}
            </>
          )}
        </DialogContentText>
      </DialogContent>
      <DialogActions sx={{ px: 3, pb: 2 }}>
        <Button 
          onClick={onClose}
          variant="outlined"
          sx={{ textTransform: "none" }}
        >
          Cancel
        </Button>
        <Button 
          onClick={onConfirm} 
          variant="contained"
          disabled={isDownloading}
          sx={{ textTransform: "none" }}
        >
          {isDownloading ? 'Downloading...' : 'Download'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};