import { useContext, memo } from "react";
import { Typography } from "@mui/material";
import { UnitsContext } from "../../providers/UnitsContext";
import { convertWindspeed, getOutOfBoundsMessage } from "../../utils";
import { useWindData } from "../../hooks";
import {
  OutOfBoundsCard,
  ErrorCard,
  LoadingCard,
  EmptyCard,
  DataCard,
} from "../shared/CardStates";

export const WindSpeedCard = memo(() => {
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
      <OutOfBoundsCard message={getOutOfBoundsMessage(lat, lng, dataModel)} />
    );
  }

  if (error) {
    return <ErrorCard title={title} />;
  }

  if (isLoading) {
    return <LoadingCard title={title} />;
  }

  if (!hasData) {
    return <EmptyCard title={title} />;
  }

  const windSpeedData = convertWindspeed(windData.global_avg, units.windspeed);

  return (
    <DataCard title={title}>
      <Typography variant="h5" color="primary" sx={{ fontWeight: "bold" }}>
        {windSpeedData}
      </Typography>
      <Typography variant="caption" color="text.secondary">
        {subheader}
      </Typography>
    </DataCard>
  );
});
