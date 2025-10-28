"use client";

import { useCallback } from "react";
import { UnitsContext, defaultUnitValues } from "./UnitsContext";
import { StoredUnits } from "./types";
import { useLocalStorage } from "./useLocalStorage";

export function UnitsProvider({ children }: { children: React.ReactNode }) {
  const [units, setUnits] = useLocalStorage<StoredUnits>(
    "units",
    defaultUnitValues
  );

  const updateUnit = useCallback(
    (key: string, value: string) => {
      setUnits((prev) => ({
        ...prev,
        [key]: value
      }));
    },
    [setUnits]
  );

  const updateUnits = useCallback(
    (newValues: StoredUnits) => {
      setUnits((prev) => ({
        ...prev,
        ...newValues
      }));
    },
    [setUnits]
  );

  return (
    <UnitsContext.Provider value={{ units, setUnits, updateUnit, updateUnits }}>
      {children}
    </UnitsContext.Provider>
  );
}
