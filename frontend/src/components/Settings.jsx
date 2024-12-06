import { Box, Modal, Typography, Slider, Radio, RadioGroup, FormControlLabel, FormControl } from '@mui/material';
import PropTypes from 'prop-types';

const powerCurveOptions = [
  2.5, 100, 250, 2000
];

const hubHeightMarks = [ 40, 60, 80, 100, 120, 140 ].map(
  (value) => ({ value: value, label: `${value}m` })
);

const Settings = ({ openSettings, handleClose, hubHeight, setHubHeight, powerCurve, setPowerCurve }) => {

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
              {powerCurveOptions.map((option, idx) => (
                <FormControlLabel 
                  key={'power_curve_option_' + idx} 
                  value={option} 
                  control={<Radio sx={{ '& .MuiSvgIcon-root': { fontSize: 20 } }}/>} 
                  label={
                    <Typography variant='body2'>
                      {`NREL's reference power curve for ${option}kW`}
                    </Typography>}
                />
              ))
            }
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