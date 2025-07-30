import { GoogleMap, InfoWindow, Marker } from "@react-google-maps/api";
import { useContext } from "react";
import { SearchBar } from "../core";
import { Box, Backdrop, CircularProgress } from "@mui/material";
import { SettingsContext } from "../../providers/SettingsContext";
import { getOutOfBoundsMessage } from "../../utils";
import { OutOfBoundsWarning } from "../shared";
import { useGeolocation, useOutOfBounds, useMapView } from "../../hooks";
import { DEFAULT_MAP_CENTER } from "../../constants";

export const MapViewDesktop = () => {
  const { toggleSettings, setCurrentPosition } = useContext(SettingsContext);
  const {
    outOfBounds,
    infoWindowOpen,
    setInfoWindowOpen,
    currentPosition,
    preferredModel,
  } = useOutOfBounds();
  const { isLoaded, onLoad } = useMapView(currentPosition);

  // Get Device Current Location
  useGeolocation();

  const handlePlaceSelected = (place: google.maps.places.PlaceResult) => {
    const lat = place.geometry?.location?.lat();
    const lng = place.geometry?.location?.lng();
    if (lat === undefined || lng === undefined) {
      console.error("Selected place does not have valid coordinates.");
      return;
    }
    handleSetLocation({ lat, lng });
  };

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
      <Box
        sx={{
          display: "flex",
          position: "absolute",
          width: "100%",
          justifyContent: "center",
          top: 20,
          zIndex: 1000,
          px: 2,
        }}
      >
        <Box
          sx={{
            width: "100%",
            maxWidth: 500,
            bgcolor: "rgba(255, 255, 255, 0.98)",
            borderRadius: 2,
            p: 1.5,
            boxShadow: "0 4px 20px rgba(0, 0, 0, 0.15)",
            backdropFilter: "blur(10px)",
          }}
        >
          <SearchBar
            useGoogleAutocomplete={true}
            onPlaceSelected={handlePlaceSelected}
            onSettingsClick={toggleSettings}
          />
        </Box>
      </Box>
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
            streetViewControl: false,
            fullscreenControl: false,
            disableDefaultUI: true,
            zoomControl: true,
            zoomControlOptions: {
              position: window.google.maps.ControlPosition.TOP_RIGHT,
            },
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
