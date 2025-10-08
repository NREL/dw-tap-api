const POWER_CURVE_LABELS: Record<string, string> = {
  "nrel-reference-2.5kW": "NREL Reference 2.5kW",
  "nrel-reference-100kW": "NREL Reference 100kW",
  "nrel-reference-250kW": "NREL Reference 250kW",
  "nrel-reference-2000kW": "NREL Reference 2000kW",
};

type RightPaneSimpleProps = {
  params: { lat: number; lng: number; hubHeight: number; model: string; powerCurve: string; lossAssumption?: number };
  windData: { global_avg: number } | null;
  productionData: any;
  error: string | null;
  onOpenSettings: () => void;
};

export function RightPaneSimple({ params, windData, productionData, error, onOpenSettings }: RightPaneSimpleProps) {
  const { lat, lng, hubHeight, powerCurve } = params;

  const avgProduction = productionData?.summary_avg_energy_production?.["Average year"]?.["kWh produced"];
  const lowProduction = productionData?.summary_avg_energy_production?.["Lowest year"]?.["kWh produced"];
  const highProduction = productionData?.summary_avg_energy_production?.["Highest year"]?.["kWh produced"];

  return (
    <div style={{ padding: 16 }}>
      <div style={{ textAlign: "center", borderBottom: "1px solid #ddd", paddingBottom: 12, marginBottom: 16, fontWeight: 600, color: "#666" }}>
        Summary Results Based on
      </div>

      {/* Settings Cards */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 8, marginBottom: 16 }}>
        <div style={{ border: "1px solid #ddd", borderRadius: 4, padding: 8, textAlign: "center", backgroundColor: "#f9f9f9" }}>
          <div style={{ fontSize: "0.875rem", fontWeight: 600, marginBottom: 4 }}>Location</div>
          <div style={{ fontSize: "0.875rem", color: "#666" }}>{lat.toFixed(3)}, {lng.toFixed(3)}</div>
        </div>
        <div style={{ border: "1px solid #ddd", borderRadius: 4, padding: 8, textAlign: "center", backgroundColor: "#f9f9f9" }}>
          <div style={{ fontSize: "0.875rem", fontWeight: 600, marginBottom: 4 }}>Hub height</div>
          <div style={{ fontSize: "0.875rem", color: "#666" }}>{hubHeight} meters</div>
        </div>
        <div style={{ border: "1px solid #ddd", borderRadius: 4, padding: 8, textAlign: "center", backgroundColor: "#f9f9f9" }}>
          <div style={{ fontSize: "0.875rem", fontWeight: 600, marginBottom: 4 }}>Power curve</div>
          <div style={{ fontSize: "0.875rem", color: "#666" }}>{POWER_CURVE_LABELS[powerCurve] || powerCurve}</div>
        </div>
      </div>

      {/* Edit Settings Button */}
      <button
        onClick={onOpenSettings}
        style={{
          display: "flex",
          alignItems: "center",
          gap: 6,
          marginLeft: "auto",
          marginBottom: 16,
          padding: "6px 16px",
          fontSize: "0.9rem",
          border: "1px solid #0279c2",
          borderRadius: 8,
          backgroundColor: "white",
          color: "#0279c2",
          cursor: "pointer",
        }}
      >
        <span>⚙️</span> Edit settings
      </button>

      {/* Error */}
      {error && (
        <div style={{ border: "1px solid #f44336", borderRadius: 4, padding: 16, marginBottom: 16, backgroundColor: "#ffebee", color: "#c62828" }}>
          Error: {error}
        </div>
      )}

      {/* Wind Speed Card */}
      {windData && (
        <div style={{ border: "1px solid #ddd", borderRadius: 4, padding: 24, marginBottom: 16, textAlign: "center" }}>
          <div style={{ fontSize: "0.875rem", color: "#666", marginBottom: 8 }}>Average Wind Speed *</div>
          <div style={{ fontSize: "2rem", fontWeight: "bold", color: "#0279c2", marginBottom: 4 }}>
            {windData.global_avg.toFixed(2)} m/s
          </div>
          <div style={{ fontSize: "0.75rem", color: "#999" }}>Average wind speed at selected height</div>
        </div>
      )}

      {/* Production Card */}
      {productionData && avgProduction && (
        <div style={{ border: "1px solid #ddd", borderRadius: 4, padding: 16, marginBottom: 16 }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
            <div style={{ fontSize: "1.25rem", fontWeight: "bold" }}>Production</div>
            <div style={{ backgroundColor: "#0279c2", color: "white", padding: "4px 12px", borderRadius: 4, fontSize: "0.7rem" }}>
              Primary Analysis
            </div>
          </div>
          <div style={{ fontSize: "0.875rem", color: "#666", marginBottom: 16 }}>
            Estimated annual production potential
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 8, marginBottom: 16 }}>
            <div style={{ padding: 16, textAlign: "center", backgroundColor: "#1976d2", color: "white", borderRadius: 4 }}>
              <div style={{ fontSize: "0.75rem", opacity: 0.9, marginBottom: 4 }}>Average</div>
              <div style={{ fontSize: "1.25rem", fontWeight: "bold", marginBottom: 2 }}>{Math.round(avgProduction).toLocaleString()}</div>
              <div style={{ fontSize: "0.75rem" }}>kWh</div>
            </div>
            <div style={{ padding: 16, textAlign: "center", backgroundColor: "#2e7d32", color: "white", borderRadius: 4 }}>
              <div style={{ fontSize: "0.75rem", opacity: 0.9, marginBottom: 4 }}>Highest Year</div>
              <div style={{ fontSize: "1rem", fontWeight: "bold", marginBottom: 2 }}>{Math.round(highProduction).toLocaleString()}</div>
              <div style={{ fontSize: "0.75rem" }}>kWh</div>
            </div>
            <div style={{ padding: 16, textAlign: "center", backgroundColor: "#ed6c02", color: "white", borderRadius: 4 }}>
              <div style={{ fontSize: "0.75rem", opacity: 0.9, marginBottom: 4 }}>Lowest Year</div>
              <div style={{ fontSize: "1rem", fontWeight: "bold", marginBottom: 2 }}>{Math.round(lowProduction).toLocaleString()}</div>
              <div style={{ fontSize: "0.75rem" }}>kWh</div>
            </div>
          </div>

          <div style={{ fontSize: "0.875rem", color: "#666" }}>
            Wind energy production can vary significantly from year to year. Understanding both the average resource and its variability is key to setting realistic expectations.
          </div>
        </div>
      )}

      {!windData && !productionData && !error && (
        <div style={{ border: "1px solid #ddd", borderRadius: 4, padding: 32, textAlign: "center", color: "#999" }}>
          Select a location and settings to view analysis results.
        </div>
      )}
    </div>
  );
}

