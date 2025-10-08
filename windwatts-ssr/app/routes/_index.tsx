import type { LoaderFunctionArgs, MetaFunction } from "@remix-run/node";
import { json } from "@remix-run/node";
import { useLoaderData } from "@remix-run/react";
import { ClientOnlyMap } from "../components/ClientOnlyMap";
import { RightPaneSimple } from "../components/RightPaneSimple";
import { SettingsSimple } from "../components/SettingsSimple";
import { ApiDebugInfo } from "../components/ApiDebugInfo";
import { useState } from "react";
import { parseLocationParams, generateShareableUrl, isOutOfBounds, getOutOfBoundsMessage } from "../utils/urlParams";
import { applyLossToProductionData, factorToPercent } from "../utils/lossAdjustment";

type WindDataResponse = { global_avg: number };
type ProductionDataResponse = {
  energy_production?: number;
  summary_avg_energy_production?: Record<string, Record<string, number>>;
  yearly_avg_energy_production?: Array<{ year: number; kWh: number }>;
};

export const meta: MetaFunction<typeof loader> = ({ data }) => {
  if (!data) return [{ title: "WindWatts SSR POC" }];

  const { params } = data;
  return [
    { title: `WindWatts - ${params.lat.toFixed(2)}, ${params.lng.toFixed(2)}` },
    {
      name: "description",
      content: `Wind resource analysis for location ${params.lat.toFixed(2)}, ${params.lng.toFixed(2)} at ${params.hubHeight}m hub height`
    },
  ];
};

export async function loader({ request }: LoaderFunctionArgs) {
  const url = new URL(request.url);

  // Parse and validate all parameters
  const { lat, lng, hubHeight, model, powerCurve, lossAssumption } = parseLocationParams(url);
  const lossPercent = factorToPercent(lossAssumption);

  const apiBase = process.env.API_BASE_URL || "http://windwatts-api:8000";
  const useDummy = (process.env.USE_DUMMY_DATA === "1" || process.env.USE_DUMMY_DATA === "true");

  let windData: WindDataResponse | null = null;
  let productionData: ProductionDataResponse | null = null;
  let error: string | null = null;

  // Check if location is out of bounds
  const outOfBounds = isOutOfBounds(lat, lng, model);
  if (outOfBounds) {
    error = getOutOfBoundsMessage(lat, lng, model);
  }

  if (useDummy) {
    windData = { global_avg: 7.5 };
    productionData = {
      energy_production: 47187,
      summary_avg_energy_production: {
        "Average year": { "kWh produced": 47187 },
        "Lowest year": { "kWh produced": 38820 },
        "Highest year": { "kWh produced": 52940 },
      },
      yearly_avg_energy_production: [
        { year: 2019, kWh: 44184 },
        { year: 2020, kWh: 53170 },
        { year: 2021, kWh: 38820 },
      ],
    };
  } else if (!outOfBounds) {
    try {
      const controller = new AbortController();
      const timeout = setTimeout(() => controller.abort(), 10000);

      const windUrl = `${apiBase}/api/${model}/windspeed?lat=${lat}&lng=${lng}&height=${hubHeight}`;
      const prodUrl = `${apiBase}/api/${model}/energy-production?lat=${lat}&lng=${lng}&height=${hubHeight}&selected_powercurve=${powerCurve}&time_period=all`;

      // Log the API requests for debugging
      console.log('🌐 API Requests:', {
        wind: windUrl,
        production: prodUrl,
        params: { lat, lng, hubHeight, model, powerCurve }
      });

      const [windRes, prodRes] = await Promise.all([
        fetch(windUrl, { headers: { "Content-Type": "application/json" }, signal: controller.signal }),
        fetch(prodUrl, { headers: { "Content-Type": "application/json" }, signal: controller.signal }),
      ]);

      clearTimeout(timeout);

      console.log('📊 API Responses:', {
        wind: { status: windRes.status, ok: windRes.ok },
        production: { status: prodRes.status, ok: prodRes.ok }
      });

      if (windRes.ok) {
        windData = await windRes.json();
        console.log('💨 Wind Data:', windData);
      } else {
        console.error('❌ Wind API Error:', windRes.status, await windRes.text());
      }

      if (prodRes.ok) {
        const rawData = await prodRes.json();
        console.log('📦 Raw API Response:', {
          hasData: !!rawData,
          hasSummary: !!rawData?.summary_avg_energy_production,
          summaryKeys: rawData?.summary_avg_energy_production ? Object.keys(rawData.summary_avg_energy_production) : [],
          averageYearData: rawData?.summary_avg_energy_production?.["Average year"],
        });
        productionData = applyLossToProductionData(rawData, lossAssumption);
        console.log('⚡ Production Data Summary:', {
          raw: rawData?.summary_avg_energy_production?.["Average year"]?.["kWh produced"],
          withLoss: productionData?.summary_avg_energy_production?.["Average year"]?.["kWh produced"],
          lossFactor: lossAssumption,
          lossPercent: `${lossPercent}%`,
          calculation: `${rawData?.summary_avg_energy_production?.["Average year"]?.["kWh produced"]} × ${lossAssumption} = ${Math.floor((rawData?.summary_avg_energy_production?.["Average year"]?.["kWh produced"] || 0) * lossAssumption)}`,
        });
      } else {
        console.error('❌ Production API Error:', prodRes.status, await prodRes.text());
      }
    } catch (e) {
      error = e instanceof Error ? e.message : "Unknown error";
      console.error('🚨 API Request Error:', error);
    }
  }

  // Generate shareable URL for this configuration
  const shareableUrl = generateShareableUrl({ lat, lng, hubHeight, model, powerCurve, lossAssumption });

  return json({
    params: { lat, lng, hubHeight, model, powerCurve, lossAssumption },
    windData,
    productionData,
    error,
    shareableUrl,
    lossPercent,
    publicEnv: {
      VITE_MAP_API_KEY: process.env.VITE_MAP_API_KEY || "",
    },
  });
}

