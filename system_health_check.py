#!/usr/bin/env python3

import requests
import json
import sys

def check_system_health():
    """Comprehensive system health check"""
    base_url = "http://localhost:3001"
    frontend_url = "http://localhost:3000"
    
    print("🔍 COMPREHENSIVE SYSTEM HEALTH CHECK")
    print("=" * 60)
    
    errors_found = []
    warnings_found = []
    
    # 1. Test Backend Health
    print("\n1. BACKEND HEALTH CHECK")
    print("-" * 30)
    
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend server is responding")
        else:
            error_msg = f"❌ Backend health check failed: {response.status_code}"
            print(error_msg)
            errors_found.append(error_msg)
    except requests.exceptions.ConnectionError:
        error_msg = "❌ Cannot connect to backend server"
        print(error_msg)
        errors_found.append(error_msg)
    except Exception as e:
        error_msg = f"❌ Backend error: {str(e)}"
        print(error_msg)
        errors_found.append(error_msg)
    
    # 2. Test Frontend Health
    print("\n2. FRONTEND HEALTH CHECK")
    print("-" * 30)
    
    try:
        response = requests.get(frontend_url, timeout=5)
        if response.status_code == 200:
            print("✅ Frontend server is responding")
        else:
            error_msg = f"❌ Frontend health check failed: {response.status_code}"
            print(error_msg)
            errors_found.append(error_msg)
    except requests.exceptions.ConnectionError:
        error_msg = "❌ Cannot connect to frontend server"
        print(error_msg)
        errors_found.append(error_msg)
    except Exception as e:
        error_msg = f"❌ Frontend error: {str(e)}"
        print(error_msg)
        errors_found.append(error_msg)
    
    # 3. Test Database Connection
    print("\n3. DATABASE CONNECTION CHECK")
    print("-" * 30)
    
    try:
        # Try to login first
        login_data = {"email": "admin@example.com", "password": "admin123"}
        response = requests.post(f"{base_url}/api/users/login", json=login_data, timeout=5)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                token = result.get('data', {}).get('token')
                if token:
                    print("✅ Database connection and authentication working")
                    
                    # Test basic database query
                    headers = {'Authorization': f'Bearer {token}'}
                    response = requests.get(f"{base_url}/api/analytics/system-status", headers=headers, timeout=5)
                    
                    if response.status_code == 200:
                        status_result = response.json()
                        if status_result.get('success'):
                            db_status = status_result.get('data', {}).get('database_status')
                            if db_status == 'online':
                                print("✅ Database is online and accessible")
                            else:
                                warning_msg = f"⚠️  Database status: {db_status}"
                                print(warning_msg)
                                warnings_found.append(warning_msg)
                        else:
                            error_msg = f"❌ Database query failed: {status_result.get('message')}"
                            print(error_msg)
                            errors_found.append(error_msg)
                    else:
                        error_msg = f"❌ Database query request failed: {response.status_code}"
                        print(error_msg)
                        errors_found.append(error_msg)
                else:
                    error_msg = "❌ No authentication token received"
                    print(error_msg)
                    errors_found.append(error_msg)
            else:
                error_msg = f"❌ Login failed: {result.get('message')}"
                print(error_msg)
                errors_found.append(error_msg)
        else:
            error_msg = f"❌ Login request failed: {response.status_code}"
            print(error_msg)
            errors_found.append(error_msg)
            
    except Exception as e:
        error_msg = f"❌ Database connection error: {str(e)}"
        print(error_msg)
        errors_found.append(error_msg)
    
    # 4. Test Core API Endpoints
    print("\n4. CORE API ENDPOINTS CHECK")
    print("-" * 30)
    
    if not errors_found:  # Only test if basic connectivity works
        try:
            # Re-login for API tests
            login_data = {"email": "admin@example.com", "password": "admin123"}
            response = requests.post(f"{base_url}/api/users/login", json=login_data)
            token = response.json().get('data', {}).get('token')
            headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
            
            # Test Analytics endpoint
            try:
                response = requests.get(f"{base_url}/api/analytics/system-performance", headers=headers, timeout=5)
                if response.status_code == 200:
                    print("✅ Analytics endpoint working")
                else:
                    error_msg = f"❌ Analytics endpoint failed: {response.status_code}"
                    print(error_msg)
                    errors_found.append(error_msg)
            except Exception as e:
                error_msg = f"❌ Analytics endpoint error: {str(e)}"
                print(error_msg)
                errors_found.append(error_msg)
            
            # Test Database Tools endpoint
            try:
                query_data = {"query": "SELECT COUNT(*) FROM users;"}
                response = requests.post(f"{base_url}/api/database/execute-query", json=query_data, headers=headers, timeout=5)
                if response.status_code == 200:
                    result = response.json()
                    if result.get('success'):
                        print("✅ Database query endpoint working")
                    else:
                        error_msg = f"❌ Database query failed: {result.get('message')}"
                        print(error_msg)
                        errors_found.append(error_msg)
                else:
                    error_msg = f"❌ Database query endpoint failed: {response.status_code}"
                    print(error_msg)
                    errors_found.append(error_msg)
            except Exception as e:
                error_msg = f"❌ Database query endpoint error: {str(e)}"
                print(error_msg)
                errors_found.append(error_msg)
            
            # Test User Management
            try:
                response = requests.get(f"{base_url}/api/users/profile", headers=headers, timeout=5)
                if response.status_code == 200:
                    print("✅ User management endpoint working")
                else:
                    error_msg = f"❌ User management endpoint failed: {response.status_code}"
                    print(error_msg)
                    errors_found.append(error_msg)
            except Exception as e:
                error_msg = f"❌ User management endpoint error: {str(e)}"
                print(error_msg)
                errors_found.append(error_msg)
                
        except Exception as e:
            error_msg = f"❌ API testing error: {str(e)}"
            print(error_msg)
            errors_found.append(error_msg)
    else:
        print("⏭️  Skipping API tests due to basic connectivity issues")
    
    # 5. Check File System Issues
    print("\n5. FILE SYSTEM CHECK")
    print("-" * 30)
    
    import os
    
    # Check if backup directory exists
    backup_dir = "d:\\year2\\year2_term3\\DatabaseAdmin\\project_db\\backups"
    if os.path.exists(backup_dir):
        print("✅ Backup directory exists")
    else:
        warning_msg = "⚠️  Backup directory missing"
        print(warning_msg)
        warnings_found.append(warning_msg)
    
    # Check if .env file exists
    env_file = "d:\\year2\\year2_term3\\DatabaseAdmin\\project_db\\backend\\.env"
    if os.path.exists(env_file):
        print("✅ Backend .env file exists")
    else:
        error_msg = "❌ Backend .env file missing"
        print(error_msg)
        errors_found.append(error_msg)
    
    # Check database schema file
    schema_file = "d:\\year2\\year2_term3\\DatabaseAdmin\\project_db\\db\\schema.sql"
    if os.path.exists(schema_file):
        print("✅ Database schema file exists")
    else:
        error_msg = "❌ Database schema file missing"
        print(error_msg)
        errors_found.append(error_msg)
    
    # 6. Summary
    print(f"\n6. SYSTEM HEALTH SUMMARY")
    print("-" * 30)
    
    if not errors_found and not warnings_found:
        print("🎉 SYSTEM IS HEALTHY!")
        print("✅ All components are working correctly")
        return True
    else:
        print("🚨 ISSUES DETECTED!")
        
        if errors_found:
            print(f"\n❌ CRITICAL ERRORS ({len(errors_found)}):")
            for i, error in enumerate(errors_found, 1):
                print(f"   {i}. {error}")
        
        if warnings_found:
            print(f"\n⚠️  WARNINGS ({len(warnings_found)}):")
            for i, warning in enumerate(warnings_found, 1):
                print(f"   {i}. {warning}")
        
        print(f"\n🔧 RECOMMENDED ACTIONS:")
        if errors_found:
            print("   1. Fix critical errors first")
            print("   2. Restart servers if needed")
            print("   3. Check database connectivity")
            print("   4. Verify configuration files")
        
        if warnings_found:
            print("   5. Address warnings for optimal performance")
        
        return False

if __name__ == "__main__":
    is_healthy = check_system_health()
    sys.exit(0 if is_healthy else 1)
