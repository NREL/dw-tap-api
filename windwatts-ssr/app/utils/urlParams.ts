// Constants
export const DEFAULT_LAT = 39.7392;
export const DEFAULT_LNG = -104.9903;
export const DEFAULT_HUB = 40;
export const DEFAULT_MODEL = "era5";
export const DEFAULT_POWER_CURVE = "nrel-reference-100kW";

export const VALID_MODELS = ["era5", "wtk"];
export const VALID_HUB_HEIGHTS = [30, 40, 50, 60, 80, 100, 120, 140];
export const VALID_POWER_CURVES = [
  "nrel-reference-2.5kW",
  "nrel-reference-100kW",
  "nrel-reference-250kW",
  "nrel-reference-2000kW",
];

// Model coordinate bounds
export const MODEL_COORDINATES_BOUNDS: Record<
  string,
  {
    minLat: number;
    maxLat: number;
    minLng: number;
    maxLng: number;
  }
> = {
  era5: {
    minLat: 23.402,
    maxLat: 51.403,
    minLng: -137.725,
    maxLng: -44.224,
  },
  wtk: {
    minLat: 7.75129,
    maxLat: 78.392685,
    minLng: -179.99918,
    maxLng: 180.0,
  },
};

// Validation helpers
function isValidLatitude(lat: number): boolean {
  return !isNaN(lat) && lat >= -90 && lat <= 90;
}

function isValidLongitude(lng: number): boolean {
  return !isNaN(lng) && lng >= -180 && lng <= 180;
}

function isValidHubHeight(height: number): boolean {
  return VALID_HUB_HEIGHTS.includes(height);
}

function isValidModel(model: string): boolean {
  return VALID_MODELS.includes(model);
}

function isValidPowerCurve(curve: string): boolean {
  return VALID_POWER_CURVES.includes(curve);
}

export interface LocationParams {
  lat: number;
  lng: number;
  hubHeight: number;
  model: string;
  powerCurve: string;
  lossAssumption: number; // Loss factor (0-1), default 0.83 (17% loss)
}

/**
 * Check if coordinates are within model bounds
 */
export function isOutOfBounds(
  lat: number,
  lng: number,
  model: string
): boolean {
  const bounds = MODEL_COORDINATES_BOUNDS[model];
  if (!bounds) return false;
  return (
    lat < bounds.minLat ||
    lat > bounds.maxLat ||
    lng < bounds.minLng ||
    lng > bounds.maxLng
  );
}

/**
 * Get user-friendly out of bounds message
 */
export function getOutOfBoundsMessage(
  lat: number,
  lng: number,
  model: string
): string {
  const bounds = MODEL_COORDINATES_BOUNDS[model];
  if (!bounds) return "Location is out of bounds.";

  const modelName = model.toUpperCase();
  return `The selected location (${lat.toFixed(2)}, ${lng.toFixed(
    2
  )}) is outside the ${modelName} data coverage area. ${modelName} data is available for latitudes ${
    bounds.minLat
  }° to ${bounds.maxLat}° and longitudes ${bounds.minLng}° to ${
    bounds.maxLng
  }°.`;
}

/**
 * Parse and validate URL parameters for location and settings
 * Supports both query params (?lat=40&lng=-105) and path params (/:lat/:lng)
 */
export function parseLocationParams(url: URL): LocationParams {
  // Try query params first
  const latParam = url.searchParams.get("lat");
  const lngParam = url.searchParams.get("lng");
  const hubParam = url.searchParams.get("hubHeight");
  const modelParam = url.searchParams.get("model");
  const powerCurveParam = url.searchParams.get("powerCurve");
  const lossParam = url.searchParams.get("lossAssumption");

  // Parse and validate latitude
  let lat = latParam ? Number(latParam) : DEFAULT_LAT;
  if (!isValidLatitude(lat)) {
    console.warn(
      `Invalid latitude: ${latParam}, using default: ${DEFAULT_LAT}`
    );
    lat = DEFAULT_LAT;
  }

  // Parse and validate longitude
  let lng = lngParam ? Number(lngParam) : DEFAULT_LNG;
  if (!isValidLongitude(lng)) {
    console.warn(
      `Invalid longitude: ${lngParam}, using default: ${DEFAULT_LNG}`
    );
    lng = DEFAULT_LNG;
  }

  // Parse and validate hub height
  let hubHeight = hubParam ? Number(hubParam) : DEFAULT_HUB;
  if (!isValidHubHeight(hubHeight)) {
    console.warn(
      `Invalid hub height: ${hubParam}, using default: ${DEFAULT_HUB}`
    );
    hubHeight = DEFAULT_HUB;
  }

  // Validate model
  let model = modelParam || DEFAULT_MODEL;
  if (!isValidModel(model)) {
    console.warn(
      `Invalid model: ${modelParam}, using default: ${DEFAULT_MODEL}`
    );
    model = DEFAULT_MODEL;
  }

  // Validate power curve
  let powerCurve = powerCurveParam || DEFAULT_POWER_CURVE;
  if (!isValidPowerCurve(powerCurve)) {
    console.warn(
      `Invalid power curve: ${powerCurveParam}, using default: ${DEFAULT_POWER_CURVE}`
    );
    powerCurve = DEFAULT_POWER_CURVE;
  }

  // Parse loss assumption (default 0.83 = 17% loss, matching original UI)
  let lossAssumption = lossParam ? Number(lossParam) : 0.83;
  if (isNaN(lossAssumption) || lossAssumption < 0 || lossAssumption > 1) {
    console.warn(`Invalid loss assumption: ${lossParam}, using default: 0.83`);
    lossAssumption = 0.83;
  }

  return { lat, lng, hubHeight, model, powerCurve, lossAssumption };
}

/**
 * Generate a shareable URL with current location and settings
 */
export function generateShareableUrl(
  params: LocationParams,
  baseUrl?: string
): string {
  const base = baseUrl || "";
  const urlParams = new URLSearchParams();

  // Always include required params
  urlParams.set("lat", params.lat.toFixed(4));
  urlParams.set("lng", params.lng.toFixed(4));
  urlParams.set("hubHeight", String(params.hubHeight));
  urlParams.set("model", params.model);
  urlParams.set("powerCurve", params.powerCurve);

  // Only include loss assumption if not default (0.83)
  if (params.lossAssumption !== 0.83) {
    urlParams.set("lossAssumption", params.lossAssumption.toFixed(2));
  }

  return `${base}?${urlParams.toString()}`;
}

/**
 * Parse legacy URL formats for backwards compatibility
 * Example: /location/40.5/-105.2/hub/80
 */
export function parseLegacyPathParams(
  pathname: string
): Partial<LocationParams> | null {
  // Match pattern like /location/:lat/:lng/hub/:height
  const match = pathname.match(
    /\/location\/([-\d.]+)\/([-\d.]+)(?:\/hub\/(\d+))?/
  );

  if (match) {
    const [, lat, lng, hubHeight] = match;
    return {
      lat: Number(lat),
      lng: Number(lng),
      ...(hubHeight && { hubHeight: Number(hubHeight) }),
    };
  }

  return null;
}
