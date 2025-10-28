import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  DialogContentText,
  Button,
  Box,
  Typography,
  CircularProgress,
  Alert,
  Skeleton,
} from "@mui/material";
import { getDownloadInfo } from "../../constants/downloadInfo";
import { DataModel } from "../../types";

interface DownloadDialogProps {
  open: boolean;
  onClose: () => void;
  onConfirm: () => void;
  isDownloading: boolean;
  lat: number;
  lng: number;
  nearestGridLocation: {
    latitude: number;
    longitude: number;
  } | null;
  dataModel: DataModel;
  isLoadingGridLocation?: boolean;
  gridLocationError?: string | null;
  downloadError?: string | null;
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
  isLoadingGridLocation = false,
  gridLocationError = null,
  downloadError = null,
}: DownloadDialogProps) => {

  const downloadInfo = getDownloadInfo(dataModel);
  const canConfirm = !isLoadingGridLocation && !gridLocationError && !isDownloading && nearestGridLocation;

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
        {(isLoadingGridLocation || isDownloading) && (
          <CircularProgress size={20} sx={{ ml: 2 }} />
        )}
      </DialogTitle>
      <DialogContent>
        <DialogContentText id="download-dialog-description" component="div">
          <Typography variant="body2" sx={{ mb: 1 }}>
            <strong>Selected Coordinates:</strong> ({lat?.toFixed(3)}, {lng?.toFixed(3)})
          </Typography>
          
          {isLoadingGridLocation && (
            <Box sx={{ mb: 1 }}>
              <Typography variant="body2" sx={{ mb: 1 }}>
                <strong>Data Grid Coordinates:</strong>
              </Typography>
              <Skeleton variant="text" width="60%" height={20} />
              <Skeleton variant="text" width="80%" height={16} sx={{ mt: 0.5 }} />
            </Box>
          )}

          {gridLocationError && (
            <Alert severity="error" sx={{ mb: 2 }}>
              <Typography variant="body2">
                <strong>Failed to fetch grid location:</strong> {gridLocationError}
              </Typography>
              <Typography variant="body2" sx={{ mt: 1, fontSize: '0.85em' }}>
                Please try again or contact support if the problem persists.
              </Typography>
            </Alert>
          )}

          {downloadError && (
            <Alert severity="error" sx={{ mb: 2 }}>
              <Typography variant="body2">
                <strong>Download failed:</strong> {downloadError}
              </Typography>
              <Typography variant="body2" sx={{ mt: 1, fontSize: '0.85em' }}>
                Please try again.
              </Typography>
            </Alert>
          )}

          {nearestGridLocation && !isLoadingGridLocation && (
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

          {isLoadingGridLocation ? (
            <Box>
              <Skeleton variant="text" width="70%" height={20} sx={{ mb: 1 }} />
              <Skeleton variant="text" width="50%" height={20} sx={{ mb: 1 }} />
              <Skeleton variant="text" width="90%" height={20} sx={{ mb: 1 }} />
              <Skeleton variant="text" width="85%" height={20} />
            </Box>
          ) : (
            downloadInfo && (
              <>
                <Typography variant="body2" sx={{ mb: 1 }}>
                  <strong>Data Source:</strong> {downloadInfo.description}
                </Typography>
                
                <Typography variant="body2" sx={{ mb: 1 }}>
                  <strong>Year Range:</strong> {downloadInfo.yearRange}
                </Typography>

                {downloadInfo.windspeed_heights && (
                  <Typography variant="body2" sx={{ mb: 1 }}>
                    <strong>Windspeed Heights:</strong> {downloadInfo.windspeed_heights.join(", ")}
                  </Typography>
                )}

                {downloadInfo.winddirection_heights && (
                  <Typography variant="body2" sx={{ mb: 1 }}>
                    <strong>Wind Direction Heights:</strong> {downloadInfo.winddirection_heights.join(", ")}
                  </Typography>
                )}
              </>
            )
          )}

          {isDownloading && (
            <Alert severity="info" sx={{ mt: 2 }}>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <CircularProgress size={16} sx={{ mr: 1 }} />
                <Typography variant="body2">
                  Preparing your download... This may take a few moments.
                </Typography>
              </Box>
            </Alert>
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
          disabled={!canConfirm}
          sx={{ textTransform: "none" }}
        >
          {isDownloading ? 'Downloading...' :
          isLoadingGridLocation ? 'Loading...' : 
           gridLocationError ? 'Retry' : 'Download'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};