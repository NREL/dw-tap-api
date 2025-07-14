import { useState, useEffect } from "react";
import useToggle from "../hooks/useToggle";
import {
  SettingsContext,
  defaultValues,
  CurrentPosition,
  StoredSettings,
} from "./SettingsContext";

function getStoredSettings(): StoredSettings {
  const storedSettings = localStorage.getItem("settings");
  const retrievedSettings = storedSettings ? JSON.parse(storedSettings) : {};
  return {
    ...defaultValues, // default values
    ...retrievedSettings, // override with stored values
  };
}

export default function SettingsProvider({
  children,
}: {
  children: React.ReactNode;
}) {
  const storedSettings = getStoredSettings();

  // setting modal states
  const [settingsOpen, toggleSettings] = useToggle(storedSettings.settingsOpen);

  // Results modal states
  const [resultsOpen, toggleResults] = useToggle(storedSettings.resultsOpen);

  // main app inputs
  const [currentPosition, setCurrentPosition] =
    useState<CurrentPosition | null>(storedSettings.currentPosition);
  const [hubHeight, setHubHeight] = useState(storedSettings.hubHeight);
  const [powerCurve, setPowerCurve] = useState(storedSettings.powerCurve);
  const [preferredModel, setPreferredModel] = useState(
    storedSettings.preferredModel
  );

  useEffect(() => {
    const settings = {
      settingsOpen,
      resultsOpen,
      currentPosition,
      hubHeight,
      powerCurve,
      preferredModel,
    };
    localStorage.setItem("settings", JSON.stringify(settings));
  }, [
    settingsOpen,
    resultsOpen,
    currentPosition,
    hubHeight,
    powerCurve,
    preferredModel,
  ]);

  return (
    <SettingsContext.Provider
      value={{
        settingsOpen,
        toggleSettings,
        resultsOpen,
        toggleResults,
        currentPosition,
        setCurrentPosition,
        hubHeight,
        setHubHeight,
        powerCurve,
        setPowerCurve,
        preferredModel,
        setPreferredModel,
      }}
    >
      {children}
    </SettingsContext.Provider>
  );
}
