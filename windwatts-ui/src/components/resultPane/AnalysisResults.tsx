import { Box, Stack, Divider } from "@mui/material";
import { ProductionCard } from "./ProductionCard";
import { BiasCorrectedTiles } from "./BiasCorrectedResultsCard";
import { useContext } from "react";
import { SettingsContext } from "../../providers/SettingsContext";
import { WindSpeedCard } from "./WindSpeedCard";
import { WindResourceCard } from "./WindResourceCard";

export const AnalysisResults = () => {
  const { biasCorrection } = useContext(SettingsContext);
  return (
    <Stack spacing={2}>
      {/* Top row: either Wind Speed + Resource, or Bias Corrected tiles */}
      {biasCorrection ? (
        <>
          <Divider
            textAlign="center"
            sx={{ my: 1, fontWeight: 600, color: "text.secondary" }}
          >
            Bias Corrected Results
          </Divider>
          <BiasCorrectedTiles />
        </>
      ) : (
        <Box sx={{ display: "flex", gap: 2 }}>
          <Box sx={{ flex: 1 }}>
            <WindSpeedCard />
          </Box>
          <Box sx={{ flex: 1 }}>
            <WindResourceCard />
          </Box>
        </Box>
      )}

      {/* Production card separate */}
      <ProductionCard />
    </Stack>
  );
};
