import { createContext } from "react";
import { DataModel } from "../types/Requests";

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
  preferredModel: DataModel;
}

export interface Settings extends StoredSettings {
  toggleSettings: () => void;
  toggleResults: () => void;
  setCurrentPosition: (position: CurrentPosition) => void;
  setHubHeight: (hubHeight: number) => void;
  setPowerCurve: (curve: string) => void;
  setPreferredModel: (preferredModel: DataModel) => void;
}

export const defaultValues: StoredSettings = {
  settingsOpen: false,
  resultsOpen: false,
  currentPosition: null,
  hubHeight: 30,
  powerCurve: "nrel-reference-100kW",
  preferredModel: "wtk", // default to WTK model
};

export const SettingsContext = createContext<Settings>({
  ...defaultValues,
  toggleSettings: () => {},
  toggleResults: () => {},
  setCurrentPosition: () => {},
  setHubHeight: () => {},
  setPowerCurve: () => {},
  setPreferredModel: () => {},
});