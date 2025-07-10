# DATABASE RESTORE PROCESS COMPLETE FLOW
Generated: 2025-07-10 02:48:36


DATABASE RESTORE PROCESS FLOWCHART
=================================

┌─────────────────────────────────────────────────────────────────────────────────┐
│                              RESTORE METHOD SELECTION                           │
└─────────────────────────────────┬───────────────────────────────────────────────┘
                                  │
                    ┌─────────────┴─────────────┐
                    │     Choose Method:        │
                    │  1. Python Script        │
                    │  2. Main System API       │
                    │  3. Emergency Server      │
                    └─────┬───────┬───────┬─────┘
                          │       │       │
        ┌─────────────────┘       │       └─────────────────┐
        │                         │                         │
        ▼                         ▼                         ▼
┌──────────────┐         ┌─────────────────┐      ┌─────────────────┐
│ PYTHON       │         │ MAIN SYSTEM     │      │ EMERGENCY       │
│ SCRIPT       │         │ API             │      │ RECOVERY        │
│ (CLI)        │         │ (Web UI)        │      │ (Independent)   │
└──────┬───────┘         └─────────┬───────┘      └─────────┬───────┘
       │                           │                        │
       ▼                           ▼                        ▼
┌──────────────┐         ┌─────────────────┐      ┌─────────────────┐
│ 1. Load .env │         │ 1. Authenticate │      │ 1. Start        │
│ 2. Scan      │         │ 2. Validate     │      │    Emergency    │
│    backups/  │         │    Upload       │      │    Server       │
│ 3. Select    │         │ 3. Process File │      │ 2. Access UI    │
│    Backup    │         │                 │      │ 3. Upload File  │
└──────┬───────┘         └─────────┬───────┘      └─────────┬───────┘
       │                           │                        │
       │                           │                        │
       └───────────┐               │               ┌────────┘
                   │               │               │
                   ▼               ▼               ▼
         ┌─────────────────────────────────────────────────────┐
         │              COMMON RESTORE FLOW                    │
         │                                                     │
         │  ┌─────────────────────────────────────────────┐    │
         │  │         SAFETY CHECKS                       │    │
         │  │  • Verify backup file exists               │    │
         │  │  • Check file size > 0                     │    │
         │  │  • Validate file format                    │    │
         │  │  • Test database connectivity              │    │
         │  └─────────────┬───────────────────────────────┘    │
         │                ▼                                    │
         │  ┌─────────────────────────────────────────────┐    │
         │  │         PRE-RESTORE BACKUP                  │    │
         │  │  • Create safety backup (optional)         │    │
         │  │  • Log backup location                     │    │
         │  │  • Store restore metadata                  │    │
         │  └─────────────┬───────────────────────────────┘    │
         │                ▼                                    │
         │  ┌─────────────────────────────────────────────┐    │
         │  │         DATABASE PREPARATION                │    │
         │  │  • Terminate active connections            │    │
         │  │  • Drop existing database (if SQL)         │    │
         │  │  • Create fresh database                   │    │
         │  └─────────────┬───────────────────────────────┘    │
         │                ▼                                    │
         │  ┌─────────────────────────────────────────────┐    │
         │  │         RESTORE EXECUTION                   │    │
         │  │                                             │    │
         │  │  SQL Format:        Custom Format:         │    │
         │  │  • Use psql         • Use pg_restore       │    │
         │  │  • Handle .gz       • Parallel jobs        │    │
         │  │  • Stream data      • Clean/if-exists      │    │
         │  └─────────────┬───────────────────────────────┘    │
         │                ▼                                    │
         │  ┌─────────────────────────────────────────────┐    │
         │  │         POST-RESTORE VERIFICATION           │    │
         │  │  • Test database connectivity              │    │
         │  │  • Verify table existence                  │    │
         │  │  • Check record counts                     │    │
         │  │  • Validate data integrity                 │    │
         │  └─────────────┬───────────────────────────────┘    │
         │                ▼                                    │
         │  ┌─────────────────────────────────────────────┐    │
         │  │         COMPLETION & LOGGING                │    │
         │  │  • Log operation results                   │    │
         │  │  • Clean up temporary files                │    │
         │  │  • Calculate duration                      │    │
         │  │  • Return status                           │    │
         │  └─────────────┬───────────────────────────────┘    │
         └────────────────┼─────────────────────────────────────┘
                          ▼
         ┌─────────────────────────────────────────────────────┐
         │                   RESULTS                           │
         │                                                     │
         │  Success:                   Failure:                │
         │  • Database restored        • Error logged          │
         │  • Verification passed      • Rollback available    │
         │  • Logs updated            • Detailed diagnostics   │
         │  • System ready            • Recovery options       │
         └─────────────────────────────────────────────────────┘

