import { Backdrop, CircularProgress } from "@mui/material";

export function LoadingBackdrop() {
  return (
    <Backdrop
      open={true}
      sx={(theme) => ({ color: "#fff", zIndex: theme.zIndex.drawer + 1 })}
    >
      <CircularProgress color="inherit" />
    </Backdrop>
  );
}
