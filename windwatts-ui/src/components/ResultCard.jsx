import { useState } from "react";
import {
  Card,
  CardHeader,
  CardContent,
  CardActions,
  Button,
  Collapse,
  Typography,
} from "@mui/material";
import PropTypes from "prop-types";

const ResultCard = ({
  windspeed,
  energy,
}) => {
  const [expanded, setExpanded] = useState(false);

  const windspeedData = {
    title: "Wind Resource",
    subheader: "Details about wind resources",
    data: `we found average ${windspeed} m/s resources.`,
    details: [
      "Additional details about wind resources:",
      "Low wind resource refers to wind speeds below 3.00 m/s.",
      "Moderate wind resource refers to wind speeds between 3.00 m/s and 5.00 m/s.",
      "High wind resource refers to wind speeds above 5.00 m/s.",
    ],
  }
  
  const windresourceData = {
    title: "Wind Resource",
    subheader: "Details about wind resources",
    data: "This section provides information about wind resources.",
    details: [
      "Additional details about wind resources:",
      "Low wind resource refers to wind speeds below 3.00 m/s.",
      "Moderate wind resource refers to wind speeds between 3.00 m/s and 5.00 m/s.",
      "High wind resource refers to wind speeds above 5.00 m/s.",
    ],
  }

  const handleExpandClick = () => {
    setExpanded(!expanded);
  };

  return (
    <Card sx={{ margin: "auto", mt: 5 }}>
      <CardHeader
        title={windspeedData.title}
        subheader={windspeedData.subheader}
        sx={{ bgcolor: "var(--color-light)" }}
      />
      <CardContent>
        <Typography variant="body2" color="text.secondary">
          {windspeedData.data}
        </Typography>
      </CardContent>
      <CardActions>
        <Button
          onClick={handleExpandClick}
          aria-expanded={expanded}
          aria-label="show more"
        >
          {expanded ? "Hide Details" : "Show Details"}
        </Button>
      </CardActions>
      <Collapse in={expanded} timeout="auto" unmountOnExit>
        <CardContent>
          {windspeedData.details.map((detail, index) => (
            <Typography key={"result_detail" + index}>{detail}</Typography>
          ))}
        </CardContent>
      </Collapse>
    </Card>
  );
};

ResultCard.propTypes = {
  data: PropTypes.shape({
    title: PropTypes.string.isRequired,
    subheader: PropTypes.string.isRequired,
    data: PropTypes.string.isRequired,
    details: PropTypes.arrayOf(PropTypes.string).isRequired,
  }),
};
export default ResultCard;
