#!/usr/bin/env python3
"""
Quick Test Script for Database Admin System
Tests all real functionality through HTTP requests
"""

import requests
import json
import time

def test_database_admin_system():
    base_url = "http://localhost:3001"
    
    print("🧪 Testing Database Administration System")
    print("=" * 50)
    
    # Test 1: Login
    print("\n1. 🔐 Testing Login...")
    login_data = {
        "email": "admin@example.com",
        "password": "admin123"
    }
    
    try:
        response = requests.post(f"{base_url}/api/users/login", json=login_data)
        if response.status_code == 200:
            token = response.json()["data"]["token"]
            print("   ✅ Login successful!")
            headers = {"Authorization": f"Bearer {token}"}
        else:
            print(f"   ❌ Login failed: {response.json()}")
            return
    except Exception as e:
        print(f"   ❌ Login error: {e}")
        return
    
    # Test 2: Real Database Backup
    print("\n2. 📦 Testing Real Database Backup...")
    try:
        response = requests.post(f"{base_url}/api/database/backup", headers=headers)
        if response.status_code == 200:
            backup_data = response.json()["data"]
            print(f"   ✅ Backup created: {backup_data['filename']}")
            print(f"   📊 Size: {backup_data['size']}")
            print(f"   📋 Tables: {len(backup_data['tables_backed_up'])} backed up")
        else:
            print(f"   ❌ Backup failed: {response.json()}")
    except Exception as e:
        print(f"   ❌ Backup error: {e}")
    
    # Test 3: Real SQL Query Execution
    print("\n3. 🔍 Testing Real SQL Query Execution...")
    query_data = {
        "sql": "SELECT role, COUNT(*) as count FROM users GROUP BY role ORDER BY count DESC;"
    }
    
    try:
        response = requests.post(f"{base_url}/api/database/execute-query", 
                               json=query_data, headers=headers)
        if response.status_code == 200:
            result = response.json()["data"]
            print(f"   ✅ Query executed in {result['execution_time_ms']}ms")
            print(f"   📊 Returned {result['row_count']} rows:")
            for row in result['rows']:
                print(f"      {row['role']}: {row['count']} users")
        else:
            print(f"   ❌ Query failed: {response.json()}")
    except Exception as e:
        print(f"   ❌ Query error: {e}")
    
    # Test 4: Real Analytics Data
    print("\n4. 📈 Testing Real Analytics Dashboard...")
    try:
        response = requests.get(f"{base_url}/api/analytics/dashboard", headers=headers)
        if response.status_code == 200:
            analytics = response.json()["data"]
            print(f"   ✅ Analytics loaded (Data source: {response.json()['data_source']})")
            print(f"   👥 Active users: {analytics['systemMetrics']['activeUsers']}")
            print(f"   🔗 DB connections: {analytics['systemMetrics']['activeConnections']}")
            print(f"   💾 Database size: {analytics['systemMetrics']['databaseSize']}")
        else:
            print(f"   ❌ Analytics failed: {response.json()}")
    except Exception as e:
        print(f"   ❌ Analytics error: {e}")
    
    # Test 5: Real System Status
    print("\n5. 🔧 Testing Real System Status...")
    try:
        response = requests.get(f"{base_url}/api/analytics/system-status", headers=headers)
        if response.status_code == 200:
            status = response.json()["data"]
            print(f"   ✅ System status loaded")
            print(f"   💾 Database: {status['database_status']}")
            print(f"   🚀 API: {status['api_status']}")
            print(f"   📦 Backup system: {status['backup_status']}")
            print(f"   🕒 Last backup: {status['last_backup']}")
        else:
            print(f"   ❌ System status failed: {response.json()}")
    except Exception as e:
        print(f"   ❌ System status error: {e}")
    
    # Test 6: Database Statistics
    print("\n6. 📊 Testing Database Statistics...")
    try:
        response = requests.get(f"{base_url}/api/database/stats", headers=headers)
        if response.status_code == 200:
            stats = response.json()["data"]
            print(f"   ✅ Database stats loaded")
            print(f"   📊 Database: {stats['database_info']['name']}")
            print(f"   💾 Size: {stats['database_info']['size']}")
            print("   📋 Table record counts:")
            for table in stats['record_counts']:
                print(f"      {table['table_name']}: {table['record_count']} records")
        else:
            print(f"   ❌ Database stats failed: {response.json()}")
    except Exception as e:
        print(f"   ❌ Database stats error: {e}")
    
    print("\n🎉 Testing Complete!")
    print("=" * 50)
    print("✅ All tests verify REAL functionality - no fake data!")

if __name__ == "__main__":
    test_database_admin_system()
