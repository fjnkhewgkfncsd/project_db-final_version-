const request = require('supertest');
const app = require('../server');
const bcrypt = require('bcryptjs');

describe('User Routes', () => {
  let authToken;
  let testUserId;

  // Test user data
  const testUser = {
    username: 'testuser',
    email: 'test@example.com',
    password: 'TestPassword123!',
    first_name: 'Test',
    last_name: 'User'
  };

  describe('POST /api/users/register', () => {
    test('should register a new user', async () => {
      const response = await request(app)
        .post('/api/users/register')
        .send(testUser)
        .expect(201);

      expect(response.body.success).toBe(true);
      expect(response.body.message).toBe('User registered successfully');
      expect(response.body.user.username).toBe(testUser.username);
      expect(response.body.user.email).toBe(testUser.email);
      
      testUserId = response.body.user.id;
    });

    test('should not register user with duplicate email', async () => {
      const response = await request(app)
        .post('/api/users/register')
        .send(testUser)
        .expect(409);

      expect(response.body.success).toBe(false);
      expect(response.body.message).toContain('already exists');
    });

    test('should validate required fields', async () => {
      const response = await request(app)
        .post('/api/users/register')
        .send({
          username: 'test',
          // missing required fields
        })
        .expect(400);

      expect(response.body.success).toBe(false);
    });
  });

  describe('POST /api/users/login', () => {
    test('should login with valid credentials', async () => {
      const response = await request(app)
        .post('/api/users/login')
        .send({
          email: testUser.email,
          password: testUser.password
        })
        .expect(200);

      expect(response.body.success).toBe(true);
      expect(response.body.token).toBeDefined();
      
      authToken = response.body.token;
    });

    test('should not login with invalid credentials', async () => {
      const response = await request(app)
        .post('/api/users/login')
        .send({
          email: testUser.email,
          password: 'wrongpassword'
        })
        .expect(401);

      expect(response.body.success).toBe(false);
    });
  });

  describe('GET /api/users/profile', () => {
    test('should get user profile with valid token', async () => {
      const response = await request(app)
        .get('/api/users/profile')
        .set('Authorization', `Bearer ${authToken}`)
        .expect(200);

      expect(response.body.success).toBe(true);
      expect(response.body.user.email).toBe(testUser.email);
    });

    test('should not get profile without token', async () => {
      const response = await request(app)
        .get('/api/users/profile')
        .expect(401);

      expect(response.body.success).toBe(false);
    });
  });

  // Cleanup
  afterAll(async () => {
    if (testUserId) {
      // Clean up test user
      const { pool } = require('../config/database');
      await pool.query('DELETE FROM users WHERE id = $1', [testUserId]);
      await pool.end();
    }
  });
});
