-- Enable pg_stat_statements extension for query performance monitoring
-- This is optional and provides advanced query analytics

-- Connect as superuser (postgres) and run:
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- You may also need to add this to postgresql.conf:
-- shared_preload_libraries = 'pg_stat_statements'
-- pg_stat_statements.track = all
-- pg_stat_statements.max = 10000

-- Then restart PostgreSQL service

-- Verify installation:
SELECT * FROM pg_stat_statements LIMIT 1;
