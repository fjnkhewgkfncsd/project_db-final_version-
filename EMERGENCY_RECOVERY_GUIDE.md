# 🚨 Emergency Database Recovery System

## Overview

The Emergency Database Recovery System is a standalone, secure system designed to restore database backups when the main database is unavailable or corrupted. It operates independently of the main application's database connection and provides a fail-safe recovery mechanism.

## 🔑 Key Features

### Security
- **Environment-based Authentication**: Credentials stored securely in `.env.recovery`
- **Database-Independent**: Works even when main database is completely down
- **Admin-Only Access**: Special emergency credentials separate from regular user accounts
- **Comprehensive Logging**: All recovery actions are logged with timestamps

### Safety
- **Pre-restore Validation**: Checks backup file integrity before restoration
- **Pre-restore Backup**: Creates safety backup before restoration (when possible)
- **Post-restore Verification**: Validates restoration success
- **Careful Path Validation**: Prevents directory traversal attacks

### User Experience
- **Modern React Interface**: Clean, responsive UI for emergency operations
- **Real-time Status**: Live database status monitoring
- **Backup File Selection**: Easy selection from available backup files
- **Progress Tracking**: Real-time restore progress and logs

## 🚀 Quick Start

### 1. Start Emergency Recovery Server
```bash
# Using VS Code Task (Recommended)
Ctrl+Shift+P → "Tasks: Run Task" → "Start Emergency Recovery Server"

# Or manually
cd backend
node emergency-recovery-server.js
```

### 2. Access Emergency Recovery Interface
- **URL**: http://localhost:3002
- **From Login Page**: Click "🚨 Emergency Database Recovery" link
- **Direct Route**: http://localhost:3001/emergency-recovery (if main app is running)

### 3. Emergency Login Credentials
```
Username: emergency_admin
Password: EmergencyRestore2025!
```

## 📋 System Architecture

### Components

1. **Emergency Recovery Server** (`backend/emergency-recovery-server.js`)
   - Standalone Express server on port 3002
   - Independent of main database
   - Handles authentication, backup listing, and restore operations

2. **Emergency Recovery UI** (`frontend/src/components/EmergencyRecovery.js`)
   - React component for recovery interface
   - Integrated into main app as special route
   - Works with emergency recovery server

3. **Environment Configuration** (`backend/.env.recovery`)
   - Emergency credentials and settings
   - Database connection parameters for restore operations

4. **Restore Scripts** (`db/restore.py`, `db/safe_restore.py`)
   - Python scripts for actual database restoration
   - Enhanced with safety checks and validation

## 🔧 Configuration Files

### .env.recovery
```env
# Emergency Admin Credentials (for database recovery only)
EMERGENCY_ADMIN_USERNAME=emergency_admin
EMERGENCY_ADMIN_PASSWORD=EmergencyRestore2025!

# Database Recovery Settings
RECOVERY_MODE=false
RECOVERY_PORT=3002
RECOVERY_LOG_FILE=recovery.log

# Database Connection (for restore operations)
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=your_db_password
DB_NAME=ecommerce_db
```

## 🛡️ Security Features

### Authentication
- Simple but secure token-based authentication
- Credentials stored in environment variables only
- Separate from main application authentication
- Session tokens for API access

### Authorization
- Emergency admin role only
- No regular user access to recovery functions
- All actions logged with user identification

### Input Validation
- Backup file path validation
- Prevention of directory traversal attacks
- File existence and integrity checks
- Size and format validation

## 📊 API Endpoints

### Authentication
- `POST /api/emergency/login` - Emergency admin login
- `GET /health` - Server health check

### Database Operations
- `GET /api/emergency/database-status` - Check database availability
- `GET /api/emergency/backups` - List available backup files
- `POST /api/emergency/restore` - Restore database from backup
- `GET /api/emergency/logs` - View recovery operation logs

## 🔄 Recovery Process

### 1. Authentication
1. Access emergency recovery interface
2. Enter emergency admin credentials
3. System validates and issues session token

### 2. Database Assessment
1. System checks database connectivity
2. Displays current database status
3. Lists available backup files with metadata

### 3. Backup Selection
1. Review available backup files
2. Select appropriate backup for restoration
3. Confirm restoration operation

### 4. Safe Restoration
1. **Pre-checks**: Validate backup file integrity
2. **Safety Backup**: Create current state backup (if database accessible)
3. **Restoration**: Execute restore operation with progress monitoring
4. **Verification**: Validate restoration success
5. **Logging**: Record all actions and results

## 📝 Logging and Monitoring

### Recovery Logs
- Location: `logs/recovery.log`
- Format: `[timestamp] message`
- Includes: Authentication attempts, operations, errors, and results

### Log Categories
- **Authentication**: Login attempts and results
- **Operations**: Backup listing, restore operations
- **Errors**: Failed operations and error details
- **Verification**: Post-restore validation results

