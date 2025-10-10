import { useEffect, useContext, useRef } from "react";
import { SettingsContext } from "../providers/SettingsContext";
import { DEFAULT_MAP_CENTER, GEOLOCATION_OPTIONS } from "../constants";

export const useGeolocation = () => {
  const { currentPosition, setCurrentPosition } = useContext(SettingsContext);
  const hasAttemptedGeolocation = useRef(false);

  useEffect(() => {
    if (hasAttemptedGeolocation.current) return;

    if (currentPosition !== null) {
      hasAttemptedGeolocation.current = true;
      return;
    }

    hasAttemptedGeolocation.current = true;

    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          setCurrentPosition((current) => {
            if (current !== null) {
              return current;
            }
            return {
              lat: position.coords.latitude,
              lng: position.coords.longitude,
            };
          });
        },
        (error) => {
          console.error("Geolocation error:", error);
          setCurrentPosition((current) =>
            current !== null ? current : DEFAULT_MAP_CENTER
          );
        },
        GEOLOCATION_OPTIONS
      );
    } else {
      setCurrentPosition((current) =>
        current !== null ? current : DEFAULT_MAP_CENTER
      );
    }
  }, [currentPosition, setCurrentPosition]);
};
