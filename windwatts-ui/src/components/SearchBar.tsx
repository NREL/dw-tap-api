import { Box, IconButton, TextField, InputAdornment } from "@mui/material";
import { Settings, Clear } from "@mui/icons-material";
import { useContext, useState, useEffect, useRef } from "react";
import { SettingsContext } from "../providers/SettingsContext";

interface SearchBarProps {
  onSearchPredictions?: (
    predictions: google.maps.places.AutocompletePrediction[],
    searching: boolean
  ) => void;
  onPlaceSelected?: (place: google.maps.places.PlaceResult) => void;
  useGoogleAutocomplete?: boolean; // New prop to enable Google's built-in autocomplete
}

function SearchBar({
  onSearchPredictions,
  onPlaceSelected,
  useGoogleAutocomplete = false,
}: SearchBarProps) {
  const { toggleSettings } = useContext(SettingsContext);
  const [inputValue, setInputValue] = useState("");
  const [placesService, setPlacesService] =
    useState<google.maps.places.PlacesService | null>(null);
  const autocompleteRef = useRef<google.maps.places.Autocomplete | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Check if Google Maps API is available
  const isGoogleMapsReady =
    typeof window !== "undefined" &&
    window.google &&
    window.google.maps &&
    window.google.maps.places;

  // Initialize services when Google Maps is ready
  useEffect(() => {
    if (isGoogleMapsReady && !placesService) {
      // Create a dummy map element for PlacesService
      const mapDiv = document.createElement("div");
      const map = new window.google.maps.Map(mapDiv);
      setPlacesService(new window.google.maps.places.PlacesService(map));

      console.log("Places service initialized");
    }
  }, [isGoogleMapsReady, placesService]);

  // Initialize Google Autocomplete for desktop
  useEffect(() => {
    console.log("useGoogleAutocomplete:", useGoogleAutocomplete);
    console.log("isGoogleMapsReady:", isGoogleMapsReady);
    console.log("inputRef.current:", inputRef.current);
    console.log("autocompleteRef.current:", autocompleteRef.current);

    if (
      isGoogleMapsReady &&
      useGoogleAutocomplete &&
      inputRef.current &&
      !autocompleteRef.current
    ) {
      console.log("Initializing Google Autocomplete...");

      // Clean up any existing autocomplete
      if (autocompleteRef.current) {
        window.google.maps.event.clearInstanceListeners(
          autocompleteRef.current
        );
      }

      try {
        autocompleteRef.current = new window.google.maps.places.Autocomplete(
          inputRef.current,
          {
            types: ["geocode"],
            fields: ["place_id", "geometry", "name", "formatted_address"],
          }
        );

        autocompleteRef.current.addListener("place_changed", () => {
          console.log("Place changed event fired");
          const place = autocompleteRef.current?.getPlace();
          console.log("Selected place:", place);
          if (place && place.geometry?.location && onPlaceSelected) {
            onPlaceSelected(place);
            // Update the input value with the selected place
            setInputValue(place.formatted_address || place.name || "");
          }
        });

        console.log("Google Autocomplete initialized successfully");
      } catch (error) {
        console.error("Error initializing Google Autocomplete:", error);
      }
    }

    // Cleanup function
    return () => {
      if (autocompleteRef.current) {
        window.google.maps.event.clearInstanceListeners(
          autocompleteRef.current
        );
        autocompleteRef.current = null;
      }
    };
  }, [isGoogleMapsReady, useGoogleAutocomplete, onPlaceSelected]);

  // Fetch predictions when input changes (for mobile/custom autocomplete)
  useEffect(() => {
    if (useGoogleAutocomplete || !isGoogleMapsReady || inputValue.length < 2) {
      onSearchPredictions?.([], false);
      return;
    }

    const request = {
      input: inputValue,
      types: ["geocode"], // Focus on places/addresses
    };

    const autocompleteService =
      new window.google.maps.places.AutocompleteService();
    autocompleteService.getPlacePredictions(request, (results, status) => {
      if (
        status === window.google.maps.places.PlacesServiceStatus.OK &&
        results
      ) {
        onSearchPredictions?.(results, true);
        console.log("Predictions:", results);
      } else {
        onSearchPredictions?.(results || [], false);
      }
    });
  }, [
    inputValue,
    isGoogleMapsReady,
    onSearchPredictions,
    useGoogleAutocomplete,
  ]);

  const handleInputChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setInputValue(event.target.value);
  };

  const handleClear = () => {
    setInputValue("");
    // Focus the input after clearing
    if (inputRef.current) {
      inputRef.current.focus();
    }
  };

  return (
    <Box
      display="flex"
      alignItems="center"
      mt={2}
      p={1}
      width={{ xs: "100%", sm: "auto", md: "400px" }}
      sx={{
        bgcolor: "var(--color-light)",
        borderColor: "divider",
        borderRadius: 3,
        boxShadow: 1,
        gap: 1,
        zIndex: 10,
      }}
    >
      <IconButton onClick={toggleSettings}>
        <Settings />
      </IconButton>
      <Box sx={{ flexGrow: 1 }}>
        {isGoogleMapsReady ? (
          useGoogleAutocomplete ? (
            // Use regular HTML input for Google Autocomplete
            <Box sx={{ position: "relative", width: "100%" }}>
              <input
                ref={inputRef}
                id="search-bar-input"
                type="text"
                placeholder="Enter a city, address, or landmark"
                value={inputValue}
                onChange={handleInputChange}
                autoComplete="off"
                autoCorrect="off"
                autoCapitalize="off"
                spellCheck="false"
                style={{
                  width: "100%",
                  padding: "8px 12px",
                  paddingRight: inputValue ? "40px" : "12px",
                  border: "1px solid #ccc",
                  borderRadius: "4px",
                  fontSize: "14px",
                  outline: "none",
                }}
                onFocus={(e) => {
                  e.target.style.borderColor = "#1976d2";
                  e.target.style.boxShadow =
                    "0 0 0 2px rgba(25, 118, 210, 0.2)";
                }}
                onBlur={(e) => {
                  e.target.style.borderColor = "#ccc";
                  e.target.style.boxShadow = "none";
                }}
              />
              {inputValue && (
                <IconButton
                  size="small"
                  onClick={handleClear}
                  sx={{
                    position: "absolute",
                    right: "4px",
                    top: "50%",
                    transform: "translateY(-50%)",
                    color: "#666",
                    p: 0.5,
                    minWidth: "auto",
                    width: "24px",
                    height: "24px",
                  }}
                >
                  <Clear sx={{ fontSize: 16 }} />
                </IconButton>
              )}
            </Box>
          ) : (
            // Use Material-UI TextField for custom autocomplete
            <TextField
              id="search-bar-input"
              label="Search for a location"
              variant="outlined"
              size="small"
              fullWidth
              placeholder="Enter a city, address, or landmark"
              value={inputValue}
              onChange={handleInputChange}
              autoComplete="off"
              autoCorrect="off"
              autoCapitalize="off"
              spellCheck="false"
              InputProps={{
                endAdornment: inputValue && (
                  <InputAdornment position="end">
                    <IconButton
                      size="small"
                      onClick={handleClear}
                      sx={{ color: "#666", p: 0.5 }}
                    >
                      <Clear sx={{ fontSize: 18 }} />
                    </IconButton>
                  </InputAdornment>
                ),
              }}
            />
          )
        ) : (
          <TextField
            id="search-bar-input-loading"
            label="Loading..."
            variant="outlined"
            size="small"
            fullWidth
            disabled
          />
        )}
      </Box>
    </Box>
  );
}

export default SearchBar;
