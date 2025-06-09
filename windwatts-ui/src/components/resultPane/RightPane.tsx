import { Box, Typography, Paper, Grid2, Link } from "@mui/material";
import { styled } from "@mui/material/styles";
import AnalysisResults from "./AnalysisResults";
import { useContext } from "react";
import { SettingsContext } from "../../providers/SettingsContext";

const Item = styled(Paper)(({ theme }) => ({
  ...theme.typography.body2,
  padding: theme.spacing(1),
  textAlign: "center",
  color: theme.palette.text.secondary,
}));

const DATMODEL_INFO: Record<string, { label: string, href: string }> = {
    era5: {
    label: "ERA5 dataset",
    href: "https://cds.climate.copernicus.eu/datasets/reanalysis-era5-single-levels?tab=overview",
  },
  wtk: {
    label: "NREL's 20-year WTK-LED dataset",
    href: "https://www.energy.gov/eere/wind/articles/new-wind-resource-database-includes-updated-wind-toolkit",
  },
};

const RightPane = () => {

  const { currentPosition, hubHeight, powerCurve, preferredModel: dataModel } =
    useContext(SettingsContext);
  
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
      data: hubHeight ? `${hubHeight} meters` : "Not selected",
    },
    {
      title: "Power curve",
      data: powerCurve ? `${powerCurve}` : "Not selected",
    },
  ];

  const dataModelInfo = DATMODEL_INFO[dataModel] || DATMODEL_INFO.era5;

  return (
    <Box
      sx={{
        bgcolor: "background.paper",
        p: 2,
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
        <Typography variant="body1" marginBottom={2}>
          {/* Analysis presented below was performed using summary data from NREL&apos;s ERA5 dataset using the following options: */}
          Analysis presented below was performed using summary data from&nbsp;
          <Link
            href={dataModelInfo.href}
            underline="hover"
            target="_blank"
            rel="noopener noreferrer"
          >
            {dataModelInfo.label}
          </Link>
          &nbsp;using the following options:
        </Typography>
        <Grid2
          container
          direction="row"
          spacing={1}
          marginBottom={2}
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

        <AnalysisResults />

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

export default RightPane;
