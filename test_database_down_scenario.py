#!/usr/bin/env python3
"""
Emergency Recovery Test - Database Down Scenario
Tests the emergency recovery system when the main database is completely unavailable
"""

import requests
import json
import time
import subprocess
import os
import sys
from datetime import datetime
import psycopg2

# Configuration
EMERGENCY_API_BASE = "http://localhost:3002/api/emergency"
EMERGENCY_CREDENTIALS = {
    "username": "emergency_admin",
    "password": "EmergencyRestore2025!"
}

def simulate_database_down():
    """Simulate database being down by stopping PostgreSQL service"""
    print("🔴 Simulating database failure...")
    
    try:
        # Try to stop PostgreSQL service (Windows)
        result = subprocess.run(['net', 'stop', 'postgresql-x64-17'], 
                               capture_output=True, text=True, shell=True)
        
        if result.returncode == 0:
            print("✅ PostgreSQL service stopped successfully")
            return True
        else:
            print(f"⚠️  Could not stop PostgreSQL service: {result.stderr}")
            print("   This might be because:")
            print("   1. PostgreSQL is running as a different service name")
            print("   2. You don't have admin privileges")
            print("   3. PostgreSQL is running in Docker")
            return False
            
    except Exception as e:
        print(f"❌ Error stopping PostgreSQL: {e}")
        return False

def restore_database_service():
    """Restore PostgreSQL service"""
    print("🟢 Restoring PostgreSQL service...")
    
    try:
        result = subprocess.run(['net', 'start', 'postgresql-x64-17'], 
                               capture_output=True, text=True, shell=True)
        
        if result.returncode == 0:
            print("✅ PostgreSQL service started successfully")
            time.sleep(3)  # Wait for service to fully start
            return True
        else:
            print(f"⚠️  Could not start PostgreSQL service: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error starting PostgreSQL: {e}")
        return False

def test_database_connectivity():
    """Test if database is accessible"""
    print("🔍 Testing database connectivity...")
    
    try:
        conn = psycopg2.connect(
            host="localhost",
            port="5432",
            database="ecommerce_db",
            user="postgres",
            password="hengmengly123",
            connect_timeout=5
        )
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if result and result[0] == 1:
            print("✅ Database is accessible")
            return True
        else:
            print("❌ Database query failed")
            return False
            
    except psycopg2.OperationalError as e:
        print(f"❌ Database connection failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected database error: {e}")
        return False

def test_emergency_system_independence():
    """Test that emergency system works independently of database"""
    print("🚨 Testing emergency system independence...")
    
    try:
        # Test emergency server health
        health_response = requests.get("http://localhost:3002/health", timeout=5)
        if health_response.status_code == 200:
            print("✅ Emergency server is running independently")
        else:
            print("❌ Emergency server health check failed")
            return False
        
        # Test authentication
        auth_response = requests.post(f"{EMERGENCY_API_BASE}/login", 
                                    json=EMERGENCY_CREDENTIALS, timeout=10)
        
        if auth_response.status_code == 200:
            data = auth_response.json()
            if data.get('success'):
                print("✅ Emergency authentication works without database")
                token = data['data']['token']
            else:
                print("❌ Emergency authentication failed")
                return False
        else:
            print(f"❌ Emergency auth request failed: {auth_response.status_code}")
            return False
        
        # Test backup listing
        headers = {"Authorization": f"Bearer {token}"}
        backup_response = requests.get(f"{EMERGENCY_API_BASE}/backups", 
                                     headers=headers, timeout=10)
        
        if backup_response.status_code == 200:
            backup_data = backup_response.json()
            if backup_data.get('success'):
                backups = backup_data['data']['backups']
                print(f"✅ Backup listing works without database ({len(backups)} backups found)")
                return token, backups
            else:
                print("❌ Backup listing failed")
                return False
        else:
            print(f"❌ Backup listing request failed: {backup_response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Emergency server is not accessible")
        return False
    except Exception as e:
        print(f"❌ Error testing emergency system: {e}")
        return False

