const express = require('express');
const router = express.Router();
const { sendAadhaarOtp, verifyAadhaarOtp } = require('../controllers/authController');

router.post('/send-otp', sendAadhaarOtp);
router.post('/verify-otp', verifyAadhaarOtp);

module.exports = router;