import { GoogleMap } from "@react-google-maps/api";
import { useContext } from "react";
import { Box } from "@mui/material";
import { SettingsContext } from "../../providers/SettingsContext";
import { OutOfBoundsMarker, LoadingBackdrop } from "../shared";
import { useMobileBottomSheet } from "../../providers/MobileBottomSheetProvider";
import { useGeolocation, useOutOfBounds, useMapView } from "../../hooks";
import { DEFAULT_MAP_CENTER } from "../../constants";

export const MapViewMobile = () => {
  const { setCurrentPosition, zoom, setZoom } = useContext(SettingsContext);
  const {
    outOfBounds,
    infoWindowOpen,
    setInfoWindowOpen,
    currentPosition,
    preferredModel,
  } = useOutOfBounds();
  const { isLoaded, onLoad } = useMapView(currentPosition, zoom, setZoom);
  const { clearSearchInput, expandDrawer } = useMobileBottomSheet();

  useGeolocation();

  const handleSetLocation = (location: { lat: number; lng: number }) => {
    setCurrentPosition({
      lat: location.lat,
      lng: location.lng,
    });
  };

  const handleMapClick = (e: google.maps.MapMouseEvent) => {
    const lat: number = e.latLng?.lat() ?? 0;
    const lng: number = e.latLng?.lng() ?? 0;
    handleSetLocation({
      lat,
      lng,
    });

    clearSearchInput();
    expandDrawer();
  };

  if (!isLoaded) {
    return <LoadingBackdrop />;
  }

  return (
    <Box sx={{ height: "100%", width: "100%", position: "relative" }}>
      {currentPosition && (
        <GoogleMap
          center={currentPosition || DEFAULT_MAP_CENTER}
          mapContainerStyle={{ height: "100%", width: "100%" }}
          onLoad={onLoad}
          onClick={handleMapClick}
          options={{
            mapId: import.meta.env.VITE_MAP_ID,
            gestureHandling: "greedy",
            draggableCursor: "default",
            draggingCursor: "grab",
            clickableIcons: false,
            streetViewControl: false,
            fullscreenControl: false,
            disableDefaultUI: true,
          }}
        >
          {outOfBounds && currentPosition && infoWindowOpen && (
            <OutOfBoundsMarker
              position={currentPosition}
              preferredModel={preferredModel}
              onClose={() => setInfoWindowOpen(false)}
            />
          )}
        </GoogleMap>
      )}
    </Box>
  );
};
