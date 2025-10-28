"use client";

import { UnitsContext, defaultUnitValues } from "../providers/UnitsContext";

export function UnitsProvider({ children }: { children: React.ReactNode }) {
  // URL-driven app state: units remain default; future: derive from query if needed
  const units = defaultUnitValues;
  const setUnits = () => { };
  const updateUnit = () => { };
  const updateUnits = () => { };

  return (
    <UnitsContext.Provider value={{ units, setUnits, updateUnit, updateUnits }}>
      {children}
    </UnitsContext.Provider>
  );
}
