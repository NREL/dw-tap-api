"use client";

import { AppBar, Box, Toolbar, Typography } from "@mui/material";

export default function Header() {
  return (
    <AppBar position="static" color="primary" enableColorOnDark>
      <Toolbar>
        <Typography variant="h6" sx={{ flexGrow: 1 }}>
          Wind Watts
        </Typography>
        <Box sx={{ opacity: 0.8, fontSize: 12 }}>NREL</Box>
      </Toolbar>
    </AppBar>
  );
}
