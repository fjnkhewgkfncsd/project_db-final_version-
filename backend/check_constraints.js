const { Pool } = require('pg');
require('dotenv').config();

const pool = new Pool({
  host: process.env.DB_HOST,
  port: process.env.DB_PORT,
  user: process.env.DB_USER,
  password: process.env.DB_PASSWORD,
  database: process.env.DB_NAME,
});

async function checkConstraints() {
  const client = await pool.connect();
  try {
    console.log('🔍 ANALYZING USERS TABLE STRUCTURE');
    console.log('='.repeat(50));
    
    // Check for unique constraints
    const constraints = await client.query(`
      SELECT 
        conname as constraint_name,
        contype as constraint_type,
        pg_get_constraintdef(oid) as definition
      FROM pg_constraint 
      WHERE conrelid = 'public.users'::regclass;
    `);
    
    console.log('Users table constraints:');
    constraints.rows.forEach(row => {
      console.log(`  ${row.constraint_name}: ${row.constraint_type} - ${row.definition}`);
    });
    
    // Check for indexes
    const indexes = await client.query(`
      SELECT indexname, indexdef
      FROM pg_indexes 
      WHERE tablename = 'users' AND schemaname = 'public';
    `);
    
    console.log('\nUsers table indexes:');
    indexes.rows.forEach(row => {
      console.log(`  ${row.indexname}: ${row.indexdef}`);
    });
    
    // Check current user count and duplicates
    const userStats = await client.query(`
      SELECT 
        COUNT(*) as total_users,
        COUNT(DISTINCT username) as unique_usernames,
        COUNT(DISTINCT email) as unique_emails
      FROM users;
    `);
    
    console.log('\nCurrent user statistics:');
    console.log(`  Total users: ${userStats.rows[0].total_users}`);
    console.log(`  Unique usernames: ${userStats.rows[0].unique_usernames}`);
    console.log(`  Unique emails: ${userStats.rows[0].unique_emails}`);
    
    // Check if there would be duplicates with backup data
    console.log('\n🔍 Checking for potential conflicts with backup data...');
    
    // Sample some usernames/emails from the backup file content we analyzed
    const testUsers = [
      'admin',
      'maria.yoder.0',
      'matthew.medina.1'
    ];
    
    for (const username of testUsers) {
      const exists = await client.query('SELECT username, email FROM users WHERE username = $1', [username]);
      if (exists.rows.length > 0) {
        console.log(`  ⚠️  Username '${username}' already exists: ${exists.rows[0].email}`);
      } else {
        console.log(`  ✅ Username '${username}' is available`);
      }
    }
    
  } finally {
    client.release();
    await pool.end();
  }
}

checkConstraints().catch(console.error);
