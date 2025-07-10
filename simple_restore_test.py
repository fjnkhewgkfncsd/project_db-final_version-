#!/usr/bin/env python3
"""
Simplified diagnostic for restore router issues
"""

import requests
import json
import os

# Configuration
BACKEND_URL = "http://localhost:3001/api"
BACKUP_FILENAME = "ecommerce_backup_2025-07-08_21-55-18.sql"

# Demo credentials 
ADMIN_CREDENTIALS = {
    "email": "admin@example.com",
    "password": "admin123"
}

def main():
    print("🔍 SIMPLE RESTORE DIAGNOSTIC")
    print("=" * 50)
    
    # 1. Check if backend is running
    print("1. Backend server status...")
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        if response.status_code == 200:
            print("   ✅ Backend server is running")
        else:
            print(f"   ❌ Backend server error: {response.status_code}")
            return
    except Exception as e:
        print(f"   ❌ Cannot connect to backend: {e}")
        return
    
    # 2. Test authentication
    print("\n2. Authentication test...")
    try:
        response = requests.post(f"{BACKEND_URL}/users/login", json=ADMIN_CREDENTIALS)
        if response.status_code == 200:
            data = response.json()
            token = data.get('data', {}).get('token') or data.get('token')
            print("   ✅ Authentication successful")
        else:
            print(f"   ❌ Authentication failed: {response.status_code}")
            return
    except Exception as e:
        print(f"   ❌ Authentication error: {e}")
        return
    
    # 3. Check backup file listing
    print("\n3. Backup file listing...")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BACKEND_URL}/database/backups", headers=headers)
        if response.status_code == 200:
            data = response.json()
            backups = data.get('data', {}).get('backups', [])
            print(f"   ✅ Found {len(backups)} backup files")
            
            # Check if target backup exists
            target_found = any(backup['filename'] == BACKUP_FILENAME for backup in backups)
            if target_found:
                print(f"   ✅ Target backup found: {BACKUP_FILENAME}")
            else:
                print(f"   ❌ Target backup not found: {BACKUP_FILENAME}")
                print("   Available backups:")
                for backup in backups[:3]:
                    print(f"      - {backup['filename']}")
                return
        else:
            print(f"   ❌ Backup listing failed: {response.status_code}")
            return
    except Exception as e:
        print(f"   ❌ Backup listing error: {e}")
        return
    
    # 4. Test restore API call
    print("\n4. Restore API test...")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        payload = {"filename": BACKUP_FILENAME, "force": True}
        
        print(f"   Attempting restore of: {BACKUP_FILENAME}")
        response = requests.post(f"{BACKEND_URL}/database/restore", 
                               headers=headers, 
                               json=payload,
                               timeout=120)  # 2 minute timeout
        
        print(f"   Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("   ✅ Restore API call successful!")
            print(f"   Execution time: {data['data']['execution_time_ms']}ms")
            verification = data['data'].get('verification', {})
            if verification.get('verified'):
                print(f"   Verification: {verification['users_count']} users found")
            else:
                print(f"   Verification failed: {verification.get('error', 'Unknown error')}")
        else:
            print("   ❌ Restore API call failed")
            try:
                error_data = response.json()
                print(f"   Error: {error_data.get('message', 'Unknown error')}")
                if 'error' in error_data:
                    print(f"   Details: {error_data['error']}")
            except:
                print(f"   Raw response: {response.text}")
        
    except requests.Timeout:
        print("   ❌ Restore request timed out (2+ minutes)")
    except Exception as e:
        print(f"   ❌ Restore API error: {e}")
    
    print("\n" + "=" * 50)
    print("🏁 Diagnostic complete")

if __name__ == "__main__":
    main()
