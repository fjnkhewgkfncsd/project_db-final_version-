const axios = require('axios');

async function testLogin() {
    try {
        console.log('Testing login with admin@example.com / admin123...');
        
        const response = await axios.post('http://localhost:3001/api/users/login', {
            email: 'admin@example.com',
            password: 'admin123'
        });
        
        console.log('✅ Login successful!');
        console.log('Response:', response.data);
        
    } catch (error) {
        if (error.response) {
            console.log('❌ Login failed:');
            console.log('Status:', error.response.status);
            console.log('Data:', error.response.data);
        } else if (error.code === 'ECONNREFUSED') {
            console.log('❌ Server not running at http://localhost:3001');
            console.log('Please start the server first: npm start');
        } else {
            console.log('❌ Error:', error.message);
        }
    }
}

testLogin();
