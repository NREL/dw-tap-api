import { useState, useRef, useEffect, useCallback } from "react";
import { useGoogleMaps } from "./useGoogleMaps";

export const useMapView = (
  currentPosition: { lat: number; lng: number } | null,
  zoom: number,
  setZoom: (zoom: number) => void
) => {
  const [map, setMap] = useState<google.maps.Map | null>(null);
  const markerRef = useRef<google.maps.marker.AdvancedMarkerElement | null>(
    null
  );
  const hasSetInitialZoom = useRef(false);
  const { isLoaded } = useGoogleMaps();

  const onLoad = useCallback(
    (map: google.maps.Map) => {
      setMap(map);
      if (!hasSetInitialZoom.current) {
        map.setZoom(zoom);
        hasSetInitialZoom.current = true;
      }
    },
    [zoom]
  );

  useEffect(() => {
    if (isLoaded && map && currentPosition && window.google?.maps?.marker) {
      if (markerRef.current) {
        markerRef.current.map = null;
      }

      const { AdvancedMarkerElement } = window.google.maps.marker;
      const advancedMarker = new AdvancedMarkerElement({
        position: currentPosition,
        map: map,
        title: "Selected Location",
      });

      markerRef.current = advancedMarker;
    }
  }, [isLoaded, map, currentPosition]);

  useEffect(() => {
    if (!map) return;

    const listener = map.addListener("zoom_changed", () => {
      const newZoom = map.getZoom();
      if (newZoom !== undefined && newZoom !== zoom) {
        setZoom(newZoom);
      }
    });

    return () => {
      google.maps.event.removeListener(listener);
    };
  }, [map, zoom, setZoom]);

  useEffect(() => {
    return () => {
      if (markerRef.current) {
        markerRef.current.map = null;
      }
    };
  }, []);

  return {
    isLoaded,
    onLoad,
  };
};
