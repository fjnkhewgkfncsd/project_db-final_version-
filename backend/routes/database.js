const express = require('express');
const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');
const router = express.Router();
const auth = require('../middleware/auth');
const { authorizeRoles } = require('../middleware/authorize');

// Create backups directory if it doesn't exist
const backupsDir = path.join(__dirname, '..', '..', 'backups');
if (!fs.existsSync(backupsDir)) {
    fs.mkdirSync(backupsDir, { recursive: true });
}

// Real database backup endpoint with backup type options
router.post('/backup', auth, authorizeRoles(['admin']), async (req, res) => {
    try {
        const { backupType = 'complete' } = req.body; // complete, schema-only, data-only
        
        const timestamp = new Date().toISOString().replace(/[:.]/g, '-').split('T')[0] + '_' + 
                         new Date().toTimeString().split(' ')[0].replace(/:/g, '-');
        
        let backupFilename;
        switch(backupType) {
            case 'schema-only':
                backupFilename = `ecommerce_schema_${timestamp}.sql`;
                break;
            case 'data-only':
                backupFilename = `ecommerce_data_${timestamp}.sql`;
                break;
            default:
                backupFilename = `ecommerce_backup_${timestamp}.sql`;
        }
        
        const backupPath = path.join(backupsDir, backupFilename);

        // PostgreSQL connection details from environment
        const dbConfig = {
            host: process.env.DB_HOST || 'localhost',
            port: process.env.DB_PORT || '5432',
            database: process.env.DB_NAME || 'ecommerce_db',
            user: process.env.DB_USER || 'postgres'
        };

        // Set PGPASSWORD environment variable for pg_dump
        const env = { ...process.env, PGPASSWORD: process.env.DB_PASSWORD };

        // Configure pg_dump arguments based on backup type
        let pgDumpArgs = [
            '-h', dbConfig.host,
            '-p', dbConfig.port,
            '-U', dbConfig.user,
            '-d', dbConfig.database,
            '--verbose',
            '-f', backupPath
        ];

        // Add type-specific arguments
        switch(backupType) {
            case 'schema-only':
                pgDumpArgs.push('--schema-only', '--clean', '--if-exists', '--create', '--no-owner');
                break;
            case 'data-only':
                pgDumpArgs.push('--data-only', '--disable-triggers', '--no-owner');
                break;
            default: // complete backup
                pgDumpArgs.push('--clean', '--if-exists', '--create', '--no-owner', '--no-privileges');
        }

        console.log(`🚀 Starting ${backupType} database backup: ${backupFilename}`);

        const pgDump = spawn('pg_dump', pgDumpArgs, { 
            env,
            stdio: ['pipe', 'pipe', 'pipe']
        });

        let output = '';
        let errorOutput = '';

        pgDump.stdout.on('data', (data) => {
            output += data.toString();
        });

        pgDump.stderr.on('data', (data) => {
            errorOutput += data.toString();
        });

        pgDump.on('close', (code) => {
            if (code === 0) {
                // Get file size
                const stats = fs.statSync(backupPath);
                const fileSizeInMB = (stats.size / (1024 * 1024)).toFixed(2);

                console.log(`✅ Backup completed successfully: ${backupFilename} (${fileSizeInMB} MB)`);

                res.json({
                    success: true,
                    message: 'Database backup completed successfully',
                    data: {
                        filename: backupFilename,
                        path: backupPath,
                        size: `${fileSizeInMB} MB`,
                        timestamp: new Date().toISOString(),
                        tables_backed_up: [
                            'users', 'categories', 'products', 'product_sizes',
                            'cart', 'cart_items', 'orders', 'order_items',
                            'payments', 'shipments', 'notifications', 'favorites'
                        ]
                    }
                });
            } else {
                console.error(`❌ Backup failed with code ${code}: ${errorOutput}`);
                res.status(500).json({
                    success: false,
                    message: 'Database backup failed',
                    error: errorOutput
                });
            }
        });

        pgDump.on('error', (error) => {
            console.error(`❌ pg_dump error: ${error.message}`);
            res.status(500).json({
                success: false,
                message: 'Failed to start backup process',
                error: error.message
            });
        });

    } catch (error) {
        console.error('❌ Backup error:', error);
        res.status(500).json({
            success: false,
            message: 'Internal server error during backup',
            error: error.message
        });
    }
});

