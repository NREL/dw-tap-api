import { Stack, Typography } from "@mui/material";
import { era5 } from "../../src/server/api";

export const dynamic = "force-dynamic";

const DENVER = { lat: 39.7392, lng: -104.9903 };

async function getEra5Wind(lat: number, lng: number) {
  return era5.windspeed({ lat, lng, height: 40, source: "athena_era5" });
}

export default async function DenverPage() {
  const data = await getEra5Wind(DENVER.lat, DENVER.lng);
  return (
    <main style={{ padding: 24 }}>
      <Stack spacing={2}>
        <Typography variant="h5">ERA5 Windspeed @40m — Denver, CO</Typography>
        <pre style={{ background: "#f5f5f5", padding: 12, borderRadius: 6 }}>
          {JSON.stringify(data, null, 2)}
        </pre>
      </Stack>
    </main>
  );
}
