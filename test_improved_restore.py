#!/usr/bin/env python3
"""
Test the improved restore functionality
"""
import requests
import json
import time
import sys

# Configuration
BASE_URL = 'http://localhost:3001'
ADMIN_CREDENTIALS = {
    'email': 'admin@example.com',
    'password': 'admin123'
}

def get_admin_token():
    """Get admin authentication token"""
    try:
        response = requests.post(f'{BASE_URL}/api/users/login', json=ADMIN_CREDENTIALS)
        if response.status_code == 200:
            data = response.json()
            return data.get('data', {}).get('token')
        else:
            print(f"❌ Login failed: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error logging in: {e}")
        return None

def test_restore_functionality():
    """Test the restore functionality with different scenarios"""
    
    # Get authentication token
    print("🔐 Getting admin token...")
    token = get_admin_token()
    if not token:
        print("❌ Cannot get admin token. Make sure backend is running and credentials are correct.")
        return False
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    print("✅ Got admin token successfully")
    
    # Test 1: List available backups
    print("\n📋 Test 1: List available backups")
    try:
        response = requests.get(f'{BASE_URL}/api/database/backups', headers=headers)
        if response.status_code == 200:
            backups = response.json()['data']['backups']
            print(f"✅ Found {len(backups)} backup files:")
            for backup in backups[:5]:  # Show first 5
                print(f"   📄 {backup['filename']} ({backup['size']})")
        else:
            print(f"❌ Failed to list backups: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error listing backups: {e}")
        return False
    
    # Test 2: Test restore with invalid filename
    print("\n🚫 Test 2: Test restore with invalid filename")
    try:
        restore_data = {'filename': 'nonexistent_backup.sql'}
        response = requests.post(f'{BASE_URL}/api/admin/database/restore', 
                               json=restore_data, headers=headers)
        if response.status_code == 404:
            print("✅ Correctly rejected non-existent backup file")
        else:
            print(f"❌ Unexpected response for invalid file: {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing invalid filename: {e}")
    
    # Test 3: Test restore with real backup file
    if backups:
        print("\n🔄 Test 3: Test restore with real backup file")
        backup_to_test = backups[0]['filename']  # Use most recent backup
        print(f"   📄 Testing restore with: {backup_to_test}")
        
        try:
            restore_data = {'filename': 'ecommerce_backup_FIXED_MANUAL_2025-07-10_05-32-48.sql'}
            print("   🚀 Starting restore process...")
            start_time = time.time()
            
            response = requests.post(f'{BASE_URL}/api/database/restore', 
                                   json=restore_data, headers=headers, timeout=120)
            
            duration = time.time() - start_time
            print(f"   ⏱️  Restore took {duration:.2f} seconds")
            
            if response.status_code == 200:
                result = response.json()
                print("✅ Restore completed successfully!")
                
                # Show verification results
                verification = result['data'].get('verification', {})
                if verification.get('verified'):
                    user_count = verification.get('userCount', 0)
                    print(f"   👥 Verified: {user_count} users in database")
                else:
                    print(f"   ⚠️  Verification failed: {verification.get('error', 'Unknown error')}")
                
                # Show other details
                print(f"   📊 File size: {result['data'].get('file_size', 'Unknown')}")
                print(f"   🕐 Execution time: {result['data'].get('execution_time_ms', 0)}ms")
                print(f"   📝 Restore type: {result['data'].get('restore_type', 'Unknown')}")
                
            else:
                print(f"❌ Restore failed: {response.status_code}")
                print(f"   Error details: {response.text}")
                
        except requests.exceptions.Timeout:
            print("❌ Restore timed out (>120 seconds)")
        except Exception as e:
            print(f"❌ Error during restore: {e}")
    
    # Test 4: Check database stats after restore
    print("\n📊 Test 4: Check database statistics")
    try:
        response = requests.get(f'{BASE_URL}/api/database/stats', headers=headers)
        if response.status_code == 200:
            stats = response.json()['data']
            print("✅ Database statistics:")
            print(f"   🗄️  Database: {stats['database_info']['name']}")
            print(f"   💾 Size: {stats['database_info']['size']}")
            
            # Show record counts
            record_counts = stats.get('record_counts', [])
            for table in record_counts:
                print(f"   📋 {table['table_name']}: {table['record_count']} records")
        else:
            print(f"❌ Failed to get database stats: {response.text}")
    except Exception as e:
        print(f"❌ Error getting database stats: {e}")
    
    return True

def test_restore_robustness():
    """Test restore with various edge cases"""
    print("\n🧪 Testing restore robustness...")
    
    # Get token
    token = get_admin_token()
    if not token:
        return False
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    # Test empty filename
    print("🚫 Testing empty filename...")
    try:
        response = requests.post(f'{BASE_URL}/api/database/restore', 
                               json={}, headers=headers)
        if response.status_code == 400:
            print("✅ Correctly rejected empty filename")
        else:
            print(f"❌ Unexpected response: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test invalid file extension
    print("🚫 Testing invalid file extension...")
    try:
        response = requests.post(f'{BASE_URL}/api/database/restore', 
                               json={'filename': 'test.txt'}, headers=headers)
        if response.status_code == 400:
            print("✅ Correctly rejected invalid file extension")
        elif response.status_code == 404:
            print("✅ File not found (expected)")
        else:
            print(f"❌ Unexpected response: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🧪 Testing Improved Restore Functionality")
    print("=" * 50)
    
    # Run tests
    if test_restore_functionality():
        print("\n" + "=" * 50)
        test_restore_robustness()
        print("\n✅ All tests completed!")
    else:
        print("\n❌ Basic tests failed")
        sys.exit(1)
