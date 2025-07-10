#!/usr/bin/env python3

import requests
import json

def test_frontend_performance_fix():
    """Test that the frontend should now display the correct performance data"""
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
        
        print("🔧 Field Mapping Check:")
        print("=" * 30)
        
        print(f"✅ database_response_time: {data.get('database_response_time')} (should show in Avg Query Time)")
        print(f"✅ uptime_hours: {data.get('uptime_hours')} (should show as {data.get('uptime_hours')}h in Uptime)")
        print(f"✅ queries_per_hour: {data.get('queries_per_hour')} (should show in Queries/Hour)")
        
        print(f"\n📊 Additional Performance Metrics:")
        print(f"   - API Success Rate: {data.get('api_success_rate')}")
        print(f"   - Memory Usage: {data.get('memory_usage')}")
        print(f"   - Active Connections: {data.get('active_connections')}")
        print(f"   - Database Size: {data.get('database_size')}")
        print(f"   - Total Queries: {data.get('total_queries')}")
        print(f"   - Queries Last Hour: {data.get('queries_last_hour')}")
        
        # Check if values exist and are not None
        avg_time = data.get('database_response_time')
        uptime = data.get('uptime_hours')
        queries_hour = data.get('queries_per_hour')
        
        print(f"\n🔍 Values Check:")
        print(f"   - Avg Query Time exists: {avg_time is not None} → {avg_time}")
        print(f"   - Uptime exists: {uptime is not None} → {uptime}")
        print(f"   - Queries/Hour exists: {queries_hour is not None} → {queries_hour}")
        
        if avg_time and uptime and queries_hour:
            print("\n✅ All values are present - frontend should display correctly!")
        else:
            print("\n❌ Some values are missing - frontend will show N/A")
        
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    test_frontend_performance_fix()
