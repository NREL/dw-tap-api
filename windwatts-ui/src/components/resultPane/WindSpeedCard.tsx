import { useContext, memo } from "react";
import { Paper, Typography, Skeleton } from "@mui/material";
import { UnitsContext } from "../../providers/UnitsContext";
import { convertWindspeed, getOutOfBoundsMessage } from "../../utils";
import { useWindData } from "../../hooks";
import OutOfBoundsWarning from "../shared/OutOfBoundsWarning";

const WindSpeedCard = memo(() => {
  const { units } = useContext(UnitsContext);
  const {
    windData,
    isLoading,
    error,
    hasData,
    outOfBounds,
    dataModel,
    lat,
    lng,
  } = useWindData();

  const title = "Average Wind Speed";
  const subheader = "Average wind speed at selected height";

  if (outOfBounds) {
    return (
      <Paper
        sx={{
          p: 2,
          minHeight: 100,
          bgcolor: "warning.light",
        }}
      >
        <OutOfBoundsWarning
          message={getOutOfBoundsMessage(lat, lng, dataModel)}
        />
      </Paper>
    );
  }

  if (error) {
    return (
      <Paper
        sx={{
          p: 2,
          minHeight: 100,
          display: "flex",
          flexDirection: "column",
          justifyContent: "center",
          bgcolor: "error.light",
          color: "error.contrastText",
        }}
      >
        <Typography variant="subtitle2" gutterBottom>
          {title}
        </Typography>
        <Typography variant="body2">Error loading data</Typography>
      </Paper>
    );
  }

  if (isLoading) {
    return (
      <Paper
        sx={{
          p: 2,
          minHeight: 100,
          display: "flex",
          flexDirection: "column",
          justifyContent: "center",
        }}
      >
        <Typography variant="subtitle2" color="text.secondary" gutterBottom>
          {title}
        </Typography>
        <Skeleton variant="text" width="60%" height={40} />
        <Skeleton variant="text" width="40%" height={20} />
      </Paper>
    );
  }

  if (!hasData) {
    return (
      <Paper
        sx={{
          p: 2,
          minHeight: 100,
          display: "flex",
          flexDirection: "column",
          justifyContent: "center",
          bgcolor: "grey.100",
        }}
      >
        <Typography variant="subtitle2" color="text.secondary" gutterBottom>
          {title}
        </Typography>
        <Typography variant="body2" color="text.secondary">
          No data available
        </Typography>
      </Paper>
    );
  }

  const windSpeedData = convertWindspeed(windData.global_avg, units.windspeed);

  return (
    <Paper
      sx={{
        p: 2,
        minHeight: 100,
        display: "flex",
        flexDirection: "column",
        justifyContent: "center",
      }}
    >
      <Typography variant="subtitle2" color="text.secondary" gutterBottom>
        {title}
      </Typography>
      <Typography variant="h5" color="primary" sx={{ fontWeight: "bold" }}>
        {windSpeedData}
      </Typography>
      <Typography variant="caption" color="text.secondary">
        {subheader}
      </Typography>
    </Paper>
  );
});

export default WindSpeedCard;
