import requests
import json

# Test query endpoint directly
print("Testing query endpoint...")

# First login to get token
login_data = {'email': 'admin@example.com', 'password': 'admin123'}
login_response = requests.post('http://localhost:3001/api/users/login', json=login_data)
print(f"Login status: {login_response.status_code}")

if login_response.status_code == 200:
    token = login_response.json()['data']['token']
    print("✅ Token received")
    
    headers = {'Authorization': f'Bearer {token}'}
    query_data = {
        'query': 'SELECT COUNT(*) as total FROM users',
        'type': 'select'
    }
    
    try:
        response = requests.post('http://localhost:3001/api/database/query', 
                               json=query_data, headers=headers, timeout=10)
        print(f"Query status: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Query error: {e}")
        
    # Test backup endpoint
    print("\nTesting backup endpoint...")
    backup_data = {'type': 'quick'}
    try:
        response = requests.post('http://localhost:3001/api/database/backup', 
                               json=backup_data, headers=headers, timeout=30)
        print(f"Backup status: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Backup error: {e}")
else:
    print(f"❌ Login failed: {login_response.text}")
