# Database Restore - Quick Reference Guide

## 🚀 Quick Start

### Prerequisites
- PostgreSQL client tools installed (`psql`, `pg_restore`)
- Environment variables configured in `backend/.env`
- Database server running and accessible

### Command Line Restore

```bash
# Navigate to db directory
cd db/

# List all available backups
python restore.py --list

# Restore from latest backup (interactive)
python restore.py --latest

# Restore from latest backup (force, no prompts)
python restore.py --latest --force

# Interactive backup selection
python restore.py

# Restore specific file
python restore.py path/to/backup.sql
```

### API Restore (Admin Only)

```bash
# Login first
curl -X POST http://localhost:3001/api/users/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"admin123"}'

# Get available backups
curl -X GET http://localhost:3001/api/database/backups \
  -H "Authorization: Bearer YOUR_TOKEN"

# Restore from backup
curl -X POST http://localhost:3001/api/database/restore \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"filename":"ecommerce_backup_2025-06-28_04-52-16.sql"}'
```

## 📋 Command Options

### `python restore.py` Options
- `--list` - List all available backup files
- `--latest` - Use the most recent successful backup
- `--force` - Skip confirmation prompts
- `--no-clean` - Don't drop/recreate database (for SQL files)
- `backup_file` - Specific backup file to restore

### Example Commands
```bash
# List backups with details
python restore.py --list

# Quick restore from latest (production use)
python restore.py --latest --force

# Restore specific backup file
python restore.py ../backups/ecommerce_backup_2025-06-28_04-52-16.sql --force

# Interactive restore (development use)
python restore.py
```

## 🔍 Supported File Formats

| Format | Extension | Description | Command Used |
|--------|-----------|-------------|--------------|
| Plain SQL | `.sql` | Standard SQL dump | `psql` |
| Compressed SQL | `.sql.gz` | Gzipped SQL dump | `gunzip` + `psql` |
| Custom Format | `.backup` | PostgreSQL custom format | `pg_restore` |

## ⚡ Performance Guidelines

| Backup Size | Expected Restore Time | Memory Usage |
|-------------|----------------------|--------------|
| < 1 MB | < 1 second | Minimal |
| 1-10 MB | 1-5 seconds | Low |
| 10-100 MB | 5-30 seconds | Moderate |
| > 100 MB | 30+ seconds | High |

## 🛡️ Security Features

### Command Line
- ✅ Environment variable password handling
- ✅ File existence and size validation
- ✅ Connection termination for clean restore
- ✅ Pre-restore backup creation option
- ✅ Post-restore verification

### API Endpoint
- ✅ Admin-only access (JWT authentication)
- ✅ File path validation and sanitization
- ✅ Backup file existence verification
- ✅ File size and format validation
- ✅ Execution time monitoring

## 🔧 Troubleshooting

### Common Issues

**❌ "No backups found"**
```bash
# Check backup directory exists
ls -la ../backups/

# Verify environment variables
cat ../backend/.env | grep BACKUP
```

**❌ "Connection refused"**
```bash
# Check database is running
pg_isready -h localhost -p 5432

# Verify connection parameters
psql -h localhost -p 5432 -U postgres -l
```

**❌ "Permission denied"**
```bash
# Check file permissions
ls -la ../backups/

# Verify database user permissions
psql -h localhost -p 5432 -U postgres -c "\du"
```

**❌ "Backup file corrupted"**
```bash
# Check file size
ls -lh ../backups/backup_file.sql

# Test file readability
head -10 ../backups/backup_file.sql
```

### Debug Mode
```bash
# Enable verbose logging
python restore.py --list 2>&1 | tee restore_debug.log

# Check restore logs
tail -f ../backups/restore.log
```

## 📊 Verification Steps

### Post-Restore Checks
1. **Record Counts**: Verify table record counts match expectations
2. **Data Integrity**: Run sample queries to check data consistency
3. **Schema Validation**: Ensure all tables and indexes exist
4. **User Access**: Test application connectivity

### Automated Verification
```bash
# Run comprehensive test
python test_restore_comprehensive.py

# Check specific functionality
python test_restore.py
```

## 📝 Best Practices

### For Development
- Use `--latest` for quick testing
- Enable interactive mode for backup selection
- Keep recent backups for rollback scenarios

### For Production
- Always use `--force` flag for automation
- Create pre-restore backups (enabled by default)
- Monitor restore operations and logs
- Test restore procedures regularly

### For Automation
```bash
#!/bin/bash
# Production restore script
cd /path/to/project/db
python restore.py --latest --force
if [ $? -eq 0 ]; then
    echo "Restore successful"
    # Run additional verification
    python test_restore_comprehensive.py
else
    echo "Restore failed" >&2
    exit 1
fi
```

## 📞 Support

### Log Files
- **Restore Log**: `backups/restore.log`
- **Backup Log**: `backups/backup.log`
- **Metadata**: `backups/restore_YYYYMMDD_HHMMSS.json`

### Key Metrics
- Execution time
- File sizes
- Record counts
- Verification results

### Contact Information
For issues or improvements, check the project documentation or create an issue in the project repository.
