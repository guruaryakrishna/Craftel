const express = require('express');
const multer = require('multer');
const voiceController = require('../controllers/voicecontroller');

const router = express.Router();

// Catch the incoming file and safely save it in your existing test folder
const upload = multer({ dest: 'test/' });

// Flutter will send the file to this URL using the field name 'audio_file'
router.post('/translate', upload.single('audio_file'), voiceController.forwardToPython);

module.exports = router;