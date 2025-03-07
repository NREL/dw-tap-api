import React, { createContext, useState, useEffect } from "react";

export const UnitsContext = createContext();

export default function UnitsProvider({ defaultValues = {}, children }) {
  const [units, setUnits] = useState(() => {
    try {
      const stored = localStorage.getItem("units");
      return stored ? JSON.parse(stored) : defaultValues;
    } catch (error) {
      console.error("Error reading from localStorage:", error);
      return defaultValues;
    }
  });

  useEffect(() => {
    try {
      localStorage.setItem("units", JSON.stringify(units));
    } catch (error) {
      console.error("Error writing to localStorage:", error);
    }
  }, [units]);

  const updateUnit = (key, value) => {
    setUnits((prev) => ({
      ...prev,
      [key]: value,
    }));
  };

  const updateUnits = (newValues) => {
    setUnits((prev) => ({
      ...prev,
      ...newValues,
    }));
  };

  return (
    <UnitsContext.Provider value={{ units, setUnits, updateUnit, updateUnits }}>
      {children}
    </UnitsContext.Provider>
  );
}
