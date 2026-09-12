require('dotenv').config();

const express = require('express');
const cors = require('cors');
const pool = require('./config/db');

const app = express();
const PORT = process.env.PORT || 5000;

// ==========================================
// 1. MIDDLEWARE
// ==========================================

app.use(cors());
app.use(express.json());

// ==========================================
// 2. API ROUTES
// ==========================================

// Aadhaar Verification / Authentication
// DO NOT CHANGE THIS ROUTE
app.use('/api/auth', require('./routes/authRoutes'));

// Voice API
app.use('/api/voice', require('./routes/voiceRoutes'));

// Text Translation API
app.use('/api/translate-text', require('./routes/translationRoutes'));

// image_enhancement
// FIX: Require the router into a variable first to ensure Express reads it as a valid function
const productImageRoutes = require('./routes/productImageRoutes');
app.use('/api/product-image', productImageRoutes);

// ==========================================
// 3. HEALTH CHECK
// ==========================================

app.get('/health', async (req, res) => {
    try {
        await pool.query('SELECT 1');

        res.status(200).json({
            status: 'active',
            service: 'Craftel Backend',
            database: 'connected'
        });

    } catch (error) {
        console.error('❌ Health check database error:', error.message);

        res.status(503).json({
            status: 'active',
            service: 'Craftel Backend',
            database: 'disconnected'
        });
    }
});

// ==========================================
// 4. DATABASE CONNECTION TEST
// ==========================================

async function testDatabaseConnection() {
    try {
        const result = await pool.query('SELECT NOW()');

        console.log('✅ Connected to Supabase PostgreSQL database successfully!');
        console.log('🕒 Database time:', result.rows[0].now);

    } catch (error) {
        console.error('❌ Database connection failed:', error.message);
    }
}

// ==========================================
// 5. 404 HANDLER
// ==========================================

app.use((req, res) => {
    res.status(404).json({
        success: false,
        message: 'API endpoint not found'
    });
});

// ==========================================
// 6. ERROR HANDLER
// ==========================================

app.use((err, req, res, next) => {
    console.error('❌ Server Error:', err.message);

    res.status(500).json({
        success: false,
        message: 'Internal server error'
    });
});

// ==========================================
// 7. START SERVER
// ==========================================

app.listen(PORT, async () => {
    console.log('==========================================');
    console.log('🚀 Craftel Backend Started');
    console.log(`🌐 Server: http://localhost:${PORT}`);
    console.log(`❤️  Health: http://localhost:${PORT}/health`);
    console.log('==========================================');

    await testDatabaseConnection();
});