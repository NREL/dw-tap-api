import { GoogleMap, useJsApiLoader, InfoWindow, InfoWindowF } from "@react-google-maps/api";
import { useEffect, useState } from "react";
import SearchBar from "./SearchBar";
import { Box, Backdrop, CircularProgress } from "@mui/material";
import SideBar from "./Sidebar";
import InfoPopup from "./InfoPopup";

const libraries = ['places', 'marker'];

const MapView = () => {

    const [position, setPosition] = useState(null);
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
                    setPosition({
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
        if (isLoaded && map && position && google.maps) {
            const { AdvancedMarkerElement } = google.maps.marker;
            if (marker) {
                marker.setMap(null);
            }
            const advancedMarker = new AdvancedMarkerElement({
                position: position,
                map: map,
                title: 'Default Location',
            });
            setMarker(advancedMarker);
        }
    }, [position]);

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
        setPosition({
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

    const handleAnalyzeData = () => {
        console.log("Analyzing Wind Data for coordinates:", infoWindowPosition);
    };

    if (!isLoaded) {
        return <div>Loading...</div>;
    }

    return (
        <Box sx={{ height: '100%', width: '100%', position: 'relative' }}>
            <Box sx={{ display: 'flex', position: 'absolute', 
                width: '100%', justifyContent: 'center', top: 0}}>
                <SearchBar onPlaceSelected={handlePlaceSelected} toggleDrawer={toggleDrawer} />
            </Box>
            {position ? (
                <GoogleMap
                    zoom={zoom}
                    center={position || defaultCenter}
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
                            onAnalyzeClick={handleAnalyzeData}
                        />
                    )}
                </GoogleMap>
            ) : (
                <Backdrop
                    sx={(theme) => ({ color: '#fff', zIndex: theme.zIndex.drawer + 1 })}
                >
                    <CircularProgress color="inherit" />
                </Backdrop>
            )}
            <SideBar
                openSideBar={openSideBar}
                toggleSidebar={toggleDrawer}
                setLocation={handleSetLocation}
                savedLocations={savedLocations}
                recentSearches={recentSearches}
            />
        </Box>
    );
};

export default MapView;