export default function Index() {
  const { params, windData, productionData, error, shareableUrl, publicEnv } = useLoaderData<typeof loader>();
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [showCopied, setShowCopied] = useState(false);

  const handleCopyLink = () => {
    const fullUrl = window.location.origin + shareableUrl;
    navigator.clipboard.writeText(fullUrl);
    setShowCopied(true);
    setTimeout(() => setShowCopied(false), 2000);
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100vh" }}>
      {/* Header */}
      <div style={{ flexGrow: 0 }}>
        <div style={{ backgroundColor: "#0279c2", color: "white" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "8px 16px" }}>
            <a href="/" style={{ fontSize: "1.25rem", color: "white", textDecoration: "none", flexGrow: 1 }}>
              Wind Watts
            </a>
            <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
              <button
                onClick={handleCopyLink}
                style={{
                  padding: "6px 16px",
                  fontSize: "0.875rem",
                  border: "1px solid white",
                  borderRadius: 4,
                  backgroundColor: showCopied ? "rgba(255, 255, 255, 0.3)" : "transparent",
                  color: "white",
                  cursor: "pointer",
                  transition: "background-color 0.2s",
                }}
              >
                {showCopied ? "✓ Copied!" : "📋 Share Link"}
              </button>
              <img
                style={{ height: 40 }}
                src="/NREL-logo-reversed.png"
                alt="NREL Logo"
              />
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div
        style={{
          display: "flex",
          flexGrow: 1,
          overflow: "hidden",
        }}
      >
        {/* Map Area */}
        <div
          style={{
            position: "relative",
            flexGrow: 1,
            display: "flex",
            flexDirection: "column",
            overflow: "hidden",
          }}
        >
          <ClientOnlyMap
            center={{ lat: params.lat, lng: params.lng }}
            height="100%"
            apiKey={publicEnv.VITE_MAP_API_KEY}
          />
        </div>

        {/* Right Pane */}
        <div
          className="right-pane"
          style={{
            width: 420,
            backgroundColor: "white",
            overflowY: "auto",
            borderLeft: "1px solid #ddd",
          }}
        >
          <RightPaneSimple
            params={params}
            windData={windData}
            productionData={productionData}
            error={error}
            onOpenSettings={() => setSettingsOpen(true)}
          />
        </div>
      </div>

      {/* Settings Modal */}
      {settingsOpen && (
        <SettingsSimple
          onClose={() => setSettingsOpen(false)}
          params={params}
        />
      )}

      {/* Debug Info (bottom-right corner) */}
      <ApiDebugInfo
        params={params}
        windData={windData}
        productionData={productionData}
        error={error}
      />
    </div>
  );
}
