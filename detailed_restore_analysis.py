#!/usr/bin/env python3
"""
Detailed analysis of restore behavior differences
"""

import requests
import json
import time

# Configuration
MAIN_SYSTEM_URL = "http://localhost:3001/api"
BACKUP_FILENAME = "ecommerce_backup_2025-07-08_21-55-18.sql"

ADMIN_CREDENTIALS = {
    "email": "admin@example.com",
    "password": "admin123"
}

def get_token():
    response = requests.post(f"{MAIN_SYSTEM_URL}/users/login", json=ADMIN_CREDENTIALS)
    if response.status_code == 200:
        data = response.json()
        return data.get('data', {}).get('token') or data.get('token')
    return None

def check_users_before_after_restore(token):
    """Check user details before and after restore"""
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get users before restore
    print("👥 USERS BEFORE RESTORE:")
    query_payload = {"sql": "SELECT user_id, username, email, created_at FROM users ORDER BY created_at LIMIT 10"}
    response = requests.post(f"{MAIN_SYSTEM_URL}/database/query", headers=headers, json=query_payload)
    
    users_before = []
    if response.status_code == 200:
        users_before = response.json()['data']['rows']
        for user in users_before:
            print(f"   - {user['username']} ({user['email']}) - Created: {user['created_at']}")
    
    # Get user count before
    count_query = {"sql": "SELECT COUNT(*) as count FROM users"}
    response = requests.post(f"{MAIN_SYSTEM_URL}/database/query", headers=headers, json=count_query)
    count_before = response.json()['data']['rows'][0]['count'] if response.status_code == 200 else 0
    
    print(f"\n📊 Total users before restore: {count_before}")
    
    # Perform restore
    print(f"\n🔄 PERFORMING RESTORE WITH: {BACKUP_FILENAME}")
    restore_payload = {"filename": BACKUP_FILENAME, "force": True}
    
    start_time = time.time()
    response = requests.post(f"{MAIN_SYSTEM_URL}/database/restore", 
                           headers=headers, json=restore_payload)
    duration = time.time() - start_time
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Restore completed in {duration:.2f}s")
        print(f"📁 File size: {data['data']['file_size']}")
        print(f"⏱️ Reported execution time: {data['data']['execution_time_ms']}ms")
        
        verification = data['data'].get('verification', {})
        if verification.get('verified'):
            print(f"✅ Verification passed: {verification['users_count']} users")
        else:
            print(f"❌ Verification failed: {verification.get('error', 'Unknown')}")
    else:
        print(f"❌ Restore failed: {response.status_code} - {response.text}")
        return
    
    # Wait for database to settle
    time.sleep(2)
    
    # Get users after restore
    print("\n👥 USERS AFTER RESTORE:")
    response = requests.post(f"{MAIN_SYSTEM_URL}/database/query", headers=headers, json=query_payload)
    
    users_after = []
    if response.status_code == 200:
        users_after = response.json()['data']['rows']
        for user in users_after:
            print(f"   - {user['username']} ({user['email']}) - Created: {user['created_at']}")
    
    # Get user count after
    response = requests.post(f"{MAIN_SYSTEM_URL}/database/query", headers=headers, json=count_query)
    count_after = response.json()['data']['rows'][0]['count'] if response.status_code == 200 else 0
    
    print(f"\n📊 Total users after restore: {count_after}")
    
    # Analysis
    print(f"\n🔍 ANALYSIS:")
    print(f"   Users before: {count_before}")
    print(f"   Users after:  {count_after}")
    print(f"   Difference:   {count_after - count_before}")
    
    if count_before == count_after:
        print("   ✅ User count unchanged - restore worked correctly")
        print("   💡 Backup likely contains same data as current database")
    elif count_after > count_before:
        print("   ⚠️ User count increased - restore may have added data")
        print("   💡 Either backup has more users or data wasn't cleaned properly")
    elif count_after < count_before:
        print("   ⚠️ User count decreased - restore may have replaced data")
        print("   💡 Backup likely has fewer users than current database")
    
    # Check if specific users changed
    usernames_before = {user['username'] for user in users_before}
    usernames_after = {user['username'] for user in users_after}
    
    new_users = usernames_after - usernames_before
    removed_users = usernames_before - usernames_after
    
    if new_users:
        print(f"   ➕ New users: {new_users}")
    if removed_users:
        print(f"   ➖ Removed users: {removed_users}")
    if not new_users and not removed_users:
        print("   🔄 Same users found - restore maintained existing data")

def test_restore_with_different_files(token):
    """Test restore with different backup files to see behavior"""
    headers = {"Authorization": f"Bearer {token}"}
    
    backup_files = [
        "ecommerce_backup_2025-07-08_21-55-18.sql",
        "ecommerce_backup_2025-07-04_01-48-21.sql",
        "ecommerce_backup_2025-06-27_04-16-29.sql"
    ]
    
    for i, backup_file in enumerate(backup_files):
        print(f"\n{'='*60}")
        print(f"TEST {i+1}: RESTORE WITH {backup_file}")
        print(f"{'='*60}")
        
        # Get user count before
        count_query = {"sql": "SELECT COUNT(*) as count FROM users"}
        response = requests.post(f"{MAIN_SYSTEM_URL}/database/query", headers=headers, json=count_query)
        count_before = response.json()['data']['rows'][0]['count'] if response.status_code == 200 else 0
        
        # Restore
        restore_payload = {"filename": backup_file, "force": True}
        response = requests.post(f"{MAIN_SYSTEM_URL}/database/restore", 
                               headers=headers, json=restore_payload)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Restore successful")
            print(f"⏱️ Execution time: {data['data']['execution_time_ms']}ms")
            
            verification = data['data'].get('verification', {})
            if verification.get('verified'):
                print(f"👥 Verified user count: {verification['users_count']}")
        else:
            print(f"❌ Restore failed: {response.status_code}")
            continue
        
        # Wait and check count after
        time.sleep(1)
        response = requests.post(f"{MAIN_SYSTEM_URL}/database/query", headers=headers, json=count_query)
        count_after = response.json()['data']['rows'][0]['count'] if response.status_code == 200 else 0
        
        print(f"📊 Users: {count_before} → {count_after} (Δ {count_after - count_before})")

def main():
    print("=" * 80)
    print("🔍 DETAILED MAIN SYSTEM RESTORE ANALYSIS")
    print("=" * 80)
    
    token = get_token()
    if not token:
        print("❌ Authentication failed")
        return
    
    print("✅ Authenticated successfully")
    
    # Detailed single restore test
    check_users_before_after_restore(token)
    
    # Multiple restore test
    print(f"\n{'='*80}")
    print("🔄 TESTING MULTIPLE RESTORE OPERATIONS")
    print(f"{'='*80}")
    test_restore_with_different_files(token)
    
    print(f"\n{'='*80}")
    print("📋 SUMMARY")
    print(f"{'='*80}")
    print("If you're experiencing issues with the main system restore:")
    print("1. Check if the restore is actually failing (HTTP errors)")
    print("2. Check if the user count is not changing as expected")
    print("3. Check if specific users are not being restored properly")
    print("4. Compare with emergency recovery server behavior")
    print(f"{'='*80}")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n💥 ERROR: {e}")
        import traceback
        traceback.print_exc()
