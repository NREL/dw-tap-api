import { useMediaQuery } from "@mui/material";
import { useTheme } from "@mui/material/styles";
import { LayoutDesktop } from "./desktop-view";
import { LayoutMobile } from "./mobile-view";

const Layout = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down("sm"));

  return isMobile ? <LayoutMobile /> : <LayoutDesktop />;
};

export default Layout;
