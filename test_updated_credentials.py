import requests
import json

# Test the corrected demo credentials
test_credentials = [
    {"email": "admin@example.com", "password": "admin123", "role": "admin"},
    {"email": "staff@example.com", "password": "staff123", "role": "staff"},
    {"email": "customer@example.com", "password": "customer123", "role": "customer"}
]

print("🧪 Testing Updated Demo Credentials")
print("="*45)

for cred in test_credentials:
    print(f"\n🔐 Testing {cred['role'].upper()}: {cred['email']}")
    
    login_data = {
        'email': cred['email'],
        'password': cred['password']
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
print(f"📋 Updated credential list available in DEMO_CREDENTIALS.md")
print(f"\n🎯 Quick Reference:")
print(f"   Admin:    admin@example.com    / admin123")
print(f"   Staff:    staff@example.com    / staff123") 
print(f"   Customer: customer@example.com / customer123")
