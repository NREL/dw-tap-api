import { GoogleMap, InfoWindow, Marker } from "@react-google-maps/api";
import {
  useCallback,
  useContext,
  useEffect,
  useState,
  useRef,
  useMemo,
} from "react";
import { SearchBar } from "../core";
import { Box, Backdrop, CircularProgress } from "@mui/material";
import { SettingsContext } from "../../providers/SettingsContext";
import { isOutOfBounds, getOutOfBoundsMessage } from "../../utils";
import OutOfBoundsWarning from "../shared/OutOfBoundsWarning";
import { useGoogleMaps } from "../../hooks";

const MapViewDesktop = () => {
  const {
    currentPosition,
    setCurrentPosition,
    preferredModel,
    toggleSettings,
  } = useContext(SettingsContext);
  const defaultCenter = useMemo(() => ({ lat: 39.7392, lng: -104.9903 }), []);
  const [map, setMap] = useState<google.maps.Map | null>(null);
  const markerRef = useRef<google.maps.marker.AdvancedMarkerElement | null>(
    null
  );
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

  // Load Google Maps API
  const { isLoaded } = useGoogleMaps();

  // Get Device Current Location
  useEffect(() => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          setCurrentPosition({
            lat: position.coords.latitude,
            lng: position.coords.longitude,
          });
        },
        (error) => {
          console.error("Geolocation error:", error);
          setCurrentPosition(defaultCenter);
        },
        { maximumAge: 60000, timeout: 5000, enableHighAccuracy: true }
      );
    }
  }, [defaultCenter, setCurrentPosition]);

  // Updated marker management
  useEffect(() => {
    if (isLoaded && map && currentPosition && window.google?.maps?.marker) {
      // Remove existing marker if there is one
      if (markerRef.current) {
        markerRef.current.map = null;
      }

      // Create new marker
      const { AdvancedMarkerElement } = window.google.maps.marker;
      const advancedMarker = new AdvancedMarkerElement({
        position: currentPosition,
        map: map,
        title: "Selected Location",
      });

      // Save reference to the new marker
      markerRef.current = advancedMarker;
    }
  }, [isLoaded, map, currentPosition]);

  // Clean up marker on unmount
  useEffect(() => {
    return () => {
      if (markerRef.current) {
        markerRef.current.map = null;
      }
    };
  }, []);

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

  const onLoad = useCallback((map: google.maps.Map) => setMap(map), []);

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
          center={currentPosition || defaultCenter}
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
            zoom: 8,
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

export default MapViewDesktop;
