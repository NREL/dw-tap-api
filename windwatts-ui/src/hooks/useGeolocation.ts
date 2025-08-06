import { useEffect, useContext } from "react";
import { SettingsContext } from "../providers/SettingsContext";
import { DEFAULT_MAP_CENTER } from "../constants";

export const useGeolocation = () => {
  const { setCurrentPosition } = useContext(SettingsContext);

  useEffect(() => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          setCurrentPosition({
            lat: position.coords.latitude,
            lng: position.coords.longitude,
          });
        },
        (error) => {
          console.error("Geolocation error:", error);
          setCurrentPosition(DEFAULT_MAP_CENTER);
        },
        { maximumAge: 60000, timeout: 5000, enableHighAccuracy: true }
      );
    }
  }, [setCurrentPosition]);
};
