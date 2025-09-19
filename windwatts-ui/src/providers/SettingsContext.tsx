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
  ensemble: boolean;
  // Loss assumption factor stored as inverse percentage (e.g., 0.83 for 17%)
  lossAssumptionFactor: number;
}

export interface Settings extends StoredSettings {
  // Derived value for convenience (0-100)
  lossAssumptionPercent: number;
  toggleSettings: () => void;
  toggleResults: () => void;
  setCurrentPosition: (position: CurrentPosition) => void;
  setHubHeight: (hubHeight: number) => void;
  setPowerCurve: (curve: string) => void;
  setPreferredModel: (preferredModel: DataModel) => void;
  setEnsemble: (ensemble: boolean) => void;
  setLossAssumptionFactor: (factor: number) => void;
  setLossAssumptionPercent: (percent: number) => void;
}

export const defaultValues: StoredSettings = {
  settingsOpen: false,
  resultsOpen: false,
  currentPosition: null,
  hubHeight: 40, // default hub height in meters
  powerCurve: "nrel-reference-100kW", // default power curve
  preferredModel: "era5", // default to era5 model
  ensemble: false,
  lossAssumptionFactor: 0.83, // default to 17% loss
};

export const SettingsContext = createContext<Settings>({
  ...defaultValues,
  lossAssumptionPercent: 17,
  toggleSettings: () => {},
  toggleResults: () => {},
  setCurrentPosition: () => {},
  setHubHeight: () => {},
  setPowerCurve: () => {},
  setPreferredModel: () => {},
  setEnsemble: () => {},
  setLossAssumptionFactor: () => {},
  setLossAssumptionPercent: () => {},
});
