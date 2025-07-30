import { Paper, Typography, Skeleton } from "@mui/material";
import { OutOfBoundsWarning } from ".";

interface BaseCardProps {
  title: string;
  children?: React.ReactNode;
}

interface OutOfBoundsCardProps {
  message: string;
}

export const OutOfBoundsCard = ({ message }: OutOfBoundsCardProps) => (
  <Paper
    sx={{
      p: 2,
      minHeight: 100,
      bgcolor: "warning.light",
    }}
  >
    <OutOfBoundsWarning message={message} />
  </Paper>
);

export const ErrorCard = ({ title }: BaseCardProps) => (
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

export const LoadingCard = ({ title }: BaseCardProps) => (
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
    <Skeleton variant="text" width="60%" height={40} />
    <Skeleton variant="text" width="40%" height={20} />
  </Paper>
);

export const EmptyCard = ({ title }: BaseCardProps) => (
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

export const DataCard = ({ title, children }: BaseCardProps) => (
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
    {children}
  </Paper>
);
