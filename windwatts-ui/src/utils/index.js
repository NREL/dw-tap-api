export const getWindResource = (speed) => {
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

export const formatNumber = (num, decimalPlaces = 2, locale = "en-US") => {
  if (!Number.isFinite(num)) return num;

  const hasDecimals = num % 1 !== 0;
  const formattedNum = hasDecimals
    ? num.toFixed(decimalPlaces)
    : num.toString();

  return Number(formattedNum).toLocaleString(locale);
};
