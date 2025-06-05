import { Box, Stack } from "@mui/material";
import ProductionCard from "./ProductionCard";
import WindSpeedCard from "./WindSpeedCard";
import WindResourceCard from "./WindResourceCard";

const AnalysisResults = () => {
  return (
    <Stack spacing={2}>
      {/* Wind Speed and Wind Resource side-by-side */}
      <Box sx={{ display: 'flex', gap: 2 }}>
        <Box sx={{ flex: 1 }}>
          <WindSpeedCard />
        </Box>
        <Box sx={{ flex: 1 }}>
          <WindResourceCard />
        </Box>
      </Box>
      
      {/* Production card separate */}
      <ProductionCard />
    </Stack>
  );
};

export default AnalysisResults; 