FILE FORMAT SUPPORT:
┌──────────────┬────────────────────┬─────────────────────────────────┐
│ Format       │ Extension          │ Restore Method                  │
├──────────────┼────────────────────┼─────────────────────────────────┤
│ SQL Dump     │ .sql               │ psql command                    │
│ Compressed   │ .sql.gz            │ gunzip | psql                   │
│ Custom       │ .backup            │ pg_restore (parallel capable)   │
└──────────────┴────────────────────┴─────────────────────────────────┘

ERROR HANDLING FLOW:
┌─────────────────────────────────────────────────────────────────────┐
│                          ERROR SCENARIOS                           │
│                                                                     │
│  File Error → Validate path → Log error → Return failure          │
│  DB Error   → Check conn   → Log error → Suggest recovery         │
│  Auth Error → Re-auth      → Log error → Return unauthorized      │
│  Space Error→ Check disk   → Log error → Clean temp files         │
│                                                                     │
│  Recovery Options:                                                  │
│  • Use pre-restore backup for rollback                            │
│  • Try emergency recovery server                                  │
│  • Manual database recreation                                     │
│  • Contact administrator                                          │
└─────────────────────────────────────────────────────────────────────┘



DETAILED RESTORE PROCESS FLOWS
=============================

1. PYTHON SCRIPT RESTORE (db/restore.py)
==========================================

Command: python db/restore.py [options]

Step 1: Initialization
├── Load environment variables from backend/.env
├── Parse command line arguments
├── Initialize logging (console + file: logs/restore_YYYYMMDD.log)
├── Set backup directory path (../backups)
└── Create DatabaseRestore instance

Step 2: Backup Discovery
├── Scan backup directory for files matching patterns:
│   ├── ecommerce_backup_*.sql
│   ├── ecommerce_backup_*.backup
│   └── ecommerce_backup_*.sql.gz
├── Load metadata from corresponding .json files
├── Determine backup type (complete/schema/data)
├── Sort by modification time (newest first)
└── Return list with file info, size, and metadata

Step 3: Backup Selection
├── --list option: Display all available backups and exit
├── --latest option: Auto-select newest successful backup
├── backup_file argument: Use specified file path
├── Interactive mode: Show numbered menu
│   ├── Display backup files with timestamps and sizes
│   ├── Show backup type and user count (if available)
│   ├── Prompt for selection
│   └── Validate user input
└── Confirm selection unless --force specified

Step 4: Pre-Restore Safety
├── verify_backup_file():
│   ├── Check file exists and is readable
│   ├── Verify file size > 0 bytes
│   ├── Test file format (SQL/Custom/Compressed)
│   └── Log file validation results
├── get_database_connection_count():
│   ├── Connect to postgres database
│   ├── Query pg_stat_activity for active connections
│   ├── Count connections to target database
│   └── Log connection count
├── create_pre_restore_backup() [if enabled]:
│   ├── Import backup.py module
│   ├── Create timestamped safety backup
│   ├── Log backup location for rollback
│   └── Verify backup creation success
└── Final confirmation prompt (unless --force)

Step 5: Database Preparation
├── terminate_database_connections():
│   ├── Connect to postgres database
│   ├── Execute SELECT pg_terminate_backend(pid) for all sessions
│   ├── Wait for connection cleanup
│   └── Verify no active connections remain
└── drop_and_recreate_database() [for SQL files]:
    ├── Execute DROP DATABASE IF EXISTS ecommerce_db
    ├── Execute CREATE DATABASE ecommerce_db WITH ENCODING 'UTF8'
    ├── Verify database creation
    └── Log database recreation

