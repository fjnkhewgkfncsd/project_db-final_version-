const express = require('express');
const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');
const cors = require('cors');

// Load both emergency config and main database config
require('dotenv').config({ path: '.env.recovery' });
require('dotenv').config({ path: '.env' });

const app = express();
const PORT = process.env.RECOVERY_PORT || 3002;

// Middleware
app.use(cors());
app.use(express.json());

// Serve emergency recovery page
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'emergency-recovery-ui.html'));
});

// Also serve the landing page at /info for reference
app.get('/info', (req, res) => {
    res.sendFile(path.join(__dirname, 'emergency-index.html'));
});

// Emergency credentials from environment variables
const EMERGENCY_CREDENTIALS = {
    username: process.env.EMERGENCY_ADMIN_USERNAME || 'emergency_admin',
    password: process.env.EMERGENCY_ADMIN_PASSWORD || 'EmergencyRestore2025!'
};

// Paths
const BACKUPS_DIR = path.join(__dirname, '..', 'backups');
const RECOVERY_LOG = path.join(__dirname, '..', 'logs', 'recovery.log');

// Ensure logs directory exists
const logsDir = path.dirname(RECOVERY_LOG);
if (!fs.existsSync(logsDir)) {
    fs.mkdirSync(logsDir, { recursive: true });
}

// Logging function
function logRecovery(message) {
    const timestamp = new Date().toISOString();
    const logMessage = `[${timestamp}] ${message}\n`;
    console.log(logMessage.trim());
    fs.appendFileSync(RECOVERY_LOG, logMessage);
}

// Emergency authentication middleware
function emergencyAuth(req, res, next) {
    const authHeader = req.headers.authorization;
    
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
        return res.status(401).json({
            success: false,
            message: 'Emergency authentication required'
        });
    }
    
    const token = authHeader.substring(7);
    
    try {
        // Simple token validation (username:password base64 encoded)
        const decoded = Buffer.from(token, 'base64').toString('utf-8');
        const [username, password] = decoded.split(':');
        
        if (username === EMERGENCY_CREDENTIALS.username && 
            password === EMERGENCY_CREDENTIALS.password) {
            next();
        } else {
            logRecovery(`Failed emergency authentication attempt: ${username}`);
            res.status(401).json({
                success: false,
                message: 'Invalid emergency credentials'
            });
        }
    } catch (error) {
        res.status(401).json({
            success: false,
            message: 'Invalid authentication token'
        });
    }
}

// Emergency login endpoint
app.post('/api/emergency/login', (req, res) => {
    const { username, password } = req.body;
    
    logRecovery(`Emergency login attempt: ${username}`);
    
    if (username === EMERGENCY_CREDENTIALS.username && 
        password === EMERGENCY_CREDENTIALS.password) {
        
        const token = Buffer.from(`${username}:${password}`).toString('base64');
        
        logRecovery(`Emergency login successful: ${username}`);
        
        res.json({
            success: true,
            message: 'Emergency authentication successful',
            data: {
                token,
                username,
                mode: 'emergency_recovery'
            }
        });
    } else {
        logRecovery(`Emergency login failed: ${username}`);
        res.status(401).json({
            success: false,
            message: 'Invalid emergency credentials'
        });
    }
});

// Check database status
app.get('/api/emergency/database-status', emergencyAuth, async (req, res) => {
    try {
        // Try to connect to database
        const { Pool } = require('pg');
        const pool = new Pool({
            user: process.env.DB_USER || 'postgres',
            host: process.env.DB_HOST || 'localhost',
            database: process.env.DB_NAME || 'ecommerce_db',
            password: process.env.DB_PASSWORD || 'password',
            port: process.env.DB_PORT || 5432,
            connectionTimeoutMillis: 5000
        });
        
        const result = await pool.query('SELECT 1');
        await pool.end();
        
        res.json({
            success: true,
            data: {
                status: 'online',
                message: 'Database is accessible'
            }
        });
    } catch (error) {
        logRecovery(`Database status check failed: ${error.message}`);
        res.json({
            success: true,
            data: {
                status: 'offline',
                message: 'Database is not accessible',
                error: error.message
            }
        });
    }
});

