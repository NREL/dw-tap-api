import {
  GoogleMap,
  InfoWindow,
  Libraries,
  Marker,
  useJsApiLoader,
} from "@react-google-maps/api";
import {
  useCallback,
  useContext,
  useEffect,
  useState,
  useRef,
  useMemo,
} from "react";
import { Box, Backdrop, CircularProgress } from "@mui/material";
import { SettingsContext } from "../../providers/SettingsContext";
import { isOutOfBounds, getOutOfBoundsMessage } from "../../utils";
import OutOfBoundsWarning from "../shared/OutOfBoundsWarning";
import { useMobileBottomSheet } from "../../providers/MobileBottomSheetProvider";

const libraries = ["places", "marker"];

const MapViewMobile = () => {
  const { currentPosition, setCurrentPosition, preferredModel } =
    useContext(SettingsContext);
  const defaultCenter = useMemo(() => ({ lat: 39.7392, lng: -104.9903 }), []);
  const [map, setMap] = useState<google.maps.Map | null>(null);
  const markerRef = useRef<google.maps.marker.AdvancedMarkerElement | null>(
    null
  );
  const { clearSearchInput, expandDrawer } = useMobileBottomSheet();
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
  const { isLoaded } = useJsApiLoader({
    googleMapsApiKey: import.meta.env.VITE_MAP_API_KEY,
    libraries: libraries as Libraries,
  });

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

  const handleSetLocation = (location: { lat: number; lng: number }) => {
    setCurrentPosition({
      lat: location.lat,
      lng: location.lng,
    });
  };

  const handleMapClick = (e: google.maps.MapMouseEvent) => {
    const lat: number = e.latLng?.lat() ?? 0;
    const lng: number = e.latLng?.lng() ?? 0;
    console.log("Map clicked at:", { lat, lng });
    handleSetLocation({
      lat,
      lng,
    });

    // Clear search input and expand drawer on mobile when map is tapped
    console.log("Mobile detected, clearing search and expanding drawer");
    clearSearchInput();
    expandDrawer();
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
            clickableIcons: false,
            streetViewControl: false,
            fullscreenControl: false,
            disableDefaultUI: true,
            zoom: 12,
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

export default MapViewMobile;
