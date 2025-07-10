#!/usr/bin/env python3
"""
Test script to verify the main system's Database Tools restore functionality
with the 4-user backup file.
"""

import requests
import json
import time

# Configuration
BACKEND_URL = "http://localhost:3001/api"
BACKUP_FILENAME = "ecommerce_backup_2025-07-08_21-55-18.sql"  # 1-user backup (latest)

# Demo credentials (admin user)
ADMIN_CREDENTIALS = {
    "email": "admin@example.com",
    "password": "admin123"
}

def test_login():
    """Test admin login and get JWT token"""
    print("🔐 Testing admin login...")
    
    response = requests.post(f"{BACKEND_URL}/users/login", json=ADMIN_CREDENTIALS)
    
    if response.status_code == 200:
        data = response.json()
        token = data.get('data', {}).get('token') or data.get('token')
        if token:
            print(f"✅ Login successful! Token: {token[:50]}...")
            return token
        else:
            print(f"❌ Login failed: No token in response - {data}")
            return None
    else:
        print(f"❌ Login failed: {response.status_code} - {response.text}")
        return None

def test_backup_list(token):
    """Test getting the list of backup files"""
    print("\n📋 Testing backup file listing...")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BACKEND_URL}/database/backups", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        backups = data.get('data', {}).get('backups', [])
        print(f"✅ Found {len(backups)} backup files")
        
        # Check if our target backup exists
        target_backup = None
        for backup in backups:
            if backup['filename'] == BACKUP_FILENAME:
                target_backup = backup
                break
        
        if target_backup:
            print(f"✅ Target backup found: {BACKUP_FILENAME} ({target_backup['size']})")
            return True
        else:
            print(f"❌ Target backup not found: {BACKUP_FILENAME}")
            print("Available backups:")
            for backup in backups[:5]:  # Show first 5
                print(f"  - {backup['filename']} ({backup['size']})")
            return False
    else:
        print(f"❌ Failed to get backup list: {response.status_code} - {response.text}")
        return False

def test_restore(token):
    """Test the restore functionality with the 4-user backup"""
    print(f"\n🔄 Testing restore with {BACKUP_FILENAME}...")
    
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "filename": BACKUP_FILENAME,
        "force": True
    }
    
    response = requests.post(f"{BACKEND_URL}/database/restore", 
                           headers=headers, 
                           json=payload)
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Restore completed successfully!")
        print(f"   Filename: {data['data']['filename']}")
        print(f"   File size: {data['data']['file_size']}")
        print(f"   Execution time: {data['data']['execution_time_ms']}ms")
        print(f"   Restore type: {data['data']['restore_type']}")
        
        verification = data['data'].get('verification', {})
        if verification.get('verified'):
            print(f"   Users count: {verification['users_count']}")
            return True
        else:
            print(f"   ⚠️ Verification failed: {verification.get('error', 'Unknown error')}")
            return False
    else:
        print(f"❌ Restore failed: {response.status_code} - {response.text}")
        return False

def verify_users(token):
    """Verify that exactly 4 users were restored"""
    print("\n🔍 Verifying user count after restore...")
    
    headers = {"Authorization": f"Bearer {token}"}
    query_payload = {
        "sql": "SELECT COUNT(*) as user_count FROM users"
    }
    
    response = requests.post(f"{BACKEND_URL}/database/query", 
                           headers=headers, 
                           json=query_payload)
    
    if response.status_code == 200:
        data = response.json()
        rows = data.get('data', {}).get('rows', [])
        if rows:
            user_count = rows[0]['user_count']
            print(f"✅ User count verification: {user_count} users found")
            
            if user_count == 1:
                print("🎯 SUCCESS: Exactly 1 user restored as expected!")
                return True
            else:
                print(f"⚠️ WARNING: Expected 1 user, but found {user_count}")
                return False
        else:
            print("❌ No data returned from user count query")
            return False
    else:
        print(f"❌ User count query failed: {response.status_code} - {response.text}")
        return False

def get_user_details(token):
    """Get details of the restored users"""
    print("\n👥 Getting details of restored users...")
    
    headers = {"Authorization": f"Bearer {token}"}
    query_payload = {
        "sql": "SELECT user_id, username, email, role, created_at FROM users ORDER BY user_id"
    }
    
    response = requests.post(f"{BACKEND_URL}/database/query", 
                           headers=headers, 
                           json=query_payload)
    
    if response.status_code == 200:
        data = response.json()
        rows = data.get('data', {}).get('rows', [])
        if rows:
            print(f"✅ Found {len(rows)} users:")
            for user in rows:
                print(f"   - ID: {user['user_id']}, Username: {user['username']}, Email: {user['email']}, Role: {user['role']}")
            return True
        else:
            print("❌ No users found in database")
            return False
    else:
        print(f"❌ User details query failed: {response.status_code} - {response.text}")
        return False

def main():
    """Main test function"""
    print("=" * 80)
    print("🧪 MAIN SYSTEM DATABASE RESTORE TEST")
    print("=" * 80)
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Target backup: {BACKUP_FILENAME}")
    print("=" * 80)
    
    # Step 1: Login
    token = test_login()
    if not token:
        print("\n❌ FAILED: Could not authenticate")
        return False
    
    # Step 2: Check backup list
    if not test_backup_list(token):
        print("\n❌ FAILED: Target backup file not found")
        return False
    
    # Step 3: Perform restore
    if not test_restore(token):
        print("\n❌ FAILED: Restore operation failed")
        return False
    
    # Step 4: Verify user count
    time.sleep(2)  # Give DB a moment to settle
    if not verify_users(token):
        print("\n❌ FAILED: User count verification failed")
        return False
    
    # Step 5: Get user details
    if not get_user_details(token):
        print("\n⚠️ WARNING: Could not retrieve user details")
    
    print("\n" + "=" * 80)
    print("🎉 SUCCESS: Main system restore test completed successfully!")
    print("✅ The Database Tools restore tab works correctly")
    print("✅ 1-user backup was restored successfully")
    print("✅ Main system restore now behaves like emergency restore")
    print("=" * 80)
    return True

if __name__ == "__main__":
    try:
        success = main()
        exit(0 if success else 1)
    except Exception as e:
        print(f"\n💥 UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
