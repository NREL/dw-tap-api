import { useState, memo } from "react";
import {
  Paper,
  Typography,
  Box,
  Tooltip,
  IconButton,
  Button,
  Collapse,
  Skeleton,
} from "@mui/material";
import { InfoOutlined } from "@mui/icons-material";
import { getWindResource, getOutOfBoundsMessage } from "../../utils";
import { useWindData } from "../../hooks";
import OutOfBoundsWarning from "../shared/OutOfBoundsWarning";

const WindResourceCard = memo(() => {
  const [expanded, setExpanded] = useState(false);
  const {
    windData,
    isLoading,
    error,
    hasData,
    outOfBounds,
    dataModel,
    lat,
    lng,
  } = useWindData();

  const title = "Wind Resource";
  const subheader = "Broad measure of how much wind is available";
  const details: string[] = [
    // Add any wind resource details here if needed in the future
  ];

  if (outOfBounds) {
    return (
      <Paper
        sx={{
          p: 2,
          minHeight: 100,
          display: "flex",
          justifyContent: "center",
          bgcolor: "warning.light",
        }}
      >
        <OutOfBoundsWarning
          message={getOutOfBoundsMessage(lat, lng, dataModel)}
        />
      </Paper>
    );
  }

  // Helper function for wind resource colors and tooltips
  const getWindResourceInfo = (resource: string) => {
    const resourceLower = resource.toLowerCase();
    if (resourceLower.includes("high")) {
      return {
        color: "success",
        bgColor: "success.light",
        textColor: "success.contrastText",
        tooltip:
          "High wind resource refers to speeds above 5.00 m/s (11.2 mph) - excellent for wind energy generation",
      };
    } else if (resourceLower.includes("moderate")) {
      return {
        color: "info",
        bgColor: "info.light",
        textColor: "info.contrastText",
        tooltip:
          "Moderate wind resource refers to speeds between 3.00 m/s (6.7 mph) and 5.00 m/s (11.2 mph) - good for wind energy generation",
      };
    } else {
      return {
        color: "warning",
        bgColor: "warning.light",
        textColor: "warning.contrastText",
        tooltip:
          "Low wind resource refers to speeds below 3.00 m/s (6.7 mph) - limited wind energy potential",
      };
    }
  };

  const handleExpandClick = () => {
    setExpanded(!expanded);
  };

  if (error) {
    return (
      <Paper
        sx={{
          p: 2,
          minHeight: 100,
          display: "flex",
          flexDirection: "column",
          justifyContent: "center",
          bgcolor: "error.light",
          color: "error.contrastText",
        }}
      >
        <Typography variant="subtitle2" gutterBottom>
          {title}
        </Typography>
        <Typography variant="body2">Error loading data</Typography>
      </Paper>
    );
  }

  if (isLoading) {
    return (
      <Paper
        sx={{
          p: 2,
          minHeight: 100,
          display: "flex",
          flexDirection: "column",
          justifyContent: "center",
        }}
      >
        <Typography variant="subtitle2" color="text.secondary" gutterBottom>
          {title}
        </Typography>
        <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
          <Skeleton variant="text" width="60%" height={40} />
          <Skeleton variant="circular" width={24} height={24} />
        </Box>
        <Skeleton variant="text" width="40%" height={20} />
      </Paper>
    );
  }

  if (!hasData) {
    return (
      <Paper
        sx={{
          p: 2,
          minHeight: 100,
          display: "flex",
          flexDirection: "column",
          justifyContent: "center",
          bgcolor: "grey.100",
        }}
      >
        <Typography variant="subtitle2" color="text.secondary" gutterBottom>
          {title}
        </Typography>
        <Typography variant="body2" color="text.secondary">
          No data available
        </Typography>
      </Paper>
    );
  }

  const windResourceData = getWindResource(windData.global_avg);
  const windInfo = getWindResourceInfo(windResourceData);

  return (
    <Paper
      sx={{
        p: 2,
        minHeight: 100,
        display: "flex",
        flexDirection: "column",
        justifyContent: "center",
        bgcolor: windInfo.bgColor,
        color: windInfo.textColor,
      }}
    >
      <Typography variant="subtitle2" sx={{ opacity: 0.9 }} gutterBottom>
        {title}
      </Typography>
      <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
        <Typography variant="h5" sx={{ fontWeight: "bold" }}>
          {windResourceData}
        </Typography>
        <Tooltip title={windInfo.tooltip} arrow>
          <IconButton
            size="small"
            sx={{
              color: windInfo.textColor,
              opacity: 0.8,
              "&:hover": {
                opacity: 1,
                bgcolor: "rgba(255,255,255,0.1)",
              },
            }}
          >
            <InfoOutlined fontSize="small" />
          </IconButton>
        </Tooltip>
      </Box>
      <Typography variant="caption" sx={{ opacity: 0.8 }}>
        {subheader}
      </Typography>

      {details.length > 0 && (
        <>
          <Button
            onClick={handleExpandClick}
            aria-expanded={expanded}
            aria-label="show more"
            size="small"
            sx={{
              mt: 1,
              alignSelf: "flex-start",
              color: windInfo.textColor,
              "&:hover": {
                bgcolor: "rgba(255,255,255,0.1)",
              },
            }}
          >
            {expanded ? "Hide Details" : "Show Details"}
          </Button>
          <Collapse in={expanded} timeout="auto" unmountOnExit>
            <Box sx={{ mt: 2 }}>
              {details.map((detail, index) => (
                <Typography
                  mb={1}
                  key={title + "result_detail" + index}
                  variant="body2"
                  sx={{ opacity: 0.9 }}
                >
                  {detail}
                </Typography>
              ))}
            </Box>
          </Collapse>
        </>
      )}
    </Paper>
  );
});

export default WindResourceCard;
