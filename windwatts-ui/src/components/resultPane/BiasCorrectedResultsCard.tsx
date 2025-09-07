import { memo, useContext } from "react";
import { Box, Paper, Typography } from "@mui/material";
import { UnitsContext } from "../../providers/UnitsContext";
import { SettingsContext } from "../../providers/SettingsContext";
import { useWindData, useProductionData } from "../../hooks";
import { convertWindspeed, convertOutput, getWindResource } from "../../utils";

// Compact, card-less variant for embedding in the top row
export const BiasCorrectedTiles = memo(() => {
  const { units } = useContext(UnitsContext);
  const { biasCorrection } = useContext(SettingsContext);

  const {
    windData,
    isLoading: windLoading,
    error: windError,
    hasData: hasWind,
  } = useWindData();

  const {
    productionData,
    isLoading: prodLoading,
    error: prodError,
    hasData: hasProd,
  } = useProductionData();

  if (!biasCorrection) return null;

  const loading = windLoading || prodLoading;
  const error = windError || prodError;
  const hasData = hasWind && hasProd;
  const windResource = getWindResource(windData?.global_avg ?? 0);

  const getWindResourceInfo = (resource: string) => {
    const resourceLower = resource.toLowerCase();
    if (resourceLower.includes("high")) {
      return {
        bgColor: "success.light",
        textColor: "success.contrastText",
      };
    } else if (resourceLower.includes("moderate")) {
      return {
        bgColor: "info.light",
        textColor: "info.contrastText",
      };
    }
    return {
      bgColor: "warning.light",
      textColor: "warning.contrastText",
    };
  };
  const windInfo = getWindResourceInfo(windResource);

  if (loading) {
    return (
      <Box
        sx={{
          display: "grid",
          gridTemplateColumns: { xs: "1fr", sm: "repeat(3, 1fr)" },
          gap: 2,
        }}
      >
        <Paper sx={{ p: 2 }} elevation={2}>
          <Typography variant="body2" color="text.secondary">
            Loading…
          </Typography>
        </Paper>
      </Box>
    );
  }

  if (error || !hasData) {
    return null;
  }

  return (
    <Box
      sx={{
        display: "grid",
        gridTemplateColumns: { xs: "1fr", sm: "repeat(3, 1fr)" },
        gap: 2,
        alignItems: "stretch",
      }}
    >
      {/* Wind Speed */}
      <Paper sx={{ p: 2, textAlign: "center" }} elevation={2}>
        <Typography variant="subtitle2" color="text.secondary">
          Wind Speed
        </Typography>
        <Typography variant="h6" sx={{ fontWeight: 700 }}>
          {convertWindspeed(windData.global_avg, units.windspeed)}
        </Typography>
      </Paper>

      {/* Wind Resource */}
      <Paper
        sx={{
          p: 2,
          textAlign: "center",
          bgcolor: windInfo.bgColor,
          color: windInfo.textColor,
        }}
        elevation={2}
      >
        <Typography variant="subtitle2" sx={{ opacity: 0.9 }}>
          Wind Resource
        </Typography>
        <Typography variant="h6" sx={{ fontWeight: 700 }}>
          {windResource}
        </Typography>
      </Paper>

      {/* Production */}
      <Paper
        sx={{
          p: 2,
          textAlign: "center",
          bgcolor: "primary.light",
          color: "primary.contrastText",
        }}
        elevation={2}
      >
        <Typography variant="subtitle2" sx={{ opacity: 0.9 }}>
          Production
        </Typography>
        <Typography variant="h6" sx={{ fontWeight: 700 }}>
          {convertOutput(
            Number(
              productionData?.summary_avg_energy_production?.["Average year"]?.[
                "kWh produced"
              ] || 0
            ),
            units.output
          ).replace(/\s\w+$/, "")}
        </Typography>
        <Typography variant="caption">{units.output}</Typography>
      </Paper>
    </Box>
  );
});
