import { useContext } from "react";
import { SettingsContext } from "../../providers/SettingsContext";
import { Box, Slider, Typography } from "@mui/material";

const hubHeightMarks = [40, 60, 80, 100, 120, 140].map((value: number) => ({
  value: value,
  label: `${value}m`,
}));

export function HubHeightSettings() {
  const { hubHeight, setHubHeight } = useContext(SettingsContext);

  const handleHubHeightChange = (
    _: Event,
    newHubHeight: number | number[] | null
  ) => {
    if (newHubHeight !== null && typeof newHubHeight === "number") {
      setHubHeight(newHubHeight);
    }
  };

  return (
     <Box sx={{ mt: 2 }}>
      <Typography variant="h6" gutterBottom>
        Hub Height
      </Typography>
      <Typography variant="body1" gutterBottom>
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
  );
}