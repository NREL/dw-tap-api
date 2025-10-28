"use client";

import { useState, useMemo, useCallback, useEffect } from "react";
import {
  SettingsContext,
  defaultValues,
  type CurrentPosition,
  type StoredSettings
} from "./SettingsContext";
import type { DataModel } from "../types/DataModel";

export function SettingsProvider({ children }: { children: React.ReactNode }) {
  const [settings, setSettings] = useState<StoredSettings>({ ...defaultValues });

  useEffect(() => {
    // could sync URL here if needed
  }, [settings]);

  const setCurrentPosition = useCallback(
    (
      position: CurrentPosition | null | ((prev: CurrentPosition | null) => CurrentPosition | null)
    ) => {
      setSettings((current) => ({
        ...current,
        currentPosition: typeof position === "function" ? position(current.currentPosition) : position
      }));
    },
    []
  );

  const setZoom = useCallback((zoom: number) => {
    setSettings((current) => ({ ...current, zoom: Math.round(zoom) }));
  }, []);

  const setHubHeight = useCallback((height: number) => {
    setSettings((current) => ({ ...current, hubHeight: height }));
  }, []);

  const setPowerCurve = useCallback((curve: string) => {
    setSettings((current) => ({ ...current, powerCurve: curve }));
  }, []);

  const setPreferredModel = useCallback((model: DataModel) => {
    setSettings((current) => ({ ...current, preferredModel: model }));
  }, []);

  const setEnsemble = useCallback((ensemble: boolean) => {
    setSettings((current) => ({ ...current, ensemble }));
  }, []);

  const setLossAssumptionFactor = useCallback((factor: number) => {
    const clamped = Math.max(0, Math.min(1, Number(factor)));
    setSettings((current) => ({ ...current, lossAssumptionFactor: clamped }));
  }, []);

  const setLossAssumptionPercent = useCallback((percent: number) => {
    const num = Math.max(0, Math.min(100, Number(percent)));
    const factor = (100 - num) / 100;
    setLossAssumptionFactor(factor);
  }, [setLossAssumptionFactor]);

  const toggleSettings = useCallback(() => {
    setSettings((current) => ({ ...current, settingsOpen: !current.settingsOpen }));
  }, []);

  const toggleResults = useCallback(() => {
    setSettings((current) => ({ ...current, resultsOpen: !current.resultsOpen }));
  }, []);

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
      lossAssumptionFactor: settings.lossAssumptionFactor ?? defaultValues.lossAssumptionFactor,
      lossAssumptionPercent: Math.round((1 - (settings.lossAssumptionFactor ?? defaultValues.lossAssumptionFactor)) * 100),
      setLossAssumptionFactor,
      setLossAssumptionPercent
    }),
    [settings, setCurrentPosition, setZoom, setHubHeight, setPowerCurve, setPreferredModel, setEnsemble, setLossAssumptionFactor, setLossAssumptionPercent, toggleSettings, toggleResults]
  );

  return <SettingsContext.Provider value={contextValue}>{children}</SettingsContext.Provider>;
}
