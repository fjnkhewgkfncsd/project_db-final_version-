import requests
import json

# Test login directly
login_data = {
    'email': 'admin@example.com',
    'password': 'admin123'
}

print("Testing login endpoint...")
try:
    response = requests.post('http://localhost:3001/api/users/login', json=login_data, timeout=5)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200:
        data = response.json()
        if 'token' in data:
            print("✅ Login successful - token received")
        else:
            print("❌ Login failed - no token in response")
            print(f"Response keys: {list(data.keys())}")
    else:
        print(f"❌ Login failed with status {response.status_code}")
        
except Exception as e:
    print(f"❌ Error: {e}")
