const axios = require('axios');
const pool = require('../config/db');

const otpStore = new Map();

// ==========================================
// 1. SEND AADHAAR OTP
// ==========================================

exports.sendAadhaarOtp = async (req, res) => {
  const { aadhaarNumber } = req.body;

  // Validate Aadhaar number
  if (!aadhaarNumber || !/^\d{12}$/.test(aadhaarNumber)) {
    return res.status(400).json({
      success: false,
      message: 'Invalid Aadhaar number. It must be exactly 12 digits.',
    });
  }

  try {
    // Find artisan
    const result = await pool.query(
      `SELECT id, name, phone_number
       FROM artisans
       WHERE aadhaar_number = $1`,
      [aadhaarNumber]
    );

    if (result.rows.length === 0) {
      return res.status(404).json({
        success: false,
        message: 'Aadhaar details not found in artisan records.',
      });
    }

    const artisan = result.rows[0];

    // Generate 6-digit OTP
    const generatedOtp = Math.floor(
      100000 + Math.random() * 900000
    ).toString();

    // OTP valid for 5 minutes
    const expiresAt = Date.now() + 5 * 60 * 1000;

    otpStore.set(aadhaarNumber, {
      otp: generatedOtp,
      expiresAt,
    });

    // Clean phone number
    const cleanPhone = String(artisan.phone_number || '')
      .replace(/\D/g, '')
      .slice(-10);

    if (cleanPhone.length !== 10) {
      return res.status(400).json({
        success: false,
        message: 'Registered mobile number is invalid.',
      });
    }

    // Mask phone number
    const maskedPhone = `******${cleanPhone.slice(-4)}`;

    // ==========================================
    // FAST2SMS
    // ==========================================

    try {
      const response = await axios.post(
        'https://www.fast2sms.com/dev/bulkV2',
        {
          message: `Your Craftel OTP is ${generatedOtp}`,
          route: 'q',
          numbers: cleanPhone,
        },
        {
          headers: {
            authorization: process.env.FAST2SMS_API_KEY,
            'Content-Type': 'application/json',
          },
          timeout: 10000,
        }
      );

      console.log('✅ Real SMS Sent Successfully:', response.data);

      return res.status(200).json({
        success: true,
        message: `OTP sent successfully to registered mobile ending with ${cleanPhone.slice(-4)}`,
        phoneHint: maskedPhone,
      });

    } catch (smsError) {

      // ==========================================
      // DEV MODE FALLBACK
      // ==========================================

      console.error(
        '❌ Fast2SMS API Error:',
        smsError.response?.data || smsError.message
      );

      const fallbackOtp =
        otpStore.get(aadhaarNumber)?.otp || generatedOtp;

      console.log('\n========================================');
      console.log('🚀 [DEV MODE BYPASS]');
      console.log('Fast2SMS could not send the SMS.');
      console.log(`📱 Target Phone: ${cleanPhone}`);
      console.log(`🔑 GENERATED OTP: ${fallbackOtp}`);
      console.log('========================================\n');

      return res.status(200).json({
        success: true,
        message:
          '[DEV MODE] SMS gateway unavailable. Check server terminal for OTP.',
        phoneHint: maskedPhone,
        devOtp: fallbackOtp,
      });
    }

  } catch (error) {
    console.error(
      '❌ Database or Server error:',
      error.message
    );

    return res.status(500).json({
      success: false,
      message: 'Internal server error while processing the request.',
    });
  }
};


// ==========================================
// 2. VERIFY OTP & UPDATE CURRENT LOCATION
// ==========================================

exports.verifyAadhaarOtp = async (req, res) => {
  const {
    aadhaarNumber,
    otp,
    currentState,
    currentDistrict,
    currentMandal,
  } = req.body;

  // Validate Aadhaar and OTP
  if (!aadhaarNumber || !otp) {
    return res.status(400).json({
      success: false,
      message: 'Both Aadhaar number and OTP are required.',
    });
  }

  // Validate current location
  if (!currentState || !currentDistrict || !currentMandal) {
    return res.status(400).json({
      success: false,
      message:
        'Current state, district, and mandal are required.',
    });
  }

  // Get stored OTP
  const storedData = otpStore.get(aadhaarNumber);

  if (!storedData) {
    return res.status(400).json({
      success: false,
      message:
        'No active OTP request found. Please request an OTP first.',
    });
  }

  // Check OTP expiry
  if (Date.now() > storedData.expiresAt) {
    otpStore.delete(aadhaarNumber);

    return res.status(400).json({
      success: false,
      message: 'OTP has expired. Please request a new one.',
    });
  }

  // Check OTP
  if (storedData.otp !== String(otp)) {
    return res.status(401).json({
      success: false,
      message: 'Incorrect OTP entered. Please try again.',
    });
  }

  // OTP is valid, remove it
  otpStore.delete(aadhaarNumber);

  try {
    // ==========================================
    // UPDATE CURRENT LOCATION
    // ==========================================

    const updateQuery = `
      UPDATE artisans
      SET
        current_state = $1,
        current_district = $2,
        current_mandal = $3,
        updated_at = CURRENT_TIMESTAMP
      WHERE aadhaar_number = $4
      RETURNING
        id,
        name,
        phone_number,
        registered_state,
        registered_district,
        registered_mandal,
        current_state,
        current_district,
        current_mandal;
    `;

    const updatedResult = await pool.query(
      updateQuery,
      [
        currentState,
        currentDistrict,
        currentMandal,
        aadhaarNumber,
      ]
    );

    // Artisan not found during update
    if (updatedResult.rows.length === 0) {
      return res.status(404).json({
        success: false,
        message: 'Artisan record not found.',
      });
    }

    const updatedArtisan = updatedResult.rows[0];

    // ==========================================
    // SUCCESS RESPONSE
    // ==========================================

    return res.status(200).json({
      success: true,
      message:
        'Identity verified and current location updated successfully!',

      artisan: {
        id: updatedArtisan.id,

        name: updatedArtisan.name,

        phone: updatedArtisan.phone_number,

        registeredLocation: {
          state: updatedArtisan.registered_state,
          district: updatedArtisan.registered_district,
          mandal: updatedArtisan.registered_mandal,
        },

        currentLocation: {
          state: updatedArtisan.current_state,
          district: updatedArtisan.current_district,
          mandal: updatedArtisan.current_mandal,
        },
      },
    });

  } catch (err) {
    console.error(
      '❌ Database update error:',
      err.message
    );

    return res.status(500).json({
      success: false,
      message:
        'Error updating current location in database.',
    });
  }
};