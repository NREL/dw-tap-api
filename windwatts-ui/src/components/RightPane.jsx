import { Box, Typography, Link, Paper, Grid2 } from "@mui/material";
import { styled } from "@mui/material/styles";
import PropTypes from "prop-types";
import WindspeedCards from "./WindspeedCards";

const Item = styled(Paper)(({ theme }) => ({
  ...theme.typography.body2,
  padding: theme.spacing(1),
  textAlign: "center",
  color: theme.palette.text.secondary,
}));

const RightPane = ({ currentPosition, height, powerCurve }) => {
  const { lat, lng } = currentPosition ?? {};

  const settingOptions = [
    {
      title: "Location",
      data:
        currentPosition && lat && lng
          ? `${lat.toFixed(3)}, ${lng.toFixed(3)}`
          : "Not selected",
    },
    {
      title: "Hub height",
      data: height ? `${height} meters` : "Not selected",
    },
    {
      title: "Power curve",
      data: powerCurve ? `${powerCurve}` : "Not selected",
    },
  ];

  return (
    <Box
      sx={{
        bgcolor: "background.paper",
        p: 3,
        pt: 2,
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
        <Grid2
          container
          direction="row"
          spacing={1}
          sx={{
            justifyContent: "space-between",
            alignItems: "stretch",
          }}
        >
          {settingOptions.map((option, index) => (
            <Item key={"setting_option_" + index} sx={{ flexGrow: 1 }}>
              <Typography variant="h6" sx={{ fontSize: "1rem" }}>
                {option.title}
              </Typography>
              <Typography variant="body2" sx={{ fontSize: "1rem" }}>
                {option.data}
              </Typography>
            </Item>
          ))}
        </Grid2>

        <WindspeedCards
          lat={lat}
          lng={lng}
          height={height}
          powerCurve={powerCurve}
        />

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

RightPane.propTypes = {
  currentPosition: PropTypes.shape({
    lat: PropTypes.number,
    lng: PropTypes.number,
  }),
  height: PropTypes.number,
  powerCurve: PropTypes.number,
};

export default RightPane;
