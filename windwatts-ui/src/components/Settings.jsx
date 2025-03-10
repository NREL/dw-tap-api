import { Box, Modal, Typography, Slider, Radio, RadioGroup, FormControlLabel, FormControl, IconButton } from '@mui/material';
import PropTypes from 'prop-types';
import { Close } from '@mui/icons-material';
import { getAvailablePowerCurves } from "../services/api";
import useSWR from "swr";

// const powerCurveOptions = [
//   'nrel-reference-100kW',
//   'nrel-reference-2.5kW',
//   'nrel-reference-250kW',
//   'nrel-reference-2000kW'
// ];


const hubHeightMarks = [ 40, 60, 80, 100, 120, 140 ].map(
  (value) => ({ value: value, label: `${value}m` })
);

const Settings = ({ openSettings, handleClose, hubHeight, setHubHeight, powerCurve, setPowerCurve }) => {

  const { data: availablePowerCurves, error: availablePowerCurvesError } = useSWR(
    openSettings ? {} : null,
    getAvailablePowerCurves);

  // Use availablePowerCurves if available, otherwise fallback to an empty array
  const powerCurveOptions = availablePowerCurves?.available_power_curves || [];

  const handleHubHeightChange = (event, newValue) => {
    setHubHeight(newValue);
  };
  
  const handlePowerCurveChange = (event) => {
    setPowerCurve(event.target.value);
  };

  return (
    <Modal
      open={openSettings}
      onClose={handleClose}
      aria-labelledby="settings-modal-title"
      aria-describedby="settings-modal-description"
      sx={{ color: 'black'}}
    >
      <Box sx={{ 
          position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%, -50%)', 
          width: 400, bgcolor: 'background.paper', p: 4 }}>
        <IconButton
            aria-label="close"
            onClick={handleClose}
            sx={{
                position: 'absolute',
                right: 8,
                top: 8,
            }}
        >
            <Close />
        </IconButton>
        <Typography id="settings-modal-title" variant="h5" component="h2">
          Settings
        </Typography>

        <Box sx={{ mt: 2 }}>
          <Typography variant="h6" gutterBottom>
            Hub Height
          </Typography>
          <Typography variant='body1' gutterBottom>
            Choose a closest value (in meters) to the considered hub height:
          </Typography>
          <Slider
            value={hubHeight}
            onChange={handleHubHeightChange}
            aria-labelledby="hub-height-slider"
            valueLabelDisplay="auto"
            getAriaValueText={(value) => `${value}m`}
            step={10}
            marks={hubHeightMarks}
            min={30}
            max={140}
          />
        </Box>
        <Box sx={{ mt: 4 }}>
          <Typography variant="h6" gutterBottom>
            Power Curve
          </Typography>
          <Typography variant='body1' gutterBottom>
            Select a power curve option:
          </Typography>
          
          <FormControl component="fieldset" sx={{ width: '100%'}}>
            <RadioGroup
              aria-label="power-curve"
              name="power-curve"
              value={powerCurve}
              onChange={handlePowerCurveChange}
            >
              {
              powerCurveOptions.length > 0 ? (
                powerCurveOptions.map((option, idx) => (
                <FormControlLabel 
                  key={'power_curve_option_' + idx} 
                  value={option} 
                  control={<Radio sx={{ '& .MuiSvgIcon-root': { fontSize: 20 } }}/>} 
                  label={
                    <Typography variant='body2'>
                      {option}
                    </Typography>}
                />
              ))
                ) : (<Typography variant="body2">Loading power curve options...</Typography>
              )}
            </RadioGroup>
          
          </FormControl>
          <Typography variant='body2' marginTop={2} gutterBottom>
            * Make sure the selected turbine class matches the hub height 
            (higher hub heights should be chosen for larger turbines).
          </Typography>
        </Box>
      </Box>
    </Modal>
  );
};

Settings.propTypes = {
  openSettings: PropTypes.bool.isRequired,
  handleClose: PropTypes.func.isRequired,
  hubHeight: PropTypes.number.isRequired,
  setHubHeight: PropTypes.func.isRequired,
  powerCurve: PropTypes.number.isRequired,
  setPowerCurve: PropTypes.func.isRequired,
};


export default Settings;