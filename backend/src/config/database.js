// Update src/config/database.js
const { Pool } = require('pg');
require('dotenv').config();

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  // Add these for better debugging
  connectionTimeoutMillis: 5000,
  idleTimeoutMillis: 30000,
});

// Test connection immediately
pool.connect((err, client, release) => {
  if (err) {
    console.error('❌ Database connection error:', err.message);
    console.error('❌ Full error:', err);
  } else {
    console.log('✅ Database connected successfully');
    release();
  }
});

module.exports = pool;