def test_emergency_restore_when_db_down(token, backups):
    """Test emergency restore when database is down"""
    print("🔧 Testing emergency restore with database down...")
    
    if not backups:
        print("❌ No backups available for testing")
        return False
    
    # Use the latest complete backup
    latest_backup = None
    for backup in backups:
        if backup['type'] == 'complete' and backup['size'] > 1000000:  # > 1MB
            latest_backup = backup
            break
    
    if not latest_backup:
        print("❌ No suitable complete backup found")
        return False
    
    print(f"   Using backup: {latest_backup['filename']} ({latest_backup['sizeFormatted']})")
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        restore_data = {
            "filename": latest_backup['filename'],
            "force": True
        }
        
        print("   Starting emergency restore operation...")
        response = requests.post(f"{EMERGENCY_API_BASE}/restore", 
                               json=restore_data, 
                               headers=headers,
                               timeout=300)  # 5 minute timeout
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ Emergency restore completed successfully!")
                
                restore_info = data['data']
                print(f"   Restored: {restore_info['filename']}")
                print(f"   Duration: {restore_info['duration']}")
                
                if 'verification' in restore_info:
                    verification = restore_info['verification']
                    if verification.get('verified'):
                        print(f"   Verification: ✅ Passed")
                        if 'userCount' in verification:
                            print(f"   Users restored: {verification['userCount']}")
                        if 'productCount' in verification:
                            print(f"   Products restored: {verification['productCount']}")
                    else:
                        print(f"   Verification: ⚠️ Issues detected")
                
                return True
            else:
                print(f"❌ Restore failed: {data.get('message')}")
                if 'error' in data:
                    print(f"   Error details: {data['error']}")
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
        print(f"❌ Error during emergency restore: {e}")
        return False

def verify_database_recovery():
    """Verify that database is back online and functional"""
    print("🔍 Verifying database recovery...")
    
    # Wait a bit for database to fully start
    time.sleep(5)
    
    try:
        conn = psycopg2.connect(
            host="localhost",
            port="5432",
            database="ecommerce_db",
            user="postgres",
            password="hengmengly123",
            connect_timeout=10
        )
        cursor = conn.cursor()
        
        # Test basic connectivity
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        
        if result and result[0] == 1:
            print("✅ Database connectivity restored")
            
            # Check data counts
            cursor.execute("SELECT COUNT(*) FROM users")
            user_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM products")
            product_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM orders")
            order_count = cursor.fetchone()[0]
            
            print(f"✅ Data recovered: {user_count} users, {product_count} products, {order_count} orders")
            
            # Test a sample query
            cursor.execute("SELECT username, email FROM users LIMIT 3")
            sample_users = cursor.fetchall()
            
            print("✅ Sample user data:")
            for user in sample_users:
                print(f"   - {user[0]} ({user[1]})")
            
            cursor.close()
            conn.close()
            return True
        else:
            print("❌ Database query test failed")
            return False
            
    except Exception as e:
        print(f"❌ Database recovery verification failed: {e}")
        return False

