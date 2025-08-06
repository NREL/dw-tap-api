import {
  Box,
  FormControl,
  FormControlLabel,
  Radio,
  RadioGroup,
  Typography,
} from "@mui/material";
import useSWR from "swr";
import { SettingsContext } from "../../providers/SettingsContext";
import { useContext } from "react";
import { getAvailablePowerCurves } from "../../services/api";
import { POWER_CURVE_LABEL } from "../../constants";

const NRELPowerCurveOptions = [
  "nrel-reference-2.5kW",
  "nrel-reference-100kW",
  "nrel-reference-250kW",
  "nrel-reference-2000kW",
];

export function PowerCurveSettings() {
  const { powerCurve, setPowerCurve } = useContext(SettingsContext);

  // Fetch available power curves from the API
  const { data } = useSWR(
    "/api/wtk/available-powercurves",
    getAvailablePowerCurves,
    { fallbackData: { available_power_curves: NRELPowerCurveOptions } }
  );

  const powerCurveOptions: string[] = data?.available_power_curves || [];

  const handlePowerCurveChange = (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    setPowerCurve(event.target.value);
  };

  return (
    <Box sx={{ mt: 4 }}>
      <Typography variant="h6" gutterBottom>
        Power Curve
      </Typography>
      <Typography variant="body1" gutterBottom>
        Select a power curve option:
      </Typography>

      <FormControl component="fieldset" sx={{ width: "100%" }}>
        <RadioGroup
          aria-label="power-curve"
          name="power-curve"
          value={powerCurve}
          onChange={handlePowerCurveChange}
        >
          {powerCurveOptions.length > 0 ? (
            powerCurveOptions.map((option, idx) => (
              <FormControlLabel
                key={"power_curve_option_" + idx}
                value={option}
                control={
                  <Radio sx={{ "& .MuiSvgIcon-root": { fontSize: 20 } }} />
                }
                label={
                  <Typography variant="body2">
                    {POWER_CURVE_LABEL[option] || option}
                  </Typography>
                }
              />
            ))
          ) : (
            <Typography variant="body2">
              Loading power curve options...
            </Typography>
          )}
        </RadioGroup>

        <Typography variant="body2" marginTop={2} gutterBottom>
          * Make sure the selected turbine class matches the hub height (higher
          hub heights should be chosen for larger turbines).
        </Typography>
      </FormControl>
    </Box>
  );
}
