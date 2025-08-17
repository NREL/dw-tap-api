import { useContext, useEffect, useState } from "react";
import { SettingsContext } from "../providers/SettingsContext";
import { isOutOfBounds } from "../utils";

export const useOutOfBounds = () => {
  const { currentPosition, preferredModel } = useContext(SettingsContext);
  const [infoWindowOpen, setInfoWindowOpen] = useState(false);

  // Out-of-bounds state
  const outOfBounds =
    currentPosition && preferredModel
      ? isOutOfBounds(currentPosition.lat, currentPosition.lng, preferredModel)
      : false;

  useEffect(() => {
    if (outOfBounds) {
      setInfoWindowOpen(true);
    } else {
      setInfoWindowOpen(false);
    }
  }, [currentPosition, outOfBounds]);

  return {
    outOfBounds,
    infoWindowOpen,
    setInfoWindowOpen,
    currentPosition,
    preferredModel,
  };
};
