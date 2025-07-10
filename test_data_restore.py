#!/usr/bin/env python3
"""
Test restore with a data backup that contains actual users
"""

import psycopg2
import os
import sys
import subprocess
from datetime import datetime

def get_db_connection():
    """Get database connection"""
    return psycopg2.connect(
        host="localhost",
        port="5432",
        database="ecommerce_db",
        user="postgres",
        password="hengmengly123"
    )

def get_user_count():
    """Get current number of users"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users")
        count = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        return count
    except Exception as e:
        print(f"Error getting user count: {e}")
        return None

def get_users_info():
    """Get detailed user information"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT user_id, username, email, first_name, last_name 
            FROM users 
            ORDER BY created_at
        """)
        users = cursor.fetchall()
        cursor.close()
        conn.close()
        return users
    except Exception as e:
        print(f"Error getting users info: {e}")
        return []

def add_test_user():
    """Add a test user"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO users (username, email, password_hash, first_name, last_name)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING user_id
        """, (
            'restore_test_data_user',
            'restore_test_data@example.com',
            '$2b$10$example_hash',
            'RestoreData',
            'Test'
        ))
        
        user_id = cursor.fetchone()[0]
        conn.commit()
        cursor.close()
        conn.close()
        
        print(f"✅ Added test user with ID: {user_id}")
        return user_id
        
    except Exception as e:
        print(f"❌ Error adding test user: {e}")
        return None

def test_restore_with_data_backup():
    """Test restore using a data backup file"""
    print("🧪 Restore Test with Data Backup")
    print("=" * 50)
    
    # Use a data backup
    backup_file = "ecommerce_data_2025-06-28_03-50-06.sql"
    backup_path = os.path.join("backups", backup_file)
    
    if not os.path.exists(backup_path):
        print(f"❌ Backup file not found: {backup_path}")
        return False
    
    print(f"📦 Using data backup: {backup_file}")
    
    # Get initial state
    print("\n📊 Getting initial state...")
    original_count = get_user_count()
    original_users = get_users_info()
    print(f"Original user count: {original_count}")
    print("Original users:")
    for user in original_users[:3]:  # Show first 3
        print(f"  - {user[1]} ({user[2]})")
    if len(original_users) > 3:
        print(f"  ... and {len(original_users) - 3} more")
    
    # Add test user
    print("\n👤 Adding test user...")
    test_user_id = add_test_user()
    if not test_user_id:
        return False
    
    # Verify user was added
    new_count = get_user_count()
    print(f"New user count: {new_count}")
    
    # Test restore
    print(f"\n🔄 Testing restore from {backup_file}...")
    try:
        cmd = ['python', 'db/restore.py', backup_path, '--force']
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Restore command completed successfully")
            
            # Verify restore
            print("\n🔍 Verifying restore...")
            final_count = get_user_count()
            final_users = get_users_info()
            print(f"Final user count: {final_count}")
            
            # Check if test user was removed
            test_user_exists = any(user[1] == 'restore_test_data_user' for user in final_users)
            
            if not test_user_exists:
                print("✅ Test user was correctly removed by restore")
            else:
                print("❌ Test user still exists after restore")
            
            # Show restored users
            print("Restored users:")
            for user in final_users[:3]:  # Show first 3
                print(f"  - {user[1]} ({user[2]})")
            if len(final_users) > 3:
                print(f"  ... and {len(final_users) - 3} more")
            
            # Check if we got expected users back
            if final_count > 0:
                print(f"✅ Data was restored successfully ({final_count} users)")
                return not test_user_exists
            else:
                print("⚠️  No users after restore - might be schema-only backup")
                return not test_user_exists
            
        else:
            print("❌ Restore command failed")
            print("STDERR:", result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Error running restore: {e}")
        return False

if __name__ == "__main__":
    success = test_restore_with_data_backup()
    if success:
        print("\n🎉 Data restore test PASSED!")
    else:
        print("\n⚠️  Data restore test FAILED!")
    sys.exit(0 if success else 1)
