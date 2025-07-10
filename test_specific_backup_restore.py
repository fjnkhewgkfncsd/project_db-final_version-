#!/usr/bin/env python3
"""
Test the specific backup file that should contain 10,003 users
"""

import requests
import json
import time

# Configuration
BACKEND_URL = "http://localhost:3001/api"
ADMIN_CREDENTIALS = {"email": "admin@example.com", "password": "admin123"}

def get_auth_token():
    """Get authentication token"""
    try:
        response = requests.post(f"{BACKEND_URL}/users/login", json=ADMIN_CREDENTIALS, timeout=10)
        if response.status_code == 200:
            return response.json().get('data', {}).get('token')
        return None
    except Exception as e:
        print(f"Auth error: {e}")
        return None

def test_specific_backup_restore():
    """Test restore with the specific 10,003 user backup"""
    print("🔍 TESTING SPECIFIC BACKUP RESTORE")
    print("=" * 40)
    
    token = get_auth_token()
    if not token:
        print("❌ Authentication failed")
        return
    
    # The backup file that our analysis showed contains 10,003 users
    target_backup = "ecommerce_backup_2025-07-09_02-46-32.sql"
    
    print(f"🎯 Target backup: {target_backup}")
    
    # Get current user count
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{BACKEND_URL}/database/query", 
                           json={"sql": "SELECT COUNT(*) FROM users;"}, 
                           headers=headers, timeout=10)
    
    if response.status_code == 200:
        current_count = response.json().get('data', {}).get('rows', [[0]])[0][0]
        print(f"📊 Current users: {current_count}")
    else:
        print("❌ Could not get current user count")
        return
    
    # Perform restore
    print(f"\n🔄 Restoring from: {target_backup}")
    restore_data = {"filename": target_backup}
    
    start_time = time.time()
    response = requests.post(f"{BACKEND_URL}/database/restore", 
                           json=restore_data, headers=headers, timeout=120)
    duration = time.time() - start_time
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Restore completed in {duration:.2f}s")
        print(f"📄 Response data:")
        print(json.dumps(data, indent=2))
        
        # Check the verification result
        verification = data.get('data', {}).get('verification', {})
        if verification.get('verified'):
            user_count = verification.get('userCount')
            print(f"\n📊 Users after restore: {user_count}")
            
            if str(user_count) == "10003":
                print("🎉 SUCCESS! 10,003 users restored correctly!")
            elif str(user_count) == str(current_count):
                print("⚠️  WARNING: User count unchanged - restore may not have worked")
            else:
                print(f"⚠️  UNEXPECTED: Got {user_count} users")
        else:
            print("❌ Verification failed")
            print(f"   Error: {verification.get('error')}")
    else:
        print(f"❌ Restore failed: {response.status_code}")
        print(f"   Response: {response.text}")

if __name__ == "__main__":
    test_specific_backup_restore()
