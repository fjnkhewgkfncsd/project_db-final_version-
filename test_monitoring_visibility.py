#!/usr/bin/env python3

import requests
import json

def test_monitoring_tab_visibility():
    """Test what data is available for the Monitoring tab"""
    base_url = "http://localhost:3001"
    
    print("👁️ Testing Monitoring Tab Visibility Issues")
    print("=" * 50)
    
    # Login
    login_data = {"email": "admin@example.com", "password": "admin123"}
    response = requests.post(f"{base_url}/api/users/login", json=login_data)
    token = response.json().get('data', {}).get('token')
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    # Get performance data that feeds the monitoring tab
    print("\n1. CHECKING MONITORING DATA SOURCE")
    print("-" * 40)
    
    response = requests.get(f"{base_url}/api/analytics/system-performance", headers=headers)
    
    if response.status_code == 200:
        result = response.json()
        if result.get('success'):
            data = result.get('data', {})
            
            print("✅ Performance data retrieved successfully")
            
            # Check connection breakdown
            print(f"\n🔗 CONNECTION BREAKDOWN:")
            connection_breakdown = data.get('connection_breakdown', [])
            print(f"Type: {type(connection_breakdown)}")
            print(f"Length: {len(connection_breakdown) if isinstance(connection_breakdown, list) else 'N/A'}")
            
            if connection_breakdown:
                print("Connection details:")
                for i, conn in enumerate(connection_breakdown):
                    state = conn.get('state')
                    count = conn.get('count')
                    print(f"  {i+1}. State: '{state}' (type: {type(state)}), Count: {count}")
                    
                    # Check for visibility issues
                    if state is None:
                        print(f"     ⚠️  Issue: State is None - will display as blank")
                    elif state == '':
                        print(f"     ⚠️  Issue: State is empty string")
            else:
                print("❌ No connection breakdown data")
            
            # Check system resources data
            print(f"\n📊 SYSTEM RESOURCES:")
            response_time = data.get('database_response_time')
            memory_usage = data.get('memory_usage')
            api_success_rate = data.get('api_success_rate')
            
            print(f"Response Time: '{response_time}' (type: {type(response_time)})")
            print(f"Memory Usage: '{memory_usage}' (type: {type(memory_usage)})")
            print(f"API Success Rate: '{api_success_rate}' (type: {type(api_success_rate)})")
            
            # Check for progress bar parsing issues
            print(f"\n📈 PROGRESS BAR WIDTH PARSING:")
            
            # Parse response time for progress bar
            if response_time and isinstance(response_time, str) and response_time.endswith('ms'):
                try:
                    rt_num = int(response_time[:-2])
                    rt_percentage = min(100, max(0, rt_num))  # Simple conversion
                    print(f"Response Time: {response_time} → {rt_percentage}% width")
                except:
                    print(f"❌ Cannot parse response time: {response_time}")
            
            # Parse memory usage
            if memory_usage and isinstance(memory_usage, str) and memory_usage.endswith('%'):
                try:
                    mem_num = memory_usage[:-1]
                    print(f"Memory Usage: {memory_usage} → {mem_num}% width")
                except:
                    print(f"❌ Cannot parse memory usage: {memory_usage}")
            
            # Parse API success rate
            if api_success_rate and isinstance(api_success_rate, str) and api_success_rate.endswith('%'):
                try:
                    api_num = api_success_rate[:-1]
                    print(f"API Success Rate: {api_success_rate} → {api_num}% width")
                except:
                    print(f"❌ Cannot parse API success rate: {api_success_rate}")
            
            # Check largest tables data
            print(f"\n📋 LARGEST TABLES:")
            largest_tables = data.get('largest_tables', [])
            print(f"Type: {type(largest_tables)}")
            print(f"Length: {len(largest_tables) if isinstance(largest_tables, list) else 'N/A'}")
            
            if largest_tables:
                print("Table details:")
                for i, table in enumerate(largest_tables[:3]):  # Show first 3
                    print(f"  {i+1}. Table data: {table}")
                    
                    # Check field names
                    table_name_1 = table.get('table_name')
                    table_name_2 = table.get('tablename') 
                    size = table.get('size')
                    
                    print(f"     table_name: '{table_name_1}'")
                    print(f"     tablename: '{table_name_2}'")
                    print(f"     size: '{size}'")
                    
                    if table_name_1 is None and table_name_2 is None:
                        print(f"     ❌ Issue: No table name field found")
                    elif table_name_1:
                        print(f"     ✅ Use 'table_name' field")
                    elif table_name_2:
                        print(f"     ✅ Use 'tablename' field")
            else:
                print("❌ No largest tables data")
                
            # Check what might be causing invisibility
            print(f"\n🔍 POTENTIAL VISIBILITY ISSUES:")
            issues_found = []
            
            if not connection_breakdown:
                issues_found.append("❌ Connection breakdown is empty")
            else:
                for conn in connection_breakdown:
                    if conn.get('state') is None:
                        issues_found.append("⚠️  Some connection states are None (will appear blank)")
                        break
            
            if not largest_tables:
                issues_found.append("❌ Largest tables section won't show")
            
            if not response_time or not memory_usage or not api_success_rate:
                issues_found.append("⚠️  Some progress bars may not display correctly")
            
            if issues_found:
                for issue in issues_found:
                    print(f"  {issue}")
            else:
                print("  ✅ No obvious visibility issues detected")
                
        else:
            print(f"❌ Failed to get performance data: {result.get('message')}")
    else:
        print(f"❌ HTTP Error: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    test_monitoring_tab_visibility()
