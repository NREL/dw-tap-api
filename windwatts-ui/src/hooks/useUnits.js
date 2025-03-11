import { useState, useEffect } from "react";

export default function useUnits(key, defaultValue) {
  // Lazy initializer to load the key from local storage
  const [value, setValue] = useState(() => {
    try {
      const stored = localStorage.getItem("units");
      if (stored) {
        const parsed = JSON.parse(stored);
        // Use nullish coalescing in case the stored value is undefined
        return parsed[key] ?? defaultValue;
      }
    } catch (error) {
      console.error("Error reading local storage", error);
    }
    return defaultValue;
  });

  // Update local storage whenever the value changes
  useEffect(() => {
    try {
      const stored = localStorage.getItem("units");
      const unitsObj = stored ? JSON.parse(stored) : {};
      unitsObj[key] = value;
      localStorage.setItem("units", JSON.stringify(unitsObj));
    } catch (error) {
      console.error("Error writing to local storage", error);
    }
  }, [key, value]);

  return [value, setValue];
}
