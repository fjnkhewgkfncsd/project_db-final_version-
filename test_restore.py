#!/usr/bin/env python3
"""
Test Restore Functionality
"""

import requests
import json

BASE_URL = "http://localhost:3001"

def test_restore():
    """Test database restore functionality"""
    print("🧪 Testing Database Restore Functionality")
    print("=" * 50)
    
    # Test 1: Login
    print("1. 🔐 Testing Login...")
    login_data = {
        "email": "admin@example.com",
        "password": "admin123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/users/login", json=login_data)
        if response.status_code == 200:
            token = response.json()["data"]["token"]
            print("   ✅ Login successful!")
            headers = {"Authorization": f"Bearer {token}"}
        else:
            print(f"   ❌ Login failed: {response.json()}")
            return
    except Exception as e:
        print(f"   ❌ Login error: {e}")
        return
    
    # Test 2: Get backup files
    print("\n2. 📋 Testing Get Backup Files...")
    try:
        response = requests.get(f"{BASE_URL}/api/database/backups", headers=headers)
        if response.status_code == 200:
            backup_response = response.json()["data"]
            backup_files = backup_response.get("backups", [])
            print(f"   ✅ Found {len(backup_files)} backup files")
            if backup_files:
                latest_backup = backup_files[0]["filename"]
                print(f"   📄 Latest backup: {latest_backup}")
                
                # Test 3: Restore from backup
                print("\n3. 🔄 Testing Database Restore...")
                restore_data = {"filename": latest_backup}
                response = requests.post(f"{BASE_URL}/api/database/restore", 
                                       json=restore_data, headers=headers)
                if response.status_code == 200:
                    result = response.json()
                    print(f"   ✅ Restore successful!")
                    print(f"   📄 File: {result['data']['filename']}")
                    print(f"   ⏱️ Execution time: {result['data']['execution_time_ms']}ms")
                else:
                    print(f"   ❌ Restore failed: {response.json()}")
            else:
                print("   ⚠️ No backup files available for testing")
        else:
            print(f"   ❌ Failed to get backup files: {response.json()}")
    except Exception as e:
        print(f"   ❌ Backup files error: {e}")

if __name__ == "__main__":
    test_restore()
