import {
  Box,
  Modal,
  Typography,
  IconButton,
} from "@mui/material";
import { Close } from "@mui/icons-material";
import { UnitsSettings } from "./UnitsSettings";
import { useContext } from "react";
import { SettingsContext } from "../../providers/SettingsContext";
import { ModelSettings } from "./ModelSettings";
import { PowerCurveSettings } from "./PowerCurveSettings";
import { HubHeightSettings } from "./HubHeightSettings";

const Settings = () => {
  const {
    settingsOpen,
    toggleSettings,
  } = useContext(SettingsContext);

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
          width: 400,
          bgcolor: "background.paper",
          p: 4,
          maxHeight: "80vh",
          overflowY: "auto",
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

        <HubHeightSettings />

        <PowerCurveSettings />

        <UnitsSettings />

        <ModelSettings />
      </Box>
    </Modal>
  );
};

export default Settings;
