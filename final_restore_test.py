#!/usr/bin/env python3
"""
Final test of the restore functionality with the 10,003 user backup
"""

import requests
import json
import time

def test_restore_10k_users():
    print("🔄 FINAL RESTORE TEST WITH 10,003 USERS")
    print("=" * 50)
    
    # Get auth token
    auth_response = requests.post("http://localhost:3001/api/users/login", 
                                 json={"email": "admin@example.com", "password": "admin123"})
    
    if auth_response.status_code != 200:
        print("❌ Authentication failed")
        return
    
    token = auth_response.json().get('data', {}).get('token')
    headers = {"Authorization": f"Bearer {token}"}
    
    # Check current user count
    query_response = requests.post("http://localhost:3001/api/database/query", 
                                 json={"sql": "SELECT COUNT(*) FROM users;"}, 
                                 headers=headers)
    
    if query_response.status_code == 200:
        current_count = query_response.json().get('data', {}).get('rows', [[0]])[0][0]
        print(f"📊 Current users in database: {current_count}")
    else:
        print("❌ Could not get current user count")
        return
    
    # Perform restore with the specific backup
    target_backup = "ecommerce_backup_2025-07-09_02-46-32.sql"
    print(f"\n🔄 Testing restore with: {target_backup}")
    
    restore_data = {"filename": target_backup}
    
    start_time = time.time()
    restore_response = requests.post("http://localhost:3001/api/database/restore", 
                                   json=restore_data, headers=headers, timeout=120)
    duration = time.time() - start_time
    
    print(f"⏱️  Restore took: {duration:.2f} seconds")
    
    if restore_response.status_code == 200:
        data = restore_response.json()
        print("✅ Restore API call succeeded")
        
        # Check verification result
        verification = data.get('data', {}).get('verification', {})
        
        if verification.get('verified'):
            user_count = verification.get('userCount')
            print(f"📊 Users after restore: {user_count}")
            
            if user_count == 10003:
                print("🎉 SUCCESS! 10,003 users restored correctly!")
                print("   Your restore system is working perfectly!")
            elif user_count == current_count:
                print("⚠️  WARNING: User count unchanged")
                print("   This suggests the backup file may not contain 10,003 users")
                print("   or the restore didn't work as expected")
            else:
                print(f"ℹ️  Got {user_count} users (different from expected 10,003)")
        else:
            print("❌ Verification failed after restore")
            print(f"   Error: {verification.get('error', 'Unknown error')}")
        
        # Show full response for debugging
        print(f"\n📄 Full restore response:")
        print(json.dumps(data, indent=2))
        
    else:
        print(f"❌ Restore failed: HTTP {restore_response.status_code}")
        try:
            error_data = restore_response.json()
            print(f"   Error: {error_data.get('message', 'Unknown error')}")
        except:
            print(f"   Raw response: {restore_response.text}")

if __name__ == "__main__":
    test_restore_10k_users()
