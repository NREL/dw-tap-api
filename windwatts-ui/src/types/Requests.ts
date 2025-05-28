export interface WindspeedByLatLngRequest {
  lat: number;
  lng: number;
  hubHeight: number;
}

export interface EnergyProductionRequest {
  lat: number;
  lng: number;
  hubHeight: number;
  powerCurve: string;
  time_period?: string;
}
