import { useState, useEffect } from "react";
import { UnitsContext, defaultUnitValues } from "./UnitsContext";
import { StoredUnits } from "../types/Units";

export default function UnitsProvider({
  children,
}: {
  children: React.ReactNode;
}) {
  const [units, setUnits] = useState<StoredUnits>(() => {
    try {
      const stored = localStorage.getItem("units");
      return stored ? JSON.parse(stored) : defaultUnitValues;
    } catch (error) {
      console.error("Error reading from localStorage:", error);
      return defaultUnitValues;
    }
  });

  useEffect(() => {
    try {
      localStorage.setItem("units", JSON.stringify(units));
    } catch (error) {
      console.error("Error writing to localStorage:", error);
    }
  }, [units]);

  const updateUnit = (key: string, value: string) => {
    setUnits((prev) => ({
      ...prev,
      [key]: value,
    }));
  };

  const updateUnits = (newValues: StoredUnits) => {
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
