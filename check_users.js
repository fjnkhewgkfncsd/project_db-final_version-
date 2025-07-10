const { Pool } = require('pg');

const pool = new Pool({
    user: 'postgres',
    host: 'localhost',
    database: 'ecommerce_db',
    password: 'hengmengly123',
    port: 5432
});

async function checkUsers() {
    try {
        const result = await pool.query('SELECT username, email, role FROM users ORDER BY role, created_at');
        console.log('Current users in database:');
        console.log('=====================================');
        result.rows.forEach(row => {
            console.log(`${row.role.toUpperCase()}: ${row.email} (username: ${row.username})`);
        });
    } catch (error) {
        console.error('Error:', error.message);
    } finally {
        pool.end();
    }
}

checkUsers();
