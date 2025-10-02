/**
 * Apply loss assumption to production value
 * Matches the original UI's loss adjustment logic
 */
export function applyLoss(
  value: number,
  lossFactor: number,
  options?: { mode?: "floor" | "round" }
): number {
  const adjusted = value * lossFactor;
  if (options?.mode === "floor") {
    return Math.floor(adjusted);
  }
  return Math.round(adjusted);
}

/**
 * Apply loss assumption to all production data
 */
export function applyLossToProductionData(data: any, lossFactor: number): any {
  if (!data) return data;

  try {
    const clone = JSON.parse(JSON.stringify(data));

    console.log("🔧 Applying loss to data:", {
      lossFactor,
      hasSummary: !!clone.summary_avg_energy_production,
      before:
        clone.summary_avg_energy_production?.["Average year"]?.["kWh produced"],
    });

    // Apply to summary data
    if (clone.summary_avg_energy_production) {
      ["Average year", "Lowest year", "Highest year"].forEach((key) => {
        const row = clone.summary_avg_energy_production[key];
        if (row && row["kWh produced"] != null) {
          const before = row["kWh produced"];
          row["kWh produced"] = applyLoss(
            Number(row["kWh produced"]),
            lossFactor,
            { mode: "floor" }
          );
          console.log(`  ${key}: ${before} → ${row["kWh produced"]}`);
        }
      });
    }

    console.log(
      "✅ After loss:",
      clone.summary_avg_energy_production?.["Average year"]?.["kWh produced"]
    );

    // Apply to yearly data
    if (
      clone.yearly_avg_energy_production &&
      Array.isArray(clone.yearly_avg_energy_production)
    ) {
      clone.yearly_avg_energy_production =
        clone.yearly_avg_energy_production.map((row: any) => ({
          ...row,
          kWh:
            row.kWh != null
              ? applyLoss(Number(row.kWh), lossFactor, { mode: "floor" })
              : row.kWh,
        }));
    } else if (
      clone.yearly_avg_energy_production &&
      typeof clone.yearly_avg_energy_production === "object"
    ) {
      // Handle object format
      Object.keys(clone.yearly_avg_energy_production).forEach((key) => {
        const row = clone.yearly_avg_energy_production[key];
        if (row && row.kWh != null) {
          row.kWh = applyLoss(Number(row.kWh), lossFactor, { mode: "floor" });
        }
      });
    }

    // Apply to monthly data
    if (clone.monthly_avg_energy_production) {
      Object.keys(clone.monthly_avg_energy_production).forEach((key) => {
        const row = clone.monthly_avg_energy_production[key];
        if (row && row["kWh produced"] != null) {
          row["kWh produced"] = applyLoss(
            Number(row["kWh produced"]),
            lossFactor,
            { mode: "floor" }
          );
        }
      });
    }

    return clone;
  } catch (error) {
    console.error("❌ Error applying loss:", error);
    return data;
  }
}

/**
 * Convert loss percentage to factor
 * e.g., 17% loss → 0.83 factor
 */
export function percentToFactor(percent: number): number {
  return 1 - percent / 100;
}

/**
 * Convert loss factor to percentage
 * e.g., 0.83 factor → 17% loss
 */
export function factorToPercent(factor: number): number {
  return Math.round((1 - factor) * 100);
}