// List backup files
app.get('/api/emergency/backups', emergencyAuth, (req, res) => {
    try {
        logRecovery('Listing backup files for emergency recovery');
        
        if (!fs.existsSync(BACKUPS_DIR)) {
            return res.status(404).json({
                success: false,
                message: 'Backups directory not found'
            });
        }
        
        const files = fs.readdirSync(BACKUPS_DIR)
            .filter(file => file.endsWith('.sql') || file.endsWith('.backup'))
            .map(file => {
                const filePath = path.join(BACKUPS_DIR, file);
                const stats = fs.statSync(filePath);
                
                return {
                    filename: file,
                    size: stats.size,
                    sizeFormatted: `${(stats.size / (1024 * 1024)).toFixed(2)} MB`,
                    created: stats.birthtime,
                    modified: stats.mtime,
                    type: file.includes('schema') ? 'schema' : 
                          file.includes('data') ? 'data' : 'complete'
                };
            })
            .sort((a, b) => new Date(b.modified) - new Date(a.modified));
        
        res.json({
            success: true,
            data: {
                backups: files,
                total: files.length,
                directory: BACKUPS_DIR
            }
        });
    } catch (error) {
        logRecovery(`Error listing backups: ${error.message}`);
        res.status(500).json({
            success: false,
            message: 'Failed to list backup files',
            error: error.message
        });
    }
});

// Emergency database restore
app.post('/api/emergency/restore', emergencyAuth, async (req, res) => {
    const { filename, force = false } = req.body;
    
    if (!filename) {
        return res.status(400).json({
            success: false,
            message: 'Backup filename is required'
        });
    }
    
    const backupPath = path.join(BACKUPS_DIR, filename);
    
    // Security: Validate file path
    if (!backupPath.startsWith(BACKUPS_DIR)) {
        logRecovery(`Security violation: Invalid backup path attempted: ${filename}`);
        return res.status(400).json({
            success: false,
            message: 'Invalid backup file path'
        });
    }
    
    if (!fs.existsSync(backupPath)) {
        return res.status(404).json({
            success: false,
            message: 'Backup file not found'
        });
    }
    
    logRecovery(`Starting emergency database restore: ${filename}`);
    
    try {
        const startTime = Date.now();
        
        // Create pre-restore backup if database is accessible
        let preRestoreBackup = null;
        if (!force) {
            try {
                const backupScript = path.join(__dirname, '..', 'db', 'backup.py');
                if (fs.existsSync(backupScript)) {
                    logRecovery('Creating pre-restore backup...');
                    // This is optional and may fail if database is down
                }
            } catch (backupError) {
                logRecovery(`Pre-restore backup failed (continuing): ${backupError.message}`);
            }
        }
        
        // Determine restore command based on file type
        let restoreCommand;
        let args;
        
        if (filename.endsWith('.backup')) {
            // Custom format backup
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
            // SQL dump file
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
        
        logRecovery(`Executing restore command: ${restoreCommand} ${args.join(' ')}`);
        
        // Execute restore
        const restoreProcess = spawn(restoreCommand, args, {
            env: {
                ...process.env,
                PGPASSWORD: process.env.DB_PASSWORD || 'hengmengly123'
            }
        });
        
        let stdout = '';
        let stderr = '';
        
        restoreProcess.stdout.on('data', (data) => {
            stdout += data.toString();
        });
        
        restoreProcess.stderr.on('data', (data) => {
            stderr += data.toString();
        });
        
        restoreProcess.on('close', async (code) => {
            const duration = Date.now() - startTime;
            
            if (code === 0) {
                logRecovery(`Emergency restore completed successfully in ${duration}ms`);
                
                // Verify restoration
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
                        userCount: result.rows[0].count
                    };
                    logRecovery(`Restoration verified: ${result.rows[0].count} users found`);
                } catch (verifyError) {
                    logRecovery(`Verification failed: ${verifyError.message}`);
                    verificationResult = {
                        verified: false,
                        error: verifyError.message
                    };
                }
                
                res.json({
                    success: true,
                    message: 'Emergency database restore completed successfully',
                    data: {
                        filename,
                        duration: `${duration}ms`,
                        verification: verificationResult,
                        preRestoreBackup,
                        output: stdout.substring(0, 1000) // Limit output size
                    }
                });
            } else {
                logRecovery(`Emergency restore failed with code ${code}: ${stderr}`);
                res.status(500).json({
                    success: false,
                    message: 'Emergency database restore failed',
                    error: stderr,
                    exitCode: code
                });
            }
        });
        
        restoreProcess.on('error', (error) => {
            logRecovery(`Emergency restore process error: ${error.message}`);
            res.status(500).json({
                success: false,
                message: 'Failed to start restore process',
                error: error.message
            });
        });
        
    } catch (error) {
        logRecovery(`Emergency restore error: ${error.message}`);
        res.status(500).json({
            success: false,
            message: 'Emergency restore failed',
            error: error.message
        });
    }
});

