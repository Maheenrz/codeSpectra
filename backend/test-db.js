require('dotenv').config();
const pool = require('./src/config/database');

async function testDatabase() {
  console.log('🧪 Testing database connection...\n');
  
  try {
    // Test connection
    const client = await pool.connect();
    console.log('✅ Connection successful!\n');
    
    // Test users table
    const usersResult = await client.query('SELECT COUNT(*) FROM users');
    console.log(`📊 Users in database: ${usersResult.rows[0].count}`);
    
    // List all tables
    const tablesResult = await client.query(`
      SELECT table_name 
      FROM information_schema.tables 
      WHERE table_schema = 'public' 
      ORDER BY table_name
    `);
    
    console.log('\n📋 Available tables:');
    tablesResult.rows.forEach(row => {
      console.log(`   - ${row.table_name}`);
    });
    
    // Test sample user
    const sampleUser = await client.query('SELECT * FROM users LIMIT 1');
    if (sampleUser.rows.length > 0) {
      console.log('\n👤 Sample user:');
      console.log(`   Name: ${sampleUser.rows[0].first_name} ${sampleUser.rows[0].last_name}`);
      console.log(`   Email: ${sampleUser.rows[0].email}`);
      console.log(`   Role: ${sampleUser.rows[0].role}`);
    }
    
    client.release();
    console.log('\n✅ All tests passed!');
    process.exit(0);
    
  } catch (error) {
    console.error('❌ Database test failed:', error.message);
    console.error('Full error:', error);
    process.exit(1);
  }
}

testDatabase();