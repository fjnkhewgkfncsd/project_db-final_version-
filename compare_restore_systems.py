#!/usr/bin/env python3
"""
Compare the restore functionality between main system and emergency recovery
to identify why the main system restore is not working as expected.
"""

import requests
import json
import time
import base64

# Configuration
MAIN_SYSTEM_URL = "http://localhost:3001/api"
EMERGENCY_URL = "http://localhost:3002/api"
BACKUP_FILENAME = "ecommerce_backup_2025-07-08_21-55-18.sql"

# Credentials
ADMIN_CREDENTIALS = {
    "email": "admin@example.com",
    "password": "admin123"
}

EMERGENCY_CREDENTIALS = {
    "username": "emergency_admin",
    "password": "EmergencyRestore2025!"
}

def get_main_system_token():
    """Get JWT token for main system"""
    try:
        response = requests.post(f"{MAIN_SYSTEM_URL}/users/login", json=ADMIN_CREDENTIALS)
        if response.status_code == 200:
            data = response.json()
            return data.get('data', {}).get('token') or data.get('token')
        else:
            print(f"❌ Main system login failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Main system login error: {e}")
        return None

def get_emergency_token():
    """Get emergency token"""
    try:
        response = requests.post(f"{EMERGENCY_URL}/emergency/login", json=EMERGENCY_CREDENTIALS)
        if response.status_code == 200:
            data = response.json()
            return data.get('data', {}).get('token')
        else:
            print(f"❌ Emergency login failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Emergency login error: {e}")
        return None

def test_main_system_restore(token):
    """Test main system restore"""
    print("\n🔄 TESTING MAIN SYSTEM RESTORE:")
    print(f"   URL: {MAIN_SYSTEM_URL}/database/restore")
    
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"filename": BACKUP_FILENAME, "force": True}
    
    try:
        start_time = time.time()
        response = requests.post(f"{MAIN_SYSTEM_URL}/database/restore", 
                               headers=headers, json=payload, timeout=30)
        duration = time.time() - start_time
        
        print(f"   Response status: {response.status_code}")
        print(f"   Response time: {duration:.2f}s")
        
        if response.status_code == 200:
            data = response.json()
            print("   ✅ SUCCESS")
            print(f"   📁 File size: {data['data']['file_size']}")
            print(f"   ⏱️ Execution time: {data['data']['execution_time_ms']}ms")
            
            verification = data['data'].get('verification', {})
            if verification.get('verified'):
                print(f"   👥 Users count: {verification['users_count']}")
            else:
                print(f"   ⚠️ Verification failed: {verification.get('error', 'Unknown')}")
            
            return True, data
        else:
            print("   ❌ FAILED")
            print(f"   Error: {response.text}")
            return False, response.text
            
    except Exception as e:
        print(f"   💥 EXCEPTION: {e}")
        return False, str(e)

def test_emergency_restore(token):
    """Test emergency recovery restore"""
    print("\n🚨 TESTING EMERGENCY RECOVERY RESTORE:")
    print(f"   URL: {EMERGENCY_URL}/emergency/restore")
    
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"filename": BACKUP_FILENAME, "force": True}
    
    try:
        start_time = time.time()
        response = requests.post(f"{EMERGENCY_URL}/emergency/restore", 
                               headers=headers, json=payload, timeout=30)
        duration = time.time() - start_time
        
        print(f"   Response status: {response.status_code}")
        print(f"   Response time: {duration:.2f}s")
        
        if response.status_code == 200:
            data = response.json()
            print("   ✅ SUCCESS")
            print(f"   ⏱️ Duration: {data['data']['duration']}")
            
            verification = data['data'].get('verification', {})
            if verification.get('verified'):
                print(f"   👥 Users count: {verification['userCount']}")
            else:
                print(f"   ⚠️ Verification failed: {verification.get('error', 'Unknown')}")
            
            return True, data
        else:
            print("   ❌ FAILED")
            print(f"   Error: {response.text}")
            return False, response.text
            
    except Exception as e:
        print(f"   💥 EXCEPTION: {e}")
        return False, str(e)

def check_user_count(system_type, url, headers):
    """Check current user count"""
    try:
        if system_type == "main":
            query_payload = {"sql": "SELECT COUNT(*) as count FROM users"}
            response = requests.post(f"{url}/database/query", headers=headers, json=query_payload)
            if response.status_code == 200:
                return response.json()['data']['rows'][0]['count']
        elif system_type == "emergency":
            response = requests.get(f"{url}/emergency/status", headers=headers)
            if response.status_code == 200:
                # Emergency might not have query endpoint, return None
                return None
        return None
    except:
        return None

def main():
    print("=" * 80)
    print("🔍 COMPARING MAIN SYSTEM vs EMERGENCY RECOVERY RESTORE")
    print("=" * 80)
    
    # Get tokens
    print("🔐 Getting authentication tokens...")
    main_token = get_main_system_token()
    emergency_token = get_emergency_token()
    
    if not main_token:
        print("❌ Cannot test main system - authentication failed")
        return
    
    if not emergency_token:
        print("❌ Cannot test emergency system - authentication failed")
        return
    
    print("✅ Both systems authenticated successfully")
    
    # Check initial user counts
    main_headers = {"Authorization": f"Bearer {main_token}"}
    emergency_headers = {"Authorization": f"Bearer {emergency_token}"}
    
    initial_users = check_user_count("main", MAIN_SYSTEM_URL, main_headers)
    print(f"\n📊 Initial user count: {initial_users}")
    
    # Test main system restore
    main_success, main_result = test_main_system_restore(main_token)
    
    # Wait a moment
    time.sleep(2)
    
    # Test emergency recovery restore
    emergency_success, emergency_result = test_emergency_restore(emergency_token)
    
    # Final analysis
    print("\n" + "=" * 80)
    print("📋 COMPARISON RESULTS:")
    print("=" * 80)
    
    print(f"Main System Restore:     {'✅ SUCCESS' if main_success else '❌ FAILED'}")
    print(f"Emergency Recovery:      {'✅ SUCCESS' if emergency_success else '❌ FAILED'}")
    
    if not main_success and emergency_success:
        print("\n🔍 ISSUE IDENTIFIED:")
        print("❌ Main system restore is failing while emergency recovery works")
        print("💡 POSSIBLE CAUSES:")
        print("   1. Authentication/authorization issues")
        print("   2. Database connection problems in main system")
        print("   3. Different environment variables")
        print("   4. File path or permission issues")
        print("   5. Missing dependencies or configuration")
        
        print(f"\n🚨 MAIN SYSTEM ERROR:")
        print(f"   {main_result}")
        
    elif main_success and emergency_success:
        print("\n✅ Both systems are working correctly")
        
    elif not main_success and not emergency_success:
        print("\n❌ Both systems are failing - likely database or file issue")
        
    print("=" * 80)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n💥 UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
