import { useContext, useMemo } from "react";
import useSWR from "swr";
import { SettingsContext } from "../providers/SettingsContext";
import { getWindspeedByLatLong } from "../services/api";
import { applyLoss, isOutOfBounds } from "../utils";

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

  // Memoize the SWR key to prevent unnecessary re-renders
  const swrKey = useMemo(() => {
    if (!shouldFetch) return null;
    return JSON.stringify({ lat, lng, hubHeight, dataModel });
  }, [shouldFetch, lat, lng, hubHeight, dataModel]);

  const { isLoading, data, error } = useSWR(
    swrKey,
    () =>
      getWindspeedByLatLong({
        lat: lat!,
        lng: lng!,
        hubHeight,
        dataModel,
      }),
    {
      revalidateOnFocus: false,
      revalidateOnReconnect: false,
      revalidateIfStale: false,
      dedupingInterval: 0,
    }
  );

  const { lossAssumptionFactor } = useContext(SettingsContext);
  const windData = useMemo(() => {
    if (!data) return data;
    try {
      const clone = structuredClone
        ? structuredClone(data)
        : JSON.parse(JSON.stringify(data));
      if (clone.global_avg != null) {
        clone.global_avg = applyLoss(
          Number(clone.global_avg),
          lossAssumptionFactor,
          { mode: "floor", digits: 2 }
        );
      }
      return clone;
    } catch {
      return data;
    }
  }, [data, lossAssumptionFactor]);

  return {
    windData,
    isLoading,
    error,
    hasData: !!data,
    outOfBounds,
    dataModel,
    lat,
    lng,
  };
};
