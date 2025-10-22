import {
  Box,
  Typography,
  Paper,
  Grid,
  Collapse,
  Chip,
  Button,
  Divider,
  Link,
} from "@mui/material";
import { styled } from "@mui/material/styles";
import InfoOutlinedIcon from "@mui/icons-material/InfoOutlined";
import SettingsIcon from "@mui/icons-material/Settings";
import DownloadIcon from "@mui/icons-material/Download";
import { AnalysisResults } from "./AnalysisResults";
import { useContext, useState } from "react";
import { SettingsContext } from "../../providers/SettingsContext";
import { POWER_CURVE_LABEL } from "../../constants";
import { ShareButton } from "../shared";
import { useDownload } from "../../hooks/useDownload";
import { DownloadDialog } from "./DownloadDialog";

const Item = styled(Paper)(({ theme }) => ({
  ...theme.typography.body2,
  padding: theme.spacing(1),
  textAlign: "center",
  color: theme.palette.text.secondary,
}));

export const RightPane = () => {
  const {
    currentPosition,
    hubHeight,
    powerCurve,
    preferredModel,
    toggleSettings,
  } = useContext(SettingsContext);

  const { lat, lng } = currentPosition ?? {};
  const [showDisclaimer, setShowDisclaimer] = useState(false);

  const {
    isDownloading,
    showDownloadDialog,
    nearestGridLocation,
    handleDownloadClick,
    handleDownloadConfirm,
    handleDownloadCancel,
  } = useDownload();

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

  const canDownload = currentPosition && lat && lng && hubHeight;
  
  const downloadDataModel = preferredModel;

  const onDownloadClick = () => {
    if (!canDownload || !lat || !lng) return;
    
    handleDownloadClick({
      lat: lat,
      lng: lng,
      dataModel: downloadDataModel,
    });
  };

  const onDownloadConfirm = () => {
    if (!canDownload) return;
    
    handleDownloadConfirm({
      lat: lat!,
      lng: lng!,
      dataModel: downloadDataModel,
    });
  };

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
        <Divider
          textAlign="center"
          sx={{ my: 2, fontWeight: 600, color: "text.secondary" }}
        >
          Summary Results Based on
        </Divider>
        <Grid
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
        </Grid>

        <Box
          sx={{
            display: "flex",
            gap: 1,
            justifyContent: "flex-end",
            marginBottom: 2,
          }}
        >
          <ShareButton size="small" variant="outlined" />
          <Button
            variant="outlined"
            size="small"
            startIcon={<SettingsIcon />}
            onClick={toggleSettings}
            sx={{
              fontSize: "0.9em",
              textTransform: "none",
              borderRadius: 2,
              px: 2,
              py: 0.5,
              borderColor: "primary.main",
              color: "primary.main",
              "&:hover": {
                backgroundColor: "primary.main",
                color: "white",
                borderColor: "primary.main",
              },
            }}
          >
            Edit settings
          </Button>
        </Box>

        <AnalysisResults />

        {canDownload && (
          <Box sx={{ display: "flex", justifyContent: "flex-end", mt: 2, mb: 2 }}>
            <Button
              variant="contained"
              size="small"
              startIcon={<DownloadIcon />}
              onClick={onDownloadClick}
              disabled={isDownloading}
              sx={{
                fontSize: "0.9em",
                textTransform: "none",
                borderRadius: 2,
                px: 2,
                py: 0.5,
                backgroundColor: "primary.main",
                "&:hover": {
                  backgroundColor: "primary.dark",
                },
              }}
            >
              {isDownloading ? 'Downloading...' : 'Download Example Hourly Data'}
            </Button>
          </Box>
        )}

        <DownloadDialog
          open={showDownloadDialog}
          onClose={handleDownloadCancel}
          onConfirm={onDownloadConfirm}
          isDownloading={isDownloading}
          lat={lat}
          lng={lng}
          nearestGridLocation={nearestGridLocation}
          dataModel={downloadDataModel}
        />
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
          <Typography
            variant="body2"
            color="textSecondary"
            marginBottom={2}
            px={1}
          >
            WindWatts offers quick, approximate wind resource estimates. For
            more detailed or location-specific data, consider reaching out to
            local wind installers who may share insights from nearby projects.
            To access alternative wind models, visit&nbsp;
            <Link
              href="https://wrdb.nrel.gov"
              target="_blank"
              rel="noopener noreferrer"
              underline="hover"
            >
              NREL's Wind Resource Database
            </Link>
            .
          </Typography>
        </Collapse>
      </Box>
    </Box>
  );
};
