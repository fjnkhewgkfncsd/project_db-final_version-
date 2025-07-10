#!/usr/bin/env python3
"""
Quick test restore with the safest backup file
"""
import requests
import json

def test_safe_restore():
    """Test restore with the recommended safe backup"""
    
    # Use the best backup file (10,006 users)
    SAFE_BACKUP = "ecommerce_backup_FIXED_MANUAL_2025-07-10_05-32-48.sql"
    BASE_URL = "http://localhost:3001"
    
    print("🧪 TESTING SAFE RESTORE")
    print("=" * 40)
    print(f"📄 Using: {SAFE_BACKUP}")
    print(f"👥 Expected users: 10,006")
    print()
    
    try:
        # Login
        print("🔐 Logging in...")
        login_response = requests.post(f"{BASE_URL}/api/users/login", json={
            "email": "admin@example.com", 
            "password": "admin123"
        })
        
        if login_response.status_code != 200:
            print(f"❌ Login failed: {login_response.text}")
            return False
        
        token = login_response.json()["data"]["token"]
        headers = {"Authorization": f"Bearer {token}"}
        print("✅ Login successful")
        
        # Check current user count
        print("\n📊 Checking current database state...")
        stats_response = requests.get(f"{BASE_URL}/api/database/stats", headers=headers)
        if stats_response.status_code == 200:
            current_users = None
            for record in stats_response.json()["data"]["record_counts"]:
                if record["table_name"] == "users":
                    current_users = record["record_count"]
                    break
            print(f"👥 Current users: {current_users}")
        
        # Perform restore
        print(f"\n🔄 Starting restore with {SAFE_BACKUP}...")
        restore_response = requests.post(f"{BASE_URL}/api/database/restore", 
                                       json={"filename": SAFE_BACKUP}, 
                                       headers=headers, 
                                       timeout=60)
        
        if restore_response.status_code == 200:
            result = restore_response.json()
            verification = result["data"]["verification"]
            
            print("✅ RESTORE SUCCESSFUL!")
            print(f"👥 Users after restore: {verification.get('userCount', 'Unknown')}")
            print(f"📊 File size: {result['data'].get('file_size', 'Unknown')}")
            print(f"⏱️  Execution time: {result['data'].get('execution_time_ms', 0)}ms")
            
            # Verify success
            if verification.get("userCount") == 10006:
                print("\n🎉 PERFECT! Restore worked exactly as expected!")
                return True
            else:
                print(f"\n⚠️  Restore completed but user count unexpected")
                return False
                
        else:
            print(f"❌ Restore failed: {restore_response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Restore timed out")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def list_all_safe_files():
    """List all safe backup files"""
    safe_files = [
        ("ecommerce_backup_FIXED_MANUAL_2025-07-10_05-32-48.sql", 10006, "🏆 BEST"),
        ("ecommerce_backup_2025-07-09_05-01-55.sql", 10006, "🏆 BEST"),
        ("ecommerce_backup_2025-07-09_03-47-34.sql", 10003, "✅ Good"),
        ("ecommerce_backup_2025-07-09_02-46-32.sql", 10003, "✅ Good"),
        ("ecommerce_backup_2025-07-09_02-39-07.sql", 10003, "✅ Good"),
        ("ecommerce_backup_2025-07-09_01-52-43.sql", 10003, "✅ Good"),
        ("ecommerce_backup_2025-07-09_01-51-34.sql", 10002, "✅ Good"),
        ("ecommerce_backup_2025-07-09_01-20-36.sql", 10003, "✅ Good"),
        ("ecommerce_backup_2025-07-09_14-27-30.sql", 10002, "✅ Good"),
        ("ecommerce_backup_2025-07-08_21-55-18.sql", 10002, "✅ Good"),
        ("ecommerce_backup_2025-07-08_21-06-33.sql", 10002, "✅ Good"),
        ("ecommerce_backup_2025-06-27_02-59-02.sql", 10002, "✅ Good")
    ]
    
    print("\n📋 ALL SAFE BACKUP FILES FOR RESTORE")
    print("=" * 60)
    for i, (filename, users, status) in enumerate(safe_files, 1):
        print(f"{i:2d}. {status} {filename}")
        print(f"    👥 Users: {users:,}")
    
    print(f"\n💡 TIP: Use files marked '🏆 BEST' for maximum data recovery")

if __name__ == "__main__":
    list_all_safe_files()
    
    print(f"\n" + "=" * 60)
    user_input = input("🔥 Test restore with the best backup file? (y/N): ")
    
    if user_input.lower() == 'y':
        success = test_safe_restore()
        if success:
            print(f"\n🎉 SUCCESS! Your restore functionality is working perfectly!")
        else:
            print(f"\n❌ Test failed. Check the error messages above.")
    else:
        print(f"\n✅ You can restore safely using any file from the list above!")
