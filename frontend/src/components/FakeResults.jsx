import useSWR from "swr";
import {
  Box,
  Typography,
  Link,
  ListItem,
  ListItemText,
  Grid2,
  Stack,
  Skeleton,
} from "@mui/material";
import PropTypes from "prop-types";
import ResultCard from "./ResultCard";
import { getWindResourceDataByCoordinates } from "../services/api";

const FakeResults = ({ currentPosition, hubHeight, powerCurve }) => {
  const { lat, lng } = currentPosition ?? {};
  const {
    isLoading,
    data: resultCardData,
    error,
  } = useSWR({ lat, lng }, getWindResourceDataByCoordinates); // cache key for this lat, lng; see https://swr.vercel.app/docs/arguments#passing-objects

  // console.log(
  //   "FakeResults: isLoading",
  //   isLoading,
  //   "resultCardData",
  //   resultCardData,
  //   "error",
  //   error
  // );

  const settingOptions = [
    {
      title: "Selected location (lat, lng)",
      data:
        currentPosition && lat && lng
          ? `${lat.toFixed(3)}, ${lng.toFixed(3)}`
          : "Not selected",
    },
    {
      title: "Selected hub height",
      data: hubHeight ? `${hubHeight} meters` : "Not selected",
    },
    {
      title: "Selected power curve",
      data: powerCurve ? `nrel-reference-${powerCurve}kW` : "Not selected",
    },
  ];

  return (
    <Box
      sx={{
        bgcolor: "background.paper",
        p: 3,
        pt: 6,
        "> *": {
          color: "text.primary",
        },
      }}
    >
      <Box
        sx={{
          display: "flex",
          flexDirection: "column",
        }}
      >
        <Typography variant="body1" marginBottom={3}>
          Analysis presented below was performed using summary data from&nbsp;
          <Link
            href="https://www.energy.gov/eere/wind/articles/new-wind-resource-database-includes-updated-wind-toolkit"
            underline="hover"
            target="_blank"
            rel="noopener noreferrer"
          >
            NREL&apos;s 20-year WTK-LED dataset
          </Link>
          &nbsp;using the following options:
        </Typography>
        <Stack container spacing={2}>
          {settingOptions.map((option, index) => (
            <Grid2 key={"setting_option_" + index}>
              <ListItem
                sx={{
                  borderRadius: 1,
                  boxShadow: 3,
                  minWidth: 200,
                }}
              >
                <ListItemText primary={option.title} secondary={option.data} />
              </ListItem>
            </Grid2>
          ))}
        </Stack>

        <Stack container spacing={2}>
          {error && (
            <Box>
              <Typography
                marginTop={2}
                variant="body1"
                color="error"
                gutterBottom
              >
                There was an error loading data: {error.message}
              </Typography>
            </Box>
          )}
          {isLoading ? (
            <Box>
              <Skeleton sx={{ marginTop: 5 }} variant="rounded" height={190} />
              <Skeleton sx={{ marginTop: 5 }} variant="rounded" height={190} />
              <Skeleton sx={{ marginTop: 5 }} variant="rounded" height={190} />
            </Box>
          ) : resultCardData ? (
            resultCardData.winddataexample.map((data, index) => (
              <Grid2 key={"result_card_" + index}>
                <ResultCard data={data} />
              </Grid2>
            ))
          ) : null}
        </Stack>
        <Typography variant="body2" color="textSecondary" marginTop={2}>
          Disclaimer: This summary represents a PRELIMINARY analysis. Research
          conducted at national laboratories suggests that multiple models
          should be used for more thorough analysis. Reach out to a qualified
          installer for a refined estimate.
        </Typography>
      </Box>
    </Box>
  );
};

FakeResults.propTypes = {
  openResults: PropTypes.bool.isRequired,
  handleClose: PropTypes.func.isRequired,
  currentPosition: PropTypes.shape({
    lat: PropTypes.number,
    lng: PropTypes.number,
  }),
  hubHeight: PropTypes.number,
  powerCurve: PropTypes.number,
};

export default FakeResults;
