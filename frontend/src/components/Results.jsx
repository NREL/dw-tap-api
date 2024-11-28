import { Modal } from "@mui/material";
import PropTypes from 'prop-types';

const Results = ({ openResults, handleClose }) => {
    const results = [
        {
            title: "Title 1",
            description: "Description 1",
        },
        {
            title: "Title 2",
            description: "Description 2",
        },
        {
            title: "Title 3",
            description: "Description 3",
        },
    ];
    return (
        <Modal open={openResults} onClose={handleClose}>
        <div>
        {results.map((result, index) => (
            <div key={index}>
            <h3>{result.title}</h3>
            <p>{result.description}</p>
            </div>
        ))}
        </div>
        </Modal>
    );
};
Results.propTypes = {
    openResults: PropTypes.bool.isRequired,
    handleClose: PropTypes.func.isRequired,
};

export default Results;