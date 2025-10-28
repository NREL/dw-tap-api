import { DataModel } from "./DataModel";

export interface WindspeedByLatLngRequest {
  lat: number;
  lng: number;
  hubHeight: number;
  dataModel: DataModel;
  ensemble?: boolean;
}

export interface EnergyProductionRequest {
  lat: number;
  lng: number;
  hubHeight: number;
  powerCurve: string;
  dataModel: DataModel;
  time_period?: string;
  ensemble?: boolean;
}

export interface NearestGridLocationRequest {
  lat: number;
  lng: number;
  n_neighbors?: number;
  dataModel: DataModel;
}

export interface DownloadCSVRequest {
  lat: number;
  lng: number;
  n_neighbors?: number;
  dataModel: DataModel;
  gridLat: number;
  gridLng: number;
}
