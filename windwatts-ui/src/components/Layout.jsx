import { Footer } from "nrel-branding-react";
import { Outlet, Link as RouterLink } from "react-router-dom";
import { Link, Box, AppBar, Toolbar } from "@mui/material";
import Settings from "./settings";
import RightPane from "./RightPane";
import useMainLayoutLogic from "../hooks/useMainLayoutLogic";

function Layout() {
  const APP_TITLE = import.meta.env.VITE_APP_TITLE || "Wind Watts";

  const {
    settingsOpen,
    currentPosition,
    hubHeight,
    powerCurve,
    toggleResultsOpen,
    toggleSettingsOpen,
    handleUnitsChange,
    setCurrentPosition,
    setHubHeight,
    setPowerCurve,
  } = useMainLayoutLogic();

  return (
    <Box sx={{ display: "flex", flexDirection: "column", height: "100vh" }}>
      <Box sx={{ flexGrow: 0 }}>
        <AppBar position="static" sx={{ bgcolor: "#0279c2" }}>
          <Toolbar sx={{ display: "flex", justifyContent: "space-between" }}>
            <Link
              to="/"
              variant="h5"
              component={RouterLink}
              underline="none"
              sx={{ flexGrow: 1, color: "white" }}
            >
              {APP_TITLE}
            </Link>
            <Box
              component="img"
              sx={{ height: 40 }}
              src="https://windwatts.nrel.gov/static/NREL-logo-reversed.png"
              alt="NREL Logo"
            />
          </Toolbar>
        </AppBar>
      </Box>

      <Box
        sx={{
          display: "flex",
          flexGrow: 1,
          overflow: "hidden",
        }}
      >
        <Box
          sx={{
            position: "relative",
            flexGrow: 1,
            display: "flex",
            flexDirection: "column",
            overflow: "hidden",
          }}
        >
          <Outlet
            context={{
              toggleResultsOpen,
              toggleSettingsOpen,
              currentPosition,
              setCurrentPosition,
            }}
          />
        </Box>

        <Box
          className="right-pane"
          sx={{
            width: 420,
            bgcolor: "white",
            overflowY: "auto",
            borderLeft: "1px solid #ddd",
          }}
        >
          <Box>
            <RightPane
              currentPosition={currentPosition}
              height={hubHeight}
              powerCurve={powerCurve}
            />
          </Box>
          <Footer />
        </Box>
      </Box>
      <Settings
        setUnits={handleUnitsChange}
        settingsOpen={settingsOpen}
        toggleSettings={toggleSettingsOpen}
        hubHeight={hubHeight}
        setHubHeight={setHubHeight}
        powerCurve={powerCurve}
        setPowerCurve={setPowerCurve}
      />
    </Box>
  );
}

export default Layout;
