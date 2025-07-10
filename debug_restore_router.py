#!/usr/bin/env python3
"""
Debug script to identify restore router issues
"""

import requests
import json
import subprocess
import os

# Configuration
BACKEND_URL = "http://localhost:3001/api"
BACKUP_FILENAME = "ecommerce_backup_2025-07-08_21-55-18.sql"  # Latest backup

# Demo credentials (admin user)
ADMIN_CREDENTIALS = {
    "email": "admin@example.com", 
    "password": "admin123"
}

def get_auth_token():
    """Get authentication token"""
    print("🔐 Getting authentication token...")
    response = requests.post(f"{BACKEND_URL}/users/login", json=ADMIN_CREDENTIALS)
    
    if response.status_code == 200:
        data = response.json()
        token = data.get('data', {}).get('token') or data.get('token')
        print("✅ Authentication successful")
        return token
    else:
        print(f"❌ Authentication failed: {response.status_code} - {response.text}")
        return None

def check_backup_exists():
    """Check if backup file exists"""
    backup_path = f"d:\\year2\\year2_term3\\DatabaseAdmin\\project_db(v2)\\backups\\{BACKUP_FILENAME}"
    exists = os.path.exists(backup_path)
    size = os.path.getsize(backup_path) if exists else 0
    
    print(f"📁 Backup file check:")
    print(f"   Path: {backup_path}")
    print(f"   Exists: {exists}")
    print(f"   Size: {size / (1024*1024):.2f} MB" if exists else "   Size: N/A")
    
    return exists

def test_manual_restore():
    """Test manual psql restore command"""
    print("\n🔧 Testing manual psql restore...")
    
    backup_path = f"d:\\year2\\year2_term3\\DatabaseAdmin\\project_db(v2)\\backups\\{BACKUP_FILENAME}"
    
    # Test command that the router uses
    cmd = [
        "psql",
        "-h", "localhost",
        "-p", "5432", 
        "-U", "postgres",
        "-d", "postgres",
        "--no-password",
        "-f", backup_path
    ]
    
    env = os.environ.copy()
    env["PGPASSWORD"] = "hengmengly123"
    
    print(f"   Command: {' '.join(cmd)}")
    print(f"   PGPASSWORD: {env.get('PGPASSWORD', 'Not set')}")
    
    try:
        result = subprocess.run(cmd, env=env, capture_output=True, text=True, timeout=30)
        print(f"   Exit code: {result.returncode}")
        print(f"   Stdout: {result.stdout[:200]}..." if result.stdout else "   Stdout: (empty)")
        print(f"   Stderr: {result.stderr[:200]}..." if result.stderr else "   Stderr: (empty)")
        
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print("   ❌ Command timed out")
        return False
    except Exception as e:
        print(f"   ❌ Command failed: {e}")
        return False

def test_api_restore(token):
    """Test the API restore endpoint"""
    print("\n🌐 Testing API restore endpoint...")
    
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "filename": BACKUP_FILENAME,
        "force": True
    }
    
    print(f"   Endpoint: {BACKEND_URL}/database/restore")
    print(f"   Filename: {BACKUP_FILENAME}")
    
    try:
        response = requests.post(f"{BACKEND_URL}/database/restore", 
                               headers=headers, 
                               json=payload,
                               timeout=60)
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ API restore successful!")
            print(f"   Execution time: {data['data']['execution_time_ms']}ms")
            print(f"   Verification: {data['data']['verification']}")
            return True
        else:
            print(f"❌ API restore failed")
            try:
                error_data = response.json()
                print(f"   Error: {error_data.get('message', 'Unknown error')}")
                if 'error' in error_data:
                    print(f"   Details: {error_data['error']}")
            except:
                print(f"   Raw response: {response.text}")
            return False
            
    except requests.Timeout:
        print("   ❌ Request timed out")
        return False
    except Exception as e:
        print(f"   ❌ Request failed: {e}")
        return False

def check_database_connection():
    """Check if database is accessible"""
    print("\n🔗 Testing database connection...")
    
    try:
        result = subprocess.run([
            "psql", 
            "-h", "localhost",
            "-p", "5432",
            "-U", "postgres", 
            "-d", "ecommerce_db",
            "--no-password",
            "-c", "SELECT current_database(), current_user, COUNT(*) FROM users;"
        ], env={"PGPASSWORD": "hengmengly123"}, capture_output=True, text=True, timeout=10)
        
        print(f"   Exit code: {result.returncode}")
        if result.returncode == 0:
            print("✅ Database connection successful")
            print(f"   Result: {result.stdout.strip()}")
            return True
        else:
            print("❌ Database connection failed")
            print(f"   Error: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"   ❌ Database connection test failed: {e}")
        return False

def check_environment_variables():
    """Check environment variables"""
    print("\n🔧 Checking environment variables...")
    
    env_vars = ['DB_HOST', 'DB_PORT', 'DB_NAME', 'DB_USER', 'DB_PASSWORD']
    
    for var in env_vars:
        value = os.environ.get(var, 'Not set')
        # Mask password
        if 'PASSWORD' in var and value != 'Not set':
            value = '*' * len(value)
        print(f"   {var}: {value}")

def main():
    """Main diagnostic function"""
    print("=" * 80)
    print("🔍 RESTORE ROUTER DIAGNOSTIC")
    print("=" * 80)
    
    # Step 1: Check environment
    check_environment_variables()
    
    # Step 2: Check backup file
    if not check_backup_exists():
        print("\n❌ CRITICAL: Backup file not found!")
        return False
    
    # Step 3: Check database connection
    if not check_database_connection():
        print("\n❌ CRITICAL: Cannot connect to database!")
        return False
    
    # Step 4: Test manual restore
    manual_success = test_manual_restore()
    
    # Step 5: Get auth token
    token = get_auth_token()
    if not token:
        print("\n❌ CRITICAL: Cannot authenticate!")
        return False
    
    # Step 6: Test API restore
    api_success = test_api_restore(token)
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 DIAGNOSTIC SUMMARY")
    print("=" * 80)
    print(f"✅ Backup file exists: ✓")
    print(f"✅ Database connection: {'✓' if check_database_connection() else '✗'}")
    print(f"✅ Manual restore: {'✓' if manual_success else '✗'}")
    print(f"✅ API authentication: ✓")
    print(f"✅ API restore: {'✓' if api_success else '✗'}")
    
    if not api_success:
        print("\n🔧 RECOMMENDATIONS:")
        if not manual_success:
            print("   • Manual psql restore also fails - check PostgreSQL setup")
            print("   • Verify PGPASSWORD environment variable")
            print("   • Check PostgreSQL service is running")
        else:
            print("   • Manual restore works but API fails - check Node.js spawn process")
            print("   • Verify environment variables in Node.js process")
            print("   • Check file paths and permissions")
    
    return api_success

if __name__ == "__main__":
    try:
        success = main()
        exit(0 if success else 1)
    except Exception as e:
        print(f"\n💥 UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
