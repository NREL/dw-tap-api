import { useContext, useEffect, useMemo } from "react";
import { SettingsContext } from "../../providers/SettingsContext";
import { Box, Slider, Typography } from "@mui/material";
import { DataModel } from "../../types/Requests";
import { Heights } from "../../types/Heights";

const HUB_HEIGHTS: Record<DataModel | "default", Heights> = {
  era5: { values: [30, 40, 50, 60, 80, 100], interpolation: null },
  wtk: { values: [40, 60, 80, 100, 120, 140], interpolation: 10 },
  default: { values: [40, 60, 80, 100], interpolation: null },
};

export function HubHeightSettings() {
  const {
    hubHeight,
    setHubHeight,
    preferredModel: dataModel,
  } = useContext(SettingsContext);

  const { values: availableHeights, interpolation: step } = useMemo(() => {
    if (dataModel && HUB_HEIGHTS[dataModel]) {
      return HUB_HEIGHTS[dataModel];
    }
    return HUB_HEIGHTS.default;
  }, [dataModel]);

  // ensure slider compatibility with model switching and available heights changes
  useEffect(() => {
    if (!availableHeights.includes(hubHeight)) {
      // if current height not available, set to the closest available height
      const closestHeight = availableHeights.reduce((prev, curr) =>
        Math.abs(curr - hubHeight) < Math.abs(prev - hubHeight) ? curr : prev,
      );
      setHubHeight(closestHeight);
    }
  }, [availableHeights, hubHeight, setHubHeight]);

  const hubHeightMarks = availableHeights.map((value: number) => ({
    value: value,
    label: `${value}m`,
  }));

  const handleHubHeightChange = (
    _: Event,
    newHubHeight: number | number[] | null,
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
        step={step}
        marks={hubHeightMarks}
        min={Math.min(...availableHeights)}
        max={Math.max(...availableHeights)}
      />
    </Box>
  );
}
