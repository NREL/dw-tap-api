import { Button, Stack, Typography } from "@mui/material";
import UnitsDebug from "../src/components/UnitsDebug";

export default function Page() {
  return (
    <main style={{ padding: 24 }}>
      <Stack spacing={2}>
        <Typography variant="h4">Windwatts UI (SSR)</Typography>
        <Typography>SSR baseline page is rendering.</Typography>
        <Button variant="contained">MUI Button (SSR)</Button>
        <UnitsDebug />
      </Stack>
    </main>
  );
}
