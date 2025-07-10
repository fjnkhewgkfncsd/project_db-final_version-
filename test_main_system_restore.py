#!/usr/bin/env python3
"""
Test the main system's Database Tools restore functionality
"""
import requests
import json
import sys

def test_main_system_restore():
    # Main system backend URL
    base_url = 'http://localhost:8000'
    
    print("🧪 Testing Main System Database Tools Restore...")
    
    # First, try to get auth token with demo admin credentials
    login_url = f"{base_url}/api/auth/login"
    login_data = {
        "username": "demo_admin",
        "password": "demo123"
    }
    
    print("📝 Attempting login...")
    try:
        login_response = requests.post(login_url, json=login_data, timeout=10)
        if login_response.status_code != 200:
            print(f"❌ Login failed: {login_response.status_code}")
            print(f"Response: {login_response.text}")
            return False
            
        login_result = login_response.json()
        if not login_result.get('success'):
            print(f"❌ Login unsuccessful: {login_result}")
            return False
            
        token = login_result.get('token')
        if not token:
            print("❌ No token received from login")
            return False
            
        print("✅ Login successful, got auth token")
        
    except Exception as e:
        print(f"❌ Login request failed: {e}")
        return False
    
    # Now test the restore endpoint
    restore_url = f"{base_url}/api/database/restore"
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    # Use the 4-user backup file
    restore_data = {
        "filename": "ecommerce_backup_2025-07-04_01-48-21.sql",
        "force": True
    }
    
    print("🔄 Attempting database restore via main system...")
    print(f"Backup file: {restore_data['filename']}")
    
    try:
        restore_response = requests.post(restore_url, json=restore_data, headers=headers, timeout=60)
        
        print(f"📊 Response Status: {restore_response.status_code}")
        
        if restore_response.status_code == 200:
            result = restore_response.json()
            print("✅ RESTORE SUCCESS!")
            print(f"📈 Response: {json.dumps(result, indent=2)}")
            
            # Extract verification info
            if 'data' in result and 'verification' in result['data']:
                verification = result['data']['verification']
                if verification.get('verified'):
                    user_count = verification.get('users_count', 'unknown')
                    print(f"✅ Verification successful - Users restored: {user_count}")
                else:
                    print(f"⚠️ Verification failed: {verification.get('error', 'unknown error')}")
            
            return True
        else:
            print(f"❌ RESTORE FAILED with status {restore_response.status_code}")
            try:
                error_data = restore_response.json()
                print(f"Error details: {json.dumps(error_data, indent=2)}")
            except:
                print(f"Raw response: {restore_response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Restore request timed out (>60s)")
        return False
    except Exception as e:
        print(f"❌ Restore request failed: {e}")
        return False

def check_system_status():
    """Check if the main system is running"""
    try:
        response = requests.get('http://localhost:8000/api/health', timeout=5)
        if response.status_code == 200:
            print("✅ Main system is running")
            return True
        else:
            print(f"⚠️ Main system returned status {response.status_code}")
            return False
    except:
        print("❌ Main system is not running or not accessible")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("TESTING MAIN SYSTEM DATABASE TOOLS RESTORE")
    print("=" * 60)
    
    if not check_system_status():
        print("\n💡 Please start the main system first:")
        print("   cd backend && npm start")
        sys.exit(1)
    
    success = test_main_system_restore()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 MAIN SYSTEM RESTORE TEST: PASSED")
        print("✅ The Database Tools restore tab should now work!")
    else:
        print("💥 MAIN SYSTEM RESTORE TEST: FAILED")
        print("❌ The Database Tools restore still has issues")
    print("=" * 60)
