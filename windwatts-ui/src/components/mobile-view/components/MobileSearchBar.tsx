import React, {
  useState,
  useEffect,
  forwardRef,
  useImperativeHandle,
} from "react";
import { Box, TextField, InputAdornment } from "@mui/material";
import { Search } from "@mui/icons-material";
import { MobileSearchBarProps, MobileSearchBarRef } from "../types";
import { SEARCH_MIN_LENGTH } from "../../../constants";

const MobileSearchBar = forwardRef<MobileSearchBarRef, MobileSearchBarProps>(
  (
    {
      onSearchPredictions,
      inputValue,
      onInputChange,
      isSettingFromSelectionRef,
    },
    ref
  ) => {
    const [placesService, setPlacesService] =
      useState<google.maps.places.PlacesService | null>(null);

    // Check if Google Maps API is available
    const isGoogleMapsReady =
      typeof window !== "undefined" &&
      window.google &&
      window.google.maps &&
      window.google.maps.places;

    // Expose clearInput method to parent
    useImperativeHandle(ref, () => ({
      clearInput: () => {
        onInputChange("");
        onSearchPredictions([], false);
      },
    }));

    // Initialize services when Google Maps is ready
    useEffect(() => {
      if (isGoogleMapsReady && !placesService) {
        // Create a dummy map element for PlacesService
        const mapDiv = document.createElement("div");
        const map = new window.google.maps.Map(mapDiv);
        setPlacesService(new window.google.maps.places.PlacesService(map));
      }
    }, [isGoogleMapsReady, placesService]);

    // Fetch predictions when input changes
    useEffect(() => {
      const isSettingFromSelection =
        isSettingFromSelectionRef?.current || false;

      if (
        !isGoogleMapsReady ||
        inputValue.length < SEARCH_MIN_LENGTH ||
        isSettingFromSelection
      ) {
        onSearchPredictions([], false);
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
          onSearchPredictions(results, true);
        } else {
          onSearchPredictions([], false);
        }
      });
      // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [inputValue, isGoogleMapsReady]); // Remove onSearchPredictions from deps

    const handleInputChange = (event: React.ChangeEvent<HTMLInputElement>) => {
      onInputChange(event.target.value);
    };

    return (
      <Box sx={{ width: "100%" }}>
        {isGoogleMapsReady ? (
          <TextField
            id="mobile-search-input"
            placeholder="Search for a location"
            variant="outlined"
            size="small"
            fullWidth
            value={inputValue}
            onChange={handleInputChange}
            autoComplete="off"
            autoCorrect="off"
            autoCapitalize="off"
            spellCheck="false"
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <Search sx={{ color: "#666" }} />
                </InputAdornment>
              ),

              sx: {
                borderRadius: 3,
                bgcolor: "#f5f5f5",
                "& .MuiOutlinedInput-notchedOutline": {
                  border: "none",
                },
                "&:hover .MuiOutlinedInput-notchedOutline": {
                  border: "none",
                },
                "&.Mui-focused .MuiOutlinedInput-notchedOutline": {
                  border: "2px solid #007AFF",
                },
                fontSize: "16px",
                height: 44, // Match the close button height
                "& input": {
                  py: 0, // Remove extra padding
                },
              },
            }}
            sx={{
              "& .MuiInputLabel-root": {
                display: "none", // Hide label for cleaner look
              },
            }}
          />
        ) : (
          <TextField
            placeholder="Loading..."
            variant="outlined"
            size="small"
            fullWidth
            disabled
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <Search sx={{ color: "#666" }} />
                </InputAdornment>
              ),
              sx: {
                borderRadius: 3,
                bgcolor: "#f5f5f5",
                "& .MuiOutlinedInput-notchedOutline": {
                  border: "none",
                },
                height: 44, // Match the close button height
                "& input": {
                  py: 0, // Remove extra padding
                },
              },
            }}
          />
        )}
      </Box>
    );
  }
);

MobileSearchBar.displayName = "MobileSearchBar";

export default MobileSearchBar;
