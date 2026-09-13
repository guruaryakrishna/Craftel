const express = require('express');
const router = express.Router();
const { getPricePrediction } = require('../controllers/pricingController');

// This creates the endpoint: POST /api/pricing/predict
router.post('/predict', getPricePrediction);

module.exports = router;