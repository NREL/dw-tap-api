import { Box, IconButton, TextField } from "@mui/material";
import { Autocomplete } from "@react-google-maps/api";
import { Menu, Settings } from "@mui/icons-material";
import { useState } from "react";
import PropTypes from 'prop-types';
import { useOutletContext } from "react-router-dom";

function SearchBar({ onPlaceSelected, toggleDrawer }) {
    const [autocomplete, setAutocomplete] = useState(null);
    const { handleOpenSettings } = useOutletContext();

    const onLoad = (instance) => {
        setAutocomplete(instance);
    };

    const onPlaceChanged = () => {
        if (autocomplete !== null) {
            const place = autocomplete.getPlace();
            onPlaceSelected
            onPlaceSelected(place);
        } else {
            console.error("Autocomplete is not loaded yet!");
        }
    };

    return (
        <Box display="flex" alignItems="center" mt={2} p={1}
            width={{ xs: '100%', sm: 'auto', md: '400px'}}
            sx={{ bgcolor: 'var(--color-light)', borderColor: 'divider', 
                borderRadius: 3, boxShadow: 1, gap: 1, zIndex: 10 }}
            >
            <IconButton onClick={toggleDrawer}>
                <Menu />
            </IconButton>
            <IconButton onClick={handleOpenSettings}>
                <Settings />
            </IconButton>
            <Box sx={{ flexGrow: 1 }}>
                <Autocomplete
                    onLoad={onLoad}
                    onPlaceChanged={onPlaceChanged}
                >
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
SearchBar.propTypes = {
    onPlaceSelected: PropTypes.func.isRequired,
    toggleDrawer: PropTypes.func.isRequired,
};

export default SearchBar;