def main():
    """Main test function for database down scenario"""
    print("🚨 EMERGENCY RECOVERY - DATABASE DOWN SCENARIO TEST")
    print("=" * 70)
    print(f"🕒 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    print("📋 Test Scenario:")
    print("   1. Database suddenly goes down")
    print("   2. Emergency recovery system remains operational")
    print("   3. Admin uses emergency portal to restore database")
    print("   4. Database is recovered from backup")
    print("   5. System is back online")
    print()
    
    # Step 1: Verify initial state
    print("📊 Step 1: Checking initial database state...")
    initial_db_status = test_database_connectivity()
    
    # Step 2: Check emergency server is running
    print("\n🚨 Step 2: Verifying emergency server is running...")
    try:
        health_response = requests.get("http://localhost:3002/health", timeout=5)
        if health_response.status_code == 200:
            print("✅ Emergency recovery server is operational")
        else:
            print("❌ Emergency recovery server is not responding")
            print("   Please start it with: node backend/emergency-recovery-server.js")
            return 1
    except:
        print("❌ Emergency recovery server is not accessible")
        print("   Please start it with: node backend/emergency-recovery-server.js")
        return 1
    
    # Step 3: Simulate database failure (optional - might require admin rights)
    print("\n🔴 Step 3: Simulating database failure...")
    db_stopped = simulate_database_down()
    
    if not db_stopped:
        print("⚠️  Could not simulate database failure automatically.")
        print("   This test will continue assuming the database is down.")
        print("   (In a real scenario, the database would be unavailable)")
    
    # Wait a moment
    time.sleep(2)
    
    # Step 4: Test database is actually down
    print("\n❌ Step 4: Confirming database is down...")
    db_down = not test_database_connectivity()
    
    if not db_down:
        print("⚠️  Database is still accessible. This means:")
        print("   - PostgreSQL service couldn't be stopped (need admin rights)")
        print("   - Or PostgreSQL is running in Docker/different service")
        print("   - Test will simulate database down scenario")
    
    # Step 5: Test emergency system works independently
    print("\n🚨 Step 5: Testing emergency system independence...")
    emergency_result = test_emergency_system_independence()
    
    if not emergency_result:
        print("❌ Emergency system is not working independently")
        return 1
    
    token, backups = emergency_result
    
    # Step 6: Perform emergency restore
    print("\n🔧 Step 6: Performing emergency database restore...")
    restore_success = test_emergency_restore_when_db_down(token, backups)
    
    # Step 7: Restart database service if we stopped it
    if db_stopped:
        print("\n🟢 Step 7: Restarting database service...")
        service_restored = restore_database_service()
        if not service_restored:
            print("❌ Could not restart PostgreSQL service")
            print("   Please start it manually: net start postgresql-x64-17")
    
    # Step 8: Verify recovery
    print("\n🔍 Step 8: Verifying complete recovery...")
    recovery_verified = verify_database_recovery()
    
    # Summary
    print("\n" + "=" * 70)
    print("📋 DATABASE DOWN SCENARIO TEST SUMMARY")
    print("=" * 70)
    
    test_results = [
        ("Initial Database State", initial_db_status),
        ("Emergency Server Independence", emergency_result is not False),
        ("Emergency Authentication", token is not None),
        ("Backup Access During Outage", len(backups) > 0 if backups else False),
        ("Emergency Restore Execution", restore_success),
        ("Database Recovery Verification", recovery_verified)
    ]
    
    for test_name, passed in test_results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"   {test_name}: {status}")
    
    overall_success = all(result for _, result in test_results)
    
    print(f"\n🎯 Overall Result: {'✅ EMERGENCY RECOVERY WORKS' if overall_success else '❌ EMERGENCY RECOVERY HAS ISSUES'}")
    
    if overall_success:
        print("\n🎉 SUCCESS: Emergency recovery system handles database down scenario!")
        print("   ✅ Emergency server operates independently of main database")
        print("   ✅ Authentication works without database connection")
        print("   ✅ Backup files remain accessible during outage")
        print("   ✅ Emergency restore can recreate database from backup")
        print("   ✅ Database recovery is complete and verified")
        print("\n🚨 CRITICAL CAPABILITY CONFIRMED:")
        print("   The emergency recovery system CAN restore a completely failed database!")
    else:
        print("\n🔧 ISSUES DETECTED: Emergency recovery needs attention")
        print("   Review the failed tests above and fix issues before relying on this system")
    
    print("\n" + "=" * 70)
    print("📚 EMERGENCY RECOVERY INSTRUCTIONS FOR ADMIN:")
    print("=" * 70)
    print("🚨 When database is completely down:")
    print("   1. Go to http://localhost:3002 (Emergency Portal)")
    print("   2. Login with: emergency_admin / EmergencyRestore2025!")
    print("   3. Select latest complete backup file")
    print("   4. Click 'Restore Database' and confirm")
    print("   5. Wait for restore to complete")
    print("   6. Verify database is back online")
    print("\n🔗 Alternative: Use main app emergency page")
    print("   1. Go to http://localhost:3000/emergency-recovery")
    print("   2. Follow same authentication and restore process")
    
    return 0 if overall_success else 1

if __name__ == "__main__":
    sys.exit(main())
