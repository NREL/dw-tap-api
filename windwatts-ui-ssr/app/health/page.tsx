import { Stack, Typography } from "@mui/material";

export const dynamic = "force-dynamic";

async function getHealth() {
  const base = process.env.WINDWATTS_API_BASE || "http://localhost:8000/api";
  const res = await fetch(`${base}/healthcheck`, {
    // User-specific and rapidly changing; do not cache by default
    cache: "no-store",
    // Propagate headers/cookies here if needed
    headers: {}
  });
  if (!res.ok) throw new Error("Failed to fetch healthcheck");
  return res.json() as Promise<{ status: string }>;
}

export default async function HealthPage() {
  const data = await getHealth();
  return (
    <main style={{ padding: 24 }}>
      <Stack spacing={2}>
        <Typography variant="h5">API Health</Typography>
        <Typography>Status: {data.status}</Typography>
      </Stack>
    </main>
  );
}
