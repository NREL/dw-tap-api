import { GoogleMap, InfoWindow, Marker } from "@react-google-maps/api";
import { useContext } from "react";
import { Box, Backdrop, CircularProgress } from "@mui/material";
import { SettingsContext } from "../../providers/SettingsContext";
import { getOutOfBoundsMessage } from "../../utils";
import { OutOfBoundsWarning } from "../shared";
import { useMobileBottomSheet } from "../../providers/MobileBottomSheetProvider";
import { useGeolocation, useOutOfBounds, useMapView } from "../../hooks";
import { DEFAULT_MAP_CENTER } from "../../constants";

export const MapViewMobile = () => {
  const { setCurrentPosition } = useContext(SettingsContext);
  const {
    outOfBounds,
    infoWindowOpen,
    setInfoWindowOpen,
    currentPosition,
    preferredModel,
  } = useOutOfBounds();
  const { isLoaded, onLoad } = useMapView(currentPosition);
  const { clearSearchInput, expandDrawer } = useMobileBottomSheet();

  // Get Device Current Location
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

    // Clear search input and expand drawer on mobile when map is tapped
    clearSearchInput();
    expandDrawer();
  };

  if (!isLoaded) {
    return (
      <Backdrop
        open={true}
        sx={(theme) => ({ color: "#fff", zIndex: theme.zIndex.drawer + 1 })}
      >
        <CircularProgress color="inherit" />
      </Backdrop>
    );
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
            <>
              <Marker
                position={currentPosition}
                icon={{
                  path: window.google.maps.SymbolPath.CIRCLE,
                  scale: 10,
                  fillColor: "#d32f2f",
                  fillOpacity: 1,
                  strokeWeight: 2,
                  strokeColor: "#fff",
                }}
              />
              <InfoWindow
                position={currentPosition}
                onCloseClick={() => setInfoWindowOpen(false)}
              >
                <OutOfBoundsWarning
                  message={getOutOfBoundsMessage(
                    currentPosition.lat,
                    currentPosition.lng,
                    preferredModel
                  )}
                />
              </InfoWindow>
            </>
          )}
        </GoogleMap>
      )}
    </Box>
  );
};
