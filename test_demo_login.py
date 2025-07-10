import requests
import json

# Test the demo credentials
demo_accounts = [
    {"email": "admin@example.com", "password": "admin123", "role": "admin"},
    {"email": "staff@example.com", "password": "staff123", "role": "staff"},
    {"email": "customer@example.com", "password": "customer123", "role": "customer"}
]

print("🧪 Testing Demo Login Credentials")
print("=" * 40)

for account in demo_accounts:
    print(f"\n🔐 Testing {account['role'].upper()}: {account['email']}")
    
    try:
        response = requests.post('http://localhost:3001/api/users/login', 
                               json={'email': account['email'], 'password': account['password']}, 
                               timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            user_info = data['data']['user']
            print(f"   ✅ Login successful!")
            print(f"   👤 Username: {user_info['username']}")
            print(f"   🎭 Role: {user_info['role']}")
        else:
            print(f"   ❌ Login failed: {response.status_code}")
            print(f"   📝 Response: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")

print(f"\n📋 Demo credentials test complete!")