Step 6: Restore Execution (Format Dependent)
├── Custom Format (.backup files):
│   └── restore_from_custom_format():
│       ├── Build pg_restore command:
│       │   ├── --host, --port, --username
│       │   ├── --dbname=ecommerce_db
│       │   ├── --clean --if-exists
│       │   ├── --jobs=4 (parallel restoration)
│       │   └── --verbose
│       ├── Execute command with subprocess
│       ├── Capture stdout/stderr
│       ├── Monitor exit code
│       └── Log restoration output
└── SQL Format (.sql/.sql.gz files):
    └── restore_from_sql():
        ├── Handle compression:
        │   ├── .gz files: Use gunzip
        │   ├── Windows: Decompress to temp file
        │   └── Unix/Linux: Pipe gunzip to psql
        ├── Build psql command:
        │   ├── --host, --port, --username
        │   ├── --dbname=ecommerce_db
        │   ├── --quiet (suppress notices)
        │   └── --file or stdin
        ├── Execute restoration
        ├── Handle large files with streaming
        └── Log restoration progress

Step 7: Post-Restore Verification
├── verify_restore():
│   ├── Test database connectivity
│   ├── Execute verification queries:
│   │   ├── SELECT COUNT(*) FROM users;
│   │   ├── SELECT COUNT(*) FROM products;
│   │   ├── SELECT COUNT(*) FROM orders;
│   │   ├── SELECT COUNT(*) FROM order_items;
│   │   └── SELECT version();
│   ├── Compare with expected counts (if available)
│   ├── Log all verification results
│   └── Return verification status
├── Check table existence:
│   ├── Query information_schema.tables
│   ├── Verify core e-commerce tables
│   └── Log missing tables (if any)
└── Validate data integrity:
    ├── Check for referential integrity
    ├── Verify no null required fields
    └── Test sample queries

Step 8: Completion and Metadata
├── log_restore_metadata():
│   ├── Create restore_YYYYMMDD_HHMMSS.json file
│   ├── Record operation details:
│   │   ├── Backup file used
│   │   ├── Restore method
│   │   ├── Start/end timestamps
│   │   ├── Duration
│   │   ├── Success/failure status
│   │   ├── User counts (before/after)
│   │   ├── Pre-restore backup path
│   │   └── Error details (if any)
│   └── Store in logs/ directory
├── Calculate total operation duration
├── Clean up temporary files (if any)
├── Log final success/failure message
└── Return exit code (0 = success, 1 = failure)

Example Command Flows:
├── python restore.py --list
│   └── Lists all backups and exits
├── python restore.py --latest --force
│   └── Restores newest backup without prompts
├── python restore.py backups/specific_backup.sql
│   └── Restores specified file with confirmation
└── python restore.py (interactive)
    └── Shows menu, prompts for selection and confirmation

2. MAIN SYSTEM API RESTORE (backend/routes/database.js)
======================================================

Endpoint: POST /api/database/restore

Step 1: Request Processing
├── Express.js route handling
├── Authentication middleware:
│   ├── Verify JWT token in Authorization header
│   ├── Extract user information
│   └── Check admin role requirement
├── Multer file upload middleware:
│   ├── Handle multipart/form-data
│   ├── Validate file type (.sql, .backup, .gz)
│   ├── Set file size limits
│   └── Store in temporary uploads/ directory
└── Request validation

Step 2: File Handling
├── Extract file information:
│   ├── req.file: Uploaded file
│   ├── req.body.backupPath: Path to existing backup
│   └── req.body.backupFile: File content (for small files)
├── Validate file format and size
├── Determine restore method based on extension
├── Check file accessibility and permissions
└── Log file processing details

Step 3: Database Connection Management
├── Get connection from PostgreSQL pool
├── Test database connectivity
├── Handle connection timeouts and errors
├── Set appropriate target database:
│   ├── 'postgres' for SQL file restores (to drop/create DB)
│   └── 'ecommerce_db' for custom format restores
└── Log connection status

