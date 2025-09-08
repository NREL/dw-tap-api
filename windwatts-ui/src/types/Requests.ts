import { DataModel } from "./DataModel";

export interface WindspeedByLatLngRequest {
  lat: number;
  lng: number;
  hubHeight: number;
  dataModel: DataModel;
  biasCorrection?: boolean;
}

export interface EnergyProductionRequest {
  lat: number;
  lng: number;
  hubHeight: number;
  powerCurve: string;
  dataModel: DataModel;
  time_period?: string;
  biasCorrection?: boolean;
}
