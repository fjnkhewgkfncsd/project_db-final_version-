#!/usr/bin/env python3
"""
PostgreSQL Database Backup Script
Automated backup with compression, rotation, and monitoring
"""

import os
import sys
import subprocess
import datetime
import logging
import json
import shutil
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class DatabaseBackup:
    def __init__(self):
        self.db_config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': os.getenv('DB_PORT', '5432'),
            'database': os.getenv('DB_NAME', 'ecommerce_db'),
            'user': os.getenv('DB_USER', 'postgres'),
            'password': os.getenv('DB_PASSWORD', 'password')
        }
        
        self.backup_config = {
            'backup_path': os.getenv('BACKUP_PATH', './backups'),
            'retention_days': int(os.getenv('BACKUP_RETENTION_DAYS', '30')),
            'compression': True,
            'include_schema': True,
            'include_data': True
        }
        
        # Setup logging
        self.setup_logging()
        
        # Ensure backup directory exists
        Path(self.backup_config['backup_path']).mkdir(parents=True, exist_ok=True)

    def setup_logging(self):
        """Setup logging configuration"""
        log_format = '%(asctime)s - %(levelname)s - %(message)s'
        logging.basicConfig(
            level=logging.INFO,
            format=log_format,
            handlers=[
                logging.FileHandler(f"{self.backup_config['backup_path']}/backup.log"),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)

    def create_backup_filename(self, backup_type='full'):
        """Generate backup filename with timestamp"""
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"ecommerce_db_{backup_type}_{timestamp}"
        
        if self.backup_config['compression']:
            filename += '.sql.gz'
        else:
            filename += '.sql'
            
        return filename

    def run_pg_dump(self, output_file, backup_type='full'):
        """Execute pg_dump command"""
        # Set password environment variable
        env = os.environ.copy()
        env['PGPASSWORD'] = self.db_config['password']
        
        # Build pg_dump command
        cmd = [
            'pg_dump',
            '-h', self.db_config['host'],
            '-p', self.db_config['port'],
            '-U', self.db_config['user'],
            '-d', self.db_config['database'],
            '--verbose',
            '--no-password'
        ]
        
        # Add options based on backup type
        if backup_type == 'schema_only':
            cmd.append('--schema-only')
        elif backup_type == 'data_only':
            cmd.append('--data-only')
        
        # Add format and compression options
        if self.backup_config['compression']:
            cmd.extend(['--format=custom', '--compress=9'])
            output_file = output_file.replace('.sql.gz', '.backup')
        
        cmd.extend(['-f', output_file])
        
        try:
            self.logger.info(f"Starting backup: {' '.join(cmd[:-2])} [output_file_hidden]")
            result = subprocess.run(cmd, env=env, capture_output=True, text=True, check=True)
            
            if result.returncode == 0:
                self.logger.info(f"Backup completed successfully: {output_file}")
                return True
            else:
                self.logger.error(f"Backup failed with return code {result.returncode}")
                self.logger.error(f"Error: {result.stderr}")
                return False
                
        except subprocess.CalledProcessError as e:
            self.logger.error(f"pg_dump failed: {e}")
            self.logger.error(f"Error output: {e.stderr}")
            return False
        except FileNotFoundError:
            self.logger.error("pg_dump command not found. Please ensure PostgreSQL client tools are installed.")
            return False

    def create_backup_metadata(self, backup_file, backup_type, success):
        """Create metadata file for backup"""
        metadata = {
            'backup_file': backup_file,
            'backup_type': backup_type,
            'database': self.db_config['database'],
            'host': self.db_config['host'],
            'timestamp': datetime.datetime.now().isoformat(),
            'success': success,
            'file_size': os.path.getsize(backup_file) if success and os.path.exists(backup_file) else 0,
            'compression': self.backup_config['compression'],
            'retention_days': self.backup_config['retention_days']
        }
        
        metadata_file = backup_file.replace('.sql', '.json').replace('.backup', '.json').replace('.gz', '')
        
        try:
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
            self.logger.info(f"Metadata saved: {metadata_file}")
        except Exception as e:
            self.logger.error(f"Failed to save metadata: {e}")

    def cleanup_old_backups(self):
        """Remove backups older than retention period"""
        cutoff_date = datetime.datetime.now() - datetime.timedelta(days=self.backup_config['retention_days'])
        backup_dir = Path(self.backup_config['backup_path'])
        
        removed_count = 0
        for backup_file in backup_dir.glob('ecommerce_db_*'):
            if backup_file.stat().st_mtime < cutoff_date.timestamp():
                try:
                    backup_file.unlink()
                    self.logger.info(f"Removed old backup: {backup_file}")
                    removed_count += 1
                    
                    # Also remove corresponding metadata file
                    metadata_file = backup_file.with_suffix('.json')
                    if metadata_file.exists():
                        metadata_file.unlink()
                        
                except Exception as e:
                    self.logger.error(f"Failed to remove old backup {backup_file}: {e}")
        
        if removed_count > 0:
            self.logger.info(f"Cleaned up {removed_count} old backup files")

    def verify_backup(self, backup_file):
        """Verify backup file integrity"""
        if not os.path.exists(backup_file):
            self.logger.error(f"Backup file does not exist: {backup_file}")
            return False
        
        file_size = os.path.getsize(backup_file)
        if file_size == 0:
            self.logger.error(f"Backup file is empty: {backup_file}")
            return False
        
        self.logger.info(f"Backup verification passed. File size: {file_size:,} bytes")
        return True

    def get_database_stats(self):
        """Get database statistics before backup"""
        try:
            # Set password environment variable
            env = os.environ.copy()
            env['PGPASSWORD'] = self.db_config['password']
            
            # Get table statistics
            sql_query = """
            SELECT 
                schemaname,
                tablename,
                n_tup_ins as inserts,
                n_tup_upd as updates,
                n_tup_del as deletes,
                n_live_tup as live_tuples,
                n_dead_tup as dead_tuples,
                pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
            FROM pg_stat_user_tables 
            ORDER BY n_live_tup DESC;
            """
            
            cmd = [
                'psql',
                '-h', self.db_config['host'],
                '-p', self.db_config['port'],
                '-U', self.db_config['user'],
                '-d', self.db_config['database'],
                '-c', sql_query,
                '--no-password',
                '-t'  # tuples only
            ]
            
            result = subprocess.run(cmd, env=env, capture_output=True, text=True)
            if result.returncode == 0:
                self.logger.info("Database statistics retrieved successfully")
                return result.stdout
            else:
                self.logger.warning(f"Failed to get database stats: {result.stderr}")
                
        except Exception as e:
            self.logger.warning(f"Error getting database stats: {e}")
        
        return None

    def perform_backup(self, backup_type='full'):
        """Perform the backup operation"""
        self.logger.info(f"Starting {backup_type} backup of database '{self.db_config['database']}'")
        
        # Get database statistics
        db_stats = self.get_database_stats()
        if db_stats:
            self.logger.info("Database statistics:\n" + db_stats)
        
        # Generate backup filename
        backup_filename = self.create_backup_filename(backup_type)
        backup_path = os.path.join(self.backup_config['backup_path'], backup_filename)
        
        # Perform backup
        start_time = datetime.datetime.now()
        success = self.run_pg_dump(backup_path, backup_type)
        end_time = datetime.datetime.now()
        
        duration = (end_time - start_time).total_seconds()
        
        if success:
            # Verify backup
            if self.verify_backup(backup_path):
                file_size = os.path.getsize(backup_path)
                self.logger.info(f"Backup completed successfully in {duration:.2f} seconds")
                self.logger.info(f"Backup file: {backup_path}")
                self.logger.info(f"File size: {file_size:,} bytes ({file_size / (1024*1024):.2f} MB)")
                
                # Create metadata
                self.create_backup_metadata(backup_path, backup_type, True)
                
                # Cleanup old backups
                self.cleanup_old_backups()
                
                return backup_path
            else:
                success = False
        
        if not success:
            self.logger.error(f"Backup failed after {duration:.2f} seconds")
            self.create_backup_metadata(backup_path, backup_type, False)
            
            # Remove failed backup file
            if os.path.exists(backup_path):
                os.remove(backup_path)
                
            return None

    def list_backups(self):
        """List all available backups"""
        backup_dir = Path(self.backup_config['backup_path'])
        backups = []
        
        for backup_file in sorted(backup_dir.glob('ecommerce_db_*.sql*')):
            metadata_file = backup_file.with_suffix('.json')
            
            backup_info = {
                'file': str(backup_file),
                'size': backup_file.stat().st_size,
                'created': datetime.datetime.fromtimestamp(backup_file.stat().st_mtime)
            }
            
            # Load metadata if available
            if metadata_file.exists():
                try:
                    with open(metadata_file, 'r') as f:
                        metadata = json.load(f)
                    backup_info.update(metadata)
                except Exception as e:
                    self.logger.warning(f"Failed to load metadata for {backup_file}: {e}")
            
            backups.append(backup_info)
        
        return backups

def main():
    """Main function to handle command line execution"""
    import argparse
    
    parser = argparse.ArgumentParser(description='PostgreSQL Database Backup Tool')
    parser.add_argument('--type', choices=['full', 'schema_only', 'data_only'], 
                       default='full', help='Type of backup to perform')
    parser.add_argument('--list', action='store_true', help='List existing backups')
    parser.add_argument('--cleanup', action='store_true', help='Clean up old backups only')
    
    args = parser.parse_args()
    
    backup_tool = DatabaseBackup()
    
    if args.list:
        print("\n=== Available Backups ===")
        backups = backup_tool.list_backups()
        if not backups:
            print("No backups found.")
        else:
            for backup in backups:
                print(f"File: {backup['file']}")
                print(f"Size: {backup['size']:,} bytes")
                print(f"Created: {backup['created']}")
                if 'backup_type' in backup:
                    print(f"Type: {backup['backup_type']}")
                    print(f"Success: {backup.get('success', 'Unknown')}")
                print("-" * 50)
    
    elif args.cleanup:
        backup_tool.cleanup_old_backups()
    
    else:
        # Perform backup
        backup_path = backup_tool.perform_backup(args.type)
        if backup_path:
            print(f"\n✅ Backup completed successfully: {backup_path}")
            sys.exit(0)
        else:
            print("\n❌ Backup failed")
            sys.exit(1)

if __name__ == "__main__":
    main()
