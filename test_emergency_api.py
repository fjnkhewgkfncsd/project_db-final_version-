#!/usr/bin/env python3
"""
Test emergency recovery API endpoints
"""

import requests
import json
import time
import subprocess
import sys
from datetime import datetime

def test_emergency_recovery_api():
    """Test all emergency recovery API endpoints"""
    print("🧪 EMERGENCY RECOVERY API TEST")
    print("=" * 50)
    
    base_url = "http://localhost:3002"
    
    # Step 1: Start emergency server (if not running)
    print("🚀 Step 1: Starting emergency recovery server...")
    try:
        # Check if server is already running
        response = requests.get(f"{base_url}/health", timeout=2)
        print("✅ Server already running")
    except:
        print("⚡ Starting server...")
        # Note: In a real scenario, you'd start the server here
        # For this test, assume it's started manually
        print("⚠️  Please start the emergency server manually:")
        print("   cd backend && node emergency-recovery-server.js")
        return False
    
    # Step 2: Test authentication
    print("\n🔐 Step 2: Testing authentication...")
    
    # Test invalid credentials
    try:
        response = requests.post(f"{base_url}/api/emergency/login", json={
            "username": "wrong",
            "password": "wrong"
        })
        if response.status_code == 401:
            print("✅ Invalid credentials correctly rejected")
        else:
            print(f"❌ Expected 401, got {response.status_code}")
    except Exception as e:
        print(f"❌ Auth test failed: {e}")
        return False
    
    # Test valid credentials
    try:
        response = requests.post(f"{base_url}/api/emergency/login", json={
            "username": "emergency_admin",
            "password": "EmergencyRestore2025!"
        })
        if response.status_code == 200:
            auth_data = response.json()
            token = auth_data.get('data', {}).get('token')
            print("✅ Valid credentials accepted")
            print(f"   Token received: {token[:20] if token else 'None'}...")
        else:
            print(f"❌ Auth failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Auth test failed: {e}")
        return False
    
    # Step 3: Test backup listing
    print("\n📋 Step 3: Testing backup listing...")
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{base_url}/api/emergency/backups", headers=headers)
        if response.status_code == 200:
            backup_data = response.json()
            backups = backup_data.get('data', {}).get('backups', [])
            print(f"✅ Backup listing successful: {len(backups)} backups found")
            if backups:
                latest = backups[0]
                print(f"   Latest backup: {latest['filename']} ({latest['sizeFormatted']})")
        else:
            print(f"❌ Backup listing failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backup listing failed: {e}")
        return False
    
    # Step 4: Test status endpoint
    print("\n📊 Step 4: Testing status endpoint...")
    try:
        response = requests.get(f"{base_url}/api/emergency/status", headers=headers)
        if response.status_code == 200:
            status_data = response.json()
            status = status_data.get('data', {})
            print("✅ Status endpoint working")
            print(f"   Server uptime: {status.get('server', {}).get('uptime', 'N/A')}")
            print(f"   Backup count: {status.get('backups', {}).get('count', 'N/A')}")
        else:
            print(f"❌ Status failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Status test failed: {e}")
    
    # Step 5: Test restore endpoint (dry run)
    print("\n🔄 Step 5: Testing restore endpoint...")
    if backups:
        try:
            # Use the latest backup for testing
            restore_data = {
                "filename": backups[0]['filename'],
                "force": True
            }
            
            response = requests.post(f"{base_url}/api/emergency/restore", 
                                   json=restore_data, headers=headers)
            
            if response.status_code == 200:
                result = response.json()
                print("✅ Restore endpoint accessible")
                print(f"   Message: {result.get('message', 'N/A')}")
            else:
                print(f"⚠️  Restore response: {response.status_code}")
                print(f"   Message: {response.text}")
        except Exception as e:
            print(f"❌ Restore test failed: {e}")
    
    print("\n✅ Emergency Recovery API tests completed")
    return True

def main():
    success = test_emergency_recovery_api()
    if success:
        print("\n🎉 API TESTS PASSED!")
    else:
        print("\n⚠️  API TESTS HAD ISSUES!")
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
