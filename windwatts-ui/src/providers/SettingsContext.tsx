import { createContext, useState, useEffect } from "react";
import useToggle from "../hooks/useToggle";

export interface CurrentPosition {
  lat: number;
  lng: number;
}

export interface StoredSettings {
  settingsOpen: boolean;
  resultsOpen: boolean;
  currentPosition: CurrentPosition | null;
  hubHeight: number;
  powerCurve: string;
}

export interface Settings extends StoredSettings {
  toggleSettings: () => void;
  toggleResults: () => void;
  setCurrentPosition: (position: CurrentPosition) => void;
  setHubHeight: (hubHeight: number) => void;
  setPowerCurve: (curve: string) => void;
}

const defaultValues: StoredSettings = {
  settingsOpen: false,
  resultsOpen: false,
  currentPosition: null,
  hubHeight: 30,
  powerCurve: "nrel-reference-100kW",
};

export const SettingsContext = createContext<Settings>({
  ...defaultValues,
  toggleSettings: () => {},
  toggleResults: () => {},
  setCurrentPosition: () => {},
  setHubHeight: () => {},
  setPowerCurve: () => {},
});

function getStoredSettings(): StoredSettings {
  const storedSettings = localStorage.getItem("settings");
  return storedSettings ? JSON.parse(storedSettings) : defaultValues;
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

  useEffect(() => {
    const settings = {
      settingsOpen,
      resultsOpen,
      currentPosition,
      hubHeight,
      powerCurve,
    };
    localStorage.setItem("settings", JSON.stringify(settings));
  }, [settingsOpen, resultsOpen, currentPosition, hubHeight, powerCurve]);

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
      }}
    >
      {children}
    </SettingsContext.Provider>
  );
}
