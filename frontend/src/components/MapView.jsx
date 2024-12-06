import { GoogleMap, useJsApiLoader } from "@react-google-maps/api";
import { useEffect, useState } from "react";
import SearchBar from "./SearchBar";
import { Box, Backdrop, CircularProgress } from "@mui/material";
import SideBar from "./Sidebar";
import InfoPopup from "./InfoPopup";
import { useOutletContext } from "react-router-dom";

const libraries = ['places', 'marker'];

const MapView = () => {

    const { currentPosition, setCurrentPosition } = useOutletContext();
    const [zoom, setZoom] = useState(8);
    const defaultCenter = { lat: 39.7392, lng: -104.9903 };
    const [map, setMap] = useState(null);
    const [marker, setMarker] = useState(null);
    const [infoWindowPosition, setInfoWindowPosition] = useState(null);
    const [infoWindowVisible, setInfoWindowVisible] = useState(false);

    // Sidebar States
    const [openSideBar, setOpenSideBar] = useState(false);
    const toggleDrawer = () => {
        setOpenSideBar(!openSideBar);
    }
    const [savedLocations, setSavedLocations] = useState([
        {
        name: 'Location 1',
        lat: 39.74021,
        lng: -105.162558,
        },
        {
        name: 'Location 2',
        lat: 39.7407,
        lng: -105.1686,
        },
    ]);

    const [recentSearches, setRecentSearches] = useState([]);

    // Search Bar States

    // Load Google Maps API
    const { isLoaded } = useJsApiLoader({
        googleMapsApiKey: import.meta.env.VITE_MAP_API_KEY,
        libraries: libraries,
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
                }
            );
        }
    }, []);

    useEffect(() => {
        if (isLoaded && map && currentPosition && google.maps) {
            const { AdvancedMarkerElement } = google.maps.marker;
            if (marker) {
                marker.setMap(null);
            }
            const advancedMarker = new AdvancedMarkerElement({
                position: currentPosition,
                map: map,
                title: 'Default Location',
            });
            setMarker(advancedMarker);
        }
    }, [currentPosition]);

    const handlePlaceSelected = (place) => {
        handleSetLocation({
            lat: place.geometry.location.lat(),
            lng: place.geometry.location.lng(),
        });
        setZoom(15);
        setRecentSearches([...recentSearches, {
            name: place.name,
            lat: place.geometry.location.lat(),
            lng: place.geometry.location.lng(),
        }]);
    }

    const handleSetLocation = (location) => {
        setCurrentPosition({
            lat: location.lat,
            lng: location.lng,
        });
        setZoom(15);
        setInfoWindowPosition({
            lat: location.lat,
            lng: location.lng,
        });
        setInfoWindowVisible(true);
    };

    const handleMapClick = () => {
        if (marker) {
            marker.setMap(null);
            setMarker(null);
        }
        setInfoWindowVisible(false);
    };


    const handleMapRightClick = (e) => {
        handleSetLocation({
            lat: e.latLng.lat(),
            lng: e.latLng.lng(),
        });
    };

    const handleSaveLocation = () => {
        const formattedLat = infoWindowPosition.lat.toFixed(2);
        const formattedLng = infoWindowPosition.lng.toFixed(2);
        const newLocation = {
            name: `(${formattedLat}, ${formattedLng})`,
            lat: infoWindowPosition.lat,
            lng: infoWindowPosition.lng,
        };
        setSavedLocations([...savedLocations, newLocation]);
    };

    const deleteRecentLocation = (idx) => {
        setRecentSearches(recentSearches.filter((_, i) => i !== idx));
    };

    const deleteSavedLocation = (idx) => {
        setSavedLocations(savedLocations.filter((_, i) => i !== idx));
    };

    if (!isLoaded) {
        return (
            <Backdrop open={true}
                sx={(theme) => ({ color: '#fff', zIndex: theme.zIndex.drawer + 1 })}
            >
                <CircularProgress color="inherit" />
            </Backdrop>
        );
    }

    return (
        <Box sx={{ height: '100%', width: '100%', position: 'relative' }}>
            <Box sx={{ display: 'flex', position: 'absolute', 
                width: '100%', justifyContent: 'center', top: 0}}>
                <SearchBar onPlaceSelected={handlePlaceSelected} toggleDrawer={toggleDrawer} />
            </Box>
            {currentPosition &&
                <GoogleMap
                    zoom={zoom}
                    center={currentPosition || defaultCenter}
                    mapContainerStyle={{ height: "100%", width: "100%" }}
                    onLoad={(map) => { 
                        setMap(map);
                    }}
                    onClick={handleMapClick}
                    onRightClick={handleMapRightClick}
                    options={{ 
                        mapId: import.meta.env.VITE_MAP_ID,
                        gestureHandling: 'greedy',
                    }}
                >
                    {infoWindowVisible && infoWindowPosition && (
                        <InfoPopup
                            position={infoWindowPosition}
                            onCloseClick={() => setInfoWindowVisible(false)}
                            onSaveLocation={handleSaveLocation}
                        />
                    )}
                </GoogleMap>
            }
            <SideBar
                openSideBar={openSideBar}
                toggleSidebar={toggleDrawer}
                setLocation={handleSetLocation}
                savedLocations={savedLocations}
                recentSearches={recentSearches}
                deleteRecentLocation={deleteRecentLocation}
                deleteSavedLocation={deleteSavedLocation}
            />
        </Box>
    );
};

export default MapView;
