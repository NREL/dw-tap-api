import { useMediaQuery } from "@mui/material";
import { useTheme } from "@mui/material/styles";
import { MapViewDesktop } from "./desktop-view";
import { MapViewMobile } from "./mobile-view";

const MapView = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down("sm"));

  return isMobile ? <MapViewMobile /> : <MapViewDesktop />;
};

export default MapView;
