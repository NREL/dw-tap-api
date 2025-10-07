import { useContext, useMemo } from "react";
import useSWR from "swr";
import { SettingsContext } from "../providers/SettingsContext";
import { getEnergyProduction, getWindspeedByLatLong } from "../services/api";
import { isOutOfBounds, applyLoss } from "../utils";

export const useEnsembleTilesData = () => {
  const {
    currentPosition,
    hubHeight,
    powerCurve,
    preferredModel: dataModel,
    ensemble,
    lossAssumptionFactor,
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
    ensemble &&
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
      ensemble,
    });
  }, [shouldFetch, lat, lng, hubHeight, powerCurve, dataModel, ensemble]);

  const { isLoading, data, error } = useSWR(
    swrKey,
    async () => {
      const [wind, prod] = await Promise.all([
        getWindspeedByLatLong({
          lat: lat!,
          lng: lng!,
          hubHeight,
          dataModel,
          ensemble,
        }),
        getEnergyProduction({
          lat: lat!,
          lng: lng!,
          hubHeight,
          powerCurve,
          dataModel,
          time_period: "global",
          ensemble,
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

  // Apply loss adjustment to production data
  const productionDataWithLoss = useMemo(() => {
    if (!data?.prod || !data.prod.energy_production) return data?.prod;

    const adjustedProduction = applyLoss(
      Number(data.prod.energy_production),
      lossAssumptionFactor,
      { mode: "floor" }
    );

    return {
      ...data.prod,
      energy_production: adjustedProduction,
    };
  }, [data?.prod, lossAssumptionFactor]);

  return {
    windData: data?.wind,
    productionData: productionDataWithLoss,
    isLoading,
    error,
    hasData: !!data,
    outOfBounds,
    dataModel,
    lat,
    lng,
  };
};
