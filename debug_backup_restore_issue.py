#!/usr/bin/env python3
"""
Debug script to investigate backup/restore issue where 10,003 users become 4 users after restore.
This script will:
1. Check current database state
2. Analyze backup files for actual user count
3. Test the backup/restore process step by step
4. Identify where the data loss occurs
"""

import os
import sys
import subprocess
import json
import re
from datetime import datetime

# Add backend directory to path for database utilities
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

try:
    from dotenv import load_dotenv
    import psycopg2
    from psycopg2 import sql
except ImportError as e:
    print(f"Error importing required modules: {e}")
    print("Please install: pip install psycopg2-binary python-dotenv")
    sys.exit(1)

class BackupRestoreDebugger:
    def __init__(self):
        # Load environment variables
        env_path = os.path.join('backend', '.env')
        load_dotenv(env_path)
        
        self.db_config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': os.getenv('DB_PORT', '5432'),
            'user': os.getenv('DB_USER', 'postgres'),
            'password': os.getenv('DB_PASSWORD', 'password'),
            'database': os.getenv('DB_NAME', 'ecommerce_db')
        }
        
        self.backup_dir = 'backups'
        
    def get_database_connection(self, database=None):
        """Get database connection"""
        config = self.db_config.copy()
        if database:
            config['database'] = database
        return psycopg2.connect(**config)
    
    def check_current_user_count(self):
        """Check current number of users in database"""
        try:
            with self.get_database_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT COUNT(*) FROM users;")
                    count = cursor.fetchone()[0]
                    print(f"✓ Current database has {count} users")
                    return count
        except Exception as e:
            print(f"✗ Error checking current user count: {e}")
            return None
    
    def analyze_backup_file_content(self, backup_file):
        """Analyze backup file to count actual user records"""
        backup_path = os.path.join(self.backup_dir, backup_file)
        
        if not os.path.exists(backup_path):
            print(f"✗ Backup file not found: {backup_path}")
            return None
            
        print(f"\n📁 Analyzing backup file: {backup_file}")
        print(f"   File size: {os.path.getsize(backup_path):,} bytes")
        
        try:
            # Count different types of user-related statements
            insert_count = 0
            copy_count = 0
            copy_data_lines = 0
            
            with open(backup_path, 'r', encoding='utf-8', errors='ignore') as f:
                in_copy_block = False
                copy_table = None
                
                for line_num, line in enumerate(f, 1):
                    line_clean = line.strip()
                    
                    # Count INSERT statements for users table
                    if 'INSERT INTO' in line.upper() and 'USERS' in line.upper():
                        insert_count += 1
                    
                    # Detect COPY statements for users table
                    if line_clean.startswith('COPY ') and 'users' in line.lower():
                        in_copy_block = True
                        copy_table = 'users'
                        copy_count += 1
                        print(f"   Found COPY statement at line {line_num}: {line_clean[:100]}...")
                    
                    # Count data lines in COPY block
                    elif in_copy_block and copy_table == 'users':
                        if line_clean == '\\.' or line_clean == '\\.':
                            in_copy_block = False
                            copy_table = None
                            print(f"   End of COPY block at line {line_num}, found {copy_data_lines} data lines")
                        elif line_clean and not line_clean.startswith('--'):
                            copy_data_lines += 1
                            if copy_data_lines <= 5:  # Show first few lines
                                print(f"   Data line {copy_data_lines}: {line_clean[:100]}...")
            
            print(f"📊 Backup file analysis results:")
            print(f"   INSERT statements for users: {insert_count}")
            print(f"   COPY statements for users: {copy_count}")
            print(f"   Data lines in COPY blocks: {copy_data_lines}")
            
            return {
                'insert_count': insert_count,
                'copy_count': copy_count,
                'copy_data_lines': copy_data_lines,
                'total_user_records': insert_count + copy_data_lines
            }
            
        except Exception as e:
            print(f"✗ Error analyzing backup file: {e}")
            return None
    
    def list_recent_backups(self):
        """List recent backup files"""
        if not os.path.exists(self.backup_dir):
            print(f"✗ Backup directory not found: {self.backup_dir}")
            return []
        
        backup_files = []
        for filename in os.listdir(self.backup_dir):
            if filename.startswith('ecommerce_backup_') and filename.endswith('.sql'):
                filepath = os.path.join(self.backup_dir, filename)
                stat = os.stat(filepath)
                backup_files.append({
                    'filename': filename,
                    'size': stat.st_size,
                    'modified': datetime.fromtimestamp(stat.st_mtime)
                })
        
        # Sort by modification time (newest first)
        backup_files.sort(key=lambda x: x['modified'], reverse=True)
        return backup_files
    
    def test_backup_process(self):
        """Test creating a backup with current data"""
        print(f"\n🔄 Testing backup process...")
        
        # Check current user count
        current_users = self.check_current_user_count()
        if current_users is None:
            return False
        
        # Create a test backup
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        test_backup_file = f"test_backup_{timestamp}.sql"
        test_backup_path = os.path.join(self.backup_dir, test_backup_file)
        
        try:
            cmd = [
                'pg_dump',
                f"--host={self.db_config['host']}",
                f"--port={self.db_config['port']}",
                f"--username={self.db_config['user']}",
                '--no-password',
                '--verbose',
                '--clean',
                '--if-exists',
                '--create',
                self.db_config['database']
            ]
            
            # Set PGPASSWORD environment variable
            env = os.environ.copy()
            env['PGPASSWORD'] = self.db_config['password']
            
            print(f"   Creating test backup: {test_backup_file}")
            with open(test_backup_path, 'w') as backup_file:
                result = subprocess.run(cmd, stdout=backup_file, stderr=subprocess.PIPE, 
                                      env=env, text=True)
            
            if result.returncode == 0:
                print(f"✓ Test backup created successfully")
                
                # Analyze the test backup
                analysis = self.analyze_backup_file_content(test_backup_file)
                if analysis:
                    expected_users = current_users
                    actual_users = analysis['total_user_records']
                    
                    print(f"📊 Backup verification:")
                    print(f"   Expected users in backup: {expected_users}")
                    print(f"   Actual users in backup: {actual_users}")
                    
                    if actual_users == expected_users:
                        print(f"✓ Backup contains correct number of users")
                        return test_backup_file
                    else:
                        print(f"✗ Backup user count mismatch!")
                        return None
            else:
                print(f"✗ Backup failed: {result.stderr}")
                return None
                
        except Exception as e:
            print(f"✗ Error creating test backup: {e}")
            return None
    
    def test_restore_process(self, backup_file):
        """Test restoring a backup file"""
        print(f"\n🔄 Testing restore process with: {backup_file}")
        
        backup_path = os.path.join(self.backup_dir, backup_file)
        if not os.path.exists(backup_path):
            print(f"✗ Backup file not found: {backup_path}")
            return False
        
        # Create a safety backup first
        print("   Creating safety backup...")
        safety_backup = self.create_safety_backup()
        if not safety_backup:
            print("✗ Could not create safety backup")
            return False
        
        try:
            # Step 1: Drop and recreate database
            print("   Step 1: Recreating database...")
            with self.get_database_connection('postgres') as conn:
                conn.autocommit = True
                with conn.cursor() as cursor:
                    # Terminate connections
                    cursor.execute("""
                        SELECT pg_terminate_backend(pid)
                        FROM pg_stat_activity
                        WHERE datname = %s AND pid <> pg_backend_pid()
                    """, (self.db_config['database'],))
                    
                    # Drop and recreate
                    cursor.execute(f"DROP DATABASE IF EXISTS {self.db_config['database']}")
                    cursor.execute(f"CREATE DATABASE {self.db_config['database']}")
            
            print("✓ Database recreated")
            
            # Step 2: Restore from backup
            print("   Step 2: Restoring from backup...")
            cmd = [
                'psql',
                f"--host={self.db_config['host']}",
                f"--port={self.db_config['port']}",
                f"--username={self.db_config['user']}",
                '--no-password',
                '--dbname', self.db_config['database'],
                '--file', backup_path
            ]
            
            env = os.environ.copy()
            env['PGPASSWORD'] = self.db_config['password']
            
            result = subprocess.run(cmd, capture_output=True, text=True, env=env)
            
            if result.returncode == 0:
                print("✓ Restore completed")
                
                # Step 3: Verify restore
                print("   Step 3: Verifying restore...")
                restored_users = self.check_current_user_count()
                
                return restored_users
            else:
                print(f"✗ Restore failed: {result.stderr}")
                return None
                
        except Exception as e:
            print(f"✗ Error during restore: {e}")
            return None
    
    def create_safety_backup(self):
        """Create a safety backup before testing"""
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        safety_backup_file = f"safety_backup_{timestamp}.sql"
        safety_backup_path = os.path.join(self.backup_dir, safety_backup_file)
        
        try:
            cmd = [
                'pg_dump',
                f"--host={self.db_config['host']}",
                f"--port={self.db_config['port']}",
                f"--username={self.db_config['user']}",
                '--no-password',
                '--clean',
                '--if-exists',
                '--create',
                self.db_config['database']
            ]
            
            env = os.environ.copy()
            env['PGPASSWORD'] = self.db_config['password']
            
            with open(safety_backup_path, 'w') as backup_file:
                result = subprocess.run(cmd, stdout=backup_file, stderr=subprocess.PIPE, 
                                      env=env, text=True)
            
            if result.returncode == 0:
                print(f"✓ Safety backup created: {safety_backup_file}")
                return safety_backup_file
            else:
                print(f"✗ Safety backup failed: {result.stderr}")
                return None
                
        except Exception as e:
            print(f"✗ Error creating safety backup: {e}")
            return None
    
    def run_comprehensive_debug(self):
        """Run comprehensive debugging of backup/restore issue"""
        print("🔍 BACKUP/RESTORE ISSUE DEBUGGING")
        print("=" * 50)
        
        # Step 1: Check current state
        print("\n1. CURRENT DATABASE STATE")
        current_users = self.check_current_user_count()
        
        # Step 2: List available backups
        print("\n2. AVAILABLE BACKUP FILES")
        backups = self.list_recent_backups()
        
        if not backups:
            print("✗ No backup files found")
            return
        
        print(f"Found {len(backups)} backup files:")
        for i, backup in enumerate(backups[:10]):  # Show top 10
            print(f"   {i+1}. {backup['filename']}")
            print(f"      Size: {backup['size']:,} bytes")
            print(f"      Modified: {backup['modified']}")
        
        # Step 3: Analyze backup files
        print("\n3. BACKUP FILE ANALYSIS")
        for backup in backups[:5]:  # Analyze top 5 backups
            analysis = self.analyze_backup_file_content(backup['filename'])
            if analysis:
                print(f"\n📄 {backup['filename']}:")
                print(f"   Total user records: {analysis['total_user_records']}")
                if analysis['total_user_records'] > 1000:
                    print(f"   ⚠️  This backup contains {analysis['total_user_records']} users")
                    print(f"       Testing restore with this file...")
                    
                    # Test restore with this file
                    restored_count = self.test_restore_process(backup['filename'])
                    if restored_count is not None:
                        print(f"   📊 RESTORE RESULT: {restored_count} users")
                        if restored_count != analysis['total_user_records']:
                            print(f"   ⚠️  MISMATCH: Expected {analysis['total_user_records']}, got {restored_count}")
                        else:
                            print(f"   ✓ CORRECT: Restore worked properly")
                    break
        
        # Step 4: Test backup process
        print("\n4. BACKUP PROCESS TEST")
        test_backup = self.test_backup_process()
        
        print("\n" + "=" * 50)
        print("🔍 DEBUGGING COMPLETE")
        print("\nSUMMARY:")
        print(f"- Current database has {current_users} users")
        print(f"- Found {len(backups)} backup files")
        print("- Check the analysis above for backup/restore issues")

def main():
    """Main function"""
    debugger = BackupRestoreDebugger()
    debugger.run_comprehensive_debug()

if __name__ == "__main__":
    main()
