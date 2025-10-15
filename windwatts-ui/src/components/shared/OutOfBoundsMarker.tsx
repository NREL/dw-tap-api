import { InfoWindow, Marker } from "@react-google-maps/api";
import { OutOfBoundsWarning } from "./OutOfBoundsWarning";
import { getOutOfBoundsMessage } from "../../utils";
import { OUT_OF_BOUNDS_MARKER_CONFIG } from "../../constants";
import { DataModel } from "../../types";

interface OutOfBoundsMarkerProps {
  position: { lat: number; lng: number };
  preferredModel: DataModel;
  onClose: () => void;
}

export function OutOfBoundsMarker({
  position,
  preferredModel,
  onClose,
}: OutOfBoundsMarkerProps) {
  return (
    <>
      <Marker position={position} icon={OUT_OF_BOUNDS_MARKER_CONFIG} />
      <InfoWindow position={position} onCloseClick={onClose}>
        <OutOfBoundsWarning
          message={getOutOfBoundsMessage(
            position.lat,
            position.lng,
            preferredModel
          )}
        />
      </InfoWindow>
    </>
  );
}
