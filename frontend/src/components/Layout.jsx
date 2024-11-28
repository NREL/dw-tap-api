import { Header, Footer } from 'nrel-branding-react';
import { Outlet, Link as RouterLink } from 'react-router-dom';
import { Link, Box } from '@mui/material';
import { useState } from 'react';
import Settings from './Settings';

function Layout() {
    // const API_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000/';
    const APP_TITLE = import.meta.env.VITE_APP_TITLE || 'Wind Watts';

    // setting modal states
    const [openSettings, setOpenSettings] = useState(false);
    const handleOpenSettings = () => setOpenSettings(true);
    const handleCloseSettings = () => setOpenSettings(false);

    return (
        <div>
            <Header
                appTitle={<Link to="/" component={RouterLink} underline='none'>{APP_TITLE}</Link>}
                isSlim={true}
            />
            <Box
                sx={{ name: "header-box", 
                    height: 90, 
                    bgcolor: 'white', 
                    }}
            />
            
            <Box sx={{ name: "content-box", minHeight: "80vh", height: 80, bgcolor: 'white', color: 'black' }}>
                <Outlet context={{ handleOpenSettings }} />
            </Box>
            <Footer />
            <Settings openSettings={openSettings} handleClose={handleCloseSettings} />
        </div>
    )
}

export default Layout;