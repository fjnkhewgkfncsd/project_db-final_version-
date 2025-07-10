#!/usr/bin/env python3
"""
Comprehensive Restore Functionality Test
Tests both command-line restore script and API restore endpoint
"""

import os
import sys
import time
import subprocess
import requests
import json
from pathlib import Path

BASE_URL = "http://localhost:3001"
PROJECT_ROOT = Path(__file__).parent
DB_DIR = PROJECT_ROOT / "db"
BACKUPS_DIR = PROJECT_ROOT / "backups"

def run_command(cmd, cwd=None):
    """Run a command and return the result"""
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            capture_output=True, 
            text=True, 
            cwd=cwd or PROJECT_ROOT
        )
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def test_command_line_restore():
    """Test the command line restore functionality"""
    print("\n" + "="*60)
    print("🧪 TESTING COMMAND LINE RESTORE FUNCTIONALITY")
    print("="*60)
    
    os.chdir(DB_DIR)
    
    # Test 1: List available backups
    print("\n1. 📋 Testing Backup Listing...")
    success, stdout, stderr = run_command("python restore.py --list", cwd=DB_DIR)
    
    if success and "Available Backups" in stdout:
        lines = stdout.split('\n')
        backup_count = len([line for line in lines if line.strip().endswith('.sql')])
        print(f"   ✅ Found {backup_count} backup files")
        
        # Extract latest backup for testing
        latest_backup = None
        for line in lines:
            if ".sql" in line and "Path:" in line:
                latest_backup = line.split("Path: ")[-1].strip()
                break
        
        if latest_backup:
            print(f"   📄 Latest backup: {os.path.basename(latest_backup)}")
            
            # Test 2: Dry run verification
            print("\n2. 🔍 Testing Backup File Verification...")
            if os.path.exists(latest_backup):
                file_size = os.path.getsize(latest_backup)
                print(f"   ✅ Backup file exists ({file_size:,} bytes)")
                
                # Test 3: Restore from latest backup
                print("\n3. 🔄 Testing Database Restore...")
                restore_cmd = f"python restore.py --latest --force"
                success, stdout, stderr = run_command(restore_cmd, cwd=DB_DIR)
                
                if success:
                    print("   ✅ Command line restore completed successfully")
                    
                    # Check if verification passed
                    if "Restore verification completed successfully" in stdout:
                        print("   ✅ Post-restore verification passed")
                    else:
                        print("   ⚠️ Post-restore verification not confirmed")
                    
                    # Check execution time
                    if "Restore completed in" in stdout:
                        time_line = [line for line in stdout.split('\n') if "Restore completed in" in line][0]
                        print(f"   ⏱️ {time_line.strip()}")
                        
                    return True
                else:
                    print(f"   ❌ Restore failed: {stderr}")
                    return False
            else:
                print(f"   ❌ Backup file not found: {latest_backup}")
                return False
        else:
            print("   ❌ Could not find latest backup path")
            return False
    else:
        print(f"   ❌ Failed to list backups: {stderr}")
        return False

