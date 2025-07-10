#!/usr/bin/env python3
"""
Comprehensive restore functionality test
This script will:
1. Create a test backup
2. Modify some data
3. Restore from backup
4. Verify the restore worked
"""

import psycopg2
import os
import sys
import subprocess
import json
import time
from datetime import datetime

class RestoreTest:
    def __init__(self):
        self.db_config = {
            'host': 'localhost',
            'port': '5432',
            'database': 'ecommerce_db',
            'user': 'postgres',
            'password': 'hengmengly123'
        }
        self.test_results = []
    
    def log_result(self, test_name, success, message=""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        if message:
            print(f"    {message}")
        self.test_results.append({
            'test': test_name,
            'success': success,
            'message': message,
            'timestamp': datetime.now().isoformat()
        })
    
    def get_db_connection(self):
        """Get database connection"""
        return psycopg2.connect(**self.db_config)
    
    def get_user_count(self):
        """Get current number of users"""
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM users")
            count = cursor.fetchone()[0]
            cursor.close()
            conn.close()
            return count
        except Exception as e:
            print(f"Error getting user count: {e}")
            return None
    
    def create_test_backup(self):
        """Create a backup for testing"""
        try:
            print("\n📦 Creating test backup...")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = f"backups/test_backup_{timestamp}.sql"
            
            # Use pg_dump to create backup
            cmd = [
                'pg_dump',
                f"--host={self.db_config['host']}",
                f"--port={self.db_config['port']}",
                f"--username={self.db_config['user']}",
                '--no-password',
                '--verbose',
                '--clean',
                '--if-exists',
                '--format=plain',
                f"--file={backup_file}",
                self.db_config['database']
            ]
            
            # Set password environment variable
            env = os.environ.copy()
            env['PGPASSWORD'] = self.db_config['password']
            
            result = subprocess.run(cmd, env=env, capture_output=True, text=True)
            
            if result.returncode == 0:
                size = os.path.getsize(backup_file) / 1024 / 1024
                self.log_result("Create test backup", True, f"Created {backup_file} ({size:.2f} MB)")
                return backup_file
            else:
                self.log_result("Create test backup", False, f"pg_dump failed: {result.stderr}")
                return None
                
        except Exception as e:
            self.log_result("Create test backup", False, str(e))
            return None
    
    def add_test_user(self):
        """Add a test user to modify database state"""
        try:
            print("\n👤 Adding test user...")
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            # Add a test user
            cursor.execute("""
                INSERT INTO users (username, email, password_hash, first_name, last_name)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING user_id
            """, (
                'restore_test_user',
                'restore_test@example.com',
                '$2b$10$example_hash',
                'Restore',
                'Test'
            ))
            
            user_id = cursor.fetchone()[0]
            conn.commit()
            cursor.close()
            conn.close()
            
            self.log_result("Add test user", True, f"Added user with ID {user_id}")
            return user_id
            
        except Exception as e:
            self.log_result("Add test user", False, str(e))
            return None
    
    def test_restore_script(self, backup_file):
        """Test our restore script"""
        try:
            print(f"\n🔄 Testing restore from {backup_file}...")
            
            # Run our restore script
            cmd = ['python', 'db/restore.py', backup_file]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                self.log_result("Restore script execution", True, "Restore completed successfully")
                return True
            else:
                self.log_result("Restore script execution", False, f"Restore failed: {result.stderr}")
                return False
                
        except Exception as e:
            self.log_result("Restore script execution", False, str(e))
            return False
    
    def verify_restore(self, original_user_count):
        """Verify that restore worked correctly"""
        try:
            print("\n🔍 Verifying restore...")
            
            # Check if test user was removed (restored to previous state)
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM users WHERE username = 'restore_test_user'")
            test_user_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM users")
            current_user_count = cursor.fetchone()[0]
            
            cursor.close()
            conn.close()
            
            # Test user should be gone (restored to backup state)
            if test_user_count == 0:
                self.log_result("Test user removed", True, "Test user correctly removed by restore")
            else:
                self.log_result("Test user removed", False, "Test user still exists after restore")
            
            # User count should match original
            if current_user_count == original_user_count:
                self.log_result("User count restored", True, f"User count correctly restored to {original_user_count}")
            else:
                self.log_result("User count restored", False, 
                              f"User count mismatch: expected {original_user_count}, got {current_user_count}")
            
            return test_user_count == 0 and current_user_count == original_user_count
            
        except Exception as e:
            self.log_result("Verify restore", False, str(e))
            return False
    
    def cleanup_test_backup(self, backup_file):
        """Clean up test backup file"""
        try:
            if backup_file and os.path.exists(backup_file):
                os.remove(backup_file)
                self.log_result("Cleanup test backup", True, f"Removed {backup_file}")
            else:
                self.log_result("Cleanup test backup", True, "No cleanup needed")
        except Exception as e:
            self.log_result("Cleanup test backup", False, str(e))
    
    def run_full_test(self):
        """Run the complete restore test"""
        print("🧪 Starting Comprehensive Restore Test")
        print("=" * 60)
        
        # Step 1: Get initial state
        print("\n📊 Getting initial database state...")
        original_user_count = self.get_user_count()
        if original_user_count is None:
            print("❌ Failed to get initial user count")
            return False
        
        self.log_result("Get initial state", True, f"Initial user count: {original_user_count}")
        
        # Step 2: Create backup
        backup_file = self.create_test_backup()
        if not backup_file:
            return False
        
        # Step 3: Modify database
        test_user_id = self.add_test_user()
        if test_user_id is None:
            self.cleanup_test_backup(backup_file)
            return False
        
        # Verify user was added
        new_user_count = self.get_user_count()
        if new_user_count == original_user_count + 1:
            self.log_result("Verify user added", True, f"User count increased to {new_user_count}")
        else:
            self.log_result("Verify user added", False, f"Expected {original_user_count + 1}, got {new_user_count}")
        
        # Step 4: Test restore
        restore_success = self.test_restore_script(backup_file)
        if not restore_success:
            self.cleanup_test_backup(backup_file)
            return False
        
        # Step 5: Verify restore
        verify_success = self.verify_restore(original_user_count)
        
        # Step 6: Cleanup
        self.cleanup_test_backup(backup_file)
        
        # Summary
        self.print_summary()
        
        return verify_success
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for r in self.test_results if r['success'])
        total = len(self.test_results)
        
        for result in self.test_results:
            status = "✅" if result['success'] else "❌"
            print(f"{status} {result['test']}")
            if result['message']:
                print(f"    {result['message']}")
        
        print(f"\nResults: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 ALL TESTS PASSED! Restore functionality is working correctly.")
        else:
            print("⚠️  Some tests failed. Please check the restore implementation.")

def main():
    tester = RestoreTest()
    success = tester.run_full_test()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
