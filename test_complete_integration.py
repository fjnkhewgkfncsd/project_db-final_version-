#!/usr/bin/env python3
"""
Complete Database Recovery System Integration Test
Tests both the emergency recovery system and its integration with the main application
"""

import requests
import json
import sys
import time
from datetime import datetime

# Configuration
MAIN_APP_BASE = "http://localhost:3001/api"
EMERGENCY_API_BASE = "http://localhost:3002/api/emergency"
FRONTEND_BASE = "http://localhost:3000"

ADMIN_CREDENTIALS = {
    "email": "admin@example.com",
    "password": "admin123"
}

EMERGENCY_CREDENTIALS = {
    "username": "emergency_admin",
    "password": "EmergencyRestore2025!"
}

def test_main_app_login():
    """Test main application admin login"""
    print("🔐 Testing Main Application Login...")
    
    try:
        response = requests.post(f"{MAIN_APP_BASE}/users/login", json=ADMIN_CREDENTIALS)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ Main app admin login successful!")
                print(f"   Admin: {data['data']['user']['first_name']} {data['data']['user']['last_name']}")
                print(f"   Role: {data['data']['user']['role']}")
                return data['data']['token']
            else:
                print(f"❌ Login failed: {data.get('message')}")
                return None
        else:
            print(f"❌ Login request failed with status {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Login error: {e}")
        return None

def test_emergency_recovery():
    """Test emergency recovery system"""
    print("\n🚨 Testing Emergency Recovery System...")
    
    try:
        # Test emergency login
        response = requests.post(f"{EMERGENCY_API_BASE}/login", json=EMERGENCY_CREDENTIALS)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ Emergency authentication successful!")
                emergency_token = data['data']['token']
                
                # Test backup listing
                headers = {"Authorization": f"Bearer {emergency_token}"}
                backup_response = requests.get(f"{EMERGENCY_API_BASE}/backups", headers=headers)
                
                if backup_response.status_code == 200:
                    backup_data = backup_response.json()
                    if backup_data.get('success'):
                        backups = backup_data['data']['backups']
                        print(f"✅ Found {len(backups)} backup files")
                        if backups:
                            latest = backups[0]
                            print(f"   Latest: {latest['filename']} ({latest['sizeFormatted']})")
                        return True
                    else:
                        print(f"❌ Backup listing failed: {backup_data.get('message')}")
                        return False
                else:
                    print(f"❌ Backup listing request failed: {backup_response.status_code}")
                    return False
            else:
                print(f"❌ Emergency login failed: {data.get('message')}")
                return False
        else:
            print(f"❌ Emergency login request failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Emergency recovery error: {e}")
        return False

def test_frontend_integration():
    """Test frontend integration"""
    print("\n🌐 Testing Frontend Integration...")
    
    try:
        # Test main frontend
        response = requests.get(FRONTEND_BASE, timeout=5)
        if response.status_code == 200:
            print("✅ Main frontend accessible")
        else:
            print(f"❌ Main frontend returned {response.status_code}")
            return False
        
        # Test emergency recovery frontend
        response = requests.get("http://localhost:3002", timeout=5)
        if response.status_code == 200:
            print("✅ Emergency recovery frontend accessible")
        else:
            print(f"❌ Emergency recovery frontend returned {response.status_code}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Frontend integration error: {e}")
        return False

