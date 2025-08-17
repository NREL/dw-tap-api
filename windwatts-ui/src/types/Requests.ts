import { DataModel } from "./DataModel";

export interface WindspeedByLatLngRequest {
  lat: number;
  lng: number;
  hubHeight: number;
  dataModel: DataModel;
}

export interface EnergyProductionRequest {
  lat: number;
  lng: number;
  hubHeight: number;
  powerCurve: string;
  dataModel: DataModel;
  time_period?: string;
}
