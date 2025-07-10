import requests
import json

# Test the demo credentials
test_credentials = [
    {"email": "adam.hernandez.183@example.com", "role": "admin"},
    {"email": "aaron.campbell.2989@example.com", "role": "staff"}
]

print("🧪 Testing Demo Credentials")
print("="*40)

for cred in test_credentials:
    print(f"\n🔐 Testing {cred['role'].upper()}: {cred['email']}")
    
    login_data = {
        'email': cred['email'],
        'password': 'password123'
    }
    
    try:
        response = requests.post('http://localhost:3001/api/users/login', 
                               json=login_data, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            user_info = data['data']['user']
            print(f"   ✅ Login successful!")
            print(f"   👤 Username: {user_info['username']}")
            print(f"   📧 Email: {user_info['email']}")
            print(f"   🎭 Role: {user_info['role']}")
            print(f"   🔑 Token received: Yes")
        else:
            print(f"   ❌ Login failed: {response.status_code}")
            print(f"   📝 Response: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")

print(f"\n✅ Demo credentials testing complete!")
print(f"📋 Full credential list available in DEMO_CREDENTIALS.md")
