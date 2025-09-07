import { createContext } from "react";
import { DataModel } from "../types";

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
  biasCorrection: boolean;
}

export interface Settings extends StoredSettings {
  toggleSettings: () => void;
  toggleResults: () => void;
  setCurrentPosition: (position: CurrentPosition) => void;
  setHubHeight: (hubHeight: number) => void;
  setPowerCurve: (curve: string) => void;
  setPreferredModel: (preferredModel: DataModel) => void;
  setBiasCorrection: (biasCorrection: boolean) => void;
}

export const defaultValues: StoredSettings = {
  settingsOpen: false,
  resultsOpen: false,
  currentPosition: null,
  hubHeight: 40, // default hub height in meters
  powerCurve: "nrel-reference-100kW", // default power curve
  preferredModel: "era5", // default to era5 model
  biasCorrection: false,
};

export const SettingsContext = createContext<Settings>({
  ...defaultValues,
  toggleSettings: () => {},
  toggleResults: () => {},
  setCurrentPosition: () => {},
  setHubHeight: () => {},
  setPowerCurve: () => {},
  setPreferredModel: () => {},
  setBiasCorrection: () => {},
});
