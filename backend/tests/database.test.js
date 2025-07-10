const { pool } = require('../config/database');

describe('Database Connection', () => {
  test('should connect to database', async () => {
    const result = await pool.query('SELECT 1 as test');
    expect(result.rows[0].test).toBe(1);
  });

  test('should have required tables', async () => {
    const tables = [
      'users', 'customers', 'products', 'categories', 'orders', 
      'order_items', 'reviews', 'suppliers', 'inventory', 'payments'
    ];

    for (const table of tables) {
      const result = await pool.query(`
        SELECT EXISTS (
          SELECT FROM information_schema.tables 
          WHERE table_schema = 'public' 
          AND table_name = $1
        )
      `, [table]);
      
      expect(result.rows[0].exists).toBe(true);
    }
  });

  test('should have required roles', async () => {
    const roles = ['db_admin', 'customer_service', 'read_only', 'app_user'];

    for (const role of roles) {
      const result = await pool.query(`
        SELECT EXISTS (
          SELECT FROM pg_roles 
          WHERE rolname = $1
        )
      `, [role]);
      
      expect(result.rows[0].exists).toBe(true);
    }
  });

  afterAll(async () => {
    await pool.end();
  });
});
