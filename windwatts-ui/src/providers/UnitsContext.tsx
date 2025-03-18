import { createContext, useState, useEffect } from "react";
import { StoredUnits } from "../types/Units";

export interface Units extends StoredUnits {
  setUnits: (units: StoredUnits) => void;
  updateUnit: (key: string, value: any) => void;
  updateUnits: (newValues: StoredUnits) => void;
}

const defaultValues: Units = {
  windspeed: "m/s",
  output: "kWh",
  setUnits: () => {},
  updateUnit: () => {},
  updateUnits: () => {},
};

export const UnitsContext = createContext<Units>(defaultValues);

export default function UnitsProvider({
  children,
}: {
  children: React.ReactNode;
}) {
  const [units, setUnits] = useState<StoredUnits>(() => {
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

  const updateUnit = (key: string, value: any) => {
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
