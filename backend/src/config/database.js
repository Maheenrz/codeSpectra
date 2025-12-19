// backend/src/config/database.js
const { Pool } = require('pg');
require('dotenv').config();

// Database configuration
const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  // Connection pool settings
  connectionTimeoutMillis: 5000,
  idleTimeoutMillis: 30000,
  max: 20,  // Maximum number of clients in the pool
  
  // SSL configuration (use in production)
  ssl: process.env.NODE_ENV === 'production' ? { rejectUnauthorized: false } : false
});

// Test connection on startup
pool.on('connect', (client) => {
  console.log('✅ New client connected to PostgreSQL database');
});

pool.on('error', (err, client) => {
  console.error('❌ Unexpected error on idle client:', err);
  process.exit(-1);
});

// Initial connection test
const testConnection = async () => {
  try {
    const client = await pool.connect();
    const result = await client.query('SELECT NOW(), version()');
    console.log('✅ Database connected successfully!');
    console.log('📅 Server time:', result.rows[0].now);
    console.log('🗄️  PostgreSQL version:', result.rows[0].version.split(' ')[1]);
    
    // Test if tables exist
    const tablesResult = await client.query(`
      SELECT COUNT(*) as table_count 
      FROM information_schema.tables 
      WHERE table_schema = 'public'
    `);
    console.log('📊 Total tables:', tablesResult.rows[0].table_count);
    
    client.release();
    return true;
  } catch (err) {
    console.error('❌ Database connection failed:', err.message);
    console.error('🔧 Connection string:', process.env.DATABASE_URL?.replace(/:[^:@]+@/, ':****@'));
    console.error('💡 Make sure PostgreSQL is running: docker-compose up -d postgresql');
    return false;
  }
};

// Run test on module load
testConnection();

// Helper function to execute queries with error handling
pool.queryWithErrorHandling = async (text, params) => {
  const start = Date.now();
  try {
    const res = await pool.query(text, params);
    const duration = Date.now() - start;
    console.log('✅ Query executed', { text: text.substring(0, 50), duration, rows: res.rowCount });
    return res;
  } catch (error) {
    console.error('❌ Query error:', error.message);
    console.error('Query:', text);
    throw error;
  }
};

// Helper to get database statistics
pool.getStats = async () => {
  try {
    const client = await pool.connect();
    
    // Get database size
    const sizeResult = await client.query(`
      SELECT pg_size_pretty(pg_database_size(current_database())) as size
    `);
    
    // Get table counts
    const tablesResult = await client.query(`
      SELECT 
        schemaname,
        COUNT(*) as table_count
      FROM pg_tables 
      WHERE schemaname = 'public'
      GROUP BY schemaname
    `);
    
    // Get connection info
    const connectionsResult = await client.query(`
      SELECT 
        COUNT(*) as total_connections,
        COUNT(*) FILTER (WHERE state = 'active') as active_connections,
        COUNT(*) FILTER (WHERE state = 'idle') as idle_connections
      FROM pg_stat_activity
      WHERE datname = current_database()
    `);
    
    client.release();
    
    return {
      database_size: sizeResult.rows[0].size,
      tables: tablesResult.rows[0]?.table_count || 0,
      connections: connectionsResult.rows[0]
    };
  } catch (error) {
    console.error('Error getting database stats:', error.message);
    return null;
  }
};

module.exports = pool;