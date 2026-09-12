const axios = require('axios');
const FormData = require('form-data');
const fs = require('fs');

exports.forwardToPython = async (req, res) => {
    try {
        // 1. Check if multer caught the file
        if (!req.file) {
            return res.status(400).json({ success: false, message: "No audio file received" });
        }

        console.log("🎙️ Audio caught! Forwarding to FastAPI...");

        // 2. Package the file for Python
        const formData = new FormData();
        // MUST be 'audio' to match FastAPI's UploadFile parameter
        formData.append('audio', fs.createReadStream(req.file.path)); 

        // 3. Send to your teammate's Python server
        const pythonResponse = await axios.post('http://172.20.227.20:8000/api/transcribe-audio', formData, {
            headers: formData.getHeaders()
        });

        // 4. Extract the exact JSON key Python returns
        const translatedText = pythonResponse.data.transcription; 
        console.log("✅ Translation received:", translatedText);

        // 5. Delete the temporary file from your test folder
        fs.unlinkSync(req.file.path);

        // 6. Send the English text back to the Flutter app
        return res.status(200).json({
            success: true,
            englishText: translatedText 
        });

    } catch (error) {
        console.error("❌ Bridge failed:", error.message);
        
        // Always clean up the temporary file, even if the request crashes
        if (req.file && fs.existsSync(req.file.path)) {
            fs.unlinkSync(req.file.path);
        }
        
        res.status(500).json({ success: false, message: "Voice translation failed." });
    }
};