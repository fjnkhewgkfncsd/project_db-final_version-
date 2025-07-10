#!/usr/bin/env python3

import requests
import json
import time

def test_recent_query_performance():
    """Test the Recent Query Performance tracking"""
    base_url = "http://localhost:3001"
    
    print("🔍 Testing Recent Query Performance Tracking")
    print("=" * 50)
    
    # Login
    login_data = {"email": "admin@example.com", "password": "admin123"}
    response = requests.post(f"{base_url}/api/users/login", json=login_data)
    token = response.json().get('data', {}).get('token')
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    # Check initial recent queries
    print("\n1. CHECKING INITIAL RECENT QUERIES")
    print("-" * 40)
    response = requests.get(f"{base_url}/api/analytics/system-performance", headers=headers)
    initial_data = response.json().get('data', {})
    initial_recent = initial_data.get('recent_queries', [])
    
    print(f"📊 Current recent queries tracked: {len(initial_recent)}")
    if initial_recent:
        print("Recent queries:")
        for i, query in enumerate(initial_recent[:3], 1):
            print(f"  {i}. {query.get('query', 'N/A')[:60]}... ({query.get('duration')}ms, {query.get('status')})")
    else:
        print("  No recent queries found.")
    
    # Execute various test queries
    print(f"\n2. EXECUTING TEST QUERIES")
    print("-" * 40)
    
    test_queries = [
        # Fast queries
        "SELECT COUNT(*) FROM users;",
        "SELECT COUNT(*) FROM categories;",
        
        # Moderate queries  
        "SELECT u.username, u.email FROM users u WHERE u.role = 'customer' LIMIT 50;",
        "SELECT p.name, p.base_price FROM products p ORDER BY p.base_price DESC LIMIT 25;",
        
        # Potentially slower queries
        "SELECT c.name, COUNT(p.product_id) as product_count FROM categories c LEFT JOIN products p ON c.category_id = p.category_id GROUP BY c.name ORDER BY product_count DESC;",
        "SELECT u.username, COUNT(o.order_id) as order_count, AVG(o.total_amount) as avg_order FROM users u LEFT JOIN orders o ON u.user_id = o.user_id WHERE u.role = 'customer' GROUP BY u.user_id, u.username HAVING COUNT(o.order_id) > 0 ORDER BY order_count DESC LIMIT 20;",
        
        # Simple queries
        "SELECT name FROM categories ORDER BY name;",
        "SELECT payment_method, COUNT(*) FROM payments GROUP BY payment_method;"
    ]
    
    query_results = []
    
    for i, test_query in enumerate(test_queries, 1):
        print(f"  Executing query {i}/{len(test_queries)}...")
        start_time = time.time()
        
        query_data = {"query": test_query}
        response = requests.post(f"{base_url}/api/database/execute-query", 
                               json=query_data, headers=headers)
        
        end_time = time.time()
        request_time = (end_time - start_time) * 1000  # Convert to ms
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                exec_time = result.get('data', {}).get('execution_time_ms')
                row_count = result.get('data', {}).get('row_count')
                query_results.append({
                    'query': test_query[:50] + '...',
                    'exec_time': exec_time,
                    'row_count': row_count,
                    'status': 'Success'
                })
                print(f"    ✅ {exec_time}ms, {row_count} rows")
            else:
                print(f"    ❌ Query failed: {result.get('message')}")
                query_results.append({
                    'query': test_query[:50] + '...',
                    'status': 'Failed',
                    'error': result.get('message')
                })
        else:
            print(f"    ❌ Request failed: {response.status_code}")
        
        # Small delay between queries
        time.sleep(0.3)
    
    # Check updated recent queries
    print(f"\n3. CHECKING UPDATED RECENT QUERIES")
    print("-" * 40)
    time.sleep(1)  # Wait for tracking to update
    
    response = requests.get(f"{base_url}/api/analytics/system-performance", headers=headers)
    updated_data = response.json().get('data', {})
    recent_queries = updated_data.get('recent_queries', [])
    
    print(f"📊 Recent queries now tracked: {len(recent_queries)}")
    print(f"📈 Total queries increased: {initial_data.get('total_queries', 0)} → {updated_data.get('total_queries', 0)} (+{updated_data.get('total_queries', 0) - initial_data.get('total_queries', 0)})")
    
    if recent_queries:
        print(f"\n📋 Recent Query Performance (last {len(recent_queries)} queries):")
        print(f"{'Query':<60} {'Time':<8} {'Rows':<6} {'Status':<10}")
        print("-" * 90)
        
        for query in recent_queries:
            query_text = query.get('query', 'N/A')
            duration = query.get('duration', 'N/A')
            row_count = query.get('rowCount', 'N/A')
            status = query.get('status', 'N/A')
            
            # Truncate query text if too long
            if len(query_text) > 55:
                query_text = query_text[:55] + "..."
            
            print(f"{query_text:<60} {str(duration)+'ms':<8} {str(row_count):<6} {status:<10}")
        
        # Performance analysis
        print(f"\n📊 PERFORMANCE ANALYSIS:")
        print("-" * 40)
        
        durations = [q.get('duration', 0) for q in recent_queries if q.get('duration')]
        if durations:
            avg_time = sum(durations) / len(durations)
            min_time = min(durations)
            max_time = max(durations)
            
            fast_count = len([q for q in recent_queries if q.get('status') == 'Fast'])
            moderate_count = len([q for q in recent_queries if q.get('status') == 'Moderate'])
            slow_count = len([q for q in recent_queries if q.get('status') == 'Slow'])
            
            print(f"⏱️  Average execution time: {avg_time:.1f}ms")
            print(f"🚀 Fastest query: {min_time}ms")
            print(f"🐌 Slowest query: {max_time}ms")
            print(f"📊 Performance distribution:")
            print(f"   🟢 Fast (<50ms): {fast_count} queries")
            print(f"   🟡 Moderate (50-200ms): {moderate_count} queries") 
            print(f"   🔴 Slow (>200ms): {slow_count} queries")
            
            # Performance insights
            if avg_time < 50:
                print(f"✨ Excellent performance! Average query time is very fast.")
            elif avg_time < 100:
                print(f"👍 Good performance! Most queries are executing efficiently.")
            elif avg_time < 200:
                print(f"⚠️  Moderate performance. Consider optimization for some queries.")
            else:
                print(f"🚨 Performance needs attention. Many queries are taking too long.")
                
    else:
        print("❌ No recent queries found after executing test queries!")
        print("   This might indicate an issue with the tracking system.")
    
    print(f"\n" + "=" * 50)
    print("🎉 Recent Query Performance Test Completed!")
    
    return len(recent_queries) > 0

if __name__ == "__main__":
    success = test_recent_query_performance()
    if success:
        print("✅ Recent query tracking is working correctly!")
    else:
        print("❌ Recent query tracking may have issues!")
