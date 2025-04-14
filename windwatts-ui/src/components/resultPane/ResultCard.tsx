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

const ResultCard = ({
  data,
}: {
  data: {
    title: string;
    subheader: string;
    data: string | number;
    details: string[];
  };
}) => {
  const [expanded, setExpanded] = useState(false);

  const handleExpandClick = () => {
    setExpanded(!expanded);
  };

  return (
    <Card>
      <CardHeader
        title={data.title}
        subheader={data.subheader}
        sx={{ bgcolor: "var(--color-light)" }}
      />
      <CardContent>
        <Typography variant="body2" color="text.secondary">
          {data.data}
        </Typography>
      </CardContent>
      {data.details.length > 0 ? (
        <>
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
              {data.details.map((detail, index) => (
                <Typography key={"result_detail" + index} variant="body2">
                  {detail}
                </Typography>
              ))}
            </CardContent>
          </Collapse>
        </>
      ) : null}
    </Card>
  );
};

export default ResultCard;
