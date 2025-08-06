import { Box, Typography, ToggleButton } from "@mui/material";
import { useContext } from "react";
import { UnitsContext } from "../../providers/UnitsContext";
import { SettingToggleButtonGroup } from "./SettingToggleButtonGroup";

export function UnitsSettings() {
  const { units, updateUnit } = useContext(UnitsContext);

  const handleWindspeedChange = (
    _: React.MouseEvent<HTMLElement>,
    newWindspeedUnit: string
  ) => {
    if (newWindspeedUnit !== null) {
      updateUnit("windspeed", newWindspeedUnit);
    }
  };

  const handleOutputChange = (
    _: React.MouseEvent<HTMLElement>,
    newOutputUnit: string
  ) => {
    if (newOutputUnit !== null) {
      updateUnit("output", newOutputUnit);
    }
  };

  return (
    <Box sx={{ mt: 4 }}>
      <Typography variant="h6" gutterBottom>
        Units
      </Typography>

      <Box
        sx={{
          display: "grid",
          gridTemplateColumns: "repeat(12, 1fr)",
          gap: 1,
          justifyContent: "space-between",
          alignItems: "center",
        }}
      >
        <Box sx={{ gridColumn: "span 4" }}>
          <Typography variant="body2">Windspeed:</Typography>
        </Box>
        <Box
          sx={{
            gridColumn: "span 8",
            textAlign: "left",
          }}
        >
          <SettingToggleButtonGroup
            value={units.windspeed}
            exclusive
            size="small"
            onChange={handleWindspeedChange}
            aria-label="windspeed units"
          >
            <ToggleButton value="mph">
              <Typography variant="body2">mph</Typography>
            </ToggleButton>
            <ToggleButton value="m/s">
              <Typography variant="body2">m/s</Typography>
            </ToggleButton>
          </SettingToggleButtonGroup>
        </Box>
        <Box sx={{ gridColumn: "span 4" }}>
          <Typography variant="body2">Output:</Typography>
        </Box>
        <Box sx={{ gridColumn: "span 8", textAlign: "left" }}>
          <SettingToggleButtonGroup
            value={units.output}
            exclusive
            size="small"
            onChange={handleOutputChange}
            aria-label="output units"
          >
            <ToggleButton value="MWh">
              <Typography variant="body2">MWh</Typography>
            </ToggleButton>
            <ToggleButton value="kWh">
              <Typography variant="body2">kWh</Typography>
            </ToggleButton>
          </SettingToggleButtonGroup>
        </Box>
      </Box>
    </Box>
  );
}
