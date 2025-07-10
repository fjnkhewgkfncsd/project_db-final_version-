#!/usr/bin/env python3
"""
Emergency Database Restore Function Test
Tests the actual restore functionality to ensure it works properly
"""

import requests
import json
import time
import subprocess
import os
import sys
from datetime import datetime
import psycopg2
from psycopg2 import sql

# Configuration
EMERGENCY_API_BASE = "http://localhost:3002/api/emergency"
EMERGENCY_CREDENTIALS = {
    "username": "emergency_admin",
    "password": "EmergencyRestore2025!"
}

# Database configuration for testing
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'user': 'postgres',
    'password': 'hengmengly123',  # Updated to match .env
    'database': 'ecommerce_db'
}

def authenticate_emergency():
    """Authenticate with emergency recovery system"""
    print("🔐 Authenticating with emergency recovery system...")
    
    try:
        response = requests.post(f"{EMERGENCY_API_BASE}/login", json=EMERGENCY_CREDENTIALS)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ Emergency authentication successful")
                return data['data']['token']
            else:
                print(f"❌ Authentication failed: {data.get('message')}")
                return None
        else:
            print(f"❌ Authentication request failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Authentication error: {e}")
        return None

def get_available_backups(token):
    """Get list of available backup files"""
    print("📁 Getting available backup files...")
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{EMERGENCY_API_BASE}/backups", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                backups = data['data']['backups']
                print(f"✅ Found {len(backups)} backup files")
                
                if backups:
                    print("   Available backups:")
                    for i, backup in enumerate(backups[:5], 1):
                        print(f"   {i}. {backup['filename']} ({backup['sizeFormatted']}) - {backup['type']}")
                    
                    return backups
                else:
                    print("❌ No backup files found")
                    return []
            else:
                print(f"❌ Failed to get backups: {data.get('message')}")
                return []
        else:
            print(f"❌ Backup request failed: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ Error getting backups: {e}")
        return []

def check_database_status():
    """Check if database is accessible"""
    print("🔍 Checking database connectivity...")
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Test basic connectivity
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        
        if result and result[0] == 1:
            print("✅ Database is accessible")
            
            # Get some table counts for comparison
            cursor.execute("SELECT COUNT(*) FROM users")
            user_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM products")
            product_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM orders")
            order_count = cursor.fetchone()[0]
            
            print(f"   Current data: {user_count} users, {product_count} products, {order_count} orders")
            
            cursor.close()
            conn.close()
            
            return {
                'accessible': True,
                'users': user_count,
                'products': product_count,
                'orders': order_count
            }
        else:
            print("❌ Database query failed")
            return {'accessible': False}
            
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return {'accessible': False, 'error': str(e)}

def create_test_backup():
    """Create a fresh backup for testing"""
    print("💾 Creating a test backup...")
    
    try:
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        backup_filename = f"test_backup_{timestamp}.sql"
        backup_path = os.path.join("backups", backup_filename)
        
        # Use pg_dump to create backup
        cmd = [
            'pg_dump',
            '-h', DB_CONFIG['host'],
            '-p', str(DB_CONFIG['port']),
            '-U', DB_CONFIG['user'],
            '-d', DB_CONFIG['database'],
            '--verbose',
            '--clean',
            '--if-exists',
            '--create',
            '-f', backup_path
        ]
        
        # Set environment variable for password
        env = os.environ.copy()
        env['PGPASSWORD'] = DB_CONFIG['password']
        
        result = subprocess.run(cmd, env=env, capture_output=True, text=True)
        
        if result.returncode == 0:
            # Check if file was created and has content
            if os.path.exists(backup_path):
                file_size = os.path.getsize(backup_path)
                size_mb = file_size / (1024 * 1024)
                print(f"✅ Test backup created: {backup_filename} ({size_mb:.2f} MB)")
                return backup_filename
            else:
                print("❌ Backup file was not created")
                return None
        else:
            print(f"❌ Backup failed: {result.stderr}")
            return None
            
    except Exception as e:
        print(f"❌ Error creating test backup: {e}")
        return None

def modify_test_data():
    """Modify some test data to verify restore works"""
    print("✏️ Modifying test data for restore verification...")
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Add a test user
        test_email = f"test_restore_{int(time.time())}@example.com"
        cursor.execute("""
            INSERT INTO users (id, email, first_name, last_name, password, role, created_at, updated_at)
            VALUES (gen_random_uuid(), %s, 'Test', 'Restore', 'test123', 'customer', NOW(), NOW())
        """, (test_email,))
        
        # Get the user count after modification
        cursor.execute("SELECT COUNT(*) FROM users")
        new_user_count = cursor.fetchone()[0]
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print(f"✅ Added test user: {test_email}")
        print(f"   New user count: {new_user_count}")
        
        return {'test_email': test_email, 'new_user_count': new_user_count}
        
    except Exception as e:
        print(f"❌ Error modifying test data: {e}")
        return None

def test_emergency_restore(token, backup_filename):
    """Test the actual emergency restore functionality"""
    print(f"🔧 Testing emergency restore with backup: {backup_filename}")
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        restore_data = {
            "filename": backup_filename,
            "force": True
        }
        
        print("   Starting restore operation...")
        response = requests.post(f"{EMERGENCY_API_BASE}/restore", 
                               json=restore_data, 
                               headers=headers,
                               timeout=300)  # 5 minute timeout
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ Emergency restore completed successfully!")
                
                restore_info = data['data']
                print(f"   Filename: {restore_info['filename']}")
                print(f"   Duration: {restore_info['duration']}")
                
                if 'verification' in restore_info:
                    verification = restore_info['verification']
                    if verification['verified']:
                        print(f"   Verification: ✅ Passed (Found {verification.get('userCount', 'N/A')} users)")
                    else:
                        print(f"   Verification: ⚠️ Failed - {verification.get('error', 'Unknown error')}")
                
                return True
            else:
                print(f"❌ Restore failed: {data.get('message')}")
                return False
        else:
            print(f"❌ Restore request failed: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error: {error_data.get('message', 'Unknown error')}")
            except:
                print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error during restore: {e}")
        return False

