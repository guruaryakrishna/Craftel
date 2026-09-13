const axios = require('axios');

const getPricePrediction = async (req, res) => {
    try {
        // For now, this takes raw data from Postman/Flutter.
        // Later, we will link this to take data directly from your catalog process.
        const catalogData = req.body;

        // Point this to your friend's FastAPI server
        const pythonServerUrl = 'http://10.31.12.221:8000/api/predict-price';
        
        // Send the catalog data to the AI model
        const response = await axios.post(pythonServerUrl, catalogData);

        // Return the predicted price
        res.status(200).json({
            success: true,
            data: response.data
        });

    } catch (error) {
        console.error("Pricing Model Error:", error.message);
        res.status(500).json({
            success: false,
            message: "Failed to fetch price prediction from the AI microservice."
        });
    }
};

module.exports = { getPricePrediction };