// Get backup history
router.get('/backups', auth, authorizeRoles(['admin']), (req, res) => {
    try {
        const backupFiles = fs.readdirSync(backupsDir)
            .filter(file => file.endsWith('.sql'))
            .map(file => {
                const filePath = path.join(backupsDir, file);
                const stats = fs.statSync(filePath);
                return {
                    filename: file,
                    size: `${(stats.size / (1024 * 1024)).toFixed(2)} MB`,
                    created: stats.birthtime,
                    modified: stats.mtime
                };
            })
            .sort((a, b) => new Date(b.created) - new Date(a.created));

        res.json({
            success: true,
            data: {
                backups: backupFiles,
                total: backupFiles.length,
                backup_directory: backupsDir
            }
        });
    } catch (error) {
        console.error('❌ Error listing backups:', error);
        res.status(500).json({
            success: false,
            message: 'Failed to list backup files',
            error: error.message
        });
    }
});

// Real database statistics
router.get('/stats', auth, authorizeRoles(['admin', 'staff']), async (req, res) => {
    try {
        const { query } = require('../config/database');

        // Get table sizes and record counts
        const tableStatsQuery = `
            SELECT 
                schemaname,
                tablename,
                attname,
                n_distinct,
                correlation,
                pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size,
                pg_total_relation_size(schemaname||'.'||tablename) as size_bytes
            FROM pg_stats 
            WHERE schemaname = 'public'
            ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
        `;

        const recordCountsQuery = `
            SELECT 
                'users' as table_name, COUNT(*) as record_count FROM users
            UNION ALL
            SELECT 'categories', COUNT(*) FROM categories
            UNION ALL
            SELECT 'products', COUNT(*) FROM products
            UNION ALL
            SELECT 'orders', COUNT(*) FROM orders
            UNION ALL
            SELECT 'payments', COUNT(*) FROM payments
            ORDER BY record_count DESC;
        `;

        const dbSizeQuery = `
            SELECT 
                pg_size_pretty(pg_database_size(current_database())) as database_size,
                pg_database_size(current_database()) as database_size_bytes;
        `;

        const connectionStatsQuery = `
            SELECT 
                count(*) as total_connections,
                count(*) filter (where state = 'active') as active_connections,
                count(*) filter (where state = 'idle') as idle_connections
            FROM pg_stat_activity 
            WHERE datname = current_database();
        `;

        const [tableStats, recordCounts, dbSize, connectionStats] = await Promise.all([
            query(tableStatsQuery),
            query(recordCountsQuery),
            query(dbSizeQuery),
            query(connectionStatsQuery)
        ]);

        res.json({
            success: true,
            data: {
                database_info: {
                    name: process.env.DB_NAME || 'ecommerce_db',
                    size: dbSize.rows[0]?.database_size || 'Unknown',
                    size_bytes: dbSize.rows[0]?.database_size_bytes || 0
                },
                connections: connectionStats.rows[0] || {},
                table_statistics: tableStats.rows,
                record_counts: recordCounts.rows,
                generated_at: new Date().toISOString()
            }
        });

    } catch (error) {
        console.error('❌ Error getting database stats:', error);
        res.status(500).json({
            success: false,
            message: 'Failed to get database statistics',
            error: error.message
        });
    }
});

// Execute custom SQL queries (admin only)
router.post('/query', auth, authorizeRoles(['admin']), async (req, res) => {
    try {
        const { sql } = req.body;
        
        if (!sql || sql.trim().length === 0) {
            return res.status(400).json({
                success: false,
                message: 'SQL query is required'
            });
        }

        // Security: Only allow SELECT statements for safety
        const trimmedSql = sql.trim().toLowerCase();
        if (!trimmedSql.startsWith('select') && !trimmedSql.startsWith('explain')) {
            return res.status(403).json({
                success: false,
                message: 'Only SELECT and EXPLAIN queries are allowed for security'
            });
        }

        const { query } = require('../config/database');
        const startTime = Date.now();
        const result = await query(sql);
        const executionTime = Date.now() - startTime;

        res.json({
            success: true,
            data: {
                rows: result.rows,
                row_count: result.rowCount,
                execution_time_ms: executionTime,
                columns: result.fields?.map(field => ({
                    name: field.name,
                    type: field.dataTypeID
                })) || []
            }
        });

    } catch (error) {
        console.error('❌ Query execution error:', error);
        res.status(500).json({
            success: false,
            message: 'Query execution failed',
            error: error.message
        });
    }
});

