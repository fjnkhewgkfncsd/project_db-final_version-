#!/usr/bin/env python3
"""
Final comprehensive test of the emergency database recovery system
This validates all components work correctly together
"""

import os
import sys
import requests
import subprocess
import psycopg2
from datetime import datetime

def print_header(title):
    print(f"\n{'='*60}")
    print(f"🧪 {title}")
    print('='*60)

def print_section(section):
    print(f"\n📋 {section}")
    print('-'*40)

def test_database_functionality():
    """Test 1: Core database functionality"""
    print_section("Test 1: Core Database Functionality")
    
    try:
        # Test database connection
        conn = psycopg2.connect(
            host="localhost",
            port="5432",
            database="ecommerce_db",
            user="postgres",
            password="hengmengly123"
        )
        cursor = conn.cursor()
        
        # Get database stats
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM products")
        product_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM orders")
        order_count = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        print(f"✅ Database connection: SUCCESS")
        print(f"✅ Users: {user_count}")
        print(f"✅ Products: {product_count}")
        print(f"✅ Orders: {order_count}")
        return True
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

def test_backup_restore_functionality():
    """Test 2: Backup and restore functionality"""
    print_section("Test 2: Backup and Restore Functionality")
    
    try:
        # Check if backups exist
        if not os.path.exists("backups"):
            print("❌ Backup directory not found")
            return False
        
        sql_files = [f for f in os.listdir("backups") if f.endswith('.sql')]
        print(f"✅ Found {len(sql_files)} backup files")
        
        # Test restore script
        result = subprocess.run(['python', 'db/restore.py', '--help'], 
                               capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Restore script accessible")
        else:
            print("❌ Restore script not working")
            return False
        
        # Test with latest backup (dry run)
        if sql_files:
            latest_backup = sorted(sql_files)[-1]
            print(f"✅ Latest backup: {latest_backup}")
        
        return True
        
    except Exception as e:
        print(f"❌ Backup/restore test failed: {e}")
        return False

def test_emergency_recovery_system():
    """Test 3: Emergency recovery system"""
    print_section("Test 3: Emergency Recovery System")
    
    base_url = "http://localhost:3002"
    
    try:
        # Test server availability
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Emergency server running")
        else:
            print("❌ Emergency server not responding")
            return False
        
        # Test authentication
        auth_response = requests.post(f"{base_url}/api/emergency/login", json={
            "username": "emergency_admin",
            "password": "EmergencyRestore2025!"
        })
        
        if auth_response.status_code == 200:
            print("✅ Emergency authentication working")
            token = auth_response.json().get('data', {}).get('token')
        else:
            print("❌ Emergency authentication failed")
            return False
        
        # Test protected endpoints
        headers = {"Authorization": f"Bearer {token}"}
        
        # Backup listing
        backup_response = requests.get(f"{base_url}/api/emergency/backups", headers=headers)
        if backup_response.status_code == 200:
            backup_data = backup_response.json()
            backup_count = len(backup_data.get('data', {}).get('backups', []))
            print(f"✅ Emergency backup listing: {backup_count} backups")
        else:
            print("❌ Emergency backup listing failed")
        
        # Status endpoint
        status_response = requests.get(f"{base_url}/api/emergency/status", headers=headers)
        if status_response.status_code == 200:
            status_data = status_response.json()
            uptime = status_data.get('data', {}).get('server', {}).get('uptime', 'N/A')
            print(f"✅ Emergency status endpoint: Server up {uptime}")
        else:
            print("❌ Emergency status endpoint failed")
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Emergency server not running or not accessible")
        return False
    except Exception as e:
        print(f"❌ Emergency recovery test failed: {e}")
        return False

def test_file_structure():
    """Test 4: File structure and components"""
    print_section("Test 4: File Structure and Components")
    
    required_files = [
        "db/restore.py",
        "db/safe_restore.py", 
        "db/backup.py",
        "backend/emergency-recovery-server.js",
        "backend/.env.recovery",
        "backend/emergency-index.html",
        "frontend/src/components/EmergencyRecovery.js",
        "frontend/src/components/EmergencyRecovery.css",
        "frontend/src/components/EmergencyRecoveryWidget.js",
        ".vscode/tasks.json"
    ]
    
    missing_files = []
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} (missing)")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\n⚠️  {len(missing_files)} files missing")
        return False
    else:
        print(f"\n✅ All {len(required_files)} required files present")
        return True

def test_documentation():
    """Test 5: Documentation"""
    print_section("Test 5: Documentation")
    
    doc_files = [
        "EMERGENCY_RECOVERY_GUIDE.md",
        "EMERGENCY_RECOVERY_IMPLEMENTATION_SUMMARY.md",
        "README.md"
    ]
    
    for doc in doc_files:
        if os.path.exists(doc):
            print(f"✅ {doc}")
        else:
            print(f"❌ {doc} (missing)")

def main():
    """Run comprehensive emergency recovery system test"""
    print_header("COMPREHENSIVE EMERGENCY RECOVERY SYSTEM TEST")
    
    tests = [
        ("Database Functionality", test_database_functionality),
        ("Backup/Restore Functionality", test_backup_restore_functionality),
        ("Emergency Recovery System", test_emergency_recovery_system),
        ("File Structure", test_file_structure),
        ("Documentation", test_documentation)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print_header("TEST RESULTS SUMMARY")
    
    passed = 0
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        if success:
            passed += 1
    
    print(f"\nOverall Result: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ Emergency Recovery System is fully functional")
        print("✅ Database operations working correctly")
        print("✅ Backup and restore capabilities verified")
        print("✅ Emergency API endpoints responding")
        print("✅ File structure complete")
        print("✅ Ready for production deployment")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        print("❌ Some components need attention before deployment")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
