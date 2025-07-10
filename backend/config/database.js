const { Pool } = require('pg');
require('dotenv').config();

// Simple query statistics tracking
const queryStats = {
    totalQueries: 0,
    startTime: Date.now(),
    queryTimes: [],
    recentQueries: [] // Track recent query details for performance monitoring
};

// Database connection configuration
const dbConfig = {
    host: process.env.DB_HOST || 'localhost',
    port: process.env.DB_PORT || 5432,
    database: process.env.DB_NAME || 'ecommerce_db',
    user: process.env.DB_USER || 'postgres',
    password: process.env.DB_PASSWORD,
    max: parseInt(process.env.DB_MAX_CONNECTIONS) || 20,
    idleTimeoutMillis: 30000,
    connectionTimeoutMillis: 2000,
};

// Create connection pool
const pool = new Pool(dbConfig);

// Handle pool errors
pool.on('error', (err) => {
    console.error('Unexpected error on idle client', err);
    process.exit(-1);
});

// Test connection
pool.connect()
    .then(client => {
        console.log('✅ Database connected successfully');
        client.release();
    })
    .catch(err => {
        console.error('❌ Database connection failed:', err.message);
    });

// Helper function to execute queries with error handling
const query = async (text, params) => {
    const start = Date.now();
    try {
        const result = await pool.query(text, params);
        const duration = Date.now() - start;
        
        // Track query statistics
        queryStats.totalQueries++;
        queryStats.queryTimes.push({
            duration,
            timestamp: Date.now()
        });
        
        // Track recent queries with details for performance monitoring
        const queryPreview = text.length > 80 ? text.substring(0, 80) + '...' : text;
        queryStats.recentQueries.push({
            query: queryPreview,
            duration,
            timestamp: Date.now(),
            rowCount: result.rowCount || 0,
            status: duration < 50 ? 'Fast' : duration < 200 ? 'Moderate' : 'Slow'
        });
        
        // Keep only last 10 recent queries
        if (queryStats.recentQueries.length > 10) {
            queryStats.recentQueries = queryStats.recentQueries.slice(-10);
        }
        
        // Keep only last hour of query times
        const oneHourAgo = Date.now() - (60 * 60 * 1000);
        queryStats.queryTimes = queryStats.queryTimes.filter(q => q.timestamp > oneHourAgo);
        
        console.log(`Query executed in ${duration}ms:`, text.substring(0, 100));
        return result;
    } catch (error) {
        console.error('Query error:', error.message);
        throw error;
    }
};

// Helper function for transactions
const transaction = async (callback) => {
    const client = await pool.connect();
    try {
        await client.query('BEGIN');
        const result = await callback(client);
        await client.query('COMMIT');
        return result;
    } catch (error) {
        await client.query('ROLLBACK');
        throw error;
    } finally {
        client.release();
    }
};

// Get query statistics
const getQueryStats = () => {
    const currentTime = Date.now();
    const runtimeHours = (currentTime - queryStats.startTime) / (1000 * 60 * 60);
    const queriesPerHour = runtimeHours > 0 ? Math.round(queryStats.totalQueries / runtimeHours) : 0;
    
    // Calculate average query time from last hour
    const avgQueryTime = queryStats.queryTimes.length > 0 
        ? Math.round(queryStats.queryTimes.reduce((sum, q) => sum + q.duration, 0) / queryStats.queryTimes.length)
        : 0;
    
    return {
        total_queries: queryStats.totalQueries,
        queries_per_hour: queriesPerHour,
        queries_last_hour: queryStats.queryTimes.length,
        avg_query_time: avgQueryTime,
        runtime_hours: Math.round(runtimeHours * 10) / 10,
        recent_queries: queryStats.recentQueries.slice().reverse() // Most recent first
    };
};

module.exports = {
    pool,
    query,
    transaction,
    getQueryStats
};
