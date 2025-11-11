import { useState } from "react";
import { Button } from "@mui/material";
import DownloadIcon from "@mui/icons-material/Download";
import { DownloadDialog } from "./DownloadDialog";

export const DownloadButton = () => {
  const [isDialogOpen, setIsDialogOpen] = useState(false);

  return (
    <>
      <Button
        variant="contained"
        size="small"
        startIcon={<DownloadIcon />}
        onClick={() => setIsDialogOpen(true)}
        sx={{
          fontSize: "0.9em",
          textTransform: "none",
          borderRadius: 2,
          px: 2,
          py: 0.5,
          backgroundColor: "primary.main",
          "&:hover": {
            backgroundColor: "primary.dark",
          },
        }}
      >
        Download Hourly Data
      </Button>

      {isDialogOpen && (
        <DownloadDialog onClose={() => setIsDialogOpen(false)} />
      )}
    </>
  );
};