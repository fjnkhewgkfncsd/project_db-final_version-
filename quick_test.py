#!/usr/bin/env python3
"""
Quick API Test Script
Test individual backend endpoints
"""

import requests
import json

BASE_URL = "http://localhost:3001"

def test_login():
    """Test user authentication"""
    response = requests.post(f"{BASE_URL}/api/users/login", json={
        "email": "admin@example.com",
        "password": "admin123"
    })
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Login successful! Response: {result}")
        token = result.get("data", {}).get("token") or result.get("token")
        return token
    else:
        print(f"❌ Login failed: {response.status_code} - {response.text}")
        return None

def test_backup(token):
    """Test database backup"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{BASE_URL}/api/database/backup", headers=headers)
    print(f"📦 Backup test: {response.status_code} - {response.json()}")

def test_query(token):
    """Test SQL query execution"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{BASE_URL}/api/database/execute-query", 
                           json={"sql": "SELECT COUNT(*) as total_users FROM users"}, 
                           headers=headers)
    print(f"🔍 Query test: {response.status_code} - {response.json()}")

def test_analytics(token):
    """Test analytics dashboard"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/analytics/dashboard", headers=headers)
    print(f"📈 Analytics test: {response.status_code} - {response.json()}")

if __name__ == "__main__":
    print("🧪 Quick API Testing")
    print("=" * 30)
    
    token = test_login()
    if token:
        test_backup(token)
        test_query(token)
        test_analytics(token)
