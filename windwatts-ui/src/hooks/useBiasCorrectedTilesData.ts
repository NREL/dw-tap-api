import { useContext, useMemo } from "react";
import useSWR from "swr";
import { SettingsContext } from "../providers/SettingsContext";
import { getEnergyProduction, getWindspeedByLatLong } from "../services/api";
import { isOutOfBounds } from "../utils";

export const useBiasCorrectedTilesData = () => {
  const {
    currentPosition,
    hubHeight,
    powerCurve,
    preferredModel: dataModel,
    biasCorrection,
  } = useContext(SettingsContext);

  const { lat, lng } = currentPosition || {};
  const outOfBounds =
    lat && lng && dataModel ? isOutOfBounds(lat, lng, dataModel) : false;
  const shouldFetch = !!(
    lat &&
    lng &&
    hubHeight &&
    powerCurve &&
    dataModel &&
    biasCorrection &&
    !outOfBounds
  );

  const swrKey = useMemo(() => {
    if (!shouldFetch) return null;
    return JSON.stringify({
      lat,
      lng,
      hubHeight,
      powerCurve,
      dataModel,
      biasCorrection: true,
    });
  }, [shouldFetch, lat, lng, hubHeight, powerCurve, dataModel]);

  const { isLoading, data, error } = useSWR(
    swrKey,
    async () => {
      const [wind, prod] = await Promise.all([
        getWindspeedByLatLong({
          lat: lat!,
          lng: lng!,
          hubHeight,
          dataModel,
          biasCorrection: true,
        }),
        getEnergyProduction({
          lat: lat!,
          lng: lng!,
          hubHeight,
          powerCurve,
          dataModel,
          time_period: "global",
          biasCorrection: true,
        }),
      ]);
      return { wind, prod };
    },
    {
      revalidateOnFocus: false,
      revalidateOnReconnect: false,
      revalidateIfStale: false,
      dedupingInterval: 0,
    }
  );

  return {
    windData: data?.wind,
    productionData: data?.prod,
    isLoading,
    error,
    hasData: !!data,
    outOfBounds,
    dataModel,
    lat,
    lng,
  };
};