// Alias for execute-query endpoint (for test compatibility)
router.post('/execute-query', auth, authorizeRoles(['admin', 'staff']), async (req, res) => {
    try {
        // Accept both 'sql' and 'query' parameters for compatibility
        const { sql, query: queryText } = req.body;
        const sqlQuery = sql || queryText;
        
        if (!sqlQuery || sqlQuery.trim().length === 0) {
            return res.status(400).json({
                success: false,
                message: 'SQL query is required'
            });
        }

        // Security: Only allow SELECT statements for safety
        const trimmedSql = sqlQuery.trim().toLowerCase();
        if (!trimmedSql.startsWith('select') && !trimmedSql.startsWith('explain')) {
            return res.status(403).json({
                success: false,
                message: 'Only SELECT and EXPLAIN queries are allowed for security'
            });
        }

        const { query } = require('../config/database');
        const startTime = Date.now();
        const result = await query(sqlQuery);
        const executionTime = Date.now() - startTime;

        res.json({
            success: true,
            data: {
                rows: result.rows,
                row_count: result.rowCount,
                execution_time_ms: executionTime,
                columns: result.fields?.map(field => ({
                    name: field.name,
                    type: field.dataTypeID
                })) || []
            }
        });

    } catch (error) {
        console.error('❌ Query execution error:', error);
        res.status(500).json({
            success: false,
            message: 'Query execution failed',
            error: error.message
        });
    }
});

