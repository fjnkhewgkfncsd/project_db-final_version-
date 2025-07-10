# Database Restore Process Flow

## Overview
This document outlines the complete flow for restoring the PostgreSQL e-commerce database using multiple available methods. The system supports three primary restore approaches:

1. **Python Script Restore** (`db/restore.py`) - Standalone command-line tool
2. **Main System API Restore** (`backend/routes/database.js`) - Web UI and API endpoint
3. **Emergency Recovery Server** (`backend/emergency-recovery-server.js`) - Independent recovery system

---

## 1. Python Script Restore Flow (`db/restore.py`)

### Prerequisites
- PostgreSQL client tools installed (`psql`, `pg_restore`)
- Python 3.9+ with required packages
- Database credentials in `.env` file
- Backup files in `backups/` directory

### Flow Steps

#### Step 1: Initialize Restore Tool
```
DatabaseRestore.__init__()
├── Load environment variables from backend/.env
├── Configure database connection parameters
├── Set backup path (../backups)
└── Setup logging (console + file)
```

#### Step 2: Discover Available Backups
```
list_available_backups()
├── Scan backup directory for files
│   ├── ecommerce_backup_*.sql
│   ├── ecommerce_backup_*.backup
│   └── ecommerce_backup_*.sql.gz
├── Load metadata from .json files
├── Determine backup type (complete/schema/data)
├── Sort by modification time (newest first)
└── Return backup list with metadata
```

#### Step 3: Select Backup (Interactive/Automatic)
```
Backup Selection
├── --list: Display all available backups
├── --latest: Auto-select newest successful backup
├── backup_file argument: Use specified file
└── Interactive: Show menu for user selection
```

#### Step 4: Pre-Restore Safety Checks
```
perform_restore()
├── verify_backup_file()
│   ├── Check file exists
│   ├── Verify file size > 0
│   └── Test file readability
├── create_pre_restore_backup() (optional)
│   ├── Import backup.py module
│   ├── Create safety backup
│   └── Log backup location
└── get_database_connection_count()
    ├── Connect to postgres database
    ├── Query pg_stat_activity
    └── Return active connection count
```

#### Step 5: Prepare Database for Restore
```
Database Preparation
├── terminate_database_connections()
│   ├── Connect to postgres database
│   ├── Execute pg_terminate_backend()
│   └── Close all connections to target DB
└── drop_and_recreate_database() (for SQL files)
    ├── DROP DATABASE IF EXISTS
    ├── CREATE DATABASE
    └── Verify creation success
```

#### Step 6: Execute Restore Operation
```
Restore Execution (format-dependent)
├── Custom Format (.backup files)
│   └── restore_from_custom_format()
│       ├── Use pg_restore command
│       ├── Options: --clean, --if-exists, --jobs=4
│       └── Parallel restoration
└── SQL Format (.sql, .sql.gz files)
    └── restore_from_sql()
        ├── Handle compression (gunzip for .gz)
        ├── Use psql command
        ├── Windows: decompress to temp file
        └── Unix: pipe gunzip to psql
```

#### Step 7: Post-Restore Verification
```
verify_restore()
├── Test database connectivity
├── Execute verification queries:
│   ├── SELECT COUNT(*) FROM users;
│   ├── SELECT COUNT(*) FROM products;
│   ├── SELECT COUNT(*) FROM orders;
│   └── SELECT version();
├── Log verification results
└── Return success/failure status
```

#### Step 8: Logging and Cleanup
```
Completion
├── log_restore_metadata()
│   ├── Create restore_YYYYMMDD_HHMMSS.json
│   ├── Record operation details
│   └── Include pre-restore backup path
├── Calculate operation duration
└── Return final status
```

### Command Examples
```bash
# List available backups
python restore.py --list

# Restore latest backup automatically
python restore.py --latest --force

# Interactive restore
python restore.py

# Restore specific file
python restore.py backups/ecommerce_backup_2025-07-09_01-52-43.sql --force
```

---

## 2. Main System API Restore Flow (`backend/routes/database.js`)

### Prerequisites
- Backend server running (port 5000)
- User authentication (admin role)
- Backup files accessible to server
- Database connection pool initialized

### Flow Steps

#### Step 1: API Request Initiation
```
POST /api/database/restore
├── Authentication middleware
├── Admin role verification
├── File upload handling (multer)
└── Request validation
```

#### Step 2: File Processing
```
File Handling
├── Extract uploaded file or use existing backup
├── Validate file format (.sql, .backup, .gz)
├── Check file size and readability
└── Store temporary file if uploaded
```

#### Step 3: Database Connection Management
```
Connection Setup
├── Get connection from pool
├── Check database connectivity
├── Handle connection errors
└── Set appropriate target database
```

#### Step 4: Restore Execution
```
Restore Process (format-dependent)
├── SQL Files (.sql, .sql.gz)
│   ├── Connect to 'postgres' database
│   ├── DROP DATABASE IF EXISTS
│   ├── CREATE DATABASE
│   ├── Switch to target database
│   ├── Execute SQL content
│   └── Handle compressed files
└── Custom Format (.backup)
    ├── Use pg_restore via child_process
    ├── Stream output for progress
    └── Handle restoration errors
```

#### Step 5: Response and Logging
```
Completion
├── Return API response
│   ├── Success: { success: true, message, details }
│   └── Error: { success: false, error, details }
├── Clean up temporary files
└── Log operation to console/file
```

### API Usage Examples
```javascript
// Frontend restore request
const formData = new FormData();
formData.append('backupFile', selectedFile);

const response = await fetch('/api/database/restore', {
  method: 'POST',
  headers: { 'Authorization': `Bearer ${token}` },
  body: formData
});

// Use existing backup file
const response = await fetch('/api/database/restore', {
  method: 'POST',
  headers: { 
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    backupPath: 'backups/ecommerce_backup_2025-07-09_01-52-43.sql'
  })
});
```