def test_api_restore():
    """Test the API restore functionality"""
    print("\n" + "="*60)
    print("🧪 TESTING API RESTORE FUNCTIONALITY")
    print("="*60)
    
    # Test 1: Login to get authentication token
    print("\n1. 🔐 Testing Authentication...")
    login_data = {
        "email": "admin@example.com",
        "password": "admin123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/users/login", json=login_data, timeout=10)
        if response.status_code == 200:
            token = response.json()["data"]["token"]
            print("   ✅ Authentication successful")
            headers = {"Authorization": f"Bearer {token}"}
        else:
            print(f"   ❌ Authentication failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Authentication error: {e}")
        return False
    
    # Test 2: Get available backups via API
    print("\n2. 📋 Testing API Backup Listing...")
    try:
        response = requests.get(f"{BASE_URL}/api/database/backups", headers=headers, timeout=10)
        if response.status_code == 200:
            backup_data = response.json()["data"]
            backup_files = backup_data.get("backups", [])
            print(f"   ✅ API returned {len(backup_files)} backup files")
            
            if backup_files:
                latest_backup = backup_files[0]["filename"]
                print(f"   📄 Latest backup: {latest_backup}")
                
                # Test 3: Restore via API
                print("\n3. 🔄 Testing API Database Restore...")
                restore_data = {"filename": latest_backup}
                response = requests.post(
                    f"{BASE_URL}/api/database/restore", 
                    json=restore_data, 
                    headers=headers,
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()["data"]
                    print("   ✅ API restore completed successfully")
                    print(f"   📄 Restored file: {result['filename']}")
                    print(f"   📊 File size: {result.get('file_size', 'Unknown')}")
                    print(f"   ⏱️ Execution time: {result['execution_time_ms']}ms")
                    print(f"   🔍 Verification: {result.get('verification', {}).get('verified', 'Unknown')}")
                    
                    return True
                else:
                    error_msg = response.json().get('message', 'Unknown error')
                    print(f"   ❌ API restore failed: {error_msg}")
                    return False
            else:
                print("   ⚠️ No backup files available via API")
                return False
        else:
            print(f"   ❌ Failed to get backups via API: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ API backup listing error: {e}")
        return False

def test_database_connectivity():
    """Test database connectivity after restore"""
    print("\n" + "="*60)
    print("🧪 TESTING POST-RESTORE DATABASE CONNECTIVITY")
    print("="*60)
    
    # Test basic database queries via API
    print("\n1. 🔍 Testing Database Queries...")
    
    test_queries = [
        ("SELECT COUNT(*) as user_count FROM users", "User count"),
        ("SELECT COUNT(*) as product_count FROM products", "Product count"),
        ("SELECT COUNT(*) as order_count FROM orders", "Order count"),
        ("SELECT version() as db_version", "Database version")
    ]
    
    # Login first
    login_data = {"email": "admin@example.com", "password": "admin123"}
    try:
        response = requests.post(f"{BASE_URL}/api/users/login", json=login_data, timeout=10)
        if response.status_code == 200:
            token = response.json()["data"]["token"]
            headers = {"Authorization": f"Bearer {token}"}
        else:
            print("   ❌ Could not authenticate for database tests")
            return False
    except Exception as e:
        print(f"   ❌ Authentication error: {e}")
        return False
    
    success_count = 0
    for query, description in test_queries:
        try:
            response = requests.post(
                f"{BASE_URL}/api/database/query",
                json={"sql": query},
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()["data"]
                row_count = result["row_count"]
                execution_time = result["execution_time_ms"]
                
                if result["rows"]:
                    value = list(result["rows"][0].values())[0]
                    print(f"   ✅ {description}: {value} (in {execution_time}ms)")
                else:
                    print(f"   ✅ {description}: Query executed (in {execution_time}ms)")
                success_count += 1
            else:
                print(f"   ❌ {description}: Query failed")
        except Exception as e:
            print(f"   ❌ {description}: Error - {e}")
    
    print(f"\n   📊 Database connectivity test: {success_count}/{len(test_queries)} queries successful")
    return success_count == len(test_queries)

def check_server_status():
    """Check if the backend server is running"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def main():
    """Run comprehensive restore tests"""
    print("🧪 COMPREHENSIVE RESTORE FUNCTIONALITY TEST")
    print("=" * 60)
    print(f"Project Root: {PROJECT_ROOT}")
    print(f"DB Directory: {DB_DIR}")
    print(f"Backups Directory: {BACKUPS_DIR}")
    print(f"Backend URL: {BASE_URL}")
    
    # Check if backups exist
    if not BACKUPS_DIR.exists():
        print(f"\n❌ Backups directory not found: {BACKUPS_DIR}")
        sys.exit(1)
    
    backup_files = list(BACKUPS_DIR.glob("*.sql"))
    if not backup_files:
        print(f"\n❌ No backup files found in: {BACKUPS_DIR}")
        sys.exit(1)
    
    print(f"\n📁 Found {len(backup_files)} backup files")
    
    # Test 1: Command line restore
    cmd_success = test_command_line_restore()
    
    # Test 2: Check if server is running for API tests
    if check_server_status():
        api_success = test_api_restore()
        db_success = test_database_connectivity()
    else:
        print(f"\n⚠️ Backend server not running at {BASE_URL}")
        print("   Skipping API tests...")
        api_success = None
        db_success = None
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    print(f"Command Line Restore: {'✅ PASS' if cmd_success else '❌ FAIL'}")
    if api_success is not None:
        print(f"API Restore:          {'✅ PASS' if api_success else '❌ FAIL'}")
        print(f"Database Connectivity: {'✅ PASS' if db_success else '❌ FAIL'}")
    else:
        print("API Restore:          ⏭️ SKIPPED (server not running)")
        print("Database Connectivity: ⏭️ SKIPPED (server not running)")
    
    # Overall result
    if cmd_success and (api_success is None or (api_success and db_success)):
        print("\n🎉 ALL TESTS PASSED!")
        return True
    else:
        print("\n❌ SOME TESTS FAILED!")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
