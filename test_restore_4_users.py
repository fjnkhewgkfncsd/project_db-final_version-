#!/usr/bin/env python3
"""
Script to restore and test the 4-user backup file
"""
import psycopg2
import subprocess
import sys
import os
from datetime import datetime

# Database connection details
DB_CONFIG = {
    'host': 'localhost',
    'port': '5432',
    'database': 'ecommerce_db',
    'user': 'postgres',
    'password': 'hengmengly123'
}

BACKUP_FILE = 'backups/ecommerce_backup_2025-07-04_01-48-21.sql'

def get_db_connection():
    """Get database connection"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        print(f"❌ Error connecting to database: {e}")
        return None

def count_users():
    """Count users in the database"""
    conn = get_db_connection()
    if not conn:
        return 0
    
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users")
        count = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        return count
    except Exception as e:
        print(f"❌ Error counting users: {e}")
        return 0

def list_users():
    """List all users in the database"""
    conn = get_db_connection()
    if not conn:
        return []
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT username, email, role, first_name, last_name, is_active 
            FROM users 
            ORDER BY username
        """)
        users = cursor.fetchall()
        cursor.close()
        conn.close()
        return users
    except Exception as e:
        print(f"❌ Error listing users: {e}")
        return []

def truncate_all_tables():
    """Truncate all tables to avoid constraint conflicts"""
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        
        # Disable foreign key checks
        cursor.execute("SET session_replication_role = replica;")
        
        # Get all table names
        cursor.execute("""
            SELECT tablename FROM pg_tables 
            WHERE schemaname = 'public' 
            AND tablename NOT LIKE 'pg_%'
        """)
        tables = [row[0] for row in cursor.fetchall()]
        
        print("🗑️  Truncating all tables...")
        for table in tables:
            try:
                cursor.execute(f"TRUNCATE TABLE {table} RESTART IDENTITY CASCADE;")
                print(f"   ✅ Truncated {table}")
            except Exception as e:
                print(f"   ⚠️  Warning truncating {table}: {e}")
        
        # Re-enable foreign key checks
        cursor.execute("SET session_replication_role = DEFAULT;")
        conn.commit()
        cursor.close()
        conn.close()
        print("✅ All tables truncated successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error truncating tables: {e}")
        return False

def restore_backup():
    """Restore the backup file using psql"""
    if not os.path.exists(BACKUP_FILE):
        print(f"❌ Backup file not found: {BACKUP_FILE}")
        return False
    
    try:
        print(f"📂 Restoring from: {BACKUP_FILE}")
        
        # Build psql command
        cmd = [
            'psql',
            f"-h{DB_CONFIG['host']}",
            f"-p{DB_CONFIG['port']}",
            f"-U{DB_CONFIG['user']}",
            f"-d{DB_CONFIG['database']}",
            '-f', BACKUP_FILE,
            '-q'  # Quiet mode
        ]
        
        # Set environment variable for password
        env = os.environ.copy()
        env['PGPASSWORD'] = DB_CONFIG['password']
        
        # Run psql command
        result = subprocess.run(cmd, env=env, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Backup restored successfully")
            if result.stderr:
                print(f"ℹ️  Restore messages: {result.stderr[:200]}...")
            return True
        else:
            print(f"❌ Error restoring backup (return code: {result.returncode})")
            if result.stdout:
                print(f"STDOUT: {result.stdout[:500]}...")
            if result.stderr:
                print(f"STDERR: {result.stderr[:500]}...")
            return False
            
    except Exception as e:
        print(f"❌ Error during restore: {e}")
        return False

def verify_expected_users():
    """Verify the expected 4 users are present"""
    expected_users = {
        'admin': ('admin@example.com', 'admin'),
        'staff1': ('staff@example.com', 'staff'),
        'customer1': ('customer@example.com', 'customer'),
        'ilyghb': ('leka@example.com', 'customer')
    }
    
    users = list_users()
    found_users = {}
    
    for user in users:
        username, email, role, first_name, last_name, is_active = user
        found_users[username] = (email, role)
    
    print("🔍 Verifying expected users:")
    all_found = True
    
    for username, (expected_email, expected_role) in expected_users.items():
        if username in found_users:
            actual_email, actual_role = found_users[username]
            if actual_email == expected_email and actual_role == expected_role:
                print(f"   ✅ {username}: {actual_email} ({actual_role})")
            else:
                print(f"   ❌ {username}: Expected {expected_email} ({expected_role}), got {actual_email} ({actual_role})")
                all_found = False
        else:
            print(f"   ❌ {username}: NOT FOUND")
            all_found = False
    
    # Check for unexpected users
    for username in found_users:
        if username not in expected_users:
            email, role = found_users[username]
            print(f"   ⚠️  Unexpected user: {username} ({email}, {role})")
    
    return all_found

def main():
    print("🧪 4-User Backup Restore Test")
    print("=" * 60)
    print(f"Backup file: {BACKUP_FILE}")
    print(f"Database: {DB_CONFIG['database']} @ {DB_CONFIG['host']}:{DB_CONFIG['port']}")
    print()
    
    # Check if backup file exists
    if not os.path.exists(BACKUP_FILE):
        print(f"❌ Backup file not found: {BACKUP_FILE}")
        return
    
    # Check initial state
    print("📊 Initial database state:")
    initial_count = count_users()
    print(f"   Users before restore: {initial_count}")
    
    if initial_count > 0:
        print("   Current users:")
        users = list_users()
        for user in users:
            username, email, role, first_name, last_name, is_active = user
            status = "✅" if is_active else "❌"
            print(f"     {status} {username} ({role}) - {email}")
    
    print()
    
    # Truncate tables
    if not truncate_all_tables():
        print("❌ Failed to truncate tables. Aborting.")
        return
    
    print()
    
    # Restore backup
    print("🔄 Starting restore process...")
    if not restore_backup():
        print("❌ Restore failed. Aborting.")
        return
    
    print()
    
    # Verify restore
    print("✅ Verifying restore results:")
    final_count = count_users()
    print(f"   Users after restore: {final_count}")
    
    if final_count > 0:
        print("   Restored users:")
        users = list_users()
        for user in users:
            username, email, role, first_name, last_name, is_active = user
            status = "✅" if is_active else "❌"
            print(f"     {status} {username} ({role}) - {email} - {first_name} {last_name}")
    
    print()
    
    # Detailed verification
    all_users_correct = verify_expected_users()
    
    print()
    
    # Summary
    if final_count == 4 and all_users_correct:
        print("🎉 SUCCESS: All 4 users restored correctly!")
        print("✅ Restore process verified working with small dataset")
    elif final_count == 4:
        print("⚠️  PARTIAL SUCCESS: 4 users restored but some details don't match")
    else:
        print(f"❌ FAILURE: Expected 4 users, but got {final_count}")
    
    print(f"\n🕒 Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
