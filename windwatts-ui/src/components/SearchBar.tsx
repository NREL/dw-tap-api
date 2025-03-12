import { Box, IconButton, TextField } from "@mui/material";
import { Autocomplete } from "@react-google-maps/api";
import { Settings } from "@mui/icons-material";
import { useContext, useState } from "react";
import { SettingsContext } from "../providers/SettingsContext";

function SearchBar({ onPlaceSelected }: { onPlaceSelected: Function }) {
  const { toggleSettings } = useContext(SettingsContext);
  const [autocomplete, setAutocomplete] =
    useState<google.maps.places.Autocomplete | null>(null);

  const onLoad = (instance: google.maps.places.Autocomplete) => {
    setAutocomplete(instance);
  };

  const onPlaceChanged = () => {
    if (autocomplete !== null) {
      const place = autocomplete.getPlace();
      onPlaceSelected(place);
    } else {
      console.error("Autocomplete is not loaded yet!");
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
        <Autocomplete onLoad={onLoad} onPlaceChanged={onPlaceChanged}>
          <TextField
            id="search-bar-input"
            label="Search for a location"
            variant="outlined"
            size="small"
            fullWidth
          />
        </Autocomplete>
      </Box>
    </Box>
  );
}

export default SearchBar;
