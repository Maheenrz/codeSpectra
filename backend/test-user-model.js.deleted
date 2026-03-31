require('dotenv').config();
const User = require('./src/models/User');

async function testUserModel() {
  console.log('🧪 Testing User model...\n');
  
  try {
    // Test findByEmail
    const user = await User.findByEmail('maheen@codespectra.com');
    if (user) {
      console.log('✅ findByEmail works!');
      console.log('   User:', user.first_name, user.last_name);
    }
    
    // Test findById
    if (user) {
      const userById = await User.findById(user.user_id);
      console.log('✅ findById works!');
      console.log('   User ID:', userById.user_id);
    }
    
    console.log('\n✅ User model tests passed!');
    process.exit(0);
    
  } catch (error) {
    console.error('❌ Test failed:', error.message);
    process.exit(1);
  }
}

testUserModel();