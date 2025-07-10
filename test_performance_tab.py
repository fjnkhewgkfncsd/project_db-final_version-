#!/usr/bin/env python3

import requests
import json
import time

def test_performance_metrics():
    """Test the Performance tab functionality"""
    base_url = "http://localhost:3001"
    
    print("🔧 Testing Performance Metrics Functionality...")
    
    # First, login as admin
    login_data = {
        "email": "admin@example.com",
        "password": "admin123"
    }
    
    try:
        print("\n1. Logging in as admin...")
        response = requests.post(f"{base_url}/api/users/login", json=login_data)
        
        if response.status_code != 200:
            print(f"❌ Login failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
        login_result = response.json()
        token = login_result.get('data', {}).get('token')
        
        if not token:
            print("❌ No token received")
            return False
            
        print("✅ Login successful")
        
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        # Test system performance endpoint
        print("\n2. Testing system performance metrics...")
        response = requests.get(f"{base_url}/api/analytics/system-performance", headers=headers)
        
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                data = result.get('data', {})
                print("✅ Performance metrics retrieved successfully!")
                print("\n📊 Performance Data:")
                print(f"  - Database Response Time: {data.get('database_response_time', 'N/A')}")
                print(f"  - API Success Rate: {data.get('api_success_rate', 'N/A')}")
                print(f"  - Memory Usage: {data.get('memory_usage', 'N/A')}")
                print(f"  - Active Connections: {data.get('active_connections', 'N/A')}")
                print(f"  - Database Size: {data.get('database_size', 'N/A')}")
                print(f"  - Uptime Hours: {data.get('uptime_hours', 'N/A')}")
                print(f"  - Total Queries: {data.get('total_queries', 'N/A')}")
                print(f"  - Queries Per Hour: {data.get('queries_per_hour', 'N/A')}")
                print(f"  - Queries Last Hour: {data.get('queries_last_hour', 'N/A')}")
                
                # Connection breakdown
                connections = data.get('connection_breakdown', [])
                if connections:
                    print("\n🔗 Connection Breakdown:")
                    for conn in connections:
                        print(f"  - {conn.get('state', 'unknown')}: {conn.get('count', 0)} connections")
                
                # Largest tables
                tables = data.get('largest_tables', [])
                if tables:
                    print("\n📋 Largest Tables:")
                    for table in tables:
                        print(f"  - {table.get('table_name', 'unknown')}: {table.get('size', 'N/A')}")
                        
            else:
                print(f"❌ Performance metrics failed: {result.get('message')}")
                return False
        else:
            print(f"❌ Request failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
        
        # Generate some queries to test real-time tracking
        print("\n3. Generating test queries to track performance...")
        test_queries = [
            "SELECT COUNT(*) FROM users;",
            "SELECT COUNT(*) FROM products;",
            "SELECT COUNT(*) FROM orders;",
            "SELECT role, COUNT(*) FROM users GROUP BY role;",
            "SELECT c.name, COUNT(p.product_id) FROM categories c LEFT JOIN products p ON c.category_id = p.category_id GROUP BY c.name;"
        ]
        
        for i, test_query in enumerate(test_queries):
            print(f"  Executing query {i+1}/5...")
            query_data = {"query": test_query}
            response = requests.post(f"{base_url}/api/database/execute-query", 
                                   json=query_data, headers=headers)
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    execution_time = result.get('data', {}).get('execution_time_ms', 'N/A')
                    row_count = result.get('data', {}).get('row_count', 'N/A')
                    print(f"    ✅ Query executed in {execution_time}ms, returned {row_count} rows")
                else:
                    print(f"    ❌ Query failed: {result.get('message')}")
            else:
                print(f"    ❌ Query request failed: {response.status_code}")
            
            # Small delay between queries
            time.sleep(0.5)
        
        # Check updated performance metrics
        print("\n4. Checking updated performance metrics after test queries...")
        response = requests.get(f"{base_url}/api/analytics/system-performance", headers=headers)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                data = result.get('data', {})
                print("✅ Updated performance metrics retrieved!")
                print(f"  - Total Queries: {data.get('total_queries', 'N/A')}")
                print(f"  - Queries Per Hour: {data.get('queries_per_hour', 'N/A')}")
                print(f"  - Queries Last Hour: {data.get('queries_last_hour', 'N/A')}")
                print(f"  - Average Query Time: {data.get('database_response_time', 'N/A')}")
            else:
                print(f"❌ Updated metrics failed: {result.get('message')}")
        
        # Test system status endpoint
        print("\n5. Testing system status endpoint...")
        response = requests.get(f"{base_url}/api/analytics/system-status", headers=headers)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                data = result.get('data', {})
                print("✅ System status retrieved successfully!")
                print(f"  - Overall Health: {data.get('overall_health', 'N/A')}")
                print(f"  - Database Status: {data.get('database_status', 'N/A')}")
                print(f"  - Last Backup: {data.get('last_backup', 'N/A')}")
                
                # Recent activity
                activities = data.get('recent_activity', [])
                if activities:
                    print("\n📝 Recent Activity:")
                    for activity in activities[:3]:  # Show top 3
                        print(f"  - {activity.get('action', 'Unknown')} at {activity.get('timestamp', 'N/A')}")
            else:
                print(f"❌ System status failed: {result.get('message')}")
        else:
            print(f"❌ System status request failed: {response.status_code}")
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend server. Is it running on port 3001?")
        return False
    except Exception as e:
        print(f"❌ Error during testing: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_performance_metrics()
    if success:
        print("\n🎉 Performance tab testing completed successfully!")
    else:
        print("\n💥 Performance tab testing failed!")
