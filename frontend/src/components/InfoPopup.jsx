import { InfoWindowF } from '@react-google-maps/api';
import { Box, Typography, Button } from '@mui/material';
import PropTypes from 'prop-types';

const InfoPopup = ({ position, onCloseClick, onAnalyzeClick }) => {
    return (
        <InfoWindowF position={position} onCloseClick={onCloseClick}>
            <Box>
                <Typography variant="h5" gutterBottom>Selected Location</Typography>
                <Typography variant="body2" marginBottom={3}>
                    Coordinates: ({position.lat}, {position.lng})
                </Typography>
                <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 1 }}>
                    <Button variant="contained" 
                        color="primary" 
                        size='small'
                        onClick={onAnalyzeClick}>
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
    onAnalyzeClick: PropTypes.func.isRequired,
  };

export default InfoPopup;