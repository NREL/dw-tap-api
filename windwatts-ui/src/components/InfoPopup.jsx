import { InfoWindowF } from "@react-google-maps/api";
import { Box, Typography, Button } from "@mui/material";
import PropTypes from "prop-types";
import { useOutletContext } from "react-router-dom";

const InfoPopup = ({ position, onCloseClick, onSaveLocation }) => {
  const { handleOpenResults } = useOutletContext();
  const handleAnalyzeDataClick = () => {
    onCloseClick();
    handleOpenResults();
  };
  return (
    <InfoWindowF position={position} onCloseClick={onCloseClick}>
      <Box minWidth={300}>
        <Typography variant="h5" gutterBottom>
          Selected Location
        </Typography>
        <Typography variant="body2" marginBottom={3}>
          Coordinates: ({position.lat.toFixed(3)}, {position.lng.toFixed(3)})
        </Typography>
        <Box sx={{ display: "flex", justifyContent: "space-between", mt: 1 }}>
          <Button
            variant="contained"
            color="primary"
            size="small"
            onClick={onSaveLocation}
          >
            Save Location
          </Button>
          <Button
            variant="contained"
            color="primary"
            size="small"
            onClick={handleAnalyzeDataClick}
          >
            Analyze Data
          </Button>
        </Box>
      </Box>
    </InfoWindowF>
  );
};

InfoPopup.propTypes = {
  position: PropTypes.shape({
    lat: PropTypes.number.isRequired,
    lng: PropTypes.number.isRequired,
  }).isRequired,
  onCloseClick: PropTypes.func.isRequired,
  onSaveLocation: PropTypes.func.isRequired,
};

export default InfoPopup;
