import { useToggle, useLocalStorage } from "../hooks";
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

  // setting modal states
  const [settingsOpen, toggleSettings] = useToggle(settings.settingsOpen);

  // Results modal states
  const [resultsOpen, toggleResults] = useToggle(settings.resultsOpen);

  // Update localStorage whenever any setting changes
  const updateSettings = (updates: Partial<StoredSettings>) => {
    const newSettings = { ...settings, ...updates };
    setSettings(newSettings);
  };

  // Create setters that update localStorage
  const setCurrentPosition = (position: CurrentPosition | null) => {
    updateSettings({ currentPosition: position });
  };

  const setHubHeight = (height: number) => {
    updateSettings({ hubHeight: height });
  };

  const setPowerCurve = (curve: string) => {
    updateSettings({ powerCurve: curve });
  };

  const setPreferredModel = (model: DataModel) => {
    updateSettings({ preferredModel: model });
  };

  return (
    <SettingsContext.Provider
      value={{
        settingsOpen,
        toggleSettings,
        resultsOpen,
        toggleResults,
        currentPosition: settings.currentPosition,
        setCurrentPosition,
        hubHeight: settings.hubHeight,
        setHubHeight,
        powerCurve: settings.powerCurve,
        setPowerCurve,
        preferredModel: settings.preferredModel,
        setPreferredModel,
      }}
    >
      {children}
    </SettingsContext.Provider>
  );
}
