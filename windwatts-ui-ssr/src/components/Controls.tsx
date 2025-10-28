"use client";

import { Box, MenuItem, Stack, TextField } from "@mui/material";
import { usePathname, useRouter, useSearchParams } from "next/navigation";

const POWER_CURVES = [
  "nrel-reference-2.5kW",
  "nrel-reference-100kW"
];

export default function Controls() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const pathname = usePathname();

  const hubHeight = Number(searchParams.get("hubHeight") || 40);
  const powerCurve = searchParams.get("powerCurve") || POWER_CURVES[0];

  const updateParam = (key: string, value: string) => {
    const next = new URLSearchParams(searchParams as any);
    next.set(key, value);
    router.replace(`${pathname}?${next.toString()}`);
  };

  return (
    <Box>
      <Stack direction={{ xs: "column", sm: "row" }} spacing={2}>
        <TextField
          label="Hub Height (m)"
          type="number"
          value={hubHeight}
          inputProps={{ min: 10, max: 200 }}
          onChange={(e) => updateParam("hubHeight", String(Math.max(10, Math.min(200, Number(e.target.value)) )))}
        />
        <TextField
          select
          label="Power Curve"
          value={powerCurve}
          onChange={(e) => updateParam("powerCurve", e.target.value)}
        >
          {POWER_CURVES.map((pc) => (
            <MenuItem key={pc} value={pc}>{pc}</MenuItem>
          ))}
        </TextField>
      </Stack>
    </Box>
  );
}
