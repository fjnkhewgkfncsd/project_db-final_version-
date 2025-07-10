#!/usr/bin/env python3

import requests
import json

def test_query_console():
    """Test the query console functionality"""
    base_url = "http://localhost:3001"
    
    print("🧪 Testing Query Console Functionality...")
    
    # First, login as admin
    login_data = {
        "email": "admin@example.com",
        "password": "admin123"
    }
    
    try:
        print("\n1. Logging in as admin...")
        response = requests.post(f"{base_url}/api/users/login", json=login_data)
        
        if response.status_code != 200:
            print(f"❌ Login failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
        login_result = response.json()
        token = login_result.get('data', {}).get('token')
        user = login_result.get('data', {}).get('user')
        
        if not token:
            print("❌ No token received")
            return False
            
        print(f"✅ Login successful for user: {user.get('username')} (role: {user.get('role')})")
        
        # Test query execution
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        # Test simple query
        print("\n2. Testing simple SELECT query...")
        query_data = {
            "query": "SELECT COUNT(*) as total_users FROM users;"
        }
        
        response = requests.post(f"{base_url}/api/database/execute-query", 
                               json=query_data, headers=headers)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ Query executed successfully!")
                print(f"Rows returned: {len(result.get('data', {}).get('rows', []))}")
                print(f"Execution time: {result.get('data', {}).get('execution_time_ms')}ms")
            else:
                print(f"❌ Query failed: {result.get('message')}")
        else:
            print(f"❌ Request failed with status {response.status_code}")
            
        # Test a more complex query
        print("\n3. Testing complex query...")
        complex_query_data = {
            "query": "SELECT role, COUNT(*) as count FROM users GROUP BY role ORDER BY count DESC;"
        }
        
        response = requests.post(f"{base_url}/api/database/execute-query", 
                               json=complex_query_data, headers=headers)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ Complex query executed successfully!")
                rows = result.get('data', {}).get('rows', [])
                print(f"Results:")
                for row in rows:
                    print(f"  - {row.get('role')}: {row.get('count')} users")
            else:
                print(f"❌ Complex query failed: {result.get('message')}")
        else:
            print(f"❌ Complex query request failed with status {response.status_code}")
            
        # Test with staff user
        print("\n4. Testing with staff user...")
        staff_login_data = {
            "email": "staff@example.com",
            "password": "staff123"
        }
        
        response = requests.post(f"{base_url}/api/users/login", json=staff_login_data)
        if response.status_code == 200:
            staff_result = response.json()
            staff_token = staff_result.get('data', {}).get('token')
            
            staff_headers = {
                'Authorization': f'Bearer {staff_token}',
                'Content-Type': 'application/json'
            }
            
            staff_query_data = {
                "query": "SELECT COUNT(*) as total_products FROM products;"
            }
            
            response = requests.post(f"{base_url}/api/database/execute-query", 
                                   json=staff_query_data, headers=staff_headers)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    print("✅ Staff query executed successfully!")
                else:
                    print(f"❌ Staff query failed: {result.get('message')}")
            else:
                print(f"❌ Staff query request failed with status {response.status_code}")
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend server. Is it running on port 3001?")
        return False
    except Exception as e:
        print(f"❌ Error during testing: {str(e)}")
        return False

if __name__ == "__main__":
    test_query_console()
