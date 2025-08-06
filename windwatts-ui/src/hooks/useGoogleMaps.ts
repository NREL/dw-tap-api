import { useJsApiLoader, Libraries } from "@react-google-maps/api";

// Centralized Google Maps API configuration
const libraries: Libraries = ["places", "marker"];

export const useGoogleMaps = () => {
  const { isLoaded, loadError } = useJsApiLoader({
    googleMapsApiKey: import.meta.env.VITE_MAP_API_KEY,
    libraries,
  });

  return {
    isLoaded,
    loadError,
    libraries,
  };
};
