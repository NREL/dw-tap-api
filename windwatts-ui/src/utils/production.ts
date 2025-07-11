import { BaseTable } from "../types/Tables";

export const productionConvert2Table = (
  data: Record<string, Record<string, string | number | null>>,
  avg_type: string
): BaseTable => {
  if (!data || typeof data !== "object" || Object.keys(data).length === 0) {
    console.log("Invalid data provided for conversion:", data);
    // Return an empty table if data is invalid
    return {
      title: `Production Estimates by ${avg_type}`,
      headers: [avg_type],
      rows: [],
    };
  }

  // Extract headers from the first row of data
  const headers = [avg_type, ...Object.keys(Object.values(data)[0])];

  // Map rows from the data object
  const rows = Object.entries(data).map(([key, values]) => [
    key,
    ...Object.values(values).map((v) => (v === null ? "" : v)),
  ]);

  // Construct the BaseTable object
  return {
    title: `Production Estimates by ${avg_type}`,
    headers,
    rows,
  };
};
