#!/usr/bin/env python3
"""
Final comprehensive restore functionality test
This demonstrates the complete restore process with a working backup
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

def get_database_stats():
    """Get comprehensive database statistics"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        stats = {}
        
        # Get table counts
        tables = ['users', 'products', 'orders', 'categories']
        for table in tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                stats[table] = cursor.fetchone()[0]
            except:
                stats[table] = "N/A"
        
        # Get some sample users
        try:
            cursor.execute("SELECT username, email FROM users LIMIT 3")
            stats['sample_users'] = cursor.fetchall()
        except:
            stats['sample_users'] = []
        
        cursor.close()
        conn.close()
        return stats
        
    except Exception as e:
        print(f"Error getting database stats: {e}")
        return None

def add_test_data():
    """Add test user and order to modify database state"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Add test user
        cursor.execute("""
            INSERT INTO users (username, email, password_hash, first_name, last_name)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING user_id
        """, (
            'final_test_user',
            'final_test@example.com',
            '$2b$10$example_hash',
            'Final',
            'Test'
        ))
        
        user_id = cursor.fetchone()[0]
        
        # Add test order (if possible)
        try:
            cursor.execute("""
                INSERT INTO orders (user_id, total_amount, status)
                VALUES (%s, %s, %s)
                RETURNING order_id
            """, (user_id, 99.99, 'pending'))
            order_id = cursor.fetchone()[0]
        except:
            order_id = None
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print(f"✅ Added test user: {user_id}")
        if order_id:
            print(f"✅ Added test order: {order_id}")
        
        return user_id, order_id
        
    except Exception as e:
        print(f"❌ Error adding test data: {e}")
        return None, None

def test_comprehensive_restore():
    """Run comprehensive restore test"""
    print("🧪 COMPREHENSIVE RESTORE FUNCTIONALITY TEST")
    print("=" * 60)
    
    # Step 1: Show current database state
    print("\n📊 Step 1: Getting initial database state...")
    initial_stats = get_database_stats()
    if not initial_stats:
        print("❌ Failed to get initial state")
        return False
    
    print("Initial database state:")
    for key, value in initial_stats.items():
        if key == 'sample_users':
            print(f"  Sample users: {len(value)} found")
            for user in value:
                print(f"    - {user[0]} ({user[1]})")
        else:
            print(f"  {key}: {value}")
    
    # Step 2: Create backup
    print("\n📦 Step 2: Creating fresh backup...")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"backups/final_test_backup_{timestamp}.sql"
    
    try:
        cmd = [
            'pg_dump',
            '--host=localhost',
            '--port=5432',
            '--username=postgres',
            '--no-password',
            '--verbose',
            '--clean',
            '--if-exists',
            '--format=plain',
            f'--file={backup_file}',
            'ecommerce_db'
        ]
        
        env = os.environ.copy()
        env['PGPASSWORD'] = 'hengmengly123'
        
        result = subprocess.run(cmd, env=env, capture_output=True, text=True)
        
        if result.returncode == 0:
            size = os.path.getsize(backup_file) / 1024 / 1024
            print(f"✅ Created backup: {backup_file} ({size:.2f} MB)")
        else:
            print(f"❌ Backup failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error creating backup: {e}")
        return False
    
    # Step 3: Modify database
    print("\n✏️  Step 3: Modifying database state...")
    test_user_id, test_order_id = add_test_data()
    if not test_user_id:
        return False
    
    # Show modified state
    modified_stats = get_database_stats()
    print("Modified database state:")
    for key, value in modified_stats.items():
        if key != 'sample_users':
            change = ""
            if key in initial_stats and initial_stats[key] != "N/A":
                diff = value - initial_stats[key] if isinstance(value, int) else 0
                if diff > 0:
                    change = f" (+{diff})"
            print(f"  {key}: {value}{change}")
    
    # Step 4: Test restore
    print(f"\n🔄 Step 4: Testing restore from backup...")
    try:
        cmd = ['python', 'db/restore.py', backup_file, '--force']
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Restore completed successfully")
            
            # Extract key info from restore output
            lines = result.stdout.split('\n')
            for line in lines:
                if 'Restore completed in' in line:
                    print(f"  Duration: {line.split('Restore completed in')[1].strip()}")
                elif 'Verification passed:' in line and 'SELECT COUNT' in line:
                    print(f"  Verified: {line.split('Verification passed:')[1].strip()}")
            
        else:
            print("❌ Restore failed")
            print("Error:", result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Error running restore: {e}")
        return False
    
    # Step 5: Verify restore
    print("\n🔍 Step 5: Verifying restore results...")
    final_stats = get_database_stats()
    
    # Check if test user was removed
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users WHERE username = 'final_test_user'")
    test_user_exists = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    
    print("Final database state:")
    for key, value in final_stats.items():
        if key == 'sample_users':
            print(f"  Sample users: {len(value)} found")
            for user in value:
                print(f"    - {user[0]} ({user[1]})")
        else:
            # Compare with initial state
            match = ""
            if key in initial_stats and initial_stats[key] == value:
                match = " ✅"
            elif key in initial_stats:
                match = f" (was {initial_stats[key]})"
            print(f"  {key}: {value}{match}")
    
    # Verification results
    success = True
    if test_user_exists == 0:
        print("✅ Test user correctly removed by restore")
    else:
        print("❌ Test user still exists after restore")
        success = False
    
    # Compare counts with initial state
    for key in ['users', 'products', 'orders']:
        if key in initial_stats and key in final_stats:
            if initial_stats[key] == final_stats[key]:
                print(f"✅ {key} count correctly restored")
            else:
                print(f"❌ {key} count mismatch: expected {initial_stats[key]}, got {final_stats[key]}")
                success = False
    
    # Step 6: Cleanup
    print(f"\n🧹 Step 6: Cleaning up test backup...")
    try:
        os.remove(backup_file)
        print(f"✅ Removed {backup_file}")
    except Exception as e:
        print(f"⚠️  Could not remove backup: {e}")
    
    return success

def main():
    """Main test function"""
    success = test_comprehensive_restore()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 COMPREHENSIVE RESTORE TEST PASSED!")
        print("✅ All restore functionality is working correctly")
        print("✅ Database state properly restored")
        print("✅ Test data correctly removed")
        print("✅ Backup and restore cycle completed successfully")
    else:
        print("⚠️  COMPREHENSIVE RESTORE TEST FAILED!")
        print("❌ Some aspects of restore functionality need attention")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
