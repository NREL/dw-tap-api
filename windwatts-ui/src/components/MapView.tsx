import { GoogleMap, Libraries, useJsApiLoader } from "@react-google-maps/api";
import { useCallback, useContext, useEffect, useState, useRef } from "react";
import SearchBar from "./SearchBar";
import { Box, Backdrop, CircularProgress } from "@mui/material";
import { SettingsContext } from "../providers/SettingsContext";

const libraries = ["places", "marker"];

interface RecentSearch {
  name: string;
  lat: number;
  lng: number;
}

const MapView = () => {
  const { currentPosition, setCurrentPosition } = useContext(SettingsContext);
  const [zoom, setZoom] = useState(8);
  const defaultCenter = { lat: 39.7392, lng: -104.9903 };
  const [map, setMap] = useState<google.maps.Map | null>(null);
  const markerRef = useRef<google.maps.marker.AdvancedMarkerElement | null>(
    null
  );
  const [recentSearches, setRecentSearches] = useState<RecentSearch[]>([]);

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
  }, []);

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
    handleSetLocation({
      lat: place.geometry?.location?.lat()!,
      lng: place.geometry?.location?.lng()!,
    });
    setZoom(15);
    setRecentSearches([
      ...recentSearches,
      {
        name: place.name!,
        lat: place.geometry?.location?.lat()!,
        lng: place.geometry?.location?.lng()!,
      },
    ]);
  };

  const handleSetLocation = (location: { lat: number; lng: number }) => {
    setCurrentPosition({
      lat: location.lat,
      lng: location.lng,
    });
    setZoom(15);
  };

  const handleMapClick = (e: google.maps.MapMouseEvent) => {
    handleSetLocation({
      lat: e.latLng?.lat()!,
      lng: e.latLng?.lng()!,
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
          top: 0,
        }}
      >
        <SearchBar onPlaceSelected={handlePlaceSelected} />
      </Box>
      {currentPosition && (
        <GoogleMap
          zoom={zoom}
          center={currentPosition || defaultCenter}
          mapContainerStyle={{ height: "100%", width: "100%" }}
          onLoad={onLoad}
          onClick={handleMapClick}
          options={{
            mapId: import.meta.env.VITE_MAP_ID,
            gestureHandling: "greedy",
            draggableCursor: "default",
            draggingCursor: "grab",
          }}
        ></GoogleMap>
      )}
    </Box>
  );
};

export default MapView;
