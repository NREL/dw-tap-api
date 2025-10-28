import { Stack, Typography } from "@mui/material";
import Controls from "../src/components/Controls";
import WindDataCard from "../src/components/WindDataCard";
import { era5 } from "../src/server/api";
import { URL_PARAM_DEFAULTS } from "../src/utils/urlParams";

export const dynamic = "force-dynamic";

export default async function Page({
  searchParams
}: {
  searchParams: { [key: string]: string | string[] | undefined };
}) {
  const lat = parseFloat((searchParams.lat as string) || "39.7392");
  const lng = parseFloat((searchParams.lng as string) || "-104.9903");
  const height = parseInt(
    (searchParams.hubHeight as string) || String(URL_PARAM_DEFAULTS.hubHeight),
    10
  );
  const powerCurve =
    (searchParams.powerCurve as string) || URL_PARAM_DEFAULTS.powerCurve;

  let wind: any = null;
  let production: any = null;
  let error: string | null = null;

  try {
    wind = await era5.windspeed({ lat, lng, height, source: "athena_era5" });
    production = await era5.energyProduction({
      lat,
      lng,
      height,
      powerCurve,
      source: "athena_era5",
      time_period: "all"
    });
  } catch (e: any) {
    error = e?.message || "Failed to load";
  }

  return (
    <main style={{ padding: 24 }}>
      <Stack spacing={2}>
        <Typography variant="h5">Wind Data</Typography>
        <Typography>
          lat={lat.toFixed(4)}, lng={lng.toFixed(4)}, height={height}m,
          powerCurve={powerCurve}
        </Typography>
        <Controls />
        {error ? (
          <Typography color="error">{error}</Typography>
        ) : (
          <WindDataCard wind={wind} production={production} />
        )}
      </Stack>
    </main>
  );
}
