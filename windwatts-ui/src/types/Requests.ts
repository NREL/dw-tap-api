import { Data } from "@react-google-maps/api";

export type DataModel = 'wtk' | 'era5';

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
  dataModel: Data;
  time_period?: string;
}
