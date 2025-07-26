import { Box, Typography, List, ListItem, ListItemText } from "@mui/material";
import { LocationOn } from "@mui/icons-material";
import { SearchResultsListProps } from "../types";

function SearchResultsList({
  predictions,
  onPredictionClick,
}: SearchResultsListProps) {
  return (
    <Box>
      <Typography
        variant="h6"
        sx={{
          mb: 2,
          color: "#666",
          fontSize: "18px",
          fontWeight: 600,
          px: 2,
          pt: 2,
        }}
      >
        Search Results
      </Typography>
      <List sx={{ py: 0, px: 2 }}>
        {predictions.map((prediction) => (
          <ListItem
            key={prediction.place_id}
            onClick={() => onPredictionClick(prediction)}
            sx={{
              cursor: "pointer",
              borderRadius: 3,
              mb: 1.5,
              bgcolor: "#ffffff",
              "&:hover": {
                backgroundColor: "#f8f9fa",
                transform: "translateY(-1px)",
                boxShadow: "0 2px 8px rgba(0,0,0,0.1)",
                transition: "all 0.2s ease-in-out",
              },
              py: 2,
              px: 2.5,
              border: "1px solid #e5e7eb",
              transition: "all 0.2s ease-in-out",
              boxShadow: "0 1px 3px rgba(0,0,0,0.05)",
            }}
          >
            <Box
              sx={{
                mr: 2.5,
                minWidth: 36,
                height: 36,
                borderRadius: "50%",
                bgcolor: "#e3f2fd",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                flexShrink: 0,
              }}
            >
              <LocationOn sx={{ color: "#1976d2", fontSize: 18 }} />
            </Box>
            <ListItemText
              primary={
                <Typography
                  variant="body1"
                  sx={{
                    fontWeight: 600,
                    color: "#1a1a1a",
                    fontSize: "15px",
                    lineHeight: 1.4,
                    mb: 0.5,
                  }}
                >
                  {prediction.structured_formatting?.main_text ||
                    prediction.description}
                </Typography>
              }
              secondary={
                <Typography
                  variant="body2"
                  sx={{
                    color: "#6b7280",
                    fontSize: "13px",
                    fontWeight: 400,
                    lineHeight: 1.3,
                  }}
                >
                  {prediction.structured_formatting?.secondary_text}
                </Typography>
              }
            />
          </ListItem>
        ))}
      </List>
    </Box>
  );
}

export default SearchResultsList;
