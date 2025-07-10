const axios = require('axios');

async function testLogin() {
    try {
        console.log('🧪 Testing login functionality...');
        
        const baseURL = 'http://localhost:3001';
        
        // Test data for different roles
        const testUsers = [
            { email: 'admin@example.com', password: 'admin123', role: 'admin' },
            { email: 'staff@example.com', password: 'staff123', role: 'staff' },
            { email: 'customer@example.com', password: 'customer123', role: 'customer' }
        ];
        
        for (const user of testUsers) {
            console.log(`\n🔍 Testing login for ${user.role}...`);
            
            try {
                const response = await axios.post(`${baseURL}/api/users/login`, {
                    email: user.email,
                    password: user.password
                });
                
                if (response.data.success) {
                    console.log(`✅ ${user.role} login successful!`);
                    console.log(`   📧 Email: ${user.email}`);
                    console.log(`   👤 User: ${response.data.data.user.username}`);
                    console.log(`   🎭 Role: ${response.data.data.user.role}`);
                    console.log(`   🎫 Token: ${response.data.data.token.substring(0, 20)}...`);
                } else {
                    console.log(`❌ ${user.role} login failed: ${response.data.message}`);
                }
            } catch (error) {
                if (error.response) {
                    console.log(`❌ ${user.role} login failed: ${error.response.data.message}`);
                } else {
                    console.log(`❌ ${user.role} login error: ${error.message}`);
                }
            }
        }
        
        // Test invalid credentials
        console.log(`\n🔍 Testing invalid credentials...`);
        try {
            const response = await axios.post(`${baseURL}/api/users/login`, {
                email: 'invalid@example.com',
                password: 'wrongpassword'
            });
            console.log(`❌ Should have failed but got: ${response.data.message}`);
        } catch (error) {
            if (error.response && error.response.status === 401) {
                console.log(`✅ Invalid credentials correctly rejected: ${error.response.data.message}`);
            } else {
                console.log(`❌ Unexpected error: ${error.message}`);
            }
        }
        
        console.log('\n🎉 Login tests completed!');
        
    } catch (error) {
        console.error('❌ Test error:', error.message);
    }
}

testLogin();
