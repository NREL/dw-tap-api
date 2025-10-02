type ApiDebugInfoProps = {
  params: { lat: number; lng: number; hubHeight: number; model: string; powerCurve: string; lossAssumption?: number };
  windData: { global_avg: number } | null;
  productionData: any;
  error: string | null;
};

export function ApiDebugInfo({ params, windData, productionData, error }: ApiDebugInfoProps) {
  const { lat, lng, hubHeight, model, powerCurve } = params;

  const avgProduction = productionData?.summary_avg_energy_production?.["Average year"]?.["kWh produced"];

  return (
    <details style={{
      position: "fixed",
      bottom: 16,
      right: 16,
      background: "white",
      border: "2px solid #0279c2",
      borderRadius: 8,
      padding: 12,
      maxWidth: 400,
      fontSize: "0.75rem",
      boxShadow: "0 4px 12px rgba(0,0,0,0.15)",
      zIndex: 9999
    }}>
      <summary style={{
        cursor: "pointer",
        fontWeight: "bold",
        color: "#0279c2",
        userSelect: "none"
      }}>
        🔍 API Debug Info
      </summary>
      <div style={{ marginTop: 12, display: "flex", flexDirection: "column", gap: 8 }}>
        <div>
          <strong>Request Parameters:</strong>
          <pre style={{
            background: "#f5f5f5",
            padding: 8,
            borderRadius: 4,
            margin: "4px 0 0 0",
            overflow: "auto",
            fontSize: "0.7rem"
          }}>
            {`lat: ${lat}
lng: ${lng}
hubHeight: ${hubHeight}
model: ${model}
powerCurve: ${powerCurve}`}
          </pre>
        </div>

        <div>
          <strong>API Endpoints:</strong>
          <pre style={{
            background: "#f5f5f5",
            padding: 8,
            borderRadius: 4,
            margin: "4px 0 0 0",
            overflow: "auto",
            fontSize: "0.65rem",
            wordBreak: "break-all"
          }}>
            {`/api/${model}/windspeed?lat=${lat}&lng=${lng}&height=${hubHeight}

/api/${model}/energy-production?lat=${lat}&lng=${lng}&height=${hubHeight}&selected_powercurve=${powerCurve}&time_period=all`}
          </pre>
        </div>

        {error && (
          <div>
            <strong style={{ color: "#c62828" }}>Error:</strong>
            <pre style={{
              background: "#ffebee",
              padding: 8,
              borderRadius: 4,
              margin: "4px 0 0 0",
              color: "#c62828",
              fontSize: "0.7rem"
            }}>
              {error}
            </pre>
          </div>
        )}

        {windData && (
          <div>
            <strong>Wind Speed:</strong>
            <pre style={{
              background: "#e3f2fd",
              padding: 8,
              borderRadius: 4,
              margin: "4px 0 0 0",
              fontSize: "0.7rem"
            }}>
              {windData.global_avg.toFixed(2)} m/s
            </pre>
          </div>
        )}

        {productionData && avgProduction && (
          <div>
            <strong>Production (Average):</strong>
            <pre style={{
              background: "#e8f5e9",
              padding: 8,
              borderRadius: 4,
              margin: "4px 0 0 0",
              fontSize: "0.7rem"
            }}>
              {Math.round(avgProduction).toLocaleString()} kWh/yr
            </pre>
          </div>
        )}

        <div style={{ marginTop: 8, paddingTop: 8, borderTop: "1px solid #ddd" }}>
          <a
            href={`http://localhost:5173?lat=${lat}&lng=${lng}&hubHeight=${hubHeight}&model=${model}&powerCurve=${powerCurve}`}
            target="_blank"
            rel="noopener noreferrer"
            style={{
              color: "#0279c2",
              textDecoration: "underline",
              fontSize: "0.75rem"
            }}
          >
            🔗 Open in Original UI (port 5173)
          </a>
        </div>
      </div>
    </details>
  );
}

