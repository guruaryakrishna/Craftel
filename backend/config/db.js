require('dotenv').config();

const { Pool } = require('pg');

// Make sure DATABASE_URL exists
if (!process.env.DATABASE_URL) {
    console.error('❌ DATABASE_URL is not defined in .env');
    process.exit(1);
}

const pool = new Pool({
    connectionString: process.env.DATABASE_URL,

    // Required for Supabase PostgreSQL
    ssl: {
        rejectUnauthorized: false,
    },

    // Optional connection settings
    max: 10,
    idleTimeoutMillis: 30000,
    connectionTimeoutMillis: 10000,
});

// Test database connection
pool.on('connect', () => {
    console.log('📦 Connected to Supabase PostgreSQL');
});

pool.on('error', (err) => {
    console.error('❌ Unexpected database error:', err.message);
});

// Export pool for controllers
module.exports = pool;