import { useState } from "react";
import useToggle from "./useToggle";

export default function useMainLayoutLogic() {
  // Retrieve units from local storage or default to "metric"
  const storedUnits = localStorage.getItem("units");
  const defaultUnits = storedUnits ? storedUnits : "metric";
  const [units, setUnits] = useState(defaultUnits);

  // Update local storage whenever units change
  const handleUnitsChange = (units) => {
    setUnits(units);
    localStorage.setItem("units", units);
  };

  // setting modal states
  const [settingsOpen, toggleSettingsOpen] = useToggle(false);

  // Results modal states
  const [resultsOpen, toggleResultsOpen] = useToggle(false);

  // main app inputs
  const [currentPosition, setCurrentPosition] = useState(null);
  const [hubHeight, setHubHeight] = useState(30);
  const [powerCurve, setPowerCurve] = useState(100);

  return {
    units,
    settingsOpen,
    resultsOpen,
    currentPosition,
    hubHeight,
    powerCurve,
    toggleResultsOpen,
    toggleSettingsOpen,
    handleUnitsChange,
    setCurrentPosition,
    setHubHeight,
    setPowerCurve,
  };
}
