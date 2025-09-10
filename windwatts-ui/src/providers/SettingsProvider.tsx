import { useLocalStorage } from "../hooks";
import { useMemo, useCallback } from "react";
import {
  SettingsContext,
  defaultValues,
  CurrentPosition,
  StoredSettings,
} from "./SettingsContext";
import { DataModel } from "../types";

export function SettingsProvider({ children }: { children: React.ReactNode }) {
  // Use the useLocalStorage hook to manage settings
  const [settings, setSettings] = useLocalStorage<StoredSettings>(
    "settings",
    defaultValues
  );

  // Create setters that update localStorage
  const setCurrentPosition = useCallback(
    (position: CurrentPosition | null) => {
      setSettings((current) => ({ ...current, currentPosition: position }));
    },
    [setSettings]
  );

  const setHubHeight = useCallback(
    (height: number) => {
      setSettings((current) => ({ ...current, hubHeight: height }));
    },
    [setSettings]
  );

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

  const setBiasCorrection = useCallback(
    (biasCorrection: boolean) => {
      setSettings((current) => ({ ...current, biasCorrection }));
    },
    [setSettings]
  );

  // Loss assumption: stored as factor (0-1). Default to 0.83 if missing
  const setLossAssumptionFactor = useCallback(
    (factor: number) => {
      const clamped = Math.max(0, Math.min(1, Number(factor)));
      setSettings((current) => ({ ...current, lossAssumptionFactor: clamped }));
    },
    [setSettings]
  );

  const setLossAssumptionPercent = useCallback(
    (percent: number) => {
      const num = Number(percent);
      const clampedPercent = Math.max(0, Math.min(100, isNaN(num) ? 0 : num));
      const factor = (100 - clampedPercent) / 100;
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
      hubHeight: settings.hubHeight,
      setHubHeight,
      powerCurve: settings.powerCurve,
      setPowerCurve,
      preferredModel: settings.preferredModel,
      setPreferredModel,
      biasCorrection: settings.biasCorrection,
      setBiasCorrection,
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
      settings.hubHeight,
      settings.powerCurve,
      settings.preferredModel,
      settings.biasCorrection,
      settings.lossAssumptionFactor,
      toggleSettings,
      toggleResults,
      setCurrentPosition,
      setHubHeight,
      setPowerCurve,
      setPreferredModel,
      setBiasCorrection,
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