// Get recovery logs
app.get('/api/emergency/logs', emergencyAuth, (req, res) => {
    try {
        if (fs.existsSync(RECOVERY_LOG)) {
            const logs = fs.readFileSync(RECOVERY_LOG, 'utf-8')
                .split('\n')
                .filter(line => line.trim())
                .slice(-100) // Last 100 log entries
                .reverse(); // Most recent first
            
            res.json({
                success: true,
                data: {
                    logs,
                    total: logs.length
                }
            });
        } else {
            res.json({
                success: true,
                data: {
                    logs: [],
                    total: 0
                }
            });
        }
    } catch (error) {
        res.status(500).json({
            success: false,
            message: 'Failed to read recovery logs',
            error: error.message
        });
    }
});

// Emergency status endpoint
app.get('/api/emergency/status', emergencyAuth, (req, res) => {
    try {
        const uptime = process.uptime();
        const uptimeFormatted = `${Math.floor(uptime / 60)}m ${Math.floor(uptime % 60)}s`;
        
        // Get backup count
        let backupCount = 0;
        if (fs.existsSync(BACKUPS_DIR)) {
            backupCount = fs.readdirSync(BACKUPS_DIR)
                .filter(file => file.endsWith('.sql') || file.endsWith('.backup'))
                .length;
        }
        
        res.json({
            success: true,
            data: {
                server: {
                    status: 'online',
                    uptime: uptimeFormatted,
                    uptimeSeconds: Math.floor(uptime),
                    port: PORT,
                    mode: 'emergency_recovery'
                },
                backups: {
                    count: backupCount,
                    directory: BACKUPS_DIR,
                    available: backupCount > 0
                },
                logs: {
                    file: RECOVERY_LOG,
                    exists: fs.existsSync(RECOVERY_LOG)
                },
                timestamp: new Date().toISOString()
            }
        });
    } catch (error) {
        res.status(500).json({
            success: false,
            message: 'Failed to get emergency status',
            error: error.message
        });
    }
});

// Health check
app.get('/health', (req, res) => {
    res.json({
        success: true,
        message: 'Emergency Recovery Server is running',
        timestamp: new Date().toISOString(),
        mode: 'emergency_recovery'
    });
});

// Catch-all handler for SPA routing
app.get('*', (req, res) => {
    res.sendFile(path.join(__dirname, 'emergency-index.html'));
});

// Start server
app.listen(PORT, () => {
    logRecovery(`Emergency Recovery Server started on port ${PORT}`);
    console.log(`🚨 Emergency Recovery Server running on http://localhost:${PORT}`);
    console.log(`📋 Emergency Credentials: ${EMERGENCY_CREDENTIALS.username} / ${EMERGENCY_CREDENTIALS.password}`);
    console.log(`📁 Backups Directory: ${BACKUPS_DIR}`);
    console.log(`📝 Recovery Log: ${RECOVERY_LOG}`);
});

module.exports = app;
