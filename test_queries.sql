-- Test Database Queries
-- Copy and paste these into your PostgreSQL client or the web query console

-- Test 1: Check all tables and record counts
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables 
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Test 2: User roles distribution
SELECT role, COUNT(*) as count 
FROM users 
GROUP BY role 
ORDER BY count DESC;

-- Test 3: Product categories
SELECT c.name, COUNT(p.product_id) as product_count
FROM categories c
LEFT JOIN products p ON c.category_id = p.category_id
GROUP BY c.category_id, c.name
ORDER BY product_count DESC;

-- Test 4: Database performance metrics
SELECT 
    datname as database_name,
    pg_size_pretty(pg_database_size(datname)) as size,
    numbackends as connections
FROM pg_stat_database 
WHERE datname = 'ecommerce_db';

-- Test 5: Table statistics
SELECT 
    schemaname, 
    tablename, 
    attname, 
    n_distinct, 
    correlation
FROM pg_stats 
WHERE schemaname = 'public' 
LIMIT 10;