// Restore database from backup file
router.post('/restore', auth, authorizeRoles(['admin']), async (req, res) => {
    let responsesSent = false; // Track if response already sent
    
    try {
        const { filename, force = false } = req.body;

        if (!filename) {
            return res.status(400).json({
                success: false,
                message: 'Backup filename is required'
            });
        }

        const backupPath = path.join(__dirname, '../../backups', filename);
        
        // Check if backup file exists
        if (!fs.existsSync(backupPath)) {
            return res.status(404).json({
                success: false,
                message: 'Backup file not found'
            });
        }

        console.log(`🔄 Starting database restore from: ${filename}`);

        // Get file stats for validation
        const stats = fs.statSync(backupPath);
        if (stats.size === 0) {
            return res.status(400).json({
                success: false,
                message: 'Backup file is empty'
            });
        }

        // Validate backup file content
        const fileContent = fs.readFileSync(backupPath, 'utf8', { encoding: 'utf8' });
        if (!fileContent.includes('CREATE') && !fileContent.includes('INSERT') && !fileContent.includes('COPY')) {
            return res.status(400).json({
                success: false,
                message: 'Invalid backup file format - no SQL statements found'
            });
        }

        // Test database connection before restore
        try {
            const { Pool } = require('pg');
            const testPool = new Pool({
                user: process.env.DB_USER || 'postgres',
                host: process.env.DB_HOST || 'localhost',
                database: 'postgres', // Connect to postgres database first
                password: process.env.DB_PASSWORD || 'hengmengly123',
                port: process.env.DB_PORT || 5432,
                connectionTimeoutMillis: 5000
            });
            await testPool.query('SELECT 1');
            await testPool.end();
            console.log('✅ Database connection test passed');
        } catch (connError) {
            console.error('❌ Database connection test failed:', connError);
            return res.status(500).json({
                success: false,
                message: 'Cannot connect to database',
                error: connError.message
            });
        }
        try {
            const startTime = Date.now();
            let restoreCommand;
            let args;
            
            if (filename.endsWith('.backup')) {
                // Custom format backup - use pg_restore
                restoreCommand = 'pg_restore';
                args = [
                    '-h', process.env.DB_HOST || 'localhost',
                    '-p', process.env.DB_PORT || '5432',
                    '-U', process.env.DB_USER || 'postgres',
                    '-d', process.env.DB_NAME || 'ecommerce_db',
                    '--verbose',
                    '--no-password',
                    '--clean',
                    '--if-exists',
                    '--create',
                    backupPath
                ];
            } else if (filename.endsWith('.sql')) {
                // Plain SQL file - use psql
                // Connect to postgres database to allow dropping/creating target database
                restoreCommand = 'psql';
                args = [
                    '-h', process.env.DB_HOST || 'localhost',
                    '-p', process.env.DB_PORT || '5432',
                    '-U', process.env.DB_USER || 'postgres',
                    '-d', 'postgres', // Connect to postgres database first
                    '--no-password',
                    '-f', backupPath
                ];
            } else {
                return res.status(400).json({
                    success: false,
                    message: 'Unsupported backup file format'
                });
            }

            console.log(`🚀 Executing restore command: ${restoreCommand} ${args.join(' ')}`);

            const restoreProcess = spawn(restoreCommand, args, {
                env: {
                    ...process.env,
                    PGPASSWORD: process.env.DB_PASSWORD || 'hengmengly123'
                },
                stdio: ['pipe', 'pipe', 'pipe']
            });

            let stdout = '';
            let stderr = '';

            // Set timeout for long-running restores
            const timeout = setTimeout(() => {
                if (!responsesSent) {
                    responsesSent = true;
                    console.error('❌ Restore process timed out after 5 minutes');
                    restoreProcess.kill('SIGTERM');
                    res.status(408).json({
                        success: false,
                        message: 'Restore process timed out after 5 minutes',
                        error: 'Timeout exceeded'
                    });
                }
            }, 300000); // 5 minutes

            restoreProcess.stdout.on('data', (data) => {
                stdout += data.toString();
            });

            restoreProcess.stderr.on('data', (data) => {
                stderr += data.toString();
                console.log(`📝 Restore progress: ${data.toString().trim()}`);
            });

            restoreProcess.on('close', async (code) => {
                clearTimeout(timeout);
                
                if (responsesSent) {
                    return; // Response already sent (timeout or error)
                }

                const duration = Date.now() - startTime;
                console.log(`🏁 Restore process completed with exit code: ${code}`);
                console.log(`📊 Duration: ${duration}ms`);
                
                if (stderr) {
                    console.log(`📝 Restore stderr output: ${stderr}`);
                }

                if (code === 0) {
                    // Successful restore - verify database
                    let verificationResult = { verified: false };
                    try {
                        const { Pool } = require('pg');
                        const pool = new Pool({
                            user: process.env.DB_USER || 'postgres',
                            host: process.env.DB_HOST || 'localhost',
                            database: process.env.DB_NAME || 'ecommerce_db',
                            password: process.env.DB_PASSWORD || 'hengmengly123',
                            port: process.env.DB_PORT || 5432
                        });
                        
                        const result = await pool.query('SELECT COUNT(*) FROM users');
                        await pool.end();
                        
                        verificationResult = {
                            verified: true,
                            userCount: parseInt(result.rows[0].count)
                        };
                        
                        console.log(`✅ Database verification: ${verificationResult.userCount} users found`);
                    } catch (verifyError) {
                        console.error('❌ Database verification failed:', verifyError);
                        verificationResult = {
                            verified: false,
                            error: verifyError.message
                        };
                    }

                    responsesSent = true;
                    res.json({
                        success: true,
                        message: 'Database restored successfully',
                        data: {
                            filename,
                            file_size: `${(stats.size / (1024 * 1024)).toFixed(2)} MB`,
                            execution_time_ms: duration,
                            restored_at: new Date().toISOString(),
                            verification: verificationResult,
                            restore_type: filename.endsWith('.backup') ? 'custom_format' : 'sql_script',
                            stderr_output: stderr || 'No errors reported'
                        }
                    });
                } else {
                    // Failed restore
                    console.error(`❌ Restore failed with exit code ${code}`);
                    responsesSent = true;
                    res.status(500).json({
                        success: false,
                        message: 'Database restore failed',
                        error: stderr || 'Unknown error occurred',
                        exitCode: code,
                        stdout: stdout
                    });
                }
            });

            restoreProcess.on('error', (error) => {
                clearTimeout(timeout);
                
                if (responsesSent) {
                    return; // Response already sent
                }

                console.error('❌ Restore process error:', error);
                responsesSent = true;
                res.status(500).json({
                    success: false,
                    message: 'Failed to start restore process',
                    error: error.message
                });
            });

        } catch (error) {
            console.error('❌ Restore setup error:', error);
            if (!responsesSent) {
                responsesSent = true;
                res.status(500).json({
                    success: false,
                    message: 'Failed to setup restore process',
                    error: error.message
                });
            }
        }
    } catch (error) {
        console.error('❌ Outer restore error:', error);
        if (!responsesSent) {
            res.status(500).json({
                success: false,
                message: 'Internal server error during restore',
                error: error.message
            });
        }
    }
    }
);

module.exports = router;
