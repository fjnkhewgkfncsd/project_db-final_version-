const { pool } = require('./config/database');

async function checkUsers() {
    try {
        console.log('🔍 Checking users in database...');
        
        const result = await pool.query(`
            SELECT user_id, username, email, first_name, last_name, role, is_active, created_at
            FROM users
            ORDER BY role, username
        `);
        
        console.log(`\n📊 Found ${result.rows.length} users:`);
        
        result.rows.forEach((user, index) => {
            console.log(`\n${index + 1}. User ID: ${user.user_id}`);
            console.log(`   Username: ${user.username}`);
            console.log(`   Email: ${user.email}`);
            console.log(`   Name: ${user.first_name} ${user.last_name}`);
            console.log(`   Role: ${user.role}`);
            console.log(`   Active: ${user.is_active}`);
            console.log(`   Created: ${user.created_at}`);
        });
        
        // Test password verification for admin user
        const adminUser = await pool.query(`
            SELECT email, password_hash FROM users WHERE email = $1
        `, ['admin@example.com']);
        
        if (adminUser.rows.length > 0) {
            const bcrypt = require('bcryptjs');
            const isValidPassword = await bcrypt.compare('admin123', adminUser.rows[0].password_hash);
            console.log(`\n🔐 Password verification for admin@example.com: ${isValidPassword ? '✅ VALID' : '❌ INVALID'}`);
        }
        
        process.exit(0);
    } catch (error) {
        console.error('❌ Error checking users:', error.message);
        process.exit(1);
    }
}

checkUsers();
