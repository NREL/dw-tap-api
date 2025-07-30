import { useState, useRef, useEffect, useCallback } from "react";
import { useGoogleMaps } from "./useGoogleMaps";

export const useMapView = (
  currentPosition: { lat: number; lng: number } | null
) => {
  const [map, setMap] = useState<google.maps.Map | null>(null);
  const markerRef = useRef<google.maps.marker.AdvancedMarkerElement | null>(
    null
  );
  const { isLoaded } = useGoogleMaps();

  // Map initialization callback
  const onLoad = useCallback((map: google.maps.Map) => setMap(map), []);

  // Automatic marker management when position or map changes
  useEffect(() => {
    if (isLoaded && map && currentPosition && window.google?.maps?.marker) {
      // Remove existing marker if there is one
      if (markerRef.current) {
        markerRef.current.map = null;
      }

      // Create new marker
      const { AdvancedMarkerElement } = window.google.maps.marker;
      const advancedMarker = new AdvancedMarkerElement({
        position: currentPosition,
        map: map,
        title: "Selected Location",
      });

      // Save reference to the new marker
      markerRef.current = advancedMarker;
    }
  }, [isLoaded, map, currentPosition]);

  // Clean up marker on unmount
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
