import { UnitsContext, defaultUnitValues } from "./UnitsContext";
import { StoredUnits } from "../types/Units";
import { useLocalStorage } from "../hooks";

export default function UnitsProvider({
  children,
}: {
  children: React.ReactNode;
}) {
  const [units, setUnits] = useLocalStorage<StoredUnits>(
    "units",
    defaultUnitValues
  );

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
