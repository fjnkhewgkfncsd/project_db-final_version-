#!/usr/bin/env python3
"""
Fixed restore tester - Test restoring the backup with 10,003 users
This script will properly restore the backup file that contains 10,003 users
and verify the process works correctly.
"""

import os
import sys
import subprocess
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

class RestoreTester:
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
    
    def check_user_count(self):
        """Check current number of users in database"""
        try:
            with self.get_database_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT COUNT(*) FROM users;")
                    count = cursor.fetchone()[0]
                    return count
        except Exception as e:
            print(f"Error checking user count: {e}")
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
    
    def restore_from_backup(self, backup_file):
        """Properly restore database from backup file using psql directly"""
        backup_path = os.path.join(self.backup_dir, backup_file)
        
        if not os.path.exists(backup_path):
            print(f"✗ Backup file not found: {backup_path}")
            return False
        
        print(f"🔄 Restoring database from: {backup_file}")
        
        try:
            # Method 1: Use psql to restore the SQL file directly
            # This is more reliable than trying to manage transactions in Python
            
            cmd = [
                'psql',
                f"--host={self.db_config['host']}",
                f"--port={self.db_config['port']}",
                f"--username={self.db_config['user']}",
                '--no-password',
                '--dbname=postgres',  # Connect to postgres to handle DB operations
                '--file', backup_path,
                '--quiet'
            ]
            
            env = os.environ.copy()
            env['PGPASSWORD'] = self.db_config['password']
            
            print("   Executing restore command...")
            result = subprocess.run(cmd, capture_output=True, text=True, env=env)
            
            if result.returncode == 0:
                print("✓ Restore completed successfully")
                return True
            else:
                print(f"✗ Restore failed with return code {result.returncode}")
                if result.stderr:
                    print(f"   Error: {result.stderr}")
                if result.stdout:
                    print(f"   Output: {result.stdout}")
                return False
                
        except Exception as e:
            print(f"✗ Error during restore: {e}")
            return False
    
    def test_restore_with_10k_users(self):
        """Test restoring the backup that contains 10,003 users"""
        print("🧪 TESTING RESTORE WITH 10,003 USERS")
        print("=" * 50)
        
        # The backup file we know contains 10,003 users
        target_backup = "ecommerce_backup_2025-07-09_02-46-32.sql"
        
        # Step 1: Check current state
        print("\n1. CURRENT STATE")
        current_users = self.check_user_count()
        print(f"   Current users in database: {current_users}")
        
        # Step 2: Create safety backup
        print("\n2. CREATING SAFETY BACKUP")
        safety_backup = self.create_safety_backup()
        if not safety_backup:
            print("✗ Cannot proceed without safety backup")
            return False
        
        # Step 3: Restore from the 10K user backup
        print(f"\n3. RESTORING FROM {target_backup}")
        restore_success = self.restore_from_backup(target_backup)
        
        if not restore_success:
            print("✗ Restore failed")
            return False
        
        # Step 4: Verify the restore
        print("\n4. VERIFYING RESTORE RESULTS")
        new_user_count = self.check_user_count()
        
        if new_user_count is None:
            print("✗ Cannot verify restore - database connection failed")
            return False
        
        print(f"   Users after restore: {new_user_count}")
        
        if new_user_count == 10003:
            print("✅ SUCCESS! Restore worked correctly - 10,003 users restored")
            return True
        elif new_user_count == 4:
            print("⚠️  ISSUE: Only 4 users after restore (same as before)")
            print("   This suggests the restore process isn't working properly")
            return False
        else:
            print(f"⚠️  UNEXPECTED: Got {new_user_count} users (expected 10,003)")
            return False
    
    def show_sample_users(self, limit=10):
        """Show a sample of users to verify data"""
        try:
            with self.get_database_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        SELECT username, email, first_name, last_name 
                        FROM users 
                        ORDER BY username 
                        LIMIT %s
                    """, (limit,))
                    
                    users = cursor.fetchall()
                    print(f"\n📋 Sample of {len(users)} users:")
                    for user in users:
                        print(f"   {user[0]} | {user[1]} | {user[2]} {user[3]}")
                        
        except Exception as e:
            print(f"Error fetching sample users: {e}")

def main():
    """Main function"""
    tester = RestoreTester()
    
    # Run the test
    success = tester.test_restore_with_10k_users()
    
    if success:
        print("\n🎉 The restore process works correctly!")
        print("   The issue was likely that you were restoring a backup")
        print("   that was created when the database only had 4 users.")
        
        # Show sample of restored users
        tester.show_sample_users(10)
        
    else:
        print("\n🔍 The restore process needs investigation.")
        print("   Check the error messages above for details.")

if __name__ == "__main__":
    main()
