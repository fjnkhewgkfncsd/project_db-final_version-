#!/usr/bin/env python3
"""
Simple restore test with an existing backup file
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
            'restore_test_user_simple',
            'restore_test_simple@example.com',
            '$2b$10$example_hash',
            'RestoreSimple',
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

def test_restore_with_existing_backup():
    """Test restore using the most recent backup file"""
    print("🧪 Simple Restore Test with Existing Backup")
    print("=" * 50)
    
    # Find the most recent backup
    backup_dir = "backups"
    sql_files = [f for f in os.listdir(backup_dir) if f.endswith('.sql')]
    if not sql_files:
        print("❌ No backup files found")
        return False
    
    # Get the most recent backup
    backup_file = sorted(sql_files)[-1]
    backup_path = os.path.join(backup_dir, backup_file)
    
    print(f"📦 Using backup file: {backup_file}")
    print(f"📁 Full path: {backup_path}")
    
    # Get initial state
    print("\n📊 Getting initial state...")
    original_count = get_user_count()
    print(f"Original user count: {original_count}")
    
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
        print(f"Running command: {' '.join(cmd)}")
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        print("STDOUT:")
        print(result.stdout)
        print("\nSTDERR:")
        print(result.stderr)
        print(f"\nReturn code: {result.returncode}")
        
        if result.returncode == 0:
            print("✅ Restore command completed successfully")
            
            # Verify restore
            print("\n🔍 Verifying restore...")
            final_count = get_user_count()
            print(f"Final user count: {final_count}")
            
            # Check if test user was removed
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM users WHERE username = 'restore_test_user_simple'")
            test_user_exists = cursor.fetchone()[0]
            cursor.close()
            conn.close()
            
            if test_user_exists == 0:
                print("✅ Test user was correctly removed by restore")
            else:
                print("❌ Test user still exists after restore")
            
            return test_user_exists == 0
            
        else:
            print("❌ Restore command failed")
            return False
            
    except Exception as e:
        print(f"❌ Error running restore: {e}")
        return False

if __name__ == "__main__":
    success = test_restore_with_existing_backup()
    if success:
        print("\n🎉 Restore test PASSED!")
    else:
        print("\n⚠️  Restore test FAILED!")
    sys.exit(0 if success else 1)
