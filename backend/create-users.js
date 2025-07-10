const { pool } = require('./config/database');

async function createDefaultUsers() {
    try {
        console.log('🚀 Creating default users...');
        
        // Check if users table exists
        const tableCheck = await pool.query(`
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'users'
            );
        `);
        
        if (!tableCheck.rows[0].exists) {
            console.log('❌ Users table does not exist. Please run the schema first.');
            process.exit(1);
        }
        
        const bcrypt = require('bcryptjs');
        
        // Create default users for all roles
        const defaultUsers = [
            ['admin', 'admin@example.com', 'admin123', 'Admin', 'User', 'admin'],
            ['staff1', 'staff@example.com', 'staff123', 'Staff', 'User', 'staff'],
            ['customer1', 'customer@example.com', 'customer123', 'Customer', 'User', 'customer'],
            ['customer2', 'readonly@example.com', 'readonly123', 'Read', 'Only', 'customer']
        ];
        
        console.log('🔑 Creating users with hashed passwords...');
        
        for (const [username, email, password, firstName, lastName, role] of defaultUsers) {
            const hashedPassword = await bcrypt.hash(password, 10);
            
            try {
                await pool.query(`
                    INSERT INTO users (username, email, password_hash, first_name, last_name, role, is_active)
                    VALUES ($1, $2, $3, $4, $5, $6, $7)
                    ON CONFLICT (email) DO UPDATE SET
                        password_hash = EXCLUDED.password_hash,
                        updated_at = CURRENT_TIMESTAMP
                `, [username, email, hashedPassword, firstName, lastName, role, true]);
                
                console.log(`   ✅ ${role}: ${email}`);
            } catch (userError) {
                console.log(`   ⚠️  ${role}: ${email} - ${userError.message}`);
            }
        }
        
        // Verify users were created
        const userCount = await pool.query('SELECT COUNT(*) FROM users');
        console.log(`\n📊 Total users in database: ${userCount.rows[0].count}`);
        
        console.log('\n👥 Available login accounts:');
        console.log('   🔐 Admin: admin@example.com / admin123');
        console.log('   👨‍💼 Staff: staff@example.com / staff123');
        console.log('   👤 Customer: customer@example.com / customer123');
        console.log('   👁️  Read-Only (Customer): readonly@example.com / readonly123');
        
        console.log('\n🎉 User creation completed successfully!');
        process.exit(0);
    } catch (error) {
        console.error('❌ Error creating users:', error.message);
        process.exit(1);
    }
}

createDefaultUsers();
