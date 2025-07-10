#!/usr/bin/env python3
"""
Quick test of database restore function with 10,003 users backup
"""

import requests
import time

# Configuration
BACKEND_URL = "http://localhost:3001"
ADMIN_EMAIL = "admin@example.com"
ADMIN_PASSWORD = "admin123"
TEST_BACKUP = "ecommerce_backup_2025-07-09_01-52-43.sql"  # Has 10,003 users

def quick_test():
    """Quick test of restore functionality"""
    print("🧪 QUICK DATABASE RESTORE TEST")
    print("="*50)
    print(f"Testing restore with backup: {TEST_BACKUP}")
    print("="*50)
    
    # Step 1: Login
    print("🔐 Logging in...")
    try:
        login_response = requests.post(f"{BACKEND_URL}/api/users/login", 
                                     json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
                                     timeout=10)
        
        if login_response.status_code == 200:
            token = login_response.json()['data']['token']
            print("✅ Login successful")
        else:
            print(f"❌ Login failed: {login_response.text}")
            return
            
    except Exception as e:
        print(f"❌ Login error: {e}")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Step 2: Check current user count
    print("\n📊 Checking current user count...")
    try:
        query_response = requests.post(f"{BACKEND_URL}/api/database/query", 
                                     json={"sql": "SELECT COUNT(*) as count FROM users"}, 
                                     headers=headers, timeout=10)
        
        if query_response.status_code == 200:
            current_count = query_response.json()['data']['rows'][0]['count']
            print(f"Current users: {current_count}")
        else:
            print(f"❌ Query failed: {query_response.text}")
            current_count = "unknown"
            
    except Exception as e:
        print(f"❌ Query error: {e}")
        current_count = "unknown"
    
    # Step 3: Test restore
    print(f"\n🔄 Testing restore with {TEST_BACKUP}...")
    try:
        start_time = time.time()
        
        restore_response = requests.post(f"{BACKEND_URL}/api/database/restore", 
                                       json={"filename": TEST_BACKUP, "force": True}, 
                                       headers=headers, timeout=120)
        
        duration = time.time() - start_time
        
        if restore_response.status_code == 200:
            restore_data = restore_response.json()['data']
            verification = restore_data.get('verification', {})
            
            print(f"✅ Restore successful in {duration:.2f}s")
            print(f"📁 File size: {restore_data['file_size']}")
            print(f"⏱️ Execution time: {restore_data['execution_time_ms']}ms")
            
            if verification.get('verified'):
                users_count = verification.get('users_count', 'unknown')
                print(f"👥 Users restored: {users_count}")
                
                if str(users_count) == "10003":
                    print("✅ Successfully restored 10,003 users!")
                    print("✅ Database restore function is working correctly")
                else:
                    print(f"⚠️ Expected 10,003 users, got {users_count}")
            else:
                print("⚠️ Verification failed")
                
        else:
            print(f"❌ Restore failed: {restore_response.text}")
            
    except Exception as e:
        print(f"❌ Restore error: {e}")
    
    # Step 4: Verify final count
    print("\n🔍 Verifying final user count...")
    try:
        query_response = requests.post(f"{BACKEND_URL}/api/database/query", 
                                     json={"sql": "SELECT COUNT(*) as count FROM users"}, 
                                     headers=headers, timeout=10)
        
        if query_response.status_code == 200:
            final_count = query_response.json()['data']['rows'][0]['count']
            print(f"Final users: {final_count}")
            
            if str(final_count) == "10003":
                print("✅ VERIFICATION PASSED: 10,003 users confirmed in database")
            else:
                print(f"⚠️ Unexpected count: {final_count}")
        else:
            print(f"❌ Final query failed: {query_response.text}")
            
    except Exception as e:
        print(f"❌ Final query error: {e}")
    
    print(f"\n{'='*50}")
    print("🎯 TEST COMPLETE")
    print("="*50)

if __name__ == "__main__":
    quick_test()
