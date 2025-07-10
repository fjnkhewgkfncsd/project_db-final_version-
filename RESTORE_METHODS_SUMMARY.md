# Database Restore Methods Summary

## Available Methods

### 1. Python Script (`db/restore.py`)
- **Best for**: Command-line users, automated scripts, reliable operation
- **Command**: `python db/restore.py [--latest] [--force]`
- **Features**: Interactive menu, comprehensive logging, safety backups

### 2. Main System API (`/api/database/restore`)
- **Best for**: Web interface users, integrated workflow
- **Access**: Database Tools tab in web UI
- **Features**: File upload, progress tracking, user authentication

### 3. Emergency Recovery Server (`:3001`)
- **Best for**: Emergency situations, system failures
- **Command**: `node emergency-recovery-server.js`
- **Features**: Independent operation, minimal dependencies

## Quick Start
```bash
# Method 1: Python Script
python db/restore.py --latest --force

# Method 2: Web Interface
# Navigate to Database Tools → Upload/Select → Restore

# Method 3: Emergency Recovery
node emergency-recovery-server.js
# Then visit: http://localhost:3001
```

## File Support
- `.sql` - Plain SQL dump
- `.sql.gz` - Compressed SQL dump  
- `.backup` - PostgreSQL custom format

All methods support all file formats with automatic detection and handling.

Generated: 2025-07-10 02:48:36
