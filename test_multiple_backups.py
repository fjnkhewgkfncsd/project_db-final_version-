#!/usr/bin/env python3
"""
Test restore with a fresh database to see the actual backup contents
"""

import requests
import json
import time

# Configuration
BACKEND_URL = "http://localhost:3001/api"
BACKUP_FILENAME = "ecommerce_backup_2025-07-08_21-55-18.sql"

# Demo credentials
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

def clear_users_table(token):
    """Clear users table to test fresh restore"""
    print("🗑️  Clearing users table for clean test...")
    
    # Note: We can't use DELETE via the API (only SELECT allowed)
    # But we can test the restore process
    pass

def check_users(token):
    """Check user count"""
    headers = {"Authorization": f"Bearer {token}"}
    query_payload = {"sql": "SELECT COUNT(*) as count FROM users"}
    
    response = requests.post(f"{BACKEND_URL}/database/query", 
                           headers=headers, json=query_payload)
    
    if response.status_code == 200:
        data = response.json()
        return int(data['data']['rows'][0]['count'])
    return None

def test_restore(token):
    """Test restore"""
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"filename": BACKUP_FILENAME, "force": True}
    
    response = requests.post(f"{BACKEND_URL}/database/restore", 
                           headers=headers, json=payload)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"❌ Restore failed: {response.status_code} - {response.text}")
        return None

def test_different_backup(token, filename):
    """Test with a different backup file"""
    print(f"\n🔄 Testing with different backup: {filename}")
    
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"filename": filename, "force": True}
    
    response = requests.post(f"{BACKEND_URL}/database/restore", 
                           headers=headers, json=payload)
    
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Restore completed in {data['data']['execution_time_ms']}ms")
        print(f"   📁 File size: {data['data']['file_size']}")
        
        verification = data['data'].get('verification', {})
        if verification.get('verified'):
            print(f"   👥 Verified user count: {verification['users_count']}")
        
        # Check actual count
        time.sleep(1)
        actual_count = check_users(token)
        print(f"   📊 Actual user count: {actual_count}")
        
        return actual_count
    else:
        print(f"   ❌ Failed: {response.status_code}")
        return None

def main():
    print("=" * 80)
    print("🧪 TESTING RESTORE WITH MULTIPLE BACKUP FILES")
    print("=" * 80)
    
    token = get_token()
    if not token:
        print("❌ Failed to authenticate")
        return
    
    print("✅ Authenticated successfully")
    
    # Test current state
    current_users = check_users(token)
    print(f"\n📊 Current users in database: {current_users}")
    
    # Test with different backup files to see the pattern
    backup_files = [
        "ecommerce_backup_2025-07-08_21-55-18.sql",
        "ecommerce_backup_2025-07-08_21-06-33.sql", 
        "ecommerce_backup_2025-07-04_01-48-21.sql",
        "ecommerce_backup_2025-06-27_04-16-29.sql"
    ]
    
    results = {}
    for backup_file in backup_files:
        user_count = test_different_backup(token, backup_file)
        if user_count is not None:
            results[backup_file] = user_count
    
    print(f"\n📋 RESULTS SUMMARY:")
    print("=" * 60)
    for backup_file, user_count in results.items():
        print(f"{backup_file}: {user_count} users")
    
    print(f"\n🔍 ANALYSIS:")
    unique_counts = set(results.values())
    if len(unique_counts) == 1:
        count = list(unique_counts)[0]
        print(f"✅ All backups restore to the same user count: {count}")
        if count == 4:
            print("💡 This suggests all backups contain the same 4 demo users")
        elif count > 1000:
            print("💡 This suggests all backups contain a large dataset")
    else:
        print(f"⚠️ Different backups restore to different user counts: {unique_counts}")
        print("💡 This suggests backups were created at different times with different data")
    
    print("=" * 80)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n💥 ERROR: {e}")
        import traceback
        traceback.print_exc()
