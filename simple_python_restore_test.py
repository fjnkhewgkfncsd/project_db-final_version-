#!/usr/bin/env python3
"""
Simple test to restore the specific backup with 10,003 users using Python directly
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
except ImportError as e:
    print(f"Error importing required modules: {e}")
    print("Please install: pip install psycopg2-binary python-dotenv")
    sys.exit(1)

# Load environment variables
env_path = os.path.join('backend', '.env')
load_dotenv(env_path)

db_config = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'password'),
    'database': os.getenv('DB_NAME', 'ecommerce_db')
}

def get_user_count():
    """Get current user count"""
    try:
        conn = psycopg2.connect(
            host=db_config['host'],
            port=db_config['port'],
            user=db_config['user'],
            password=db_config['password'],
            database=db_config['database']
        )
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users;")
        count = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        return count
    except Exception as e:
        print(f"Error getting user count: {e}")
        return None

def simple_restore_test():
    """Simple restore test"""
    print("🧪 SIMPLE RESTORE TEST")
    print("=" * 30)
    
    # The backup file that contains 10,003 users
    backup_file = "ecommerce_backup_2025-07-09_02-46-32.sql"
    backup_path = os.path.join('backups', backup_file)
    
    if not os.path.exists(backup_path):
        print(f"❌ Backup file not found: {backup_path}")
        return
    
    # Check current users
    print("\n1. Current user count:")
    current_count = get_user_count()
    print(f"   Users: {current_count}")
    
    # Try to use the Python restore script that exists in the db folder
    restore_script_path = os.path.join('db', 'restore.py')
    if os.path.exists(restore_script_path):
        print(f"\n2. Using Python restore script: {restore_script_path}")
        print(f"   Restoring: {backup_file}")
        
        try:
            # Run the restore script
            result = subprocess.run([
                sys.executable, restore_script_path, backup_file
            ], capture_output=True, text=True, cwd=os.getcwd())
            
            print(f"   Return code: {result.returncode}")
            
            if result.stdout:
                print("   STDOUT:")
                for line in result.stdout.split('\n')[-10:]:  # Last 10 lines
                    if line.strip():
                        print(f"     {line}")
            
            if result.stderr:
                print("   STDERR:")
                for line in result.stderr.split('\n')[-10:]:  # Last 10 lines
                    if line.strip():
                        print(f"     {line}")
            
            # Check user count after restore
            print("\n3. User count after restore:")
            new_count = get_user_count()
            print(f"   Users: {new_count}")
            
            if new_count == 10003:
                print("✅ SUCCESS! Restored 10,003 users correctly")
            elif new_count == current_count:
                print("⚠️  No change in user count - restore may not have worked")
            else:
                print(f"⚠️  Unexpected user count: {new_count}")
                
        except Exception as e:
            print(f"   Error running restore script: {e}")
    else:
        print(f"❌ Restore script not found: {restore_script_path}")

if __name__ == "__main__":
    simple_restore_test()
