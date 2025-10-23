import { useState, useEffect } from "react";
import { useNavigate } from "@remix-run/react";

const HUB_HEIGHTS = [30, 40, 50, 60, 80, 100];
const MODELS = ["era5", "wtk"];
const POWER_CURVES = [
  { value: "nrel-reference-2.5kW", label: "NREL Reference 2.5kW" },
  { value: "nrel-reference-100kW", label: "NREL Reference 100kW" },
  { value: "nrel-reference-250kW", label: "NREL Reference 250kW" },
  { value: "nrel-reference-2000kW", label: "NREL Reference 2000kW" },
];

type SettingsSimpleProps = {
  onClose: () => void;
  params: { lat: number; lng: number; hubHeight: number; model: string; powerCurve: string };
};

export function SettingsSimple({ onClose, params }: SettingsSimpleProps) {
  const navigate = useNavigate();
  const [localParams, setLocalParams] = useState(params);
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    setLocalParams(params);
  }, [params]);

  const handleSave = () => {
    const searchParams = new URLSearchParams({
      lat: String(localParams.lat),
      lng: String(localParams.lng),
      hubHeight: String(localParams.hubHeight),
      model: localParams.model,
      powerCurve: localParams.powerCurve,
    });
    navigate(`/?${searchParams.toString()}`, { replace: true });
    onClose();
  };

  return (
    <div
      onClick={onClose}
      style={{
        position: "fixed",
        inset: 0,
        backgroundColor: "rgba(0, 0, 0, 0.5)",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        zIndex: 1300,
      }}
    >
      <div
        onClick={(e) => e.stopPropagation()}
        style={{
          width: 600,
          maxHeight: "80vh",
          backgroundColor: "white",
          borderRadius: 8,
          display: "flex",
          flexDirection: "column",
          overflow: "hidden",
        }}
      >
        {/* Header */}
        <div
          style={{
            position: "sticky",
            top: 0,
            backgroundColor: "white",
            padding: "24px 24px 16px",
            borderBottom: scrolled ? "1px solid rgba(0,0,0,0.12)" : "1px solid transparent",
            boxShadow: scrolled ? "0 2px 8px rgba(0,0,0,0.1)" : "none",
            zIndex: 1,
          }}
        >
          <button
            onClick={onClose}
            style={{
              position: "absolute",
              right: 8,
              top: 8,
              border: "none",
              backgroundColor: "transparent",
              fontSize: "1.5rem",
              cursor: "pointer",
              width: 40,
              height: 40,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
            }}
          >
            ×
          </button>
          <h2 style={{ margin: 0, fontSize: "1.5rem" }}>Settings</h2>
        </div>

        {/* Content */}
        <div
          style={{
            flex: 1,
            overflowY: "auto",
            padding: "8px 24px 24px",
          }}
          onScroll={(e) => setScrolled(e.currentTarget.scrollTop > 0)}
        >
          <div style={{ display: "flex", flexDirection: "column", gap: 24 }}>
            <div>
              <h3 style={{ marginTop: 16, marginBottom: 16 }}>Location</h3>
              <div style={{ display: "flex", gap: 16 }}>
                <div style={{ flex: 1 }}>
                  <label style={{ display: "block", marginBottom: 8, fontSize: "0.875rem", color: "#666" }}>Latitude</label>
                  <input
                    type="number"
                    step="0.001"
                    value={localParams.lat}
                    onChange={(e) => setLocalParams({ ...localParams, lat: Number(e.target.value) })}
                    style={{
                      width: "100%",
                      padding: "10px 12px",
                      border: "1px solid #ddd",
                      borderRadius: 4,
                      fontSize: "1rem",
                      boxSizing: "border-box",
                    }}
                  />
                </div>
                <div style={{ flex: 1 }}>
                  <label style={{ display: "block", marginBottom: 8, fontSize: "0.875rem", color: "#666" }}>Longitude</label>
                  <input
                    type="number"
                    step="0.001"
                    value={localParams.lng}
                    onChange={(e) => setLocalParams({ ...localParams, lng: Number(e.target.value) })}
                    style={{
                      width: "100%",
                      padding: "10px 12px",
                      border: "1px solid #ddd",
                      borderRadius: 4,
                      fontSize: "1rem",
                      boxSizing: "border-box",
                    }}
                  />
                </div>
              </div>
            </div>

            <div>
              <h3 style={{ marginTop: 16, marginBottom: 16 }}>Turbine Settings</h3>
              <div style={{ marginBottom: 16 }}>
                <label style={{ display: "block", marginBottom: 8, fontSize: "0.875rem", color: "#666" }}>Hub Height</label>
                <select
                  value={localParams.hubHeight}
                  onChange={(e) => setLocalParams({ ...localParams, hubHeight: Number(e.target.value) })}
                  style={{
                    width: "100%",
                    padding: "10px 12px",
                    border: "1px solid #ddd",
                    borderRadius: 4,
                    fontSize: "1rem",
                    boxSizing: "border-box",
                  }}
                >
                  {HUB_HEIGHTS.map((h) => (
                    <option key={h} value={h}>{h} meters</option>
                  ))}
                </select>
              </div>

              <div>
                <label style={{ display: "block", marginBottom: 8, fontSize: "0.875rem", color: "#666" }}>Power Curve</label>
                <select
                  value={localParams.powerCurve}
                  onChange={(e) => setLocalParams({ ...localParams, powerCurve: e.target.value })}
                  style={{
                    width: "100%",
                    padding: "10px 12px",
                    border: "1px solid #ddd",
                    borderRadius: 4,
                    fontSize: "1rem",
                    boxSizing: "border-box",
                  }}
                >
                  {POWER_CURVES.map((pc) => (
                    <option key={pc.value} value={pc.value}>{pc.label}</option>
                  ))}
                </select>
              </div>
            </div>

            <div>
              <h3 style={{ marginTop: 16, marginBottom: 16 }}>Data Model</h3>
              <label style={{ display: "block", marginBottom: 8, fontSize: "0.875rem", color: "#666" }}>Model</label>
              <select
                value={localParams.model}
                onChange={(e) => setLocalParams({ ...localParams, model: e.target.value })}
                style={{
                  width: "100%",
                  padding: "10px 12px",
                  border: "1px solid #ddd",
                  borderRadius: 4,
                  fontSize: "1rem",
                  boxSizing: "border-box",
                }}
              >
                {MODELS.map((m) => (
                  <option key={m} value={m}>{m.toUpperCase()}</option>
                ))}
              </select>
            </div>

            <div style={{ display: "flex", gap: 16, justifyContent: "flex-end", marginTop: 16 }}>
              <button
                onClick={onClose}
                style={{
                  padding: "8px 22px",
                  border: "1px solid #ddd",
                  borderRadius: 4,
                  backgroundColor: "white",
                  cursor: "pointer",
                  fontSize: "0.9375rem",
                }}
              >
                Cancel
              </button>
              <button
                onClick={handleSave}
                style={{
                  padding: "8px 22px",
                  border: "none",
                  borderRadius: 4,
                  backgroundColor: "#0279c2",
                  color: "white",
                  cursor: "pointer",
                  fontSize: "0.9375rem",
                }}
              >
                Save Changes
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

