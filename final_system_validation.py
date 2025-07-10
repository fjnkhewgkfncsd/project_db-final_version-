#!/usr/bin/env python3
"""
Final System Validation Script
Comprehensive check of all system components and functionality.
"""

import requests
import json
import time
from datetime import datetime

def test_component(name, test_func):
    """Test a component and report results."""
    print(f"🔍 Testing {name}...")
    try:
        result = test_func()
        if result:
            print(f"   ✅ {name}: PASSED")
            return True
        else:
            print(f"   ❌ {name}: FAILED")
            return False
    except Exception as e:
        print(f"   ❌ {name}: ERROR - {str(e)}")
        return False

def test_backend_health():
    """Test backend health endpoint."""
    response = requests.get('http://localhost:3001/api/health', timeout=5)
    return response.status_code == 200 and response.json().get('success') == True

def test_frontend_server():
    """Test frontend server is responding."""
    response = requests.get('http://localhost:3000', timeout=5)
    return response.status_code == 200

def test_authentication():
    """Test user authentication."""
    login_data = {
        'email': 'admin@example.com',
        'password': 'admin123'
    }
    response = requests.post('http://localhost:3001/api/users/login', 
                           json=login_data, timeout=5)
    data = response.json()
    return response.status_code == 200 and 'token' in data.get('data', {})

def test_database_query():
    """Test database query functionality."""
    # First login to get token
    login_data = {'email': 'admin@example.com', 'password': 'admin123'}
    login_response = requests.post('http://localhost:3001/api/users/login', json=login_data)
    token = login_response.json()['data']['token']
    
    headers = {'Authorization': f'Bearer {token}'}
    query_data = {
        'sql': 'SELECT COUNT(*) as total FROM users'
    }
    response = requests.post('http://localhost:3001/api/database/query', 
                           json=query_data, headers=headers, timeout=10)
    return response.status_code == 200 and 'data' in response.json()

def test_analytics():
    """Test analytics endpoint."""
    # First login to get token
    login_data = {'email': 'admin@example.com', 'password': 'admin123'}
    login_response = requests.post('http://localhost:3001/api/users/login', json=login_data)
    token = login_response.json()['data']['token']
    
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get('http://localhost:3001/api/analytics/dashboard', 
                          headers=headers, timeout=10)
    return response.status_code == 200 and 'data' in response.json()

def test_backup_system():
    """Test backup system."""
    # First login to get token
    login_data = {'email': 'admin@example.com', 'password': 'admin123'}
    login_response = requests.post('http://localhost:3001/api/users/login', json=login_data)
    token = login_response.json()['data']['token']
    
    headers = {'Authorization': f'Bearer {token}'}
    backup_data = {'type': 'quick'}
    response = requests.post('http://localhost:3001/api/database/backup', 
                           json=backup_data, headers=headers, timeout=30)
    return response.status_code == 200 and 'filename' in response.json().get('data', {})

def test_performance_monitoring():
    """Test performance monitoring."""
    # First login to get token
    login_data = {'email': 'admin@example.com', 'password': 'admin123'}
    login_response = requests.post('http://localhost:3001/api/users/login', json=login_data)
    token = login_response.json()['data']['token']
    
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get('http://localhost:3001/api/analytics/performance', 
                          headers=headers, timeout=10)
    return response.status_code == 200 and 'data' in response.json()

def main():
    """Run all validation tests."""
    print("🚀 FINAL SYSTEM VALIDATION")
    print("=" * 50)
    print(f"🕒 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    tests = [
        ("Backend Health", test_backend_health),
        ("Frontend Server", test_frontend_server),
        ("User Authentication", test_authentication),
        ("Database Query Engine", test_database_query),
        ("Analytics Dashboard", test_analytics),
        ("Backup System", test_backup_system),
        ("Performance Monitoring", test_performance_monitoring),
    ]
    
    passed = 0
    total = len(tests)
    
    for name, test_func in tests:
        if test_component(name, test_func):
            passed += 1
        time.sleep(1)  # Brief pause between tests
    
    print()
    print("📊 VALIDATION SUMMARY")
    print("-" * 30)
    print(f"✅ Tests Passed: {passed}/{total}")
    print(f"❌ Tests Failed: {total - passed}/{total}")
    print(f"📈 Success Rate: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("\n🎉 SYSTEM VALIDATION: SUCCESS!")
        print("✅ All components are working correctly")
        print("✅ System is ready for production use")
    else:
        print(f"\n⚠️  SYSTEM VALIDATION: {total - passed} ISSUES FOUND")
        print("❌ Please review failed components")
    
    print(f"\n🕒 Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
