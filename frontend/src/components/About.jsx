import { Typography, Box } from "@mui/material";

function About() {
    return (
        <Box paddingX={3}>
            <Typography variant="h3" component="h3">About</Typography>
            <Typography variant="body1">
                This is the WindWatt application.
            </Typography>
        </Box>
    );
}

export default About;