Step 4: Restore Execution
├── SQL Files (.sql, .sql.gz):
│   ├── Connect to 'postgres' database
│   ├── Execute DROP DATABASE IF EXISTS ecommerce_db
│   ├── Execute CREATE DATABASE ecommerce_db
│   ├── Switch connection to 'ecommerce_db'
│   ├── Read and execute SQL content:
│   │   ├── Handle large files with streaming
│   │   ├── Execute in transactions for safety
│   │   ├── Parse multi-statement SQL
│   │   └── Handle compressed files (.gz)
│   └── Log execution progress
└── Custom Format (.backup):
    ├── Use pg_restore via child_process.spawn()
    ├── Build command with options:
    │   ├── --clean --if-exists
    │   ├── --jobs=4 (parallel)
    │   ├── --verbose
    │   └── Connection parameters
    ├── Stream output for real-time progress
    ├── Capture stderr for errors
    └── Monitor process exit code

Step 5: Verification and Response
├── Execute verification queries (same as Python script)
├── Test restored data integrity
├── Clean up temporary uploaded files
├── Build API response:
│   ├── Success: { success: true, message, details: {...} }
│   │   ├── Restoration time
│   │   ├── User counts
│   │   ├── Verification results
│   │   └── Next steps
│   └── Error: { success: false, error, details: {...} }
│       ├── Error type and message
│       ├── Stack trace (development)
│       ├── Suggested actions
│       └── Rollback options
├── Log operation results
└── Return HTTP response (200/500)

Frontend Integration:
├── Database Tools tab in React UI
├── File upload component with drag-and-drop
├── Progress indicator during restore
├── Real-time status updates via WebSocket (optional)
├── Success/error notifications
└── Restore history display

API Usage Examples:
├── Upload new backup file:
│   ├── FormData with file attachment
│   ├── Multipart content-type
│   └── Authorization header with JWT
├── Use existing backup:
│   ├── JSON body with backupPath
│   ├── Application/json content-type
│   └── Authorization header
└── Response handling in JavaScript

3. EMERGENCY RECOVERY SERVER (backend/emergency-recovery-server.js)
==================================================================

Server: Independent Express server on port 3001

Step 1: Emergency Server Startup
├── Load configuration from .env.recovery file
├── Initialize independent database connection
├── Setup Express.js server with minimal dependencies
├── Configure static file serving for UI
├── Setup API endpoints:
│   ├── GET / - Serve recovery UI
│   ├── POST /emergency-restore - Restore endpoint
│   ├── GET /list-backups - List available backups
│   └── GET /health - Server health check
├── Start server on port 3001
└── Log server startup and configuration

Step 2: Emergency UI Access
├── Serve emergency-recovery-ui.html at root path
├── Simple HTML interface with:
│   ├── File upload form
│   ├── Backup file selection dropdown
│   ├── Restore progress display
│   ├── Result notifications
│   └── Basic styling for usability
├── Client-side JavaScript for:
│   ├── AJAX form submission
│   ├── File validation
│   ├── Progress updates
│   └── Error handling
└── No authentication required (emergency access)

Step 3: Backup Discovery
├── GET /list-backups endpoint:
│   ├── Scan backup directory
│   ├── Read backup metadata
│   ├── Return JSON list of available backups
│   └── Include file sizes and timestamps
├── Client populates dropdown with options
├── User can select existing backup or upload new file
└── Validation on both client and server side

Step 4: Emergency Restore Process
├── POST /emergency-restore endpoint:
│   ├── Handle file upload (same as main system)
│   ├── Validate backup file
│   ├── Execute restore using same core logic
│   ├── Return real-time progress updates
│   └── Provide detailed error information
├── Database operations:
│   ├── Independent connection pool
│   ├── Same safety checks as other methods
│   ├── Identical restore procedures
│   └── Comprehensive verification
└── Result reporting with next steps

Step 5: Recovery Completion
├── Success response:
│   ├── Database restored successfully
│   ├── Verification results
│   ├── Instructions to restart main system
│   └── Cleanup recommendations
├── Failure response:
│   ├── Detailed error analysis
│   ├── Suggested recovery steps
│   ├── Alternative options
│   └── Support contact information
├── Server-side logging of all operations
└── Optional automatic main system health check

