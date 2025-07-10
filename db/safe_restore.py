#!/usr/bin/env python3
"""
Enhanced Database Restore Script with Additional Safety Measures
"""

import os
import sys
import subprocess
import datetime
import logging
import json
import shutil
import tempfile
from pathlib import Path
from dotenv import load_dotenv

class SafeDatabaseRestore:
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
            'parallel_jobs': 4,
            'max_restore_time_minutes': 30,
            'safety_checks': True
        }
        
        # Setup logging
        self.setup_logging()

    def setup_logging(self):
        """Setup comprehensive logging configuration"""
        log_format = '%(asctime)s - %(levelname)s - [%(funcName)s] - %(message)s'
        
        # Ensure backup directory exists for log file
        os.makedirs(self.restore_config['backup_path'], exist_ok=True)
        
        # Create logs directory
        log_dir = os.path.join(self.restore_config['backup_path'], 'logs')
        os.makedirs(log_dir, exist_ok=True)
        
        log_file = os.path.join(log_dir, 'restore_detailed.log')
        
        logging.basicConfig(
            level=logging.INFO,
            format=log_format,
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)

    def validate_backup_file(self, backup_file):
        """Comprehensive backup file validation"""
        self.logger.info(f"Performing comprehensive validation of backup file: {backup_file}")
        
        # Check if file exists
        if not os.path.exists(backup_file):
            self.logger.error(f"Backup file does not exist: {backup_file}")
            return False, "File does not exist"
        
        # Check file size
        file_size = os.path.getsize(backup_file)
        if file_size == 0:
            self.logger.error(f"Backup file is empty: {backup_file}")
            return False, "File is empty"
        
        if file_size < 1024:  # Less than 1KB is suspicious
            self.logger.warning(f"Backup file is unusually small: {file_size} bytes")
        
        # Check file extension
        valid_extensions = ['.sql', '.sql.gz', '.backup']
        if not any(backup_file.endswith(ext) for ext in valid_extensions):
            self.logger.error(f"Invalid backup file extension: {backup_file}")
            return False, "Invalid file extension"
        
        # Read file header to verify format
        try:
            with open(backup_file, 'rb') as f:
                header = f.read(100)
                
                if backup_file.endswith('.sql'):
                    # Check for SQL dump header
                    header_text = header.decode('utf-8', errors='ignore')
                    if 'PostgreSQL database dump' not in header_text and 'CREATE' not in header_text:
                        self.logger.warning("File does not appear to be a valid SQL dump")
                
                elif backup_file.endswith('.backup'):
                    # Check for pg_dump custom format header
                    if not header.startswith(b'PGDMP'):
                        self.logger.error("File does not appear to be a valid pg_dump custom format")
                        return False, "Invalid custom format backup"
                
        except Exception as e:
            self.logger.error(f"Error reading backup file header: {e}")
            return False, f"Cannot read file: {e}"
        
        self.logger.info(f"Backup file validation passed: {backup_file} ({file_size:,} bytes)")
        return True, "Valid backup file"

    def check_database_connectivity(self):
        """Check if database server is accessible"""
        self.logger.info("Checking database server connectivity...")
        
        try:
            env = os.environ.copy()
            env['PGPASSWORD'] = self.db_config['password']
            
            cmd = [
                'psql',
                '-h', self.db_config['host'],
                '-p', self.db_config['port'],
                '-U', self.db_config['user'],
                '-d', 'postgres',  # Connect to default postgres database
                '-c', 'SELECT version();',
                '--no-password',
                '-t',
                '-A'
            ]
            
            result = subprocess.run(cmd, env=env, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                version = result.stdout.strip()
                self.logger.info(f"Database server is accessible: {version}")
                return True, version
            else:
                self.logger.error(f"Database connection failed: {result.stderr}")
                return False, result.stderr
                
        except subprocess.TimeoutExpired:
            self.logger.error("Database connection timeout")
            return False, "Connection timeout"
        except Exception as e:
            self.logger.error(f"Database connectivity check failed: {e}")
            return False, str(e)

    def create_safety_backup(self):
        """Create a safety backup before restore operation"""
        if not self.restore_config['create_backup_before_restore']:
            return None
        
        self.logger.info("Creating safety backup before restore operation...")
        
        try:
            # Generate safety backup filename
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            safety_backup_name = f"safety_backup_before_restore_{timestamp}.sql"
            safety_backup_path = os.path.join(self.restore_config['backup_path'], safety_backup_name)
            
            # Create the backup
            env = os.environ.copy()
            env['PGPASSWORD'] = self.db_config['password']
            
            cmd = [
                'pg_dump',
                '-h', self.db_config['host'],
                '-p', self.db_config['port'],
                '-U', self.db_config['user'],
                '-d', self.db_config['database'],
                '--verbose',
                '--no-password',
                '--clean',
                '--if-exists',
                '--create',
                '-f', safety_backup_path
            ]
            
            result = subprocess.run(cmd, env=env, capture_output=True, text=True, timeout=600)
            
            if result.returncode == 0:
                file_size = os.path.getsize(safety_backup_path)
                self.logger.info(f"Safety backup created successfully: {safety_backup_path} ({file_size:,} bytes)")
                return safety_backup_path
            else:
                self.logger.error(f"Safety backup creation failed: {result.stderr}")
                return None
                
        except subprocess.TimeoutExpired:
            self.logger.error("Safety backup creation timeout")
            return None
        except Exception as e:
            self.logger.error(f"Error creating safety backup: {e}")
            return None

    def perform_safe_restore(self, backup_file, force=False):
        """Perform restore with comprehensive safety measures"""
        self.logger.info(f"Starting safe database restore from: {backup_file}")
        
        # Phase 1: Pre-restore validations
        self.logger.info("Phase 1: Pre-restore validations")
        
        # Validate backup file
        is_valid, validation_message = self.validate_backup_file(backup_file)
        if not is_valid:
            self.logger.error(f"Backup validation failed: {validation_message}")
            return False, f"Validation failed: {validation_message}"
        
        # Check database connectivity
        is_connected, connection_info = self.check_database_connectivity()
        if not is_connected:
            self.logger.error(f"Database connectivity check failed: {connection_info}")
            if not force:
                return False, f"Database not accessible: {connection_info}"
        
        # Phase 2: Safety backup
        self.logger.info("Phase 2: Creating safety backup")
        safety_backup = None
        if is_connected:
            safety_backup = self.create_safety_backup()
            if not safety_backup and not force:
                self.logger.error("Failed to create safety backup")
                return False, "Cannot proceed without safety backup (use --force to override)"
        
        # Phase 3: Actual restore
        self.logger.info("Phase 3: Performing database restore")
        start_time = datetime.datetime.now()
        
        try:
            # Determine restore method based on file type
            if backup_file.endswith('.backup'):
                success, message = self._restore_custom_format(backup_file)
            elif backup_file.endswith('.sql.gz'):
                success, message = self._restore_compressed_sql(backup_file)
            else:  # .sql files
                success, message = self._restore_sql_file(backup_file)
            
            end_time = datetime.datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            if success:
                self.logger.info(f"Restore completed successfully in {duration:.2f} seconds")
                
                # Phase 4: Post-restore verification
                if self.restore_config['verify_after_restore']:
                    self.logger.info("Phase 4: Post-restore verification")
                    verification_success, verification_message = self.verify_restore()
                    
                    if verification_success:
                        self.logger.info("Database restore and verification completed successfully")
                        return True, {
                            'success': True,
                            'duration': duration,
                            'safety_backup': safety_backup,
                            'verification': verification_message
                        }
                    else:
                        self.logger.error(f"Post-restore verification failed: {verification_message}")
                        return False, f"Restore completed but verification failed: {verification_message}"
                else:
                    return True, {
                        'success': True,
                        'duration': duration,
                        'safety_backup': safety_backup
                    }
            else:
                self.logger.error(f"Restore failed: {message}")
                return False, f"Restore failed: {message}"
                
        except Exception as e:
            self.logger.error(f"Unexpected error during restore: {e}")
            return False, f"Unexpected error: {e}"

    def _restore_custom_format(self, backup_file):
        """Restore from pg_dump custom format"""
        self.logger.info(f"Restoring from custom format backup: {backup_file}")
        
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
            timeout_seconds = self.restore_config['max_restore_time_minutes'] * 60
            result = subprocess.run(cmd, env=env, capture_output=True, text=True, timeout=timeout_seconds)
            
            if result.returncode == 0:
                self.logger.info("Custom format restore completed successfully")
                return True, "Success"
            else:
                self.logger.error(f"Custom format restore failed: {result.stderr}")
                return False, result.stderr
                
        except subprocess.TimeoutExpired:
            self.logger.error(f"Restore operation timed out after {self.restore_config['max_restore_time_minutes']} minutes")
            return False, "Restore operation timed out"
        except Exception as e:
            self.logger.error(f"Error during custom format restore: {e}")
            return False, str(e)

    def _restore_compressed_sql(self, backup_file):
        """Restore from compressed SQL file"""
        self.logger.info(f"Restoring from compressed SQL backup: {backup_file}")
        
        # Create temporary uncompressed file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.sql', delete=False) as temp_file:
            temp_sql_file = temp_file.name
        
        try:
            # Decompress file
            self.logger.info("Decompressing backup file...")
            with open(backup_file, 'rb') as compressed_file:
                import gzip
                with gzip.open(compressed_file, 'rt') as gz_file:
                    with open(temp_sql_file, 'w') as output_file:
                        output_file.write(gz_file.read())
            
            # Restore from decompressed file
            success, message = self._restore_sql_file(temp_sql_file)
            
            return success, message
            
        except Exception as e:
            self.logger.error(f"Error restoring compressed SQL file: {e}")
            return False, str(e)
        finally:
            # Clean up temporary file
            if os.path.exists(temp_sql_file):
                os.unlink(temp_sql_file)

    def _restore_sql_file(self, backup_file):
        """Restore from SQL dump file"""
        self.logger.info(f"Restoring from SQL backup: {backup_file}")
        
        env = os.environ.copy()
        env['PGPASSWORD'] = self.db_config['password']
        
        cmd = [
            'psql',
            '-h', self.db_config['host'],
            '-p', self.db_config['port'],
            '-U', self.db_config['user'],
            '-d', self.db_config['database'],
            '--no-password',
            '-f', backup_file
        ]
        
        try:
            timeout_seconds = self.restore_config['max_restore_time_minutes'] * 60
            result = subprocess.run(cmd, env=env, capture_output=True, text=True, timeout=timeout_seconds)
            
            if result.returncode == 0:
                self.logger.info("SQL restore completed successfully")
                return True, "Success"
            else:
                self.logger.error(f"SQL restore failed: {result.stderr}")
                return False, result.stderr
                
        except subprocess.TimeoutExpired:
            self.logger.error(f"Restore operation timed out after {self.restore_config['max_restore_time_minutes']} minutes")
            return False, "Restore operation timed out"
        except Exception as e:
            self.logger.error(f"Error during SQL restore: {e}")
            return False, str(e)

    def verify_restore(self):
        """Comprehensive post-restore verification"""
        self.logger.info("Performing comprehensive post-restore verification...")
        
        verification_queries = [
            ("SELECT COUNT(*) FROM users", "User count"),
            ("SELECT COUNT(*) FROM products", "Product count"),
            ("SELECT COUNT(*) FROM orders", "Order count"),
            ("SELECT COUNT(*) FROM categories", "Category count"),
            ("SELECT version()", "Database version"),
            ("SELECT current_database()", "Database name")
        ]
        
        results = {}
        
        try:
            env = os.environ.copy()
            env['PGPASSWORD'] = self.db_config['password']
            
            for query, description in verification_queries:
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
                
                result = subprocess.run(cmd, env=env, capture_output=True, text=True, timeout=30)
                
                if result.returncode == 0:
                    value = result.stdout.strip()
                    results[description] = value
                    self.logger.info(f"Verification - {description}: {value}")
                else:
                    self.logger.error(f"Verification failed for {description}: {result.stderr}")
                    return False, f"Verification failed for {description}"
            
            self.logger.info("All verification checks passed")
            return True, results
            
        except Exception as e:
            self.logger.error(f"Error during verification: {e}")
            return False, str(e)

def main():
    """Main function for command line usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Safe PostgreSQL Database Restore Tool')
    parser.add_argument('backup_file', nargs='?', help='Path to backup file to restore')
    parser.add_argument('--force', action='store_true', help='Force restore without safety checks')
    parser.add_argument('--no-verify', action='store_true', help='Skip post-restore verification')
    parser.add_argument('--list', action='store_true', help='List available backup files')
    
    args = parser.parse_args()
    
    restore_tool = SafeDatabaseRestore()
    
    if args.list:
        # List available backups
        backup_dir = Path(restore_tool.restore_config['backup_path'])
        if backup_dir.exists():
            backups = sorted(backup_dir.glob('*.{sql,backup}'))
            print("\n=== Available Backup Files ===")
            for i, backup in enumerate(backups, 1):
                size = backup.stat().st_size
                modified = datetime.datetime.fromtimestamp(backup.stat().st_mtime)
                print(f"{i}. {backup.name}")
                print(f"   Size: {size:,} bytes ({size/(1024*1024):.2f} MB)")
                print(f"   Modified: {modified}")
                print("-" * 50)
        else:
            print("Backup directory not found")
        return
    
    if not args.backup_file:
        print("Please specify a backup file or use --list to see available backups")
        return
    
    # Disable verification if requested
    if args.no_verify:
        restore_tool.restore_config['verify_after_restore'] = False
    
    # Perform restore
    success, result = restore_tool.perform_safe_restore(args.backup_file, force=args.force)
    
    if success:
        print(f"\nRestore completed successfully!")
        if isinstance(result, dict):
            print(f"Duration: {result.get('duration', 'Unknown')} seconds")
            if result.get('safety_backup'):
                print(f"Safety backup: {result['safety_backup']}")
            if result.get('verification'):
                print("Verification results:")
                for key, value in result['verification'].items():
                    print(f"  {key}: {value}")
    else:
        print(f"\nRestore failed: {result}")
        sys.exit(1)

if __name__ == "__main__":
    main()
