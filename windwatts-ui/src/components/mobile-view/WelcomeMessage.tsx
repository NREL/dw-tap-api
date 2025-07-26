import { Box } from "@mui/material";

function WelcomeMessage() {
  return (
    <Box sx={{ textAlign: "center", py: 4, color: "#666" }}>
      <Box sx={{ fontSize: "200px", mb: -4 }}>💨</Box>
      <Box sx={{ fontSize: "24px", mb: 1, fontWeight: "bold" }}>
        Welcome to Wind Watts
      </Box>
      <Box sx={{ fontSize: "18px" }}>
        Search for a location above to see wind data and energy analysis
      </Box>
    </Box>
  );
}

export default WelcomeMessage;
