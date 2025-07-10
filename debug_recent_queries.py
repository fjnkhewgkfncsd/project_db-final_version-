#!/usr/bin/env python3

import requests
import json

def test_direct_performance_endpoint():
    """Test the performance endpoint to see what recent_queries contains"""
    base_url = "http://localhost:3001"
    
    print("🔍 Testing Performance Endpoint for Recent Queries")
    print("=" * 50)
    
    # Login
    login_data = {"email": "admin@example.com", "password": "admin123"}
    response = requests.post(f"{base_url}/api/users/login", json=login_data)
    token = response.json().get('data', {}).get('token')
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    # Execute a few queries first
    print("\n1. EXECUTING TEST QUERIES")
    print("-" * 30)
    
    test_queries = [
        "SELECT COUNT(*) as user_count FROM users;",
        "SELECT COUNT(*) as product_count FROM products;",
        "SELECT role, COUNT(*) as count FROM users GROUP BY role;"
    ]
    
    for i, test_query in enumerate(test_queries, 1):
        print(f"Executing query {i}: {test_query}")
        query_data = {"query": test_query}
        response = requests.post(f"{base_url}/api/database/execute-query", 
                               json=query_data, headers=headers)
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                exec_time = result.get('data', {}).get('execution_time_ms')
                print(f"  ✅ Executed in {exec_time}ms")
            else:
                print(f"  ❌ Failed: {result.get('message')}")
        else:
            print(f"  ❌ HTTP Error: {response.status_code}")
    
    # Now check performance endpoint
    print(f"\n2. CHECKING PERFORMANCE ENDPOINT")
    print("-" * 30)
    
    response = requests.get(f"{base_url}/api/analytics/system-performance", headers=headers)
    
    if response.status_code == 200:
        result = response.json()
        if result.get('success'):
            data = result.get('data', {})
            
            print(f"✅ Performance endpoint accessible")
            print(f"📊 Total queries: {data.get('total_queries', 'N/A')}")
            print(f"⏱️  Average query time: {data.get('database_response_time', 'N/A')}")
            
            # Check recent_queries specifically
            recent_queries = data.get('recent_queries')
            print(f"\n🔍 Recent queries field:")
            print(f"  Type: {type(recent_queries)}")
            print(f"  Value: {recent_queries}")
            
            if recent_queries is None:
                print("  ❌ recent_queries field is None")
            elif isinstance(recent_queries, list):
                print(f"  📝 recent_queries is a list with {len(recent_queries)} items")
                if recent_queries:
                    print("  Recent queries:")
                    for i, query in enumerate(recent_queries):
                        print(f"    {i+1}. {query}")
                else:
                    print("  📝 recent_queries list is empty")
            else:
                print(f"  ⚠️  recent_queries has unexpected type: {type(recent_queries)}")
            
            # Print raw response for debugging
            print(f"\n🔧 Raw response data keys: {list(data.keys())}")
            
        else:
            print(f"❌ Performance endpoint failed: {result.get('message')}")
    else:
        print(f"❌ HTTP Error: {response.status_code}")
        print(f"Response: {response.text}")

if __name__ == "__main__":
    test_direct_performance_endpoint()
