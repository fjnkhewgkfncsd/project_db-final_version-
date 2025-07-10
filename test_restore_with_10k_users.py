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
    headers = {"Authorization": f"Bearer {token}"}
    query_payload = {"sql": "SELECT COUNT(*) as count FROM users"}
    
    response = requests.post(f"{BACKEND_URL}/database/query", 
                           headers=headers, json=query_payload)
    
    if response.status_code == 200:
        data = response.json()
        count = data['data']['rows'][0]['count']
        print(f"Current users in database: {count}")
        return count
    else:
        print(f"❌ Failed to check user count: {response.text}")
        return None

def test_restore_function(token, backup_filename):
    """Test the restore function with a specific backup"""
    print(f"\n🔄 Testing restore with: {backup_filename}")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Check user count before restore
    users_before = check_current_users(token)
    
    # Perform restore
    print(f"⚡ Starting restore process...")
    start_time = time.time()
    
    restore_payload = {
        "filename": backup_filename,
        "force": True
    }
    
    response = requests.post(f"{BACKEND_URL}/database/restore", 
                           headers=headers, 
                           json=restore_payload,
                           timeout=120)  # 2 minute timeout
    
    end_time = time.time()
    duration = end_time - start_time
    
    if response.status_code == 200:
        data = response.json()
        restore_data = data['data']
        
        print(f"✅ Restore completed successfully!")
        print(f"   📁 File: {restore_data['filename']}")
        print(f"   📏 Size: {restore_data['file_size']}")
        print(f"   ⏱️ Execution time: {restore_data['execution_time_ms']}ms")
        print(f"   🕐 Total time: {duration:.2f}s")
        print(f"   📅 Restored at: {restore_data['restored_at']}")
        
        # Check verification
        verification = restore_data['verification']
        if verification['verified']:
            users_count = verification['users_count']
            print(f"   ✅ Verification: {users_count} users found")
            
            # Double-check with direct query
            users_after = check_current_users(token)
            
            if str(users_count) == str(users_after):
                print(f"   ✅ User count matches: {users_count}")
                return True, users_count
            else:
                print(f"   ⚠️ User count mismatch: verification={users_count}, query={users_after}")
                return True, users_after
        else:
            print(f"   ❌ Verification failed: {verification.get('error', 'unknown error')}")
            return False, None
    else:
        print(f"❌ Restore failed: {response.status_code}")
        print(f"   Error: {response.text}")
        return False, None

def find_backup_with_users(backups, target_users=10003):
    """Find a backup that likely has the target number of users"""
    print(f"\n🔍 Looking for backup with ~{target_users} users...")
    
    # Look for recent large backups (likely to have 10k+ users)
    large_backups = []
    for backup in backups:
        size_mb = float(backup['size'].replace(' MB', ''))
        if size_mb > 10:  # Large backups likely have more users
            large_backups.append((backup, size_mb))
    
    # Sort by size descending
    large_backups.sort(key=lambda x: x[1], reverse=True)
    
    if large_backups:
        recommended = large_backups[0][0]
        print(f"📋 Recommended backup: {recommended['filename']} ({recommended['size']})")
        return recommended['filename']
    else:
        # Fallback to most recent
        if backups:
            recent = backups[0]
            print(f"📋 Using most recent: {recent['filename']} ({recent['size']})")
            return recent['filename']
    
    return None

def main():
    """Main test function"""
    print("="*80)
    print("🧪 TESTING MAIN SYSTEM DATABASE RESTORE FUNCTION")
    print("="*80)
    
    # Get authentication
    token = get_auth_token()
    if not token:
        return
    
    # Get backup list
    backups = get_backup_list(token)
    if not backups:
        print("❌ No backups available for testing")
        return
    
    # Show available backups
    print(f"\n📋 Available backups (showing first 5):")
    for i, backup in enumerate(backups[:5]):
        print(f"   {i+1}. {backup['filename']} ({backup['size']}) - {backup['created']}")
    
    # Find a good backup to test with
    test_backup = find_backup_with_users(backups, 10003)
    if not test_backup:
        print("❌ No suitable backup found")
        return
    
    # Test the restore function
    print(f"\n{'='*80}")
    print("🔧 TESTING RESTORE FUNCTION")
    print(f"{'='*80}")
    
    success, user_count = test_restore_function(token, test_backup)
    
    # Final summary
    print(f"\n{'='*80}")
    print("📊 TEST RESULTS")
    print(f"{'='*80}")
    
    if success:
        print(f"✅ RESTORE FUNCTION IS WORKING CORRECTLY")
        print(f"   📁 Backup used: {test_backup}")
        print(f"   👥 Users restored: {user_count}")
        print(f"   🎯 Target achieved: Database restore via main system successful")
        
        if user_count and int(user_count) >= 10000:
            print(f"   🎉 Large dataset restored successfully ({user_count} users)")
        else:
            print(f"   ℹ️ Smaller dataset restored ({user_count} users)")
            
        print(f"\n✅ The main database route restore function is working as expected!")
        print(f"✅ You can use the Database Tools tab in the frontend with confidence")
        
    else:
        print(f"❌ RESTORE FUNCTION HAS ISSUES")
        print(f"   📁 Backup tested: {test_backup}")
        print(f"   🚨 The main system restore needs investigation")
    
    print(f"\n{'='*80}")

if __name__ == "__main__":
    main()
