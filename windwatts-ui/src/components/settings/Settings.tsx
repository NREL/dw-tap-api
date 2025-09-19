import {
  Box,
  Modal,
  Typography,
  IconButton,
  Divider,
  Paper,
  FormControlLabel,
  Switch,
} from "@mui/material";
import { Close } from "@mui/icons-material";
import { UnitsSettings } from "./UnitsSettings";
import { useContext, useState } from "react";
import { SettingsContext } from "../../providers/SettingsContext";
// import { ModelSettings } from "./ModelSettings";
import { PowerCurveSettings } from "./PowerCurveSettings";
import { LossAssumptionSettings } from "./LossAssumptionSettings";
import { HubHeightSettings } from "./HubHeightSettings";
import {
  SETTINGS_MODAL_WIDTH,
  SETTINGS_MODAL_MAX_HEIGHT,
} from "../../constants";

export const Settings = () => {
  const { settingsOpen, toggleSettings, ensemble, setEnsemble } =
    useContext(SettingsContext);
  const [hasScrolled, setHasScrolled] = useState(false);

  const handleScroll = (e: React.UIEvent<HTMLDivElement>) => {
    setHasScrolled(e.currentTarget.scrollTop > 0);
  };

  return (
    <Modal
      open={settingsOpen}
      onClose={toggleSettings}
      aria-labelledby="settings-modal-title"
      aria-describedby="settings-modal-description"
      sx={{ color: "black" }}
    >
      <Box
        sx={{
          position: "absolute",
          top: "50%",
          left: "50%",
          transform: "translate(-50%, -50%)",
          width: SETTINGS_MODAL_WIDTH,
          bgcolor: "background.paper",
          maxHeight: SETTINGS_MODAL_MAX_HEIGHT,
          display: "flex",
          flexDirection: "column",
          borderRadius: 2,
          overflow: "hidden",
        }}
      >
        {/* Sticky Header */}
        <Box
          sx={{
            position: "sticky",
            top: 0,
            bgcolor: "background.paper",
            p: 3,
            pb: 2,
            borderBottom: hasScrolled
              ? "1px solid rgba(0,0,0,0.12)"
              : "1px solid transparent",
            boxShadow: hasScrolled ? "0 2px 8px rgba(0,0,0,0.1)" : "none",
            transition: "all 0.2s ease",
            zIndex: 1,
          }}
        >
          <IconButton
            aria-label="close"
            onClick={toggleSettings}
            sx={{
              position: "absolute",
              right: 8,
              top: 8,
            }}
          >
            <Close />
          </IconButton>
          <Typography id="settings-modal-title" variant="h5" component="h2">
            Settings
          </Typography>
        </Box>

        {/* Scrollable Content */}
        <Box
          sx={{
            flex: 1,
            overflowY: "auto",
            p: 3,
            pt: 1,
          }}
          onScroll={handleScroll}
        >
          <HubHeightSettings />
          <PowerCurveSettings />
          <LossAssumptionSettings />
          <UnitsSettings />
          {/* <ModelSettings /> */}

          <Divider sx={{ my: 2 }} />
          <Typography variant="subtitle1" gutterBottom>
            Experimental
          </Typography>
          <Paper sx={{ p: 2 }} variant="outlined">
            <FormControlLabel
              control={
                <Switch
                  checked={!!ensemble}
                  onChange={(e) => setEnsemble(e.target.checked)}
                />
              }
              label="Enable ensemble model"
            />
          </Paper>
        </Box>
      </Box>
    </Modal>
  );
};
