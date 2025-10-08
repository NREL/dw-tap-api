import { useEffect, useRef, useState } from "react";

type LatLng = { lat: number; lng: number };

interface ClientOnlyMapProps {
  center: LatLng;
  zoom?: number;
  height?: number | string;
  apiKey?: string;
}

export function ClientOnlyMap({ center, zoom = 12, height = 400, apiKey }: ClientOnlyMapProps) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isClient, setIsClient] = useState(false);

  useEffect(() => {
    setIsClient(true);
  }, []);

  useEffect(() => {
    let canceled = false;
    if (typeof window === "undefined") return;

    async function ensureScript(): Promise<void> {
      if ((window as any).google?.maps) return;
      if (!apiKey) {
        throw new Error("Missing VITE_MAP_API_KEY");
      }
      await new Promise<void>((resolve, reject) => {
        const existing = document.querySelector<HTMLScriptElement>('script[data-ggl="1"]');
        if (existing) {
          existing.addEventListener("load", () => resolve(), { once: true });
          existing.addEventListener("error", () => reject(new Error("Google Maps failed to load")), { once: true });
          return;
        }
        const script = document.createElement("script");
        script.src = `https://maps.googleapis.com/maps/api/js?key=${encodeURIComponent(apiKey)}&libraries=marker,places&v=weekly`;
        script.async = true;
        script.defer = true;
        script.dataset.ggl = "1";
        script.onload = () => resolve();
        script.onerror = () => reject(new Error("Google Maps failed to load"));
        document.head.appendChild(script);
      });
    }

    async function init() {
      try {
        await ensureScript();
        if (canceled) return;
        if (!containerRef.current || !(window as any).google?.maps) return;
        const map = new (window as any).google.maps.Map(containerRef.current, {
          center,
          zoom,
          mapTypeControl: false,
          streetViewControl: false,
          fullscreenControl: false,
        });
        // Add a basic marker
        new (window as any).google.maps.Marker({ position: center, map });
      } catch (e) {
        if (!canceled) setError(e instanceof Error ? e.message : String(e));
      }
    }

    if (isClient) {
      console.log("ClientOnlyMap: init", { hasApiKey: Boolean(apiKey), center, zoom });
      init();
      // In case dev HMR interferes, try again shortly
      setTimeout(() => {
        if (!(window as any).google?.maps) {
          console.log("ClientOnlyMap: retry loading google maps script");
          init();
        }
      }, 500);
    }
    return () => {
      canceled = true;
    };
  }, [center, zoom, isClient]);

  // Always render the same DOM on server and client; only enhance on client
  const heightStyle = typeof height === "number" ? `${height}px` : height;

  return (
    <div data-qa="map-wrapper" style={{ height: heightStyle }}>
      <div ref={containerRef} data-qa="map-container" style={{ width: "100%", height: "100%" }} />
      {error ? (
        <div data-qa="map-error" style={{ color: "#b00020", fontSize: 12, paddingTop: 8 }}>
          {error}
        </div>
      ) : null}
    </div>
  );
}


