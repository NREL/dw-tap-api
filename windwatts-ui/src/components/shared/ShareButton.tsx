import { useState } from "react";
import { Button, Snackbar, Alert } from "@mui/material";
import ShareIcon from "@mui/icons-material/Share";
import {
  SNACKBAR_DURATION_SUCCESS,
  SNACKBAR_DURATION_ERROR,
} from "../../constants";

interface ShareButtonProps {
  variant?: "text" | "outlined" | "contained";
  size?: "small" | "medium" | "large";
  fullWidth?: boolean;
}

export function ShareButton({
  variant = "outlined",
  size = "small",
  fullWidth = false,
}: ShareButtonProps) {
  const [showSuccess, setShowSuccess] = useState(false);
  const [showError, setShowError] = useState(false);

  const handleShare = async () => {
    try {
      await navigator.clipboard.writeText(window.location.href);
      setShowSuccess(true);
    } catch (error) {
      console.error("Failed to copy URL to clipboard:", error);
      setShowError(true);
    }
  };

  return (
    <>
      <Button
        variant={variant}
        size={size}
        fullWidth={fullWidth}
        startIcon={<ShareIcon />}
        onClick={handleShare}
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
        Share Link
      </Button>

      <Snackbar
        open={showSuccess}
        autoHideDuration={SNACKBAR_DURATION_SUCCESS}
        onClose={() => setShowSuccess(false)}
        anchorOrigin={{ vertical: "bottom", horizontal: "center" }}
      >
        <Alert
          onClose={() => setShowSuccess(false)}
          severity="success"
          variant="filled"
          sx={{ width: "100%" }}
        >
          Link copied to clipboard!
        </Alert>
      </Snackbar>

      <Snackbar
        open={showError}
        autoHideDuration={SNACKBAR_DURATION_ERROR}
        onClose={() => setShowError(false)}
        anchorOrigin={{ vertical: "bottom", horizontal: "center" }}
      >
        <Alert
          onClose={() => setShowError(false)}
          severity="error"
          variant="filled"
          sx={{ width: "100%" }}
        >
          Failed to copy link. Please copy from the address bar.
        </Alert>
      </Snackbar>
    </>
  );
}