def test_database_backup_through_main_app(admin_token):
    """Test database backup through main application"""
    print("\n💾 Testing Database Backup via Main App...")
    
    try:
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.post(f"{MAIN_APP_BASE}/database/backup", json={}, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ Database backup successful!")
                print(f"   Filename: {data['data']['filename']}")
                print(f"   Size: {data['data']['size']}")
                print(f"   Timestamp: {data['data']['timestamp']}")
                return True
            else:
                print(f"❌ Backup failed: {data.get('message')}")
                return False
        else:
            print(f"❌ Backup request failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Backup error: {e}")
        return False

def test_system_health():
    """Test overall system health"""
    print("\n❤️ Testing System Health...")
    
    health_checks = []
    
    # Get admin token for authenticated requests
    admin_token = None
    try:
        response = requests.post(f"{MAIN_APP_BASE}/users/login", json=ADMIN_CREDENTIALS)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                admin_token = data['data']['token']
    except:
        pass
    
    # Main backend health
    try:
        headers = {"Authorization": f"Bearer {admin_token}"} if admin_token else {}
        response = requests.get(f"{MAIN_APP_BASE}/analytics/system-status", headers=headers, timeout=5)
        if response.status_code == 200:
            health_checks.append(("Main Backend", "✅ Healthy"))
        else:
            health_checks.append(("Main Backend", f"❌ Status {response.status_code}"))
    except:
        health_checks.append(("Main Backend", "❌ Unreachable"))
    
    # Emergency recovery health
    try:
        response = requests.get("http://localhost:3002/health", timeout=5)
        if response.status_code == 200:
            health_checks.append(("Emergency Recovery", "✅ Healthy"))
        else:
            health_checks.append(("Emergency Recovery", f"❌ Status {response.status_code}"))
    except:
        health_checks.append(("Emergency Recovery", "❌ Unreachable"))
    
    # Database connectivity (through emergency system)
    try:
        emergency_response = requests.post(f"{EMERGENCY_API_BASE}/login", json=EMERGENCY_CREDENTIALS)
        if emergency_response.status_code == 200:
            token = emergency_response.json()['data']['token']
            headers = {"Authorization": f"Bearer {token}"}
            db_response = requests.get(f"{EMERGENCY_API_BASE}/database-status", headers=headers)
            if db_response.status_code == 200:
                db_data = db_response.json()['data']
                status = "✅ Online" if db_data['status'] == 'online' else "❌ Offline"
                health_checks.append(("Database", f"{status} - {db_data['message']}"))
            else:
                health_checks.append(("Database", "❌ Status check failed"))
        else:
            health_checks.append(("Database", "❌ Cannot authenticate to check"))
    except:
        health_checks.append(("Database", "❌ Unreachable"))
    
    for component, status in health_checks:
        print(f"   {component}: {status}")
    
    return all("✅" in status for _, status in health_checks)

def main():
    """Run complete integration test"""
    print("🧪 COMPLETE DATABASE RECOVERY SYSTEM TEST")
    print("=" * 60)
    print(f"🕒 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    results = {}
    
    # Test main application login
    admin_token = test_main_app_login()
    results['main_login'] = admin_token is not None
    
    # Test emergency recovery system
    results['emergency_recovery'] = test_emergency_recovery()
    
    # Test frontend integration
    results['frontend_integration'] = test_frontend_integration()
    
    # Test database backup (if main app login worked)
    if admin_token:
        results['database_backup'] = test_database_backup_through_main_app(admin_token)
    else:
        results['database_backup'] = False
        print("\n💾 Skipping database backup test (no admin token)")
    
    # Test system health
    results['system_health'] = test_system_health()
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 INTEGRATION TEST SUMMARY")
    print("=" * 60)
    
    test_results = [
        ("Main Application Login", results['main_login']),
        ("Emergency Recovery System", results['emergency_recovery']),
        ("Frontend Integration", results['frontend_integration']),
        ("Database Backup", results['database_backup']),
        ("System Health", results['system_health'])
    ]
    
    for test_name, passed in test_results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"   {test_name}: {status}")
    
    overall_success = all(result for result in results.values())
    
    print(f"\n🎯 Overall Result: {'✅ ALL SYSTEMS OPERATIONAL' if overall_success else '❌ ISSUES DETECTED'}")
    
    if overall_success:
        print("\n🚀 SYSTEM READY FOR PRODUCTION")
        print("📋 Features Available:")
        print("   • Regular database operations through main app")
        print("   • Emergency database recovery when main app fails")
        print("   • Admin dashboard with emergency recovery widget")
        print("   • Comprehensive backup and restore capabilities")
        print("   • Real-time system monitoring and status")
        print("\n🔗 Access Points:")
        print(f"   • Main Application: {FRONTEND_BASE}")
        print(f"   • Emergency Recovery: http://localhost:3002")
        print(f"   • Emergency Route: {FRONTEND_BASE}/emergency-recovery")
    else:
        print("\n🔧 TROUBLESHOOTING NEEDED")
        print("Review failed tests above and check:")
        print("   • All servers are running (ports 3000, 3001, 3002)")
        print("   • Database is accessible")
        print("   • Environment variables are set correctly")
        print("   • Network connectivity is working")
    
    return 0 if overall_success else 1

if __name__ == "__main__":
    sys.exit(main())
