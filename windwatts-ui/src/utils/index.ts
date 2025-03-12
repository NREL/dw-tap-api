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
  locale: string = "en-US"
): string => {
  if (!Number.isFinite(num)) throw new Error(`${num} is not a number`);

  const hasDecimals = num % 1 !== 0;
  const formattedNum = hasDecimals
    ? num.toFixed(decimalPlaces)
    : num.toString();

  return Number(formattedNum).toLocaleString(locale);
};
