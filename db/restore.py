#!/usr/bin/env python3
"""
PostgreSQL Database Restore Script
Automated restore with verification and rollback capabilities
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

class DatabaseRestore:
    def __init__(self):
        # Load environment variables from backend directory
        backend_env_path = os.path.join(os.path.dirname(__file__), '..', 'backend', '.env')
        if os.path.exists(backend_env_path):
            load_dotenv(backend_env_path)
        
        self.db_config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': os.getenv('DB_PORT', '5432'),
            'database': os.getenv('DB_NAME', 'ecommerce_db'),
            'user': os.getenv('DB_USER', 'postgres'),
            'password': os.getenv('DB_PASSWORD', 'password')
        }
        
        # Fix backup path to point to correct directory
        backup_path = os.getenv('BACKUP_PATH', '../backups')
        
        # Handle absolute vs relative paths
        if backup_path.startswith('/') and os.name == 'nt':  # Unix-style path on Windows
            backup_path = '../backups'  # Use relative path instead
        elif not os.path.isabs(backup_path):
            backup_path = os.path.join(os.path.dirname(__file__), backup_path)
        
        backup_path = os.path.abspath(backup_path)
        
        self.restore_config = {
            'backup_path': backup_path,
            'create_backup_before_restore': True,
            'verify_after_restore': True,
            'parallel_jobs': 4
        }
        
        # Setup logging
        self.setup_logging()

    def setup_logging(self):
        """Setup logging configuration"""
        log_format = '%(asctime)s - %(levelname)s - %(message)s'
        
        # Ensure backup directory exists for log file
        os.makedirs(self.restore_config['backup_path'], exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format=log_format,
            handlers=[
                logging.FileHandler(f"{self.restore_config['backup_path']}/restore.log"),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)

    def list_available_backups(self):
        """List all available backup files"""
        backup_dir = Path(self.restore_config['backup_path'])
        if not backup_dir.exists():
            self.logger.error(f"Backup directory does not exist: {backup_dir}")
            return []
        
        self.logger.info(f"Scanning backup directory: {backup_dir}")
        
        backups = []
        # Updated patterns to match actual backup files
        patterns = [
            'ecommerce_backup_*.sql',
            'ecommerce_backup_*.sql.gz',
            'ecommerce_backup_*.backup',
            'ecommerce_data_*.sql',
            'ecommerce_schema_*.sql',
            'ecommerce_db_*.sql',
            'ecommerce_db_*.sql.gz',
            'ecommerce_db_*.backup'
        ]
        
        all_backup_files = []
        for pattern in patterns:
            files = list(backup_dir.glob(pattern))
            all_backup_files.extend(files)
            self.logger.debug(f"Pattern {pattern} found {len(files)} files")
        
        # Remove duplicates and sort by modification time (newest first)
        unique_files = list(set(all_backup_files))
        sorted_files = sorted(unique_files, key=lambda x: x.stat().st_mtime, reverse=True)
        
        for backup_file in sorted_files:
            metadata_file = backup_file.with_suffix('.json')
            
            backup_info = {
                'file': str(backup_file),
                'name': backup_file.name,
                'size': backup_file.stat().st_size,
                'created': datetime.datetime.fromtimestamp(backup_file.stat().st_mtime),
                'type': 'unknown'
            }
            
            # Determine backup type from filename
            if 'schema' in backup_file.name:
                backup_info['type'] = 'schema_only'
            elif 'data' in backup_file.name:
                backup_info['type'] = 'data_only'
            else:
                backup_info['type'] = 'complete'
            
            # Load metadata if available
            if metadata_file.exists():
                try:
                    with open(metadata_file, 'r') as f:
                        metadata = json.load(f)
                    backup_info.update({
                        'type': metadata.get('backup_type', backup_info['type']),
                        'success': metadata.get('success', True),
                        'compression': metadata.get('compression', False),
                        'database': metadata.get('database', 'unknown')
                    })
                except Exception as e:
                    self.logger.warning(f"Failed to load metadata for {backup_file}: {e}")
            
            # Determine file format from extension
            if backup_file.suffix == '.backup':
                backup_info['format'] = 'custom'
            elif backup_file.suffix == '.gz':
                backup_info['format'] = 'compressed_sql'
            else:
                backup_info['format'] = 'plain_sql'
            
            backups.append(backup_info)
        
        self.logger.info(f"Found {len(backups)} backup files")
        return backups

    def verify_backup_file(self, backup_file):
        """Verify backup file exists and is readable"""
        if not os.path.exists(backup_file):
            self.logger.error(f"Backup file does not exist: {backup_file}")
            return False
        
        if os.path.getsize(backup_file) == 0:
            self.logger.error(f"Backup file is empty: {backup_file}")
            return False
        
        # Try to read the first few bytes to ensure file is not corrupted
        try:
            with open(backup_file, 'rb') as f:
                header = f.read(100)
                if len(header) == 0:
                    self.logger.error(f"Cannot read backup file: {backup_file}")
                    return False
        except Exception as e:
            self.logger.error(f"Error reading backup file {backup_file}: {e}")
            return False
        
        self.logger.info(f"Backup file verification passed: {backup_file}")
        return True

    def create_pre_restore_backup(self):
        """Create a backup before restore operation"""
        if not self.restore_config['create_backup_before_restore']:
            return None
        
        self.logger.info("Creating backup before restore operation...")
        
        try:
            # Check if backup.py exists in the same directory
            backup_script_path = os.path.join(os.path.dirname(__file__), 'backup.py')
            if os.path.exists(backup_script_path):
                # Try to import and use the backup module
                sys.path.insert(0, os.path.dirname(__file__))
                try:
                    from backup import DatabaseBackup
                    backup_tool = DatabaseBackup()
                    backup_path = backup_tool.perform_backup('full')
                    if backup_path:
                        self.logger.info(f"Pre-restore backup created: {backup_path}")
                        return backup_path
                    else:
                        self.logger.warning("Failed to create pre-restore backup")
                        return None
                except ImportError as e:
                    self.logger.warning(f"Backup module import failed: {e}")
                finally:
                    # Remove the path we added
                    if os.path.dirname(__file__) in sys.path:
                        sys.path.remove(os.path.dirname(__file__))
            else:
                self.logger.warning("backup.py not found - skipping pre-restore backup")
            
            return None
                
        except Exception as e:
            self.logger.warning(f"Error creating pre-restore backup: {e}")
            return None

    def get_database_connection_count(self):
        """Get number of active connections to database"""
        try:
            env = os.environ.copy()
            env['PGPASSWORD'] = self.db_config['password']
            
            cmd = [
                'psql',
                '-h', self.db_config['host'],
                '-p', self.db_config['port'],
                '-U', self.db_config['user'],
                '-d', 'postgres',  # Connect to postgres database
                '-c', f"SELECT count(*) FROM pg_stat_activity WHERE datname = '{self.db_config['database']}';",
                '--no-password',
                '-t',
                '-A'
            ]
            
            result = subprocess.run(cmd, env=env, capture_output=True, text=True)
            if result.returncode == 0:
                return int(result.stdout.strip())
            else:
                self.logger.warning(f"Failed to get connection count: {result.stderr}")
                return -1
                
        except Exception as e:
            self.logger.warning(f"Error getting connection count: {e}")
            return -1

    def terminate_database_connections(self):
        """Terminate all connections to the target database"""
        self.logger.info(f"Terminating connections to database '{self.db_config['database']}'")
        
        try:
            env = os.environ.copy()
            env['PGPASSWORD'] = self.db_config['password']
            
            terminate_sql = f"""
            SELECT pg_terminate_backend(pg_stat_activity.pid)
            FROM pg_stat_activity 
            WHERE pg_stat_activity.datname = '{self.db_config['database']}'
              AND pid <> pg_backend_pid();
            """
            
            cmd = [
                'psql',
                '-h', self.db_config['host'],
                '-p', self.db_config['port'],
                '-U', self.db_config['user'],
                '-d', 'postgres',
                '-c', terminate_sql,
                '--no-password'
            ]
            
            result = subprocess.run(cmd, env=env, capture_output=True, text=True)
            if result.returncode == 0:
                self.logger.info("Database connections terminated successfully")
                return True
            else:
                self.logger.error(f"Failed to terminate connections: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error terminating connections: {e}")
            return False

    def drop_and_recreate_database(self):
        """Drop and recreate the target database"""
        self.logger.info(f"Dropping and recreating database '{self.db_config['database']}'")
        
        try:
            env = os.environ.copy()
            env['PGPASSWORD'] = self.db_config['password']
            
            # Drop database
            drop_cmd = [
                'psql',
                '-h', self.db_config['host'],
                '-p', self.db_config['port'],
                '-U', self.db_config['user'],
                '-d', 'postgres',
                '-c', f"DROP DATABASE IF EXISTS {self.db_config['database']};",
                '--no-password'
            ]
            
            result = subprocess.run(drop_cmd, env=env, capture_output=True, text=True)
            if result.returncode != 0:
                self.logger.error(f"Failed to drop database: {result.stderr}")
                return False
            
            # Create database
            create_cmd = [
                'psql',
                '-h', self.db_config['host'],
                '-p', self.db_config['port'],
                '-U', self.db_config['user'],
                '-d', 'postgres',
                '-c', f"CREATE DATABASE {self.db_config['database']};",
                '--no-password'
            ]
            
            result = subprocess.run(create_cmd, env=env, capture_output=True, text=True)
            if result.returncode == 0:
                self.logger.info("Database recreated successfully")
                return True
            else:
                self.logger.error(f"Failed to create database: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error recreating database: {e}")
            return False

    def restore_from_custom_format(self, backup_file):
        """Restore from pg_dump custom format backup"""
        env = os.environ.copy()
        env['PGPASSWORD'] = self.db_config['password']
        
        cmd = [
            'pg_restore',
            '-h', self.db_config['host'],
            '-p', self.db_config['port'],
            '-U', self.db_config['user'],
            '-d', self.db_config['database'],
            '--verbose',
            '--no-password',
            '--clean',
            '--if-exists',
            f'--jobs={self.restore_config["parallel_jobs"]}',
            backup_file
        ]
        
        try:
            self.logger.info(f"Starting custom format restore: {' '.join(cmd[:-1])} [backup_file]")
            result = subprocess.run(cmd, env=env, capture_output=True, text=True)
            
            if result.returncode == 0:
                self.logger.info("Custom format restore completed successfully")
                return True
            else:
                self.logger.error(f"Custom format restore failed: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error during custom format restore: {e}")
            return False

    def restore_from_sql(self, backup_file):
        """Restore from SQL dump file"""
        env = os.environ.copy()
        env['PGPASSWORD'] = self.db_config['password']
        
        # Handle compressed files
        if backup_file.endswith('.gz'):
            # For Windows PowerShell, we need to handle this differently
            if os.name == 'nt':  # Windows
                # Use Python to decompress and pipe to psql
                import gzip
                try:
                    self.logger.info(f"Decompressing and restoring from: {backup_file}")
                    
                    # Read and decompress the file
                    with gzip.open(backup_file, 'rt', encoding='utf-8') as f:
                        sql_content = f.read()
                    
                    # Write to temporary file
                    temp_file = backup_file.replace('.gz', '.tmp')
                    with open(temp_file, 'w', encoding='utf-8') as f:
                        f.write(sql_content)
                    
                    # Use the temporary file for restore
                    cmd = [
                        'psql',
                        '-h', self.db_config['host'],
                        '-p', self.db_config['port'],
                        '-U', self.db_config['user'],
                        '-d', self.db_config['database'],
                        '--no-password',
                        '-f', temp_file
                    ]
                    
                    result = subprocess.run(cmd, env=env, capture_output=True, text=True)
                    
                    # Clean up temporary file
                    try:
                        os.remove(temp_file)
                    except:
                        pass
                    
                    if result.returncode == 0:
                        self.logger.info("SQL restore completed successfully")
                        return True
                    else:
                        self.logger.error(f"SQL restore failed: {result.stderr}")
                        return False
                        
                except Exception as e:
                    self.logger.error(f"Error handling compressed file: {e}")
                    return False
            else:
                # Unix/Linux - use gunzip piping
                cmd = f"gunzip -c {backup_file} | psql -h {self.db_config['host']} -p {self.db_config['port']} -U {self.db_config['user']} -d {self.db_config['database']} --no-password"
                use_shell = True
        else:
            cmd = [
                'psql',
                '-h', self.db_config['host'],
                '-p', self.db_config['port'],
                '-U', self.db_config['user'],
                '-d', self.db_config['database'],
                '--no-password',
                '-f', backup_file
            ]
            use_shell = False
        
        try:
            self.logger.info(f"Starting SQL restore from: {backup_file}")
            
            if backup_file.endswith('.gz') and os.name != 'nt':
                result = subprocess.run(cmd, env=env, shell=True, capture_output=True, text=True)
            elif not backup_file.endswith('.gz'):
                result = subprocess.run(cmd, env=env, capture_output=True, text=True)
            else:
                # Already handled above for Windows
                return True
            
            if result.returncode == 0:
                self.logger.info("SQL restore completed successfully")
                return True
            else:
                self.logger.error(f"SQL restore failed: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error during SQL restore: {e}")
            return False

    def verify_restore(self):
        """Verify the restore operation was successful"""
        if not self.restore_config['verify_after_restore']:
            return True
        
        self.logger.info("Verifying restore operation...")
        
        try:
            env = os.environ.copy()
            env['PGPASSWORD'] = self.db_config['password']
            
            # Check if database exists and is accessible
            test_queries = [
                "SELECT COUNT(*) FROM users;",
                "SELECT COUNT(*) FROM products;",
                "SELECT COUNT(*) FROM orders;",
                "SELECT version();"
            ]
            
            for query in test_queries:
                cmd = [
                    'psql',
                    '-h', self.db_config['host'],
                    '-p', self.db_config['port'],
                    '-U', self.db_config['user'],
                    '-d', self.db_config['database'],
                    '-c', query,
                    '--no-password',
                    '-t',
                    '-A'
                ]
                
                result = subprocess.run(cmd, env=env, capture_output=True, text=True)
                if result.returncode != 0:
                    self.logger.error(f"Verification failed for query: {query}")
                    self.logger.error(f"Error: {result.stderr}")
                    return False
                else:
                    self.logger.info(f"Verification passed: {query.strip()} -> {result.stdout.strip()}")
            
            self.logger.info("Restore verification completed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error during restore verification: {e}")
            return False

    def perform_restore(self, backup_file, force=False, clean=True):
        """Perform the complete restore operation"""
        self.logger.info(f"Starting restore operation from: {backup_file}")
        
        # Verify backup file
        if not self.verify_backup_file(backup_file):
            return False
        
        # Create pre-restore backup
        pre_restore_backup = None
        if not force:
            pre_restore_backup = self.create_pre_restore_backup()
        
        # Get initial connection count
        initial_connections = self.get_database_connection_count()
        if initial_connections > 0:
            self.logger.info(f"Found {initial_connections} active connections to database")
            
            if not force:
                response = input("Active connections found. Continue with restore? (y/N): ")
                if response.lower() != 'y':
                    self.logger.info("Restore cancelled by user")
                    return False
            
            # Terminate connections
            if not self.terminate_database_connections():
                self.logger.error("Failed to terminate database connections")
                return False
        
        start_time = datetime.datetime.now()
        
        # Determine backup format and restore accordingly
        success = False
        if backup_file.endswith('.backup'):
            success = self.restore_from_custom_format(backup_file)
        elif backup_file.endswith(('.sql', '.sql.gz')):
            if clean:
                # For SQL files, we need to drop/recreate database
                if not self.drop_and_recreate_database():
                    self.logger.error("Failed to recreate database")
                    return False
            success = self.restore_from_sql(backup_file)
        else:
            self.logger.error(f"Unsupported backup format: {backup_file}")
            return False
        
        end_time = datetime.datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        if success:
            self.logger.info(f"Restore completed in {duration:.2f} seconds")
            
            # Verify restore
            if self.verify_restore():
                self.logger.info("Restore operation completed successfully")
                
                # Log restore metadata
                self.log_restore_metadata(backup_file, True, duration, pre_restore_backup)
                return True
            else:
                self.logger.error("Restore verification failed")
                success = False
        
        if not success:
            self.logger.error(f"Restore failed after {duration:.2f} seconds")
            self.log_restore_metadata(backup_file, False, duration, pre_restore_backup)
            
            if pre_restore_backup:
                self.logger.info(f"Pre-restore backup is available at: {pre_restore_backup}")
        
        return success

    def log_restore_metadata(self, backup_file, success, duration, pre_restore_backup):
        """Log restore operation metadata"""
        metadata = {
            'restore_timestamp': datetime.datetime.now().isoformat(),
            'backup_file': backup_file,
            'database': self.db_config['database'],
            'host': self.db_config['host'],
            'success': success,
            'duration_seconds': duration,
            'pre_restore_backup': pre_restore_backup
        }
        
        metadata_file = os.path.join(
            self.restore_config['backup_path'], 
            f"restore_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        
        try:
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
            self.logger.info(f"Restore metadata saved: {metadata_file}")
        except Exception as e:
            self.logger.error(f"Failed to save restore metadata: {e}")

def main():
    """Main function to handle command line execution"""
    import argparse
    
    parser = argparse.ArgumentParser(description='PostgreSQL Database Restore Tool')
    parser.add_argument('backup_file', nargs='?', help='Path to backup file to restore')
    parser.add_argument('--list', action='store_true', help='List available backup files')
    parser.add_argument('--force', action='store_true', help='Force restore without prompts')
    parser.add_argument('--no-clean', action='store_true', help='Do not drop/recreate database')
    parser.add_argument('--latest', action='store_true', help='Restore from latest backup')
    
    args = parser.parse_args()
    
    restore_tool = DatabaseRestore()
    
    if args.list:
        print("\n=== Available Backups ===")
        backups = restore_tool.list_available_backups()
        if not backups:
            print("No backups found.")
        else:
            for i, backup in enumerate(backups, 1):
                status = "SUCCESS" if backup.get('success', True) else "FAILED"
                print(f"{i}. [{status}] {backup['name']}")
                print(f"   Type: {backup['type']} | Format: {backup['format']}")
                print(f"   Size: {backup['size']:,} bytes")
                print(f"   Created: {backup['created']}")
                print(f"   Path: {backup['file']}")
                print("-" * 60)
        return
    
    if args.latest:
        backups = restore_tool.list_available_backups()
        if not backups:
            print("❌ No backups found.")
            sys.exit(1)
        
        # Find latest successful backup
        latest_backup = None
        for backup in backups:
            if backup.get('success', True):  # Assume success if no metadata
                latest_backup = backup['file']
                break
        
        if not latest_backup:
            print("No successful backups found.")
            sys.exit(1)
        
        print(f"Using latest backup: {latest_backup}")
        backup_file = latest_backup
    elif args.backup_file:
        backup_file = args.backup_file
    else:
        # Interactive selection
        backups = restore_tool.list_available_backups()
        if not backups:
            print("No backups found.")
            sys.exit(1)
        
        print("\n=== Select Backup to Restore ===")
        for i, backup in enumerate(backups[:10], 1):  # Show only last 10
            status = "SUCCESS" if backup.get('success', True) else "FAILED"
            print(f"{i}. [{status}] {backup['name']} ({backup['size']:,} bytes, {backup['created']})")
        
        try:
            choice = int(input("\nEnter backup number (1-10): ")) - 1
            if 0 <= choice < len(backups):
                backup_file = backups[choice]['file']
            else:
                print("Invalid choice.")
                sys.exit(1)
        except (ValueError, KeyboardInterrupt):
            print("Operation cancelled.")
            sys.exit(1)
    
    # Perform restore
    print(f"\nStarting restore from: {backup_file}")
    if not args.force:
        response = input("WARNING: This will overwrite the current database. Continue? (y/N): ")
        if response.lower() != 'y':
            print("Restore cancelled.")
            sys.exit(1)
    
    success = restore_tool.perform_restore(
        backup_file, 
        force=args.force, 
        clean=not args.no_clean
    )
    
    if success:
        print(f"\nRestore completed successfully from: {backup_file}")
        sys.exit(0)
    else:
        print(f"\nRestore failed from: {backup_file}")
        sys.exit(1)

if __name__ == "__main__":
    main()
