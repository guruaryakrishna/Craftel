const express = require('express');
const translationController = require('../controllers/translationcontroller');

const router = express.Router();

// ==========================================
// TEXT TRANSLATION ROUTE
// ==========================================

// Flutter sends POST requests here.
// Example:
// POST /api/translate-text
router.post('/', translationController.forwardTextToPython);

module.exports = router;