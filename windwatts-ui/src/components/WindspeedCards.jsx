import useSWR from "swr";
import ResultCard from "./ResultCard";
import { getWindspeedByLatLong } from "../services/api";
import { convertOutput, convertWindspeed, getWindResource } from "../utils";
import { Typography, Grid2, Stack, Skeleton } from "@mui/material";
import { useContext } from "react";
import { UnitsContext } from "../providers/UnitsContext";

export default function WindspeedCards({ lat, lng, height }) {
  const { units } = useContext(UnitsContext);
  const shouldFetch = lat && lng;

  const { isLoading, data, error } = useSWR(
    // use lat, lng, height as obj cache key; see https://swr.vercel.app/docs/arguments#passing-objects
    shouldFetch ? { lat, lng, height } : null,
    getWindspeedByLatLong
  );

  const dataCards = [
    {
      title: "Average Wind Speed",
      subheader: "Average wind speed at selected height",
      data: convertWindspeed(data?.avgWindspeed, units.windspeed),
      details: [data?.avgWindspeedDisclaimer],
    },
    {
      title: "Wind Resource",
      subheader: "Broad measure of how much wind is available",
      data: getWindResource(data?.avgWindspeed),
      details: [
        "Low refers to wind speeds below 3.00 m/s.",
        "Moderate refers to speeds between 3.00 m/s and 5.00 m/s.",
        "High refers to speeds above 5.00 m/s.",
      ],
    },
    {
      title: "Production",
      subheader: "Estimated annual production potential",
      data: convertOutput(data?.totalOutput, units.output),
      details: [data?.totalOutputDisclaimer],
    },
  ];

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
      ) : data ? (
        dataCards.map((data, index) => (
          <Grid2 key={"result_card_" + index}>
            <ResultCard data={data} isLoading={isLoading} />
          </Grid2>
        ))
      ) : null}
    </Stack>
  );
}
