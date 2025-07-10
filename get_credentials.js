const { Pool } = require('pg');

const pool = new Pool({ 
    user: 'postgres', 
    host: 'localhost', 
    database: 'ecommerce_db', 
    password: 'hengmengly123', 
    port: 5432 
});

async function getCredentials() {
    try {
        const result = await pool.query(`
            SELECT username, email, role 
            FROM users 
            WHERE role IN ('admin', 'staff') 
            ORDER BY role, username 
            LIMIT 10
        `);
        
        console.log('Available Login Credentials:');
        console.log('==========================');
        
        result.rows.forEach((row, idx) => {
            console.log(`${idx + 1}. ${row.role.toUpperCase()}: ${row.email} (username: ${row.username})`);
        });
        
        pool.end();
    } catch (err) {
        console.error('Error:', err.message);
        pool.end();
    }
}

getCredentials();
