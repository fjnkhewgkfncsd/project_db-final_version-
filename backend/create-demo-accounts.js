const { Pool } = require('pg');
const bcrypt = require('bcryptjs');
const { v4: uuidv4 } = require('uuid');

const pool = new Pool({
    user: 'postgres',
    host: 'localhost',
    database: 'ecommerce_db',
    password: 'hengmengly123',
    port: 5432
});

async function createDemoAccounts() {
    try {
        console.log('🔧 Creating demo accounts...');
        
        // Create admin account
        const adminPassword = await bcrypt.hash('admin123', 10);
        await pool.query(`
            INSERT INTO users (user_id, username, email, password_hash, first_name, last_name, phone, date_of_birth, created_at, role, is_active) 
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11) 
            ON CONFLICT (email) DO UPDATE SET 
                password_hash = $4,
                username = $2,
                role = $10
        `, [uuidv4(), 'admin', 'admin@example.com', adminPassword, 'Admin', 'User', '+1234567890', '1990-01-01', new Date(), 'admin', true]);
        console.log('✅ Admin: admin@example.com / admin123');
        
        // Create staff account
        const staffPassword = await bcrypt.hash('staff123', 10);
        await pool.query(`
            INSERT INTO users (user_id, username, email, password_hash, first_name, last_name, phone, date_of_birth, created_at, role, is_active) 
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11) 
            ON CONFLICT (email) DO UPDATE SET 
                password_hash = $4,
                username = $2,
                role = $10
        `, [uuidv4(), 'staff1', 'staff@example.com', staffPassword, 'Staff', 'User', '+1234567891', '1990-01-01', new Date(), 'staff', true]);
        console.log('✅ Staff: staff@example.com / staff123');
        
        // Create customer account
        const customerPassword = await bcrypt.hash('customer123', 10);
        await pool.query(`
            INSERT INTO users (user_id, username, email, password_hash, first_name, last_name, phone, date_of_birth, created_at, role, is_active) 
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11) 
            ON CONFLICT (email) DO UPDATE SET 
                password_hash = $4,
                username = $2,
                role = $10
        `, [uuidv4(), 'customer1', 'customer@example.com', customerPassword, 'Customer', 'User', '+1234567892', '1990-01-01', new Date(), 'customer', true]);
        console.log('✅ Customer: customer@example.com / customer123');
        
        console.log('🎉 Demo accounts created successfully!');
        
    } catch (error) {
        console.error('❌ Error creating demo accounts:', error.message);
    } finally {
        pool.end();
    }
}

createDemoAccounts();
