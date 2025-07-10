#!/usr/bin/env python3
"""
Diagnose restore router issue - why 10,002 users instead of expected count
"""

import requests
import json
import time

# Configuration
BACKEND_URL = "http://localhost:3001/api"
BACKUP_FILENAME = "ecommerce_backup_2025-07-08_21-55-18.sql"  # Should have 1 user according to analysis

# Demo credentials (admin user)
ADMIN_CREDENTIALS = {
    "email": "admin@example.com",
    "password": "admin123"
}

def get_token():
    """Get authentication token"""
    response = requests.post(f"{BACKEND_URL}/users/login", json=ADMIN_CREDENTIALS)
    if response.status_code == 200:
        data = response.json()
        return data.get('data', {}).get('token') or data.get('token')
    return None

def check_current_users(token):
    """Check current user count in database"""
    headers = {"Authorization": f"Bearer {token}"}
    query_payload = {"sql": "SELECT COUNT(*) as count FROM users"}
    
    response = requests.post(f"{BACKEND_URL}/database/query", 
                           headers=headers, json=query_payload)
    
    if response.status_code == 200:
        data = response.json()
        return data['data']['rows'][0]['count']
    return None

def get_user_sample(token, limit=10):
    """Get sample of users to see what's in the database"""
    headers = {"Authorization": f"Bearer {token}"}
    query_payload = {"sql": f"SELECT user_id, username, email, created_at FROM users ORDER BY user_id LIMIT {limit}"}
    
    response = requests.post(f"{BACKEND_URL}/database/query", 
                           headers=headers, json=query_payload)
    
    if response.status_code == 200:
        data = response.json()
        return data['data']['rows']
    return []

def test_restore_behavior(token):
    """Test what happens during restore"""
    print(f"🔄 Testing restore with: {BACKUP_FILENAME}")
    
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"filename": BACKUP_FILENAME, "force": True}
    
    response = requests.post(f"{BACKEND_URL}/database/restore", 
                           headers=headers, json=payload)
    
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print(f"❌ Restore failed: {response.status_code} - {response.text}")
        return None

def main():
    """Main diagnostic function"""
    print("=" * 80)
    print("🔍 DIAGNOSING RESTORE ROUTER USER COUNT ISSUE")
    print("=" * 80)
    
    # Step 1: Login
    token = get_token()
    if not token:
        print("❌ Failed to authenticate")
        return
    
    print("✅ Authenticated successfully")
    
    # Step 2: Check users before restore
    print("\n📊 BEFORE RESTORE:")
    user_count_before = check_current_users(token)
    print(f"   Users in database: {user_count_before}")
    
    # Sample of current users
    sample_users = get_user_sample(token, 5)
    if sample_users:
        print("   Sample users:")
        for user in sample_users:
            print(f"     - ID: {user['user_id']}, Username: {user['username']}, Email: {user['email']}")
    
    # Step 3: Perform restore
    print(f"\n🔄 PERFORMING RESTORE:")
    print(f"   Backup file: {BACKUP_FILENAME}")
    print(f"   Expected users (from analysis): 1")
    
    restore_result = test_restore_behavior(token)
    if not restore_result:
        return
    
    print(f"   ✅ Restore completed in {restore_result['data']['execution_time_ms']}ms")
    print(f"   📁 File size: {restore_result['data']['file_size']}")
    
    # Step 4: Check users after restore
    time.sleep(2)  # Wait for DB to settle
    print(f"\n📊 AFTER RESTORE:")
    user_count_after = check_current_users(token)
    print(f"   Users in database: {user_count_after}")
    
    # Step 5: Analysis
    print(f"\n🔍 ANALYSIS:")
    print(f"   Users before restore: {user_count_before}")
    print(f"   Users after restore:  {user_count_after}")
    print(f"   Expected users:       1")
    difference = int(user_count_after) - int(user_count_before) if user_count_before else 'N/A'
    print(f"   Difference:           {difference}")
    
    if user_count_after == user_count_before:
        print("   🤔 ISSUE: No change in user count - backup contains same data as current DB")
    elif int(user_count_after) > 1000:
        print("   🤔 ISSUE: Large user count suggests backup contains more data than analyzed")
    elif int(user_count_after) == 1:
        print("   ✅ SUCCESS: User count matches expected value")
    else:
        print(f"   ⚠️ UNEXPECTED: User count is {user_count_after}, expected 1")
    
    # Step 6: Check verification result from restore
    verification = restore_result['data'].get('verification', {})
    if verification.get('verified'):
        print(f"\n🔍 RESTORE VERIFICATION:")
        print(f"   Reported user count: {verification['users_count']}")
        print(f"   Actual user count:   {user_count_after}")
        if verification['users_count'] != user_count_after:
            print("   ❌ MISMATCH: Verification count doesn't match actual count!")
    
    # Step 7: Sample users after restore
    sample_users_after = get_user_sample(token, 10)
    if sample_users_after:
        print(f"\n👥 SAMPLE USERS AFTER RESTORE:")
        for user in sample_users_after:
            print(f"   - ID: {user['user_id']}, Username: {user['username']}, Email: {user['email']}, Created: {user['created_at']}")
    
    print("\n" + "=" * 80)
    print("🎯 CONCLUSION:")
    
    if int(user_count_after) == 10002:
        print("❌ CONFIRMED: Restore is adding 10,002 users instead of expected 1")
        print("💡 POSSIBLE CAUSES:")
        print("   1. Backup file actually contains 10,002 users (analysis script wrong)")
        print("   2. Database has existing data that's not being cleared")
        print("   3. Restore is appending instead of replacing")
        print("   4. Multiple restore operations are accumulating data")
    elif int(user_count_after) == int(user_count_before):
        print("✅ WORKING CORRECTLY: Backup contains same data as current database")
        print("💡 EXPLANATION: PostgreSQL restore with --clean handles duplicate data correctly")
    elif int(user_count_after) == 1:
        print("✅ SUCCESS: Restore is working correctly")
    else:
        print(f"⚠️ UNEXPECTED: Got {user_count_after} users, need further investigation")
    
    print("=" * 80)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n💥 ERROR: {e}")
        import traceback
        traceback.print_exc()