## 🚀 Usage Scenarios

### Scenario 1: Database Server Down
1. Main application cannot connect to database
2. Access emergency recovery at http://localhost:3002
3. Login with emergency credentials
4. Select and restore from latest backup
5. Verify database is accessible again

### Scenario 2: Database Corruption
1. Database is accessible but data is corrupted
2. Access emergency recovery through main app (/emergency-recovery)
3. System creates pre-restore backup
4. Restore from known good backup
5. Verify data integrity

### Scenario 3: Failed Migration
1. Database migration caused issues
2. Emergency recovery creates safety backup of current state
3. Restore from pre-migration backup
4. Review and fix migration scripts

## 🧪 Testing

### Automated Testing
```bash
# Test complete emergency system
python test_emergency_recovery.py

# Or using VS Code Task
Ctrl+Shift+P → "Tasks: Run Task" → "Test Emergency Recovery System"
```

### Manual Testing
1. **Start Emergency Server**: `node backend/emergency-recovery-server.js`
2. **Access Interface**: http://localhost:3002
3. **Test Authentication**: Use emergency credentials
4. **Test Backup Listing**: Verify backup files are shown
5. **Test Database Status**: Check connectivity reporting
6. **Test Restore**: Perform test restoration (use with caution)

## 📋 Troubleshooting

### Common Issues

#### Server Won't Start
- **Check Port**: Ensure port 3002 is available
- **Check Dependencies**: Run `npm install` in backend directory
- **Check Environment**: Verify `.env.recovery` file exists

#### Authentication Fails
- **Check Credentials**: Verify username/password in `.env.recovery`
- **Check File Path**: Ensure `.env.recovery` is in backend directory
- **Check Permissions**: Ensure file is readable

#### No Backup Files Found
- **Check Directory**: Verify `backups` directory exists
- **Check Permissions**: Ensure directory is readable
- **Check File Extensions**: Only `.sql` and `.backup` files are shown

#### Restore Fails
- **Check Database Connection**: Verify database credentials in environment
- **Check Backup File**: Ensure backup file is not corrupted
- **Check Permissions**: Ensure backup file is readable
- **Check Database State**: Some restores require database to be accessible

### Log Analysis
```bash
# View recent recovery logs
tail -f logs/recovery.log

# Search for errors
grep -i error logs/recovery.log

# Search for specific operations
grep -i "restore" logs/recovery.log
```

## 🔄 Maintenance

### Regular Tasks
1. **Test Recovery System**: Monthly test of emergency procedures
2. **Update Credentials**: Change emergency passwords regularly
3. **Clean Old Logs**: Archive or remove old recovery logs
4. **Verify Backups**: Ensure backup files are valid and accessible

### Security Updates
1. **Rotate Emergency Credentials**: Update `.env.recovery` passwords
2. **Review Access Logs**: Monitor authentication attempts
3. **Update Dependencies**: Keep Node.js packages updated
4. **Review Permissions**: Ensure proper file and directory access

## 🎯 Integration with Main Application

### Route Integration
- Emergency recovery is integrated as `/emergency-recovery` route in main React app
- Accessible even when main authentication fails
- Direct link available on login page for easy access

### Database Independence
- Emergency system operates separately from main database connection
- Uses its own connection pool and credentials
- Can function when main application database is completely unavailable

### Shared Resources
- Uses same backup files as main application
- Shares logging directory structure
- Integrates with existing backup creation scripts

## 🚨 Emergency Procedures

### Complete Database Loss
1. **Start Emergency Server**: `node backend/emergency-recovery-server.js`
2. **Access Recovery**: http://localhost:3002
3. **Authenticate**: Use emergency admin credentials
4. **Select Latest Backup**: Choose most recent complete backup
5. **Execute Restore**: Confirm and run restoration
6. **Verify Results**: Check database connectivity and data integrity
7. **Update Application**: Restart main application services

### Partial Data Loss
1. **Create Current Backup**: Use emergency system to backup current state
2. **Identify Good Backup**: Select backup from before data loss
3. **Perform Restoration**: Execute restore with pre-restore backup
4. **Validate Data**: Confirm data integrity and completeness
5. **Document Incident**: Record what was lost and restored

### Recovery from Corruption
1. **Assess Damage**: Use database status check to understand scope
2. **Create Safety Backup**: Backup current state for forensic analysis
3. **Select Clean Backup**: Choose backup from before corruption
4. **Execute Restoration**: Perform careful restore operation
5. **Verify Integrity**: Run database consistency checks
6. **Investigate Cause**: Analyze what caused the corruption

This emergency recovery system provides a robust, secure, and user-friendly solution for database recovery scenarios. It's designed to be the last line of defense when all other systems fail, ensuring your data can always be recovered safely and efficiently.
