#!/usr/bin/env python3
"""
Test Query Statistics - Verify that queries/hour metric is working
"""

import requests
import json
import time

def test_query_metrics():
    base_url = "http://localhost:3001"
    
    print("🧪 Testing Query Statistics Tracking")
    print("=" * 50)
    
    # Login first
    print("\n1. 🔐 Logging in...")
    login_data = {
        "email": "admin@example.com",
        "password": "admin123"
    }
    
    try:
        response = requests.post(f"{base_url}/api/users/login", json=login_data)
        if response.status_code == 200:
            token = response.json()["data"]["token"]
            headers = {"Authorization": f"Bearer {token}"}
            print("   ✅ Login successful!")
        else:
            print(f"   ❌ Login failed: {response.json()}")
            return
    except Exception as e:
        print(f"   ❌ Login error: {e}")
        return
    
    # Generate some queries to test tracking
    print("\n2. 📊 Generating test queries...")
    endpoints = [
        "/api/users/stats",
        "/api/analytics/system-status", 
        "/api/analytics/system-performance",
        "/api/analytics/dashboard"
    ]
    
    for i in range(5):
        for endpoint in endpoints:
            try:
                response = requests.get(f"{base_url}{endpoint}", headers=headers)
                print(f"   Query {i+1}: {endpoint} - {response.status_code}")
                time.sleep(0.1)  # Small delay
            except Exception as e:
                print(f"   ❌ Error with {endpoint}: {e}")
    
    # Check the query statistics
    print("\n3. 📈 Checking Query Statistics...")
    try:
        response = requests.get(f"{base_url}/api/analytics/system-performance", headers=headers)
        if response.status_code == 200:
            data = response.json()["data"]
            print(f"   ✅ Total Queries: {data.get('total_queries', 'N/A')}")
            print(f"   ✅ Queries/Hour: {data.get('queries_per_hour', 'N/A')}")
            print(f"   ✅ Queries Last Hour: {data.get('queries_last_hour', 'N/A')}")
            print(f"   ✅ Avg Response Time: {data.get('database_response_time', 'N/A')}")
            print(f"   ✅ Active Connections: {data.get('active_connections', 'N/A')}")
            
            if data.get('queries_per_hour', 0) > 0:
                print("\n🎉 SUCCESS: Queries/hour metric is now working!")
            else:
                print("\n⚠️  Queries/hour shows 0 - may need more time to calculate rate")
        else:
            print(f"   ❌ Failed to get metrics: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error getting metrics: {e}")

if __name__ == "__main__":
    test_query_metrics()
