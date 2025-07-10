const { pool } = require('./config/database');
const fs = require('fs');
const path = require('path');

async function initializeDatabase() {
    try {
        console.log('🚀 Initializing database schema...');
        
        // First, drop existing tables if they exist (in correct order due to foreign keys)
        console.log('🗑️ Dropping existing tables and roles...');
        
        // Step 1: Drop all tables with CASCADE to remove dependencies
        await pool.query(`
            -- Drop tables in dependency order with CASCADE
            DROP TABLE IF EXISTS notifications CASCADE;
            DROP TABLE IF EXISTS shipments CASCADE;
            DROP TABLE IF EXISTS payments CASCADE;
            DROP TABLE IF EXISTS order_items CASCADE;
            DROP TABLE IF EXISTS orders CASCADE;
            DROP TABLE IF EXISTS favorites CASCADE;
            DROP TABLE IF EXISTS cart_items CASCADE;
            DROP TABLE IF EXISTS cart CASCADE;
            DROP TABLE IF EXISTS product_sizes CASCADE;
            DROP TABLE IF EXISTS products CASCADE;
            DROP TABLE IF EXISTS categories CASCADE;
            DROP TABLE IF EXISTS users CASCADE;
            
            -- Drop types
            DROP TYPE IF EXISTS order_status CASCADE;
            DROP TYPE IF EXISTS user_role CASCADE;
        `);
        
        // Step 2: Revoke all privileges and drop roles safely
        try {
            await pool.query(`
                -- Revoke all privileges from roles on database
                REVOKE ALL PRIVILEGES ON DATABASE ecommerce_db FROM db_customer;
                REVOKE ALL PRIVILEGES ON DATABASE ecommerce_db FROM db_staff;
                REVOKE ALL PRIVILEGES ON DATABASE ecommerce_db FROM db_admin;
                
                -- Revoke all privileges on schema
                REVOKE ALL PRIVILEGES ON SCHEMA public FROM db_customer;
                REVOKE ALL PRIVILEGES ON SCHEMA public FROM db_staff;
                REVOKE ALL PRIVILEGES ON SCHEMA public FROM db_admin;
            `);
        } catch (error) {
            console.log('⚠️ Some privileges may not exist, continuing...');
        }
        
        // Step 3: Drop roles if they exist
        try {
            await pool.query(`DROP ROLE IF EXISTS db_customer;`);
            await pool.query(`DROP ROLE IF EXISTS db_staff;`);
            await pool.query(`DROP ROLE IF EXISTS db_admin;`);
        } catch (error) {
            console.log('⚠️ Some roles may have dependencies, continuing...');
        }
        
        console.log('✅ Existing tables, types, and roles dropped successfully!');
        
        // Read the schema file
        const schemaPath = path.join(__dirname, '..', 'db', 'schema.sql');
        const schema = fs.readFileSync(schemaPath, 'utf8');
        
        // Execute the schema
        await pool.query(schema);
        
        console.log('✅ Database schema created successfully!');
        
        // Create default admin user
        const bcrypt = require('bcryptjs');
        console.log('👥 Creating default users...');
        
        // Define all users to create
        const defaultUsers = [
            {
                username: 'admin',
                email: 'admin@example.com',
                password: 'admin123',
                first_name: 'Admin',
                last_name: 'User',
                role: 'admin'
            },
            {
                username: 'staff1',
                email: 'staff@example.com',
                password: 'staff123',
                first_name: 'Staff',
                last_name: 'User',
                role: 'staff'
            },
            {
                username: 'customer1',
                email: 'customer@example.com',
                password: 'customer123',
                first_name: 'Customer',
                last_name: 'User',
                role: 'customer'
            }
        ];
        
        for (const user of defaultUsers) {
            const hashedPassword = await bcrypt.hash(user.password, 10);
            
            try {
                const result = await pool.query(`
                    INSERT INTO users (username, email, password_hash, first_name, last_name, role, is_active)
                    VALUES ($1, $2, $3, $4, $5, $6, $7)
                    ON CONFLICT (username) DO UPDATE SET
                        email = EXCLUDED.email,
                        password_hash = EXCLUDED.password_hash,
                        first_name = EXCLUDED.first_name,
                        last_name = EXCLUDED.last_name,
                        role = EXCLUDED.role,
                        is_active = EXCLUDED.is_active,
                        updated_at = CURRENT_TIMESTAMP
                    RETURNING user_id, username
                `, [user.username, user.email, hashedPassword, user.first_name, user.last_name, user.role, true]);
                
                console.log(`✅ Created/Updated user: ${user.username} (ID: ${result.rows[0].user_id})`);
                console.log(`   📧 Email: ${user.email}`);
                console.log(`   🔑 Password: ${user.password}`);
                
            } catch (emailConflictError) {
                // Handle email conflict by updating the existing record
                if (emailConflictError.constraint === 'users_email_key') {
                    const result = await pool.query(`
                        UPDATE users 
                        SET username = $1, password_hash = $2, first_name = $3, last_name = $4, role = $5, is_active = $6, updated_at = CURRENT_TIMESTAMP
                        WHERE email = $7
                        RETURNING user_id, username
                    `, [user.username, hashedPassword, user.first_name, user.last_name, user.role, true, user.email]);
                    
                    console.log(`✅ Updated existing user: ${user.username} (ID: ${result.rows[0].user_id})`);
                    console.log(`   📧 Email: ${user.email}`);
                    console.log(`   🔑 Password: ${user.password}`);
                } else {
                    throw emailConflictError;
                }
            }
        }
        
        console.log('✅ All users created/updated successfully!');
        console.log('👥 Available test accounts:');
        console.log('   🔒 Admin: admin@example.com / admin123');
        console.log('   👤 Staff: staff@example.com / staff123');
        console.log('   🛒 Customer: customer@example.com / customer123');
        
        process.exit(0);
    } catch (error) {
        console.error('❌ Error initializing database:', error.message);
        process.exit(1);
    }
}

initializeDatabase();
