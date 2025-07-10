const { Pool } = require('pg');
const bcrypt = require('bcryptjs');

const pool = new Pool({
    user: 'postgres',
    host: 'localhost',
    database: 'ecommerce_db',
    password: 'hengmengly123',
    port: 5432
});

async function fixAdminPassword() {
    try {
        console.log('🔧 Checking all admin accounts...');
        
        // Check current admin accounts
        const adminResult = await pool.query('SELECT user_id, username, email, role FROM users WHERE role = \'admin\'');
        console.log('Current admin accounts:');
        adminResult.rows.forEach(row => {
            console.log(`- ${row.email} (${row.username})`);
        });
        
        // Create new password hash
        const newPasswordHash = await bcrypt.hash('admin123', 10);
        console.log('\n🔑 Updating password for admin@example.com...');
        
        // Update the admin@example.com account
        const updateResult = await pool.query(
            'UPDATE users SET password_hash = $1 WHERE email = $2 RETURNING email, username', 
            [newPasswordHash, 'admin@example.com']
        );
        
        if (updateResult.rows.length > 0) {
            console.log('✅ Password updated successfully for:', updateResult.rows[0].email);
        } else {
            console.log('❌ No admin@example.com account found');
        }
        
        // Also update admin@ecommerce.com if it exists
        const updateResult2 = await pool.query(
            'UPDATE users SET password_hash = $1 WHERE email = $2 RETURNING email, username', 
            [newPasswordHash, 'admin@ecommerce.com']
        );
        
        if (updateResult2.rows.length > 0) {
            console.log('✅ Password updated successfully for:', updateResult2.rows[0].email);
        }
        
        console.log('\n📋 Updated admin credentials:');
        console.log('Email: admin@example.com');
        console.log('Password: admin123');
        
    } catch (error) {
        console.error('❌ Error:', error.message);
    } finally {
        pool.end();
    }
}

fixAdminPassword();