def verify_restore_results(original_state, modified_state):
    """Verify that the restore actually worked"""
    print("🔍 Verifying restore results...")
    
    try:
        current_state = check_database_status()
        
        if not current_state['accessible']:
            print("❌ Database is not accessible after restore")
            return False
        
        print("   Comparing data counts:")
        print(f"   Original users: {original_state['users']}")
        print(f"   After modification: {modified_state['new_user_count']}")
        print(f"   After restore: {current_state['users']}")
        
        # Check if data was restored to original state
        if current_state['users'] == original_state['users']:
            print("✅ User count restored to original state")
            
            # Check if test user was removed (indicating successful restore)
            conn = psycopg2.connect(**DB_CONFIG)
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM users WHERE email = %s", 
                          (modified_state['test_email'],))
            test_user_exists = cursor.fetchone()[0] > 0
            
            cursor.close()
            conn.close()
            
            if not test_user_exists:
                print("✅ Test user was removed (restore successful)")
                return True
            else:
                print("⚠️ Test user still exists (restore may not have worked completely)")
                return False
        else:
            print("❌ User count does not match original state")
            return False
            
    except Exception as e:
        print(f"❌ Error verifying restore: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 EMERGENCY DATABASE RESTORE FUNCTION TEST")
    print("=" * 60)
    print(f"🕒 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Check if emergency server is running
    try:
        health_response = requests.get("http://localhost:3002/health", timeout=5)
        if health_response.status_code != 200:
            print("❌ Emergency recovery server is not running")
            print("   Please start it with: node backend/emergency-recovery-server.js")
            return 1
    except:
        print("❌ Emergency recovery server is not accessible")
        print("   Please start it with: node backend/emergency-recovery-server.js")
        return 1
    
    print("✅ Emergency recovery server is running")
    
    # Step 1: Check initial database state
    print("\n📊 Step 1: Checking initial database state...")
    original_state = check_database_status()
    if not original_state['accessible']:
        print("❌ Database is not accessible. Cannot proceed with restore test.")
        return 1
    
    # Step 2: Authenticate with emergency system
    print("\n🔐 Step 2: Authenticating with emergency system...")
    token = authenticate_emergency()
    if not token:
        print("❌ Failed to authenticate with emergency system")
        return 1
    
    # Step 3: Create a test backup
    print("\n💾 Step 3: Creating test backup...")
    test_backup = create_test_backup()
    if not test_backup:
        print("❌ Failed to create test backup")
        return 1
    
    # Step 4: Modify test data
    print("\n✏️ Step 4: Modifying test data...")
    modified_state = modify_test_data()
    if not modified_state:
        print("❌ Failed to modify test data")
        return 1
    
    # Step 5: Get available backups (should include our test backup)
    print("\n📁 Step 5: Getting available backups...")
    backups = get_available_backups(token)
    if not backups:
        print("❌ No backups available for testing")
        return 1
    
    # Find our test backup
    test_backup_found = any(backup['filename'] == test_backup for backup in backups)
    if not test_backup_found:
        print(f"⚠️ Test backup {test_backup} not found in backup list, using latest backup")
        test_backup = backups[0]['filename']
    
    # Step 6: Test emergency restore
    print(f"\n🔧 Step 6: Testing emergency restore...")
    restore_success = test_emergency_restore(token, test_backup)
    if not restore_success:
        print("❌ Emergency restore failed")
        return 1
    
    # Step 7: Verify restore results
    print("\n🔍 Step 7: Verifying restore results...")
    verification_success = verify_restore_results(original_state, modified_state)
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 RESTORE FUNCTION TEST SUMMARY")
    print("=" * 60)
    
    test_results = [
        ("Database Connectivity", original_state['accessible']),
        ("Emergency Authentication", token is not None),
        ("Test Backup Creation", test_backup is not None),
        ("Test Data Modification", modified_state is not None),
        ("Backup Listing", len(backups) > 0),
        ("Emergency Restore Execution", restore_success),
        ("Restore Verification", verification_success)
    ]
    
    for test_name, passed in test_results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"   {test_name}: {status}")
    
    overall_success = all(result for _, result in test_results)
    
    print(f"\n🎯 Overall Result: {'✅ RESTORE FUNCTION WORKS PROPERLY' if overall_success else '❌ RESTORE FUNCTION HAS ISSUES'}")
    
    if overall_success:
        print("\n🎉 SUCCESS: Emergency restore function is working properly!")
        print("   • Authentication system works")
        print("   • Backup listing works")
        print("   • Restore operation executes successfully")
        print("   • Data is properly restored to previous state")
        print("   • Verification confirms restore accuracy")
        print("\n✅ The emergency recovery system is READY FOR PRODUCTION")
    else:
        print("\n🔧 ISSUES DETECTED: Emergency restore function needs attention")
        print("   Review the failed tests above and fix the issues before deployment")
    
    # Cleanup
    if test_backup and test_backup.startswith('test_backup_'):
        try:
            backup_path = os.path.join("backups", test_backup)
            if os.path.exists(backup_path):
                os.remove(backup_path)
                print(f"\n🗑️ Cleaned up test backup: {test_backup}")
        except:
            pass
    
    return 0 if overall_success else 1

if __name__ == "__main__":
    sys.exit(main())
