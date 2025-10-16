import { Box, Stack, Divider, Typography } from "@mui/material";
import { ProductionCard } from "./ProductionCard";
import { EnsembleTiles } from "./EnsembleResultsCard";
import { useContext } from "react";
import { SettingsContext } from "../../providers/SettingsContext";
import { WindSpeedCard } from "./WindSpeedCard";
import { WindResourceCard } from "./WindResourceCard";
import { DataSourceLinks } from "./DataSourceLinks";

export const AnalysisResults = () => {
  const { ensemble, preferredModel } = useContext(SettingsContext);
  return (
    <Stack spacing={2}>
      {/* Top row: either Wind Speed + Resource, or Ensemble Model tiles */}
      {ensemble ? (
        <>
          <Divider
            textAlign="center"
            sx={{ my: 1, fontWeight: 600, color: "text.secondary" }}
          >
            Ensemble Model Results *
          </Divider>
          <EnsembleTiles />
          <Typography variant="body2" color="text.secondary">
            * Experimental model (under development)
          </Typography>
        </>
      ) : (
        <>
          <Box sx={{ display: "flex", gap: 2 }}>
            <Box sx={{ flex: 1 }}>
              <WindSpeedCard />
            </Box>
            <Box sx={{ flex: 1 }}>
              <WindResourceCard />
            </Box>
          </Box>
          <DataSourceLinks preferredModel={preferredModel} />
        </>
      )}

      {/* Production card separate */}
      <ProductionCard />
    </Stack>
  );
};
