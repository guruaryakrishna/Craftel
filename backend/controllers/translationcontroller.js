const axios = require('axios');

exports.forwardTextToPython = async (req, res) => {
    try {
        const { text, target_language } = req.body;

        // 1. Validate the request
        if (!text) {
            return res.status(400).json({ success: false, message: "Text is required for translation" });
        }

        console.log(`📝 Text caught! Translating to ${target_language || 'en'}...`);

        // 2. Forward the JSON directly to Python (Port 8000)
       const pythonResponse = await axios.post(
    'http://172.20.227.20:8000/api/translate',
    {
        text: text,
        target_lang: target_language || "en"
    }
);

        // 3. Extract the exact key Python returns ("translated_text")
        const resultText = pythonResponse.data.translated_text;
        console.log("✅ Text translated:", resultText);

        // 4. Send it back to Flutter
        return res.status(200).json({
            success: true,
            translatedText: resultText
        });

    } catch (error) {
        console.error("❌ Translation bridge failed:", error.message);
        res.status(500).json({ success: false, message: "Text translation failed." });
    }
};