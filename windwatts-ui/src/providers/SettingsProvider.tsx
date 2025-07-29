import { useLocalStorage } from "../hooks";
import { useMemo, useCallback } from "react";
import {
  SettingsContext,
  defaultValues,
  CurrentPosition,
  StoredSettings,
} from "./SettingsContext";
import { DataModel } from "../types";

export default function SettingsProvider({
  children,
}: {
  children: React.ReactNode;
}) {
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
    }),
    [
      settings.settingsOpen,
      settings.resultsOpen,
      settings.currentPosition,
      settings.hubHeight,
      settings.powerCurve,
      settings.preferredModel,
      toggleSettings,
      toggleResults,
      setCurrentPosition,
      setHubHeight,
      setPowerCurve,
      setPreferredModel,
    ]
  );

  return (
    <SettingsContext.Provider value={contextValue}>
      {children}
    </SettingsContext.Provider>
  );
}