---

## 3. Emergency Recovery Server Flow (`backend/emergency-recovery-server.js`)

### Prerequisites
- Emergency server running (port 3001)
- Independent configuration (.env.recovery)
- Access to backup files
- No dependency on main system

### Flow Steps

#### Step 1: Emergency Server Startup
```
Emergency Server Initialization
├── Load .env.recovery configuration
├── Setup independent database connection
├── Initialize Express server on port 3001
├── Serve emergency recovery UI
└── Setup API endpoints
```

#### Step 2: Emergency UI Access
```
Recovery Interface
├── Navigate to http://localhost:3001
├── Simple HTML interface
├── File upload capability
├── Backup file selection
└── Restore progress display
```

#### Step 3: Emergency Restore Process
```
POST /emergency-restore
├── File upload handling
├── Backup validation
├── Database connection (independent)
├── Restore execution (same logic as main system)
├── Real-time progress updates
└── Success/failure notification
```

#### Step 4: Recovery Completion
```
Emergency Recovery Result
├── Database restoration status
├── Error details (if any)
├── Verification results
└── Next steps guidance
```

### Emergency Usage
```bash
# Start emergency recovery server
node emergency-recovery-server.js

# Access recovery interface
# Open browser: http://localhost:3001

# Use API directly
curl -X POST http://localhost:3001/emergency-restore \
  -F "backupFile=@backups/ecommerce_backup_2025-07-09_01-52-43.sql"
```

---

## 4. Backup File Formats Supported

### SQL Format (.sql)
- Plain text SQL dump
- Created by `pg_dump` with default options
- Human-readable
- Can be edited manually
- Restored using `psql`

### Compressed SQL (.sql.gz)
- Gzipped SQL dump
- Smaller file size
- Requires decompression before restore
- Handled automatically by all restore methods

### Custom Format (.backup)
- PostgreSQL custom format
- Created by `pg_dump -Fc`
- Binary format, not human-readable
- Supports parallel restore
- Restored using `pg_restore`

---

## 5. Safety Features

### Pre-Restore Backup
```
Safety Backup Creation
├── Automatic backup before restore (configurable)
├── Stored with timestamp
├── Available for rollback if needed
└── Logged in restore metadata
```

### Connection Management
```
Database Safety
├── Terminate active connections
├── Prevent data corruption
├── Handle connection cleanup
└── Verify database state
```

### Verification Process
```
Post-Restore Verification
├── Test database connectivity
├── Verify table existence
├── Check record counts
├── Validate data integrity
└── Report verification status
```

---

## 6. Error Handling and Recovery

### Common Error Scenarios
1. **File Not Found**: Check backup file path and permissions
2. **Database Connection Failed**: Verify credentials and PostgreSQL service
3. **Insufficient Permissions**: Ensure user has CREATE/DROP database rights
4. **Active Connections**: Automatically terminated during restore
5. **Corrupted Backup**: File validation catches most issues
6. **Disk Space**: Monitor available space before large restores

### Recovery Strategies
```
Error Recovery
├── Pre-restore backup available for rollback
├── Detailed error logging for diagnosis
├── Manual intervention steps documented
├── Emergency recovery server as fallback
└── Database recreation from scratch if needed
```

---

## 7. Performance Considerations

### Optimization Features
- **Parallel Jobs**: Custom format restores use multiple connections
- **Connection Pooling**: Efficient database connection management
- **Streaming**: Large files processed in chunks
- **Compression**: Automatic handling of compressed backups

### Performance Monitoring
```
Timing Metrics
├── Operation start/end timestamps
├── Duration calculation
├── Progress reporting (where applicable)
└── Performance logging
```

---

## 8. Quick Reference Commands

### Python Script Usage
```bash
# Interactive restore
python db/restore.py

# Force restore latest backup
python db/restore.py --latest --force

# List all backups
python db/restore.py --list
```

### Main System Usage
- Access Database Tools tab in web interface
- Upload backup file or select existing
- Click "Restore Database" button
- Monitor progress and results

### Emergency Recovery
```bash
# Start emergency server
cd backend && node emergency-recovery-server.js

# Access recovery UI
# Browser: http://localhost:3001
```

---

## 9. Best Practices

### Before Restore
1. **Create backup** of current database
2. **Stop application services** using the database
3. **Verify backup file** integrity and size
4. **Check disk space** for restore operation
5. **Ensure proper permissions** for database operations

### During Restore
1. **Monitor progress** through logs or UI
2. **Don't interrupt** the restore process
3. **Keep backup files** until verification complete
4. **Watch for errors** in real-time logs

### After Restore
1. **Verify data integrity** using test queries
2. **Check application functionality** 
3. **Update sequences** if needed (rarely required)
4. **Restart application services**
5. **Monitor system performance**

---

## 10. Troubleshooting Guide

### Connection Issues
```sql
-- Test database connectivity
psql -h localhost -p 5432 -U postgres -d postgres -c "SELECT version();"

-- Check active connections
SELECT count(*) FROM pg_stat_activity WHERE datname = 'ecommerce_db';
```

### File Permission Issues
```bash
# Check file permissions
ls -la backups/

# Fix permissions if needed (Unix/Linux)
chmod 644 backups/*.sql
```

### Service Status
```bash
# Check PostgreSQL service
# Windows
net start postgresql

# Check backend server
curl http://localhost:5000/api/health

# Check emergency server
curl http://localhost:3001/health
```

This comprehensive flow documentation covers all restore methods available in your e-commerce database administration system, providing clear guidance for different scenarios and user types.
