import PropTypes from 'prop-types';
import { BookmarkBorder, Schedule, HelpOutline, Email } from '@mui/icons-material';
import { Divider, Drawer, List, ListItemIcon, ListItemText, Box, ListItemButton } from '@mui/material';
import { styled } from '@mui/material/styles';
import { Link } from 'react-router-dom';

function SideBar({ openSideBar, toggleSidebar, setLocation, savedLocations, recentSearches }) {

  const TrimmedListItemText = styled(ListItemText)({
    '.MuiTypography-root': {
      whiteSpace: 'nowrap',
      overflow: 'hidden',
      textOverflow: 'ellipsis',
    },
  });

  const sidebarWidth = 150;
  return (
    <Drawer 
      open={openSideBar} 
      onClose={toggleSidebar}
      variant="persistent"
        sx={{
          width: sidebarWidth,
          flexShrink: 0,
          '& .MuiDrawer-paper': { 
            width: sidebarWidth,
            boxSizing: 'border-box',
          },
        }}
    >
      <Box height={90} />
      <Divider />
      <Box sx={{ overflow: 'auto' }}>
        <List>
          {/* About / Contact */}
          <ListItemButton component={Link} to="/about">
            <ListItemIcon sx={{ minWidth: "30px" }}>
              <HelpOutline />
            </ListItemIcon>
            <TrimmedListItemText primary="About" />
          </ListItemButton>

          <ListItemButton component={Link} to="/contact">
            <ListItemIcon sx={{ minWidth: "30px" }}>
              <Email />
            </ListItemIcon>
            <TrimmedListItemText primary="Contact" />
          </ListItemButton>
          <Divider />

          {/* Saved Searches */}
          <ListItemButton>
            <ListItemIcon sx={{ minWidth: "30px" }}>
              <BookmarkBorder />
            </ListItemIcon>
            <TrimmedListItemText primary="Saved" />
          </ListItemButton>
          <Divider />
          { savedLocations.map((location, idx) => (
            <ListItemButton
              key={"saved_searches" + idx}
              onClick={() => setLocation({ lat: location.lat, lng: location.lng})}
            >
              <TrimmedListItemText 
                primary={location.name}
                />
            </ListItemButton>
          ))}
          <Divider />

          {/* Recent Searches */}
          <ListItemButton>
            <ListItemIcon sx={{ minWidth: "30px" }}>
              <Schedule />
            </ListItemIcon>
            <TrimmedListItemText primary="Recent" />
          </ListItemButton>
          <Divider />
          { recentSearches.map((location, idx) => (
            <ListItemButton 
              key={"recent_searches" + idx}
              onClick={() => setLocation({ lat: location.lat, lng: location.lng})}
            >
              <TrimmedListItemText 
                primary={location.name}
                />
            </ListItemButton>
          ))}
        </List>
      </Box>
    </Drawer>
  );
}

SideBar.propTypes = {
  openSideBar: PropTypes.bool.isRequired,
  toggleSidebar: PropTypes.func.isRequired,
  setLocation: PropTypes.func.isRequired,
  savedLocations: PropTypes.arrayOf(
    PropTypes.shape({
      lat: PropTypes.number.isRequired,
      lng: PropTypes.number.isRequired,
      name: PropTypes.string.isRequired,
    })
  ).isRequired,
  recentSearches: PropTypes.arrayOf(
    PropTypes.shape({
      lat: PropTypes.number.isRequired,
      lng: PropTypes.number.isRequired,
      name: PropTypes.string.isRequired,
    })
  ).isRequired,
};

export default SideBar;