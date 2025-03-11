import useSWR from "swr";
import ResultCard from "./ResultCard";
import { getWindspeedByLatLong, getEnergyProduction } from "../services/api";
import { convertOutput, convertWindspeed, getWindResource } from "../utils";
import { Typography, Grid2, Stack, Skeleton } from "@mui/material";
import { useContext } from "react";
import { UnitsContext } from "../providers/UnitsContext";

export default function WindspeedCards({ lat, lng, height, powerCurve }) {
  const { units } = useContext(UnitsContext);
  const shouldFetch = lat && lng;

  const { isLoading: isLoadingWindspeed, data: windspeedData, error: windspeedError } = useSWR(
    // use lat, lng, height as obj cache key; see https://swr.vercel.app/docs/arguments#passing-objects
    shouldFetch ? { lat, lng, height } : null,
    getWindspeedByLatLong
  );

  const { isLoading: isLoadingEnergy, data: energyData, error: energyError } = useSWR(
    shouldFetch ? { lat, lng, height, powerCurve } : null,
    getEnergyProduction
  );

  const dataCards = [
    {
      title: "Average Wind Speed",
      subheader: "Average wind speed at selected height",
      data: convertWindspeed(windspeedData?.global_avg, units.windspeed),
      details: [
        "Average wind speed estimated using WTK dataset",
        `Wind speed data is taken from a nearby location at lat: and lng: at a height of ${height} meters`,
        "Average wind speed is calculated over a 20-year period",
      ],
    },
    {
      title: "Wind Resource",
      subheader: "Broad measure of how much wind is available",
      data: getWindResource(windspeedData?.global_avg),
      details: [
        "Low refers to wind speeds below 3.00 m/s.",
        "Moderate refers to speeds between 3.00 m/s and 5.00 m/s.",
        "High refers to speeds above 5.00 m/s.",
      ],
    },
    {
      title: "Production",
      subheader: "Estimated annual production potential",
      data: convertOutput(energyData?.energy_production, units.output),
      details: [energyData?.totalOutputDisclaimer],
    },
  ];

  const isLoading = isLoadingWindspeed || isLoadingEnergy;
  const error = windspeedError || energyError;

  return (
    <Stack spacing={2} sx={{ marginTop: 4 }}>
      {error && (
        <Grid2>
          <Typography marginTop={2} variant="body1" color="error" gutterBottom>
            There was an error loading data: {error.message}
          </Typography>
        </Grid2>
      )}
      {isLoading ? (
        <Grid2>
          <Skeleton variant="rounded" animation="wave" height={192.5} />
          <Skeleton
            sx={{ marginTop: 2 }}
            variant="rounded"
            animation="wave"
            height={192.5}
          />
          <Skeleton
            sx={{ marginTop: 2 }}
            variant="rounded"
            animation="wave"
            height={192.5}
          />
        </Grid2>
      ) : windspeedData && energyData ? (
        dataCards.map((data, index) => (
          <Grid2 key={"result_card_" + index}>
            <ResultCard data={data} isLoading={isLoading} />
          </Grid2>
        ))
      ) : null}
    </Stack>
  );
}
