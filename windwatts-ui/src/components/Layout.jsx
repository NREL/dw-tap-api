import { Footer } from "nrel-branding-react";
import { Outlet, Link as RouterLink } from "react-router-dom";
import { Link, Box, AppBar, Container, Toolbar } from "@mui/material";
import { useState } from "react";
import Settings from "./Settings";
import Results from "./Results";
import RightPane from "./RightPane";

function Layout() {
  // const API_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000/';
  const APP_TITLE = import.meta.env.VITE_APP_TITLE || "Wind Watts";

  // setting modal states
  const [openSettings, setOpenSettings] = useState(false);
  const handleOpenSettings = () => setOpenSettings(true);
  const handleCloseSettings = () => setOpenSettings(false);

  // Results modal states
  const [openResults, setOpenResults] = useState(false);
  const handleOpenResults = () => setOpenResults(true);
  const handleCloseResults = () => setOpenResults(false);

  // Settings modal states
  const [currentPosition, setCurrentPosition] = useState(null);
  const [hubHeight, setHubHeight] = useState(30);
  const [powerCurve, setPowerCurve] = useState(100);

  return (
    <Box sx={{ display: "flex", flexDirection: "column", height: "100vh" }}>
      <Box sx={{ flexGrow: 0 }}>
        <AppBar position="static" sx={{ bgcolor: "#0279c2" }}>
          <Container maxWidth="lg">
            <Toolbar
              disableGutters
              sx={{ display: "flex", justifyContent: "space-between" }}
            >
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
          </Container>
        </AppBar>
      </Box>

      <Box
        sx={{
          display: "flex",
          flexGrow: 1, // Occupy remaining height between header and footer
          overflow: "hidden", // Prevent scrollbars
        }}
      >
        {/* Left Pane: Map */}
        <Box
          sx={{
            position: "relative", // Ensures absolute elements (like a map) fit
            flexGrow: 1, // Allow this Box to grow and fill available space
            display: "flex", // Optional: Use flex for internal alignment if needed
            flexDirection: "column", // Optional: Set direction for child elements
            overflow: "hidden", // Prevent overflow issues
          }}
        >
          <Outlet
            context={{
              handleOpenSettings,
              handleOpenResults,
              currentPosition,
              setCurrentPosition,
            }}
          />
        </Box>

        {/* Right Pane: Scrolling Content */}
        <Box
          className="right-pane"
          sx={{
            width: 420, // Fixed width for the right pane
            bgcolor: "white",
            overflowY: "auto", // Enable vertical scrolling for content
            borderLeft: "1px solid #ddd", // Optional: add a divider
          }}
        >
          {/* Example Content */}
          <Box>
            <RightPane
              openResults={openResults}
              handleClose={handleCloseResults}
              currentPosition={currentPosition}
              hubHeight={hubHeight}
              powerCurve={powerCurve}
            />
          </Box>
          <Footer />
        </Box>
      </Box>
      <Settings
        openSettings={openSettings}
        handleClose={handleCloseSettings}
        hubHeight={hubHeight}
        setHubHeight={setHubHeight}
        powerCurve={powerCurve}
        setPowerCurve={setPowerCurve}
      />
      <Results
        openResults={openResults}
        handleClose={handleCloseResults}
        currentPosition={currentPosition}
        hubHeight={hubHeight}
        powerCurve={powerCurve}
      />
    </Box>
  );
}

export default Layout;
