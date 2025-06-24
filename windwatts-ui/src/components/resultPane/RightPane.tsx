import { Box, Typography, Paper, Grid2, Link, Collapse, Chip } from "@mui/material";
import { styled } from "@mui/material/styles";
import InfoOutlinedIcon from "@mui/icons-material/InfoOutlined";
import AnalysisResults from "./AnalysisResults";
import { useContext, useState } from "react";
import { SettingsContext } from "../../providers/SettingsContext";
import { POWER_CURVE_LABEL } from "../../constants/powerCurves";

const Item = styled(Paper)(({ theme }) => ({
  ...theme.typography.body2,
  padding: theme.spacing(1),
  textAlign: "center",
  color: theme.palette.text.secondary,
}));

const DATA_MODEL_INFO: Record<string, { label: string, source_href: string, help_href: string }> = {
  era5: {
    label: "ERA5",
    source_href: "https://www.ecmwf.int/en/forecasts/dataset/ecmwf-reanalysis-v5",
    help_href: "https://github.com/NREL/dw-tap-api/blob/master/about/era5.md",
  },
  wtk: {
    label: "NREL's 20-year WTK-LED dataset",
    source_href: "https://www.energy.gov/eere/wind/articles/new-wind-resource-database-includes-updated-wind-toolkit",
    help_href: "",
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
      data: powerCurve ? `${POWER_CURVE_LABEL[powerCurve]}` : "Not selected",
    },
  ];

  const dataModelInfo = DATA_MODEL_INFO[dataModel] || DATA_MODEL_INFO.era5;

  const [showDisclaimer, setShowDisclaimer] = useState(false);

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
        <Typography variant="body1" marginBottom={2} sx={{ lineHeight: 1.7 }}>
          WindWatts is currently based on&nbsp;
          <Link
            href={ dataModelInfo.source_href }
            underline="hover"
            target="_blank"
            rel="noopener noreferrer"
            sx={{ fontWeight: 500 }}
          >
            { dataModelInfo.label.toUpperCase() } reanalysis dataset
          </Link>
          &nbsp;provided by ECMWF.
          <br />
          <Link
            href={ dataModelInfo.help_href }
            underline="hover"
            target="_blank"
            rel="noopener noreferrer"
            sx={{ fontSize: "0.95em", fontWeight: 400, display: "inline-flex", alignItems: "center" }}
          >
            Why { dataModelInfo.label.toUpperCase()}?
            <InfoOutlinedIcon fontSize="small" sx={{ ml: 0.5 }} />
          </Link>
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

        <Box sx={{ display: "flex", alignItems: "center", mt: 2 }}>
          <Chip
            label="Disclaimer"
            color="info"
            variant="outlined"
            sx={{ border: "none", fontSize: "0.95rem" }}
            onClick={() => setShowDisclaimer((v) => !v)}
            icon={<InfoOutlinedIcon sx={{ fontSize: "1.1rem" }} />}
          />
        </Box>
        <Collapse in={showDisclaimer}>
          <Typography variant="body2" color="textSecondary" marginBottom={2} px={1}>
            WindWatts offers quick, approximate wind resource estimates. For more detailed or location-specific data, consider reaching out to local wind installers who may share insights from nearby projects. To access alternative wind models, visit&nbsp;
            <Link
              href="https://wrdb.nrel.gov"
              target="_blank"
              rel="noopener noreferrer"
              underline="hover"
            >
              NREL's Wind Resource Database
            </Link>.
          </Typography>
        </Collapse>
      </Box>
    </Box>
  );
};

export default RightPane;