Emergency Usage Scenarios:
├── Main system completely down
├── Database corrupted or deleted
├── Authentication system failure
├── Configuration errors in main system
├── Emergency restoration outside business hours
└── Disaster recovery situations

Commands to Start Emergency Server:
├── cd backend
├── node emergency-recovery-server.js
├── Access: http://localhost:3001
└── No other dependencies required

COMMON FEATURES ACROSS ALL METHODS
==================================

File Format Support:
├── SQL Dump (.sql):
│   ├── Plain text PostgreSQL dump
│   ├── Human-readable and editable
│   ├── Restored using psql command
│   ├── Supports full database recreation
│   └── Cross-platform compatible
├── Compressed SQL (.sql.gz):
│   ├── Gzipped SQL dump for smaller size
│   ├── Automatically decompressed during restore
│   ├── Significant space savings
│   ├── Streaming decompression support
│   └── Platform-specific handling (Windows vs Unix)
└── Custom Format (.backup):
    ├── PostgreSQL custom binary format
    ├── Created with pg_dump -Fc
    ├── Supports parallel restoration
    ├── Includes built-in compression
    ├── Not human-readable
    └── Restored using pg_restore

Safety Features:
├── Pre-restore backup creation (configurable)
├── Connection termination before restore
├── File validation and integrity checks
├── Comprehensive error handling and rollback
├── Detailed logging of all operations
├── Verification of restore success
├── Cleanup of temporary files
└── Metadata tracking for auditing

Performance Optimizations:
├── Connection pooling for database access
├── Parallel restoration for custom format
├── Streaming for large files
├── Efficient memory usage
├── Progress tracking and reporting
├── Background processing where appropriate
└── Resource cleanup and monitoring

Error Recovery:
├── Automatic rollback using pre-restore backup
├── Detailed error logging and analysis
├── Multiple fallback methods available
├── Manual intervention procedures documented
├── Emergency recovery server as last resort
├── Database recreation from scratch if needed
└── Support escalation procedures

Verification Process:
├── Database connectivity testing
├── Table existence verification
├── Record count validation
├── Data integrity checks
├── Referential integrity verification
├── Performance baseline testing
└── Application functionality testing

This comprehensive flow covers all aspects of the database restore system,
providing multiple robust methods for database recovery in various scenarios.


## QUICK REFERENCE COMMANDS

### Python Script Method
```bash
# Interactive restore with menu
python db/restore.py

# Force restore latest backup
python db/restore.py --latest --force

# List all available backups
python db/restore.py --list

# Restore specific backup
python db/restore.py backups/ecommerce_backup_2025-07-09_01-52-43.sql --force
```

### Main System API Method
```bash
# Start backend server (if not running)
cd backend && npm start

# Access web interface
# Navigate to: http://localhost:3000
# Go to: Database Tools tab
# Use: Upload or select backup file
# Click: "Restore Database" button
```

### Emergency Recovery Method
```bash
# Start emergency server
cd backend && node emergency-recovery-server.js

# Access emergency interface
# Navigate to: http://localhost:3001
# Upload backup file or select existing
# Click restore and monitor progress
```

## TROUBLESHOOTING QUICK FIXES

### Common Issues and Solutions
1. **Permission Denied**: Check file permissions and database user privileges
2. **Connection Failed**: Verify PostgreSQL service is running and credentials are correct
3. **File Not Found**: Check backup file path and ensure file exists
4. **Out of Space**: Free up disk space or clean old backup files
5. **Active Connections**: All methods automatically terminate connections

### Emergency Commands
```bash
# Check PostgreSQL service status
# Windows: net start postgresql
# Linux: sudo systemctl status postgresql

# Test database connection
psql -h localhost -p 5432 -U postgres -d postgres -c "SELECT version();"

# Check backup file integrity
ls -la backups/
file backups/ecommerce_backup_*.sql

# Force cleanup and restart
# Stop all connections: python db/restore.py --force-cleanup
# Restart services: docker-compose restart
```

### Recovery Escalation Path
1. Try Python script restore (most reliable)
2. Use emergency recovery server (independent)
3. Manual psql restoration from command line
4. Recreate database schema and restore data only
5. Contact database administrator

---
Generated by Database Restore Flow Visualization Generator
