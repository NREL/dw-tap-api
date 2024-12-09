import { Modal, Box, Accordion, AccordionSummary, AccordionDetails, Typography, Link, ListItem, ListItemText, Grid2 } from "@mui/material";
import { ExpandMore, Close } from "@mui/icons-material";
import PropTypes from 'prop-types';
import ResultCard from "./ResultCard";
import { IconButton } from "@mui/material";

const Results = ({ openResults, handleClose,  currentPosition, hubHeight, powerCurve}) => {

    const settingOptions = [
        {
            title: "Selected location (lat, lng)",
            data: currentPosition && currentPosition.lat && currentPosition.lng ? 
                `${currentPosition.lat.toFixed(3)}, ${currentPosition.lng.toFixed(3)}` : "Not selected"
        },
        {
            title: "Selected hub height",
            data: hubHeight ? `${hubHeight} meters` : "Not selected"
        },
        {
            title: "Selected power curve",
            data: powerCurve ? `nrel-reference-${powerCurve}kW` : "Not selected"
        }
    ];

    const resultCardData = [
        {
            title: "Wind Resource 1",
            subheader: "Details about wind resource 1",
            data: "Data for wind resource 1",
            details: ["Detail 1", "Detail 2", "Detail 3"]
        },
        {
            title: "Wind Resource 2",
            subheader: "Details about wind resource 2",
            data: "Data for wind resource 2",
            details: ["Detail 1", "Detail 2", "Detail 3"]
        },
        {
            title: "Wind Resource 3",
            subheader: "Details about wind resource 3",
            data: "Data for wind resource 3",
            details: ["Detail 1", "Detail 2", "Detail 3"]
        }
    ];

    return (
        <Modal open={openResults} onClose={handleClose}>
            <Box sx={{ 
            position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%, -50%)', 
            width:800, minWidth: 600, bgcolor: 'background.paper', p: 3, pt: 6 }}>
                <IconButton
                    aria-label="close"
                    onClick={handleClose}
                    sx={{
                        position: 'absolute',
                        right: 8,
                        top: 8,
                    }}
                >
                    <Close />
                </IconButton>
                <Accordion >
                    <AccordionSummary
                        expandIcon={<ExpandMore />}
                        aria-controls="summary-panel-content"
                        id="summary-panel-header"
                        bgcolor="primary.main"
                    >
                        <Typography variant="h5">Summary</Typography>
                    </AccordionSummary>
                    <AccordionDetails>
                        <Typography variant="body1" marginBottom={3}>
                            Analysis presented below was performed using summary data from&nbsp;
                            <Link href="https://www.energy.gov/eere/wind/articles/new-wind-resource-database-includes-updated-wind-toolkit"
                                underline="hover" target="_blank" rel="noopener noreferrer">
                                NREL&apos;s 20-year WTK-LED dataset
                            </Link>&nbsp;using the following options:
                        </Typography>
                        <Grid2 container spacing={2}>
                            {settingOptions.map((option, index) => (
                                <Grid2 xs={12} sm={6} md={3} key={'setting_option_' + index}>
                                    <ListItem sx={{ 
                                        borderRadius: 1,
                                        boxShadow: 3,
                                        minWidth: 200 }}>
                                        <ListItemText primary={option.title} secondary={option.data} />
                                    </ListItem>
                                </Grid2>
                            ))}
                        </Grid2>
                        
                        <Grid2 container spacing={2}>
                            {resultCardData.map((data, index) => (
                                <Grid2 xs={12} sm={6} md={3} key={'result_card_' + index}>
                                    <ResultCard data={data} />
                                </Grid2>
                            ))}
                        </Grid2>
                        <Typography variant="body2" color="textSecondary" marginTop={2}>
                            Disclaimer: This summary represents a PRELIMINARY analysis. 
                            Research conducted at national laboratories suggests that 
                            multiple models should be used for more thorough analysis. 
                            Reach out to a qualified installer for a refined estimate.
                        </Typography>
                    </AccordionDetails>
                </Accordion>
            </Box>

        </Modal>
    );
};

Results.propTypes = {
    openResults: PropTypes.bool.isRequired,
    handleClose: PropTypes.func.isRequired,
    currentPosition: PropTypes.shape({
        lat: PropTypes.number,
        lng: PropTypes.number
    }),
    hubHeight: PropTypes.number,
    powerCurve: PropTypes.number
};

export default Results;