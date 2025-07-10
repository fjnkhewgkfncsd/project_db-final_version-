#!/usr/bin/env python3

import requests
import json

def check_performance_data_fields():
    """Check what fields are actually returned by the performance endpoint"""
    base_url = "http://localhost:3001"
    
    # Login
    login_data = {"email": "admin@example.com", "password": "admin123"}
    response = requests.post(f"{base_url}/api/users/login", json=login_data)
    token = response.json().get('data', {}).get('token')
    
    headers = {'Authorization': f'Bearer {token}'}
    
    # Get performance data
    response = requests.get(f"{base_url}/api/analytics/system-performance", headers=headers)
    
    if response.status_code == 200:
        data = response.json().get('data', {})
        print("📊 Performance API Response Fields:")
        print("=" * 40)
        for key, value in data.items():
            print(f"{key}: {value}")
        
        print("\n🔍 Frontend is looking for:")
        print("- avg_query_time")
        print("- uptime") 
        print("- queries_per_hour")
        
        print("\n🔍 Backend is sending:")
        print(f"- database_response_time: {data.get('database_response_time')}")
        print(f"- uptime_hours: {data.get('uptime_hours')}")
        print(f"- queries_per_hour: {data.get('queries_per_hour')}")
        
    else:
        print(f"Error: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    check_performance_data_fields()
