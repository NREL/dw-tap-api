import { useState, useMemo, useCallback, useEffect } from "react";
import {
  SettingsContext,
  defaultValues,
  CurrentPosition,
  StoredSettings,
} from "./SettingsContext";
import { DataModel } from "../types";
import { percentToFactor } from "../utils";
import {
  parseUrlParams,
  buildUrlFromSettings,
  hasLaunchParams,
  URL_PARAM_DEFAULTS,
} from "../utils/urlParams";

export function SettingsProvider({ children }: { children: React.ReactNode }) {
  const [settings, setSettings] = useState<StoredSettings>(() => {
    const urlParams = parseUrlParams();

    if (hasLaunchParams(urlParams)) {
      return {
        ...defaultValues,
        currentPosition: {
          lat: urlParams.lat!,
          lng: urlParams.lng!,
        },
        zoom: urlParams.zoom ?? URL_PARAM_DEFAULTS.zoom,
        hubHeight: urlParams.hubHeight ?? URL_PARAM_DEFAULTS.hubHeight,
        powerCurve: urlParams.powerCurve ?? URL_PARAM_DEFAULTS.powerCurve,
        preferredModel: urlParams.dataModel ?? URL_PARAM_DEFAULTS.dataModel,
        ensemble: urlParams.ensemble ?? URL_PARAM_DEFAULTS.ensemble,
        lossAssumptionFactor:
          urlParams.lossAssumption !== undefined
            ? percentToFactor(urlParams.lossAssumption)
            : defaultValues.lossAssumptionFactor,
      };
    }

    return {
      ...defaultValues,
      currentPosition: null,
    };
  });

  useEffect(() => {
    if (!settings.currentPosition) {
      return;
    }

    const url = buildUrlFromSettings({
      currentPosition: settings.currentPosition,
      zoom: settings.zoom,
      hubHeight: settings.hubHeight,
      powerCurve: settings.powerCurve,
      preferredModel: settings.preferredModel,
      ensemble: settings.ensemble,
      lossAssumptionPercent: Math.round(
        (1 - settings.lossAssumptionFactor) * 100
      ),
    });

    if (url !== "/") {
      window.history.replaceState({}, "", url);
    }
  }, [
    settings.currentPosition,
    settings.zoom,
    settings.hubHeight,
    settings.powerCurve,
    settings.preferredModel,
    settings.ensemble,
    settings.lossAssumptionFactor,
  ]);

  const setCurrentPosition = useCallback(
    (
      position:
        | CurrentPosition
        | null
        | ((prev: CurrentPosition | null) => CurrentPosition | null)
    ) => {
      setSettings((current) => ({
        ...current,
        currentPosition:
          typeof position === "function"
            ? position(current.currentPosition)
            : position,
      }));
    },
    []
  );

  const setZoom = useCallback((zoom: number) => {
    const rounded = Math.round(zoom);
    setSettings((current) => ({ ...current, zoom: rounded }));
  }, []);

  const setHubHeight = useCallback((height: number) => {
    setSettings((current) => ({ ...current, hubHeight: height }));
  }, []);

  const setPowerCurve = useCallback(
    (curve: string) => {
      setSettings((current) => ({ ...current, powerCurve: curve }));
    },
    [setSettings]
  );

  const setPreferredModel = useCallback(
    (model: DataModel) => {
      setSettings((current) => ({ ...current, preferredModel: model }));
    },
    [setSettings]
  );

  const setEnsemble = useCallback(
    (ensemble: boolean) => {
      setSettings((current) => ({ ...current, ensemble }));
    },
    [setSettings]
  );

  const setLossAssumptionFactor = useCallback(
    (factor: number) => {
      const clamped = Math.max(0, Math.min(1, Number(factor)));
      setSettings((current) => ({ ...current, lossAssumptionFactor: clamped }));
    },
    [setSettings]
  );

  const setLossAssumptionPercent = useCallback(
    (percent: number) => {
      const factor = percentToFactor(percent);
      setLossAssumptionFactor(factor);
    },
    [setLossAssumptionFactor]
  );

  // Toggle functions that update the settings directly
  const toggleSettings = useCallback(() => {
    setSettings((current) => ({
      ...current,
      settingsOpen: !current.settingsOpen,
    }));
  }, [setSettings]);

  const toggleResults = useCallback(() => {
    setSettings((current) => ({
      ...current,
      resultsOpen: !current.resultsOpen,
    }));
  }, [setSettings]);

  // Memoize the provider value to prevent unnecessary re-renders
  const contextValue = useMemo(
    () => ({
      settingsOpen: settings.settingsOpen,
      toggleSettings,
      resultsOpen: settings.resultsOpen,
      toggleResults,
      currentPosition: settings.currentPosition,
      setCurrentPosition,
      zoom: settings.zoom,
      setZoom,
      hubHeight: settings.hubHeight,
      setHubHeight,
      powerCurve: settings.powerCurve,
      setPowerCurve,
      preferredModel: settings.preferredModel,
      setPreferredModel,
      ensemble: settings.ensemble,
      setEnsemble,
      lossAssumptionFactor:
        settings.lossAssumptionFactor ?? defaultValues.lossAssumptionFactor,
      lossAssumptionPercent: Math.round(
        (1 -
          (settings.lossAssumptionFactor ??
            defaultValues.lossAssumptionFactor)) *
          100
      ),
      setLossAssumptionFactor,
      setLossAssumptionPercent,
    }),
    [
      settings.settingsOpen,
      settings.resultsOpen,
      settings.currentPosition,
      settings.zoom,
      settings.hubHeight,
      settings.powerCurve,
      settings.preferredModel,
      settings.ensemble,
      settings.lossAssumptionFactor,
      toggleSettings,
      toggleResults,
      setCurrentPosition,
      setZoom,
      setHubHeight,
      setPowerCurve,
      setPreferredModel,
      setEnsemble,
      setLossAssumptionFactor,
      setLossAssumptionPercent,
    ]
  );

  return (
    <SettingsContext.Provider value={contextValue}>
      {children}
    </SettingsContext.Provider>
  );
}
