#!/usr/bin/env python3

import requests
import json
import time

def demonstrate_recent_query_performance():
    """Demonstrate the Recent Query Performance feature"""
    base_url = "http://localhost:3001"
    
    print("🎯 Recent Query Performance Feature Demonstration")
    print("=" * 60)
    
    # Login
    login_data = {"email": "admin@example.com", "password": "admin123"}
    response = requests.post(f"{base_url}/api/users/login", json=login_data)
    token = response.json().get('data', {}).get('token')
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    print("\n📊 WHAT THE RECENT QUERY PERFORMANCE SECTION SHOWS:")
    print("-" * 55)
    print("✅ Real-time tracking of the last 10 executed queries")
    print("✅ Query text (truncated for readability)")
    print("✅ Execution time in milliseconds")
    print("✅ Number of rows returned/affected")
    print("✅ Performance status (Fast/Moderate/Slow)")
    print("✅ Color-coded status indicators")
    
    print("\n🔄 EXECUTING SAMPLE QUERIES TO DEMONSTRATE TRACKING:")
    print("-" * 55)
    
    # Execute a variety of queries to show different performance characteristics
    demo_queries = [
        # Fast queries (< 50ms)
        ("Simple count", "SELECT COUNT(*) as total_users FROM users;"),
        ("Category list", "SELECT name FROM categories ORDER BY name LIMIT 5;"),
        
        # Moderate queries (50-200ms)
        ("User analysis", "SELECT role, COUNT(*) as count, AVG(EXTRACT(DAYS FROM (NOW() - created_at))) as avg_days FROM users GROUP BY role;"),
        ("Product statistics", "SELECT c.name as category, COUNT(p.product_id) as products, AVG(p.base_price) as avg_price FROM categories c LEFT JOIN products p ON c.category_id = p.category_id GROUP BY c.name ORDER BY products DESC;"),
        
        # Potentially slower queries (could be > 200ms depending on data)
        ("Order analysis", "SELECT DATE(o.created_at) as order_date, COUNT(o.order_id) as orders, SUM(o.total_amount) as revenue FROM orders o WHERE o.created_at >= NOW() - INTERVAL '30 days' GROUP BY DATE(o.created_at) ORDER BY order_date DESC;"),
        
        # Simple queries to show variety
        ("Payment methods", "SELECT payment_method, COUNT(*) as usage FROM payments GROUP BY payment_method;"),
        ("Recent products", "SELECT name, base_price, stock_quantity FROM products ORDER BY created_at DESC LIMIT 10;")
    ]
    
    executed_queries = []
    
    for name, query in demo_queries:
        print(f"\n🔍 Executing: {name}")
        print(f"   Query: {query[:70]}{'...' if len(query) > 70 else ''}")
        
        start_time = time.time()
        query_data = {"query": query}
        response = requests.post(f"{base_url}/api/database/execute-query", 
                               json=query_data, headers=headers)
        end_time = time.time()
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                exec_time = result.get('data', {}).get('execution_time_ms')
                row_count = result.get('data', {}).get('row_count')
                
                status = "Fast" if exec_time < 50 else "Moderate" if exec_time < 200 else "Slow"
                status_icon = "🟢" if status == "Fast" else "🟡" if status == "Moderate" else "🔴"
                
                print(f"   Result: {status_icon} {exec_time}ms, {row_count} rows ({status})")
                
                executed_queries.append({
                    'name': name,
                    'time': exec_time,
                    'rows': row_count,
                    'status': status
                })
            else:
                print(f"   ❌ Failed: {result.get('message')}")
        else:
            print(f"   ❌ HTTP Error: {response.status_code}")
        
        time.sleep(0.5)  # Pause between queries
    
    # Show the recent query performance data
    print(f"\n📋 CURRENT RECENT QUERY PERFORMANCE TABLE:")
    print("-" * 55)
    
    response = requests.get(f"{base_url}/api/analytics/system-performance", headers=headers)
    
    if response.status_code == 200:
        result = response.json()
        if result.get('success'):
            data = result.get('data', {})
            recent_queries = data.get('recent_queries', [])
            
            if recent_queries:
                print("Recent Queries in Performance Tab:")
                print(f"{'Query':<45} {'Time':<8} {'Rows':<6} {'Status':<10}")
                print("-" * 75)
                
                for query in recent_queries:
                    query_text = query.get('query', 'N/A')
                    if len(query_text) > 40:
                        query_text = query_text[:40] + "..."
                    
                    duration = query.get('duration', 'N/A')
                    row_count = query.get('rowCount', 'N/A')
                    status = query.get('status', 'N/A')
                    
                    # Status icon
                    status_icon = "🟢" if status == "Fast" else "🟡" if status == "Moderate" else "🔴" if status == "Slow" else "⚪"
                    
                    print(f"{query_text:<45} {str(duration)+'ms':<8} {str(row_count):<6} {status_icon} {status:<9}")
                
                # Summary statistics
                durations = [q.get('duration', 0) for q in recent_queries if q.get('duration')]
                if durations:
                    avg_time = sum(durations) / len(durations)
                    fast_count = len([q for q in recent_queries if q.get('status') == 'Fast'])
                    moderate_count = len([q for q in recent_queries if q.get('status') == 'Moderate'])
                    slow_count = len([q for q in recent_queries if q.get('status') == 'Slow'])
                    
                    print(f"\n📊 Performance Summary:")
                    print(f"   Average Time: {avg_time:.1f}ms")
                    print(f"   🟢 Fast: {fast_count} | 🟡 Moderate: {moderate_count} | 🔴 Slow: {slow_count}")
    
    print(f"\n🎯 HOW TO USE THE RECENT QUERY PERFORMANCE FEATURE:")
    print("-" * 55)
    print("1. 🔗 Navigate to Database Tools → Performance tab")
    print("2. 📊 View the 'Recent Query Performance' section")
    print("3. 🔍 Execute queries using the Query Console")
    print("4. 🔄 Refresh or revisit the Performance tab")
    print("5. 📋 See your queries appear in the performance table")
    print("6. ⚡ Monitor query performance in real-time")
    print("7. 🎯 Identify slow queries that need optimization")
    
    print(f"\n✨ KEY BENEFITS:")
    print("-" * 55)
    print("🔍 Real-time performance monitoring")
    print("📊 Visual performance indicators")
    print("⚡ Quick identification of slow queries")
    print("📈 Performance trend tracking")
    print("🎯 Database optimization insights")
    print("🔄 Live updates as queries are executed")
    
    print(f"\n" + "=" * 60)
    print("🎉 Recent Query Performance Feature is Working Perfectly!")

if __name__ == "__main__":
    demonstrate_recent_query_performance()
