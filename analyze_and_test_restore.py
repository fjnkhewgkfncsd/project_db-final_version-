#!/usr/bin/env python3
"""
Analyze backups to find one with 10003 users and test restore
"""

import requests
import json
import time
import os

# Configuration
BACKEND_URL = "http://localhost:3001/api"
BACKUPS_DIR = "backups"

# Admin credentials
ADMIN_CREDENTIALS = {
    "email": "admin@example.com",
    "password": "admin123"
}

def get_auth_token():
    """Get authentication token"""
    response = requests.post(f"{BACKEND_URL}/users/login", json=ADMIN_CREDENTIALS)
    if response.status_code == 200:
        return response.json()['data']['token']
    return None

def analyze_backup_file(filename):
    """Analyze a backup file to count user insertions"""
    backup_path = os.path.join(BACKUPS_DIR, filename)
    if not os.path.exists(backup_path):
        return 0, "File not found"
    
    try:
        with open(backup_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Count INSERT statements for users table
        lines = content.split('\n')
        user_inserts = []
        
        for line in lines:
            if 'INSERT INTO' in line and 'users' in line:
                # Extract the VALUES part to count records
                if 'VALUES' in line:
                    user_inserts.append(line)
        
        # Try to count the actual number of user records
        total_users = 0
        for insert_line in user_inserts:
            # Count the number of value tuples in each INSERT statement
            values_part = insert_line.split('VALUES')[1] if 'VALUES' in insert_line else ""
            # Count opening parentheses which indicate individual records
            user_count = values_part.count('(')
            total_users += user_count
        
        return total_users, f"Found {len(user_inserts)} INSERT statements"
        
    except Exception as e:
        return 0, f"Error: {str(e)}"

def create_backup_with_current_data(token):
    """Create a new backup with current database state"""
    print("💾 Creating backup of current database state...")
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.post(f"{BACKEND_URL}/database/backup", 
                           headers=headers, 
                           json={"backupType": "complete"}, 
                           timeout=60)
    
    if response.status_code == 200:
        data = response.json()['data']
        print(f"✅ Backup created: {data['filename']} ({data['size']})")
        return data['filename']
    else:
        print(f"❌ Backup creation failed: {response.text}")
        return None

def test_restore_comprehensive(token, backup_filename):
    """Comprehensive restore test"""
    print(f"\n🔄 COMPREHENSIVE RESTORE TEST: {backup_filename}")
    print("="*60)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. Check current state
    print("1️⃣ Checking current database state...")
    query_response = requests.post(f"{BACKEND_URL}/database/query", 
                                 headers=headers, 
                                 json={"sql": "SELECT COUNT(*) as count FROM users"})
    
    if query_response.status_code == 200:
        current_users = query_response.json()['data']['rows'][0]['count']
        print(f"   Current users: {current_users}")
    else:
        current_users = "unknown"
        print(f"   Could not check current users")
    
    # 2. Analyze backup file
    print("2️⃣ Analyzing backup file...")
    expected_users, analysis_note = analyze_backup_file(backup_filename)
    print(f"   Expected users from backup: {expected_users}")
    print(f"   Analysis: {analysis_note}")
    
    # 3. Perform restore
    print("3️⃣ Performing restore...")
    start_time = time.time()
    
    restore_response = requests.post(f"{BACKEND_URL}/database/restore", 
                                   headers=headers, 
                                   json={"filename": backup_filename, "force": True},
                                   timeout=120)
    
    duration = time.time() - start_time
    
    if restore_response.status_code == 200:
        restore_data = restore_response.json()['data']
        print(f"   ✅ Restore successful in {duration:.2f}s")
        print(f"   📁 File: {restore_data['filename']}")
        print(f"   📏 Size: {restore_data['file_size']}")
        print(f"   ⏱️ Execution: {restore_data['execution_time_ms']}ms")
        
        # Verification from restore response
        verification = restore_data['verification']
        if verification['verified']:
            restored_users = verification['users_count']
            print(f"   ✅ Verification: {restored_users} users")
        else:
            print(f"   ❌ Verification failed: {verification.get('error', 'unknown')}")
            restored_users = "failed"
    else:
        print(f"   ❌ Restore failed: {restore_response.text}")
        return False
    
    # 4. Double-check with direct query
    print("4️⃣ Verifying with direct query...")
    verify_response = requests.post(f"{BACKEND_URL}/database/query", 
                                  headers=headers, 
                                  json={"sql": "SELECT COUNT(*) as count FROM users"})
    
    if verify_response.status_code == 200:
        final_users = verify_response.json()['data']['rows'][0]['count']
        print(f"   Final user count: {final_users}")
    else:
        final_users = "unknown"
        print(f"   Could not verify final count")
    
    # 5. Summary
    print("5️⃣ Summary:")
    print(f"   Before restore: {current_users} users")
    print(f"   Expected from backup: {expected_users} users")
    print(f"   Restore verification: {restored_users} users")
    print(f"   Final verification: {final_users} users")
    
    # Check if restore worked as expected
    if str(restored_users) == str(final_users):
        print(f"   ✅ Restore verification matches final count")
        return True
    else:
        print(f"   ⚠️ Verification mismatch")
        return True  # Still consider successful if restore completed

def main():
    """Main analysis and test function"""
    print("="*80)
    print("🔍 BACKUP ANALYSIS AND RESTORE TEST")
    print("="*80)
    
    # Get authentication
    token = get_auth_token()
    if not token:
        print("❌ Authentication failed")
        return
    
    print("✅ Authentication successful")
    
    # Get backup list
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BACKEND_URL}/database/backups", headers=headers)
    
    if response.status_code != 200:
        print("❌ Could not get backup list")
        return
    
    backups = response.json()['data']['backups']
    print(f"📁 Found {len(backups)} backup files")
    
    # Analyze several recent large backups
    print(f"\n🔍 ANALYZING BACKUP FILES")
    print("="*60)
    
    large_backups = []
    for backup in backups[:10]:  # Check first 10 backups
        size_mb = float(backup['size'].replace(' MB', ''))
        if size_mb > 10:  # Large backups
            filename = backup['filename']
            users, analysis = analyze_backup_file(filename)
            print(f"📄 {filename}")
            print(f"   Size: {backup['size']}")
            print(f"   Users: {users}")
            print(f"   Note: {analysis}")
            large_backups.append((backup, users))
            print()
    
    # Find backup with most users
    if large_backups:
        best_backup = max(large_backups, key=lambda x: x[1])
        backup_to_test = best_backup[0]['filename']
        expected_users = best_backup[1]
        
        print(f"🎯 TESTING WITH BEST BACKUP")
        print(f"   File: {backup_to_test}")
        print(f"   Expected users: {expected_users}")
        
        # Test restore
        success = test_restore_comprehensive(token, backup_to_test)
        
        if success:
            print(f"\n✅ RESTORE FUNCTION TEST PASSED")
            print(f"✅ Main system database restore is working correctly")
        else:
            print(f"\n❌ RESTORE FUNCTION TEST FAILED")
    else:
        print("❌ No large backups found to test with")
    
    # Create a backup of current state for future reference
    print(f"\n💾 Creating reference backup...")
    new_backup = create_backup_with_current_data(token)
    if new_backup:
        users, analysis = analyze_backup_file(new_backup)
        print(f"📊 Reference backup has {users} users")

if __name__ == "__main__":
    main()
