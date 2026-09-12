const express = require('express');
const multer = require('multer');

// Import the perfect controller you just showed me
const { processProductImage } = require('../controllers/productImageController');

const router = express.Router();

// Setup multer for image uploads
const upload = multer({
    dest: 'uploads/'
});

// Define the POST route
router.post(
    '/process',
    upload.single('image'),
    processProductImage
);

// THIS IS THE LINE THAT FIXES YOUR CRASH
module.exports = router;