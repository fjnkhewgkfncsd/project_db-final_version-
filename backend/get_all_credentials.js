const { Pool } = require('pg');

const pool = new Pool({ 
    user: 'postgres', 
    host: 'localhost', 
    database: 'ecommerce_db', 
    password: 'hengmengly123', 
    port: 5432 
});

async function getAllCredentials() {
    try {
        // Get original admin account
        const originalAdmin = await pool.query(`
            SELECT username, email, role 
            FROM users 
            WHERE email = 'admin@example.com'
        `);
        
        // Get a few generated admin accounts
        const adminAccounts = await pool.query(`
            SELECT username, email, role 
            FROM users 
            WHERE role = 'admin' AND email != 'admin@example.com'
            ORDER BY email 
            LIMIT 3
        `);
        
        // Get a few staff accounts  
        const staffAccounts = await pool.query(`
            SELECT username, email, role 
            FROM users 
            WHERE role = 'staff'
            ORDER BY email 
            LIMIT 3
        `);
        
        console.log('🔐 DEMO LOGIN CREDENTIALS');
        console.log('=========================');
        console.log('Password for ALL accounts: admin123');
        console.log('');
        
        if (originalAdmin.rows.length > 0) {
            console.log('🎯 ORIGINAL ADMIN ACCOUNT:');
            const admin = originalAdmin.rows[0];
            console.log(`   Email: ${admin.email}`);
            console.log(`   Username: ${admin.username}`);
            console.log(`   Role: ${admin.role}`);
            console.log('');
        }
        
        console.log('👑 ADMIN ACCOUNTS:');
        adminAccounts.rows.forEach((row, idx) => {
            console.log(`   ${idx + 1}. ${row.email}`);
            console.log(`      Username: ${row.username}`);
            console.log(`      Role: ${row.role}`);
        });
        console.log('');
        
        console.log('👤 STAFF ACCOUNTS:');
        staffAccounts.rows.forEach((row, idx) => {
            console.log(`   ${idx + 1}. ${row.email}`);
            console.log(`      Username: ${row.username}`);
            console.log(`      Role: ${row.role}`);
        });
        
        pool.end();
    } catch (err) {
        console.error('Error:', err.message);
        pool.end();
    }
}

getAllCredentials();
