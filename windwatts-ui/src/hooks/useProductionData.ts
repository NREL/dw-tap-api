import { useContext, useMemo } from "react";
import useSWR from "swr";
import { SettingsContext } from "../providers/SettingsContext";
import { getEnergyProduction } from "../services/api";
import { isOutOfBounds } from "../utils";

export const useProductionData = () => {
  const {
    currentPosition,
    hubHeight,
    powerCurve,
    preferredModel: dataModel,
  } = useContext(SettingsContext);
  const { lat, lng } = currentPosition || {};
  const outOfBounds =
    lat && lng && dataModel ? isOutOfBounds(lat, lng, dataModel) : false;
  const shouldFetch =
    lat && lng && hubHeight && powerCurve && dataModel && !outOfBounds;

  // Memoize the SWR key to prevent unnecessary re-renders
  const swrKey = useMemo(() => {
    if (!shouldFetch) return null;
    return JSON.stringify({
      lat,
      lng,
      hubHeight,
      powerCurve,
      dataModel,
      time_period: "all",
    });
  }, [shouldFetch, lat, lng, hubHeight, powerCurve, dataModel]);

  const { isLoading, data, error } = useSWR(
    swrKey,
    () =>
      getEnergyProduction({
        lat: lat!,
        lng: lng!,
        hubHeight,
        powerCurve,
        dataModel,
        time_period: "all",
      }),
    {
      revalidateOnFocus: false,
      revalidateOnReconnect: false,
      revalidateIfStale: false,
      dedupingInterval: 0,
    }
  );

  return {
    productionData: data,
    isLoading,
    error,
    hasData: !!data,
    outOfBounds,
    dataModel,
    lat,
    lng,
  };
};
