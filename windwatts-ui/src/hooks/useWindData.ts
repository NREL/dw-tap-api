import { useContext } from "react";
import useSWR from "swr";
import { SettingsContext } from "../providers/SettingsContext";
import { getWindspeedByLatLong } from "../services/api";

export const useWindData = () => {
  const { currentPosition, hubHeight } = useContext(SettingsContext);
  const { lat, lng } = currentPosition || {};
  const shouldFetch = lat && lng && hubHeight;

  const {
    isLoading,
    data,
    error,
  } = useSWR(
    shouldFetch ? { lat, lng, hubHeight } : null,
    getWindspeedByLatLong
  );

  return {
    windData: data,
    isLoading,
    error,
    hasData: !!data
  };
}; 