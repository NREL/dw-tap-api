import { Typography, Box } from "@mui/material";

function Contact() {
    return (
        <Box paddingX={3}>
            <Typography variant="h3" component="h3">Contact</Typography>
            <Typography variant="body1">
                Send us a message.
            </Typography>
        </Box>
    );
}

export default Contact;