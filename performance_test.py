#!/usr/bin/env python3
"""
Performance Testing Script
Test database and API performance
"""

import time
import requests
import statistics
from concurrent.futures import ThreadPoolExecutor

BASE_URL = "http://localhost:3001"

def get_auth_token():
    """Get authentication token"""
    response = requests.post(f"{BASE_URL}/api/users/login", json={
        "username": "admin",
        "password": "password"
    })
    return response.json()["token"]

def time_request(url, headers=None, method='GET', json_data=None):
    """Time a single request"""
    start = time.time()
    if method == 'GET':
        response = requests.get(url, headers=headers)
    else:
        response = requests.post(url, headers=headers, json=json_data)
    end = time.time()
    return end - start, response.status_code

def test_endpoint_performance(endpoint, headers, iterations=10):
    """Test endpoint performance"""
    times = []
    for _ in range(iterations):
        duration, status = time_request(f"{BASE_URL}{endpoint}", headers)
        if status == 200:
            times.append(duration)
    
    if times:
        avg_time = statistics.mean(times)
        min_time = min(times)
        max_time = max(times)
        print(f"   📊 {endpoint}")
        print(f"      Average: {avg_time:.3f}s | Min: {min_time:.3f}s | Max: {max_time:.3f}s")
    else:
        print(f"   ❌ {endpoint} - Failed")

def concurrent_test(endpoint, headers, concurrent_users=5):
    """Test with concurrent users"""
    def make_request():
        return time_request(f"{BASE_URL}{endpoint}", headers)
    
    start_time = time.time()
    with ThreadPoolExecutor(max_workers=concurrent_users) as executor:
        futures = [executor.submit(make_request) for _ in range(concurrent_users)]
        results = [f.result() for f in futures]
    
    total_time = time.time() - start_time
    successful = [r for r in results if r[1] == 200]
    
    print(f"   🚀 Concurrent test ({concurrent_users} users):")
    print(f"      Total time: {total_time:.3f}s")
    print(f"      Success rate: {len(successful)}/{len(results)}")
    if successful:
        avg_response = statistics.mean([r[0] for r in successful])
        print(f"      Avg response: {avg_response:.3f}s")

def main():
    print("⚡ Performance Testing")
    print("=" * 40)
    
    try:
        token = get_auth_token()
        headers = {"Authorization": f"Bearer {token}"}
        
        print("\n1. 📈 Analytics Performance:")
        test_endpoint_performance("/api/analytics/dashboard", headers)
        
        print("\n2. 📊 Database Stats Performance:")
        test_endpoint_performance("/api/database/stats", headers)
        
        print("\n3. 🔧 System Status Performance:")
        test_endpoint_performance("/api/analytics/system-status", headers)
        
        print("\n4. 🚀 Concurrent User Test:")
        concurrent_test("/api/analytics/dashboard", headers)
        
    except Exception as e:
        print(f"❌ Performance test error: {e}")

if __name__ == "__main__":
    main()
