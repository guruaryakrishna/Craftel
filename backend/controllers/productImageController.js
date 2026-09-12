const axios = require('axios');
const FormData = require('form-data');
const fs = require('fs');

exports.processProductImage = async (req, res) => {
    try {
        if (!req.file) {
            return res.status(400).json({
                success: false,
                message: 'No image file received'
            });
        }

        console.log('🖼️ Product image received! Sending to FastAPI...');

        const formData = new FormData();

        formData.append(
            'image',
            fs.createReadStream(req.file.path)
        );

        // ✅ THE URL IS NOW FIXED TO MATCH YOUR FRIEND'S PYTHON SERVER
        const pythonResponse = await axios.post(
            'http://172.20.242.78:8000/api/extract-visuals',
            formData,
            {
                headers: formData.getHeaders(),
                maxContentLength: Infinity,
                maxBodyLength: Infinity
            }
        );

        console.log('✅ Product image processed by FastAPI');

        // Delete temporary uploaded file
        if (fs.existsSync(req.file.path)) {
            fs.unlinkSync(req.file.path);
        }

        return res.status(200).json({
            success: true,
            status: pythonResponse.data.status,
            message: pythonResponse.data.message,
            path: pythonResponse.data.saved_file_path, 
            blur_score: pythonResponse.data.blur_score
        });

    } catch (error) {
        console.error(
            '❌ Product image processing failed:',
            error.response?.data || error.message
        );

        // Clean up temporary file if something fails
        if (req.file && fs.existsSync(req.file.path)) {
            fs.unlinkSync(req.file.path);
        }

        return res.status(500).json({
            success: false,
            message: 'Product image processing failed.',
            error: error.response?.data?.detail || error.message
        });
    }
};