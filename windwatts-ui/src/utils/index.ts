import { MODEL_COORDINATES_BOUNDS } from "../constants/coordinates";
import { DataModel } from "../types/Requests";

export const getWindResource = (speed: number) => {
  return speed > 5 ? "High" : speed >= 3 ? "Moderate" : "Low";
};

export const convertWindspeed = (speed = 0, units = "mph") => {
  const value = units === "mph" ? (speed * 2.2369).toFixed(2) : speed;
  return `${value} ${units === "mph" ? "mph" : "m/s"}`;
};

export const convertOutput = (output = 0, units = "kWh") => {
  const value = units === "MWh" ? output / 1000 : output;
  return `${formatNumber(value)} ${units}`;
};

/**
 * Simple number formatting function. Only handles NUMBER types currently.
 *
 * @param {number} num number to format
 * @param {number} decimalPlaces number of decimal places to round to
 * @param {string} locale locale to use for formatting
 * @returns {string} formatted number as a string
 */
export const formatNumber = (
  num: number,
  decimalPlaces: number = 2,
  locale: string = "en-US",
): string => {
  if (!Number.isFinite(num)) throw new Error(`${num} is not a number`);

  const hasDecimals = num % 1 !== 0;
  const formattedNum = hasDecimals
    ? num.toFixed(decimalPlaces)
    : num.toString();

  return Number(formattedNum).toLocaleString(locale);
};

export function isOutOfBounds(
  lat: number,
  lng: number,
  model: DataModel,
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

export function getOutOfBoundsMessage(
  lat: number | undefined,
  lng: number | undefined,
  model: DataModel,
): string {
  if (lat === undefined || lng === undefined) {
    return "No location selected.";
  }
  const bounds = MODEL_COORDINATES_BOUNDS[model];
  if (!bounds) return "No bounds defined for this model.";
  return (
    `(${lat.toFixed(3)}, ${lng.toFixed(
      3,
    )}) is outside the supported region for ${model.toUpperCase()}:\n` +
    `Lat: [${bounds.minLat} ~ ${bounds.maxLat}], Lng: [${bounds.minLng} ~ ${bounds.maxLng}]`
  );
}
