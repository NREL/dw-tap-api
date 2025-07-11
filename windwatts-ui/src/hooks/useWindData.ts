import { useContext } from "react";
import useSWR from "swr";
import { SettingsContext } from "../providers/SettingsContext";
import { getWindspeedByLatLong } from "../services/api";
import { isOutOfBounds } from "../utils";

export const useWindData = () => {
  const {
    currentPosition,
    hubHeight,
    preferredModel: dataModel,
  } = useContext(SettingsContext);
  const { lat, lng } = currentPosition || {};
  const outOfBounds =
    lat && lng && dataModel ? isOutOfBounds(lat, lng, dataModel) : false;
  const shouldFetch = lat && lng && hubHeight && dataModel && !outOfBounds;

  const { isLoading, data, error } = useSWR(
    shouldFetch ? { lat, lng, hubHeight, dataModel } : null,
    getWindspeedByLatLong
  );

  return {
    windData: data,
    isLoading,
    error,
    hasData: !!data,
    outOfBounds,
    dataModel,
    lat,
    lng,
  };
};
