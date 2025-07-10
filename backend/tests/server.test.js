const request = require('supertest');
const app = require('../server');

describe('Health Check Endpoints', () => {
  test('GET /health should return server status', async () => {
    const response = await request(app)
      .get('/health')
      .expect(200);
    
    expect(response.body.success).toBe(true);
    expect(response.body.message).toBe('Server is running');
    expect(response.body.timestamp).toBeDefined();
  });

  test('GET /api/health should return API status', async () => {
    const response = await request(app)
      .get('/api/health')
      .expect(200);
    
    expect(response.body.success).toBe(true);
    expect(response.body.message).toBe('API is healthy');
    expect(response.body.timestamp).toBeDefined();
  });
});

describe('API Root Endpoint', () => {
  test('GET / should return API information', async () => {
    const response = await request(app)
      .get('/')
      .expect(200);
    
    expect(response.body.success).toBe(true);
    expect(response.body.message).toBe('E-Commerce Database Administration API');
  });
});
