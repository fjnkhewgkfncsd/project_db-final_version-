#!/usr/bin/env python3
"""
Test multiple restore scenarios to identify specific failures
"""

import requests
import json
import time

BACKEND_URL = "http://localhost:3001/api"
ADMIN_CREDENTIALS = {"email": "admin@example.com", "password": "admin123"}

def get_token():
    response = requests.post(f"{BACKEND_URL}/users/login", json=ADMIN_CREDENTIALS)
    return response.json()['data']['token']

def test_different_backups():
    """Test restore with different backup files"""
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get list of available backups
    response = requests.get(f"{BACKEND_URL}/database/backups", headers=headers)
    backups = response.json()['data']['backups']
    
    print("🧪 TESTING DIFFERENT BACKUP FILES")
    print("=" * 60)
    
    # Test with 3 different backup files
    test_backups = backups[:3] if len(backups) >= 3 else backups
    
    for i, backup in enumerate(test_backups, 1):
        filename = backup['filename']
        size = backup['size']
        
        print(f"\n{i}. Testing: {filename} ({size})")
        
        try:
            payload = {"filename": filename, "force": True}
            start_time = time.time()
            
            response = requests.post(f"{BACKEND_URL}/database/restore", 
                                   headers=headers, 
                                   json=payload,
                                   timeout=90)
            
            end_time = time.time()
            elapsed = (end_time - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                exec_time = data['data']['execution_time_ms']
                verification = data['data']['verification']
                
                print(f"   ✅ SUCCESS")
                print(f"   API time: {elapsed:.0f}ms, DB time: {exec_time}ms")
                print(f"   Users: {verification.get('users_count', 'Unknown')}")
            else:
                print(f"   ❌ FAILED: {response.status_code}")
                try:
                    error = response.json()
                    print(f"   Error: {error.get('message', 'Unknown')}")
                except:
                    print(f"   Raw error: {response.text[:100]}")
        
        except requests.Timeout:
            print(f"   ❌ TIMEOUT (90+ seconds)")
        except Exception as e:
            print(f"   ❌ EXCEPTION: {e}")

def test_invalid_scenarios():
    """Test error handling scenarios"""
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    print("\n🚨 TESTING ERROR SCENARIOS")
    print("=" * 60)
    
    scenarios = [
        {"filename": "nonexistent.sql", "expected": "Backup file not found"},
        {"filename": "", "expected": "Backup filename is required"},
        {"filename": "test.unsupported", "expected": "Unsupported backup file format"}
    ]
    
    for scenario in scenarios:
        filename = scenario['filename']
        expected = scenario['expected']
        
        print(f"\nTesting: {filename or '(empty)'}")
        
        try:
            payload = {"filename": filename, "force": True}
            response = requests.post(f"{BACKEND_URL}/database/restore", 
                                   headers=headers, 
                                   json=payload,
                                   timeout=30)
            
            if response.status_code != 200:
                error_data = response.json()
                error_msg = error_data.get('message', 'Unknown error')
                
                if expected.lower() in error_msg.lower():
                    print(f"   ✅ Expected error: {error_msg}")
                else:
                    print(f"   ⚠️ Unexpected error: {error_msg}")
            else:
                print(f"   ❌ Unexpectedly succeeded")
                
        except Exception as e:
            print(f"   ❌ Exception: {e}")

def check_database_state():
    """Check current database state"""
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    print("\n🔍 DATABASE STATE CHECK")
    print("=" * 60)
    
    try:
        # Check user count
        response = requests.post(f"{BACKEND_URL}/database/query", 
                               headers=headers,
                               json={"sql": "SELECT COUNT(*) as count FROM users"})
        
        if response.status_code == 200:
            count = response.json()['data']['rows'][0]['count']
            print(f"Current users in database: {count}")
        else:
            print("Could not query user count")
            
        # Check database stats
        response = requests.get(f"{BACKEND_URL}/database/stats", headers=headers)
        if response.status_code == 200:
            stats = response.json()['data']
            print(f"Database size: {stats['database_info']['size']}")
            print(f"Active connections: {stats['connections']['active_connections']}")
        else:
            print("Could not get database stats")
            
    except Exception as e:
        print(f"Database state check failed: {e}")

def main():
    print("🔬 COMPREHENSIVE RESTORE TESTING")
    print("=" * 80)
    
    check_database_state()
    test_different_backups()
    test_invalid_scenarios()
    
    print("\n🏁 Testing complete")

if __name__ == "__main__":
    main()
