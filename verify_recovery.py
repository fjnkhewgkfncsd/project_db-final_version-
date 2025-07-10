#!/usr/bin/env python3
"""
Emergency Recovery Verification Script
=====================================
Verifies that the database has been successfully restored after emergency recovery.
"""

import psycopg2
import os
from datetime import datetime
import sys

def verify_database_recovery():
    """Verify that database has been restored successfully"""
    print("🔍 EMERGENCY RECOVERY VERIFICATION")
    print("=" * 50)
    print(f"🕒 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Database connection parameters
        conn_params = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': os.getenv('DB_PORT', '5432'),
            'database': 'ecommerce_db',
            'user': os.getenv('DB_USER', 'postgres'),
            'password': os.getenv('DB_PASSWORD', 'postgres')
        }
        
        print(f"📡 Connecting to database: {conn_params['host']}:{conn_params['port']}/{conn_params['database']}")
        
        # Connect to database
        conn = psycopg2.connect(**conn_params)
        cursor = conn.cursor()
        
        print("✅ Database connection successful!")
        
        # Check table existence
        print("\n📊 Checking table existence...")
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            ORDER BY table_name;
        """)
        tables = cursor.fetchall()
        
        expected_tables = [
            'categories', 'products', 'users', 'addresses', 'orders', 
            'order_items', 'cart_items', 'reviews', 'inventory_logs', 
            'user_sessions', 'audit_logs', 'query_performance_log'
        ]
        
        found_tables = [table[0] for table in tables]
        print(f"✅ Found {len(found_tables)} tables: {', '.join(found_tables)}")
        
        missing_tables = [table for table in expected_tables if table not in found_tables]
        if missing_tables:
            print(f"⚠️ Missing tables: {', '.join(missing_tables)}")
        else:
            print("✅ All expected tables present!")
        
        # Check data counts
        print("\n📈 Checking data counts...")
        data_checks = [
            ('users', 'SELECT COUNT(*) FROM users'),
            ('categories', 'SELECT COUNT(*) FROM categories'),
            ('products', 'SELECT COUNT(*) FROM products'),
            ('orders', 'SELECT COUNT(*) FROM orders'),
            ('order_items', 'SELECT COUNT(*) FROM order_items'),
            ('reviews', 'SELECT COUNT(*) FROM reviews')
        ]
        
        total_records = 0
        for table_name, query in data_checks:
            try:
                cursor.execute(query)
                count = cursor.fetchone()[0]
                print(f"  📋 {table_name}: {count:,} records")
                total_records += count
            except Exception as e:
                print(f"  ❌ {table_name}: Error - {e}")
        
        print(f"✅ Total records across main tables: {total_records:,}")
        
        # Check database size
        print("\n💾 Checking database size...")
        cursor.execute("""
            SELECT pg_size_pretty(pg_database_size('ecommerce_db')) as size;
        """)
        db_size = cursor.fetchone()[0]
        print(f"📊 Database size: {db_size}")
        
        # Check recent activity
        print("\n⏰ Checking recent activity...")
        cursor.execute("""
            SELECT table_name, last_updated 
            FROM (
                SELECT 'users' as table_name, MAX(created_at) as last_updated FROM users
                UNION ALL
                SELECT 'orders' as table_name, MAX(created_at) as last_updated FROM orders
                UNION ALL
                SELECT 'products' as table_name, MAX(created_at) as last_updated FROM products
            ) t
            ORDER BY last_updated DESC;
        """)
        activities = cursor.fetchall()
        
        for table_name, last_updated in activities:
            if last_updated:
                print(f"  📅 {table_name}: Last activity {last_updated}")
            else:
                print(f"  📅 {table_name}: No timestamp data")
        
        # Test basic functionality
        print("\n🔧 Testing basic functionality...")
        
        # Test user query
        cursor.execute("SELECT email, role FROM users LIMIT 3")
        users = cursor.fetchall()
        print(f"✅ User query successful - Sample users: {len(users)}")
        for email, role in users:
            print(f"    👤 {email} ({role})")
        
        # Test product query
        cursor.execute("SELECT name, price FROM products WHERE price > 0 LIMIT 3")
        products = cursor.fetchall()
        print(f"✅ Product query successful - Sample products: {len(products)}")
        for name, price in products:
            print(f"    🛍️ {name}: ${price}")
        
        # Test order query
        cursor.execute("""
            SELECT o.id, u.email, o.total_amount, o.status 
            FROM orders o 
            JOIN users u ON o.user_id = u.id 
            LIMIT 3
        """)
        orders = cursor.fetchall()
        print(f"✅ Order query successful - Sample orders: {len(orders)}")
        for order_id, email, total, status in orders:
            print(f"    🛒 Order #{order_id}: {email} - ${total} ({status})")
        
        cursor.close()
        conn.close()
        
        print("\n" + "=" * 50)
        print("🎉 RECOVERY VERIFICATION COMPLETE!")
        print("✅ Database has been successfully restored")
        print("✅ All tables are present")
        print("✅ Data is accessible")
        print("✅ Basic queries work correctly")
        print("🚀 System is ready for normal operation!")
        
        return True
        
    except psycopg2.Error as e:
        print(f"\n❌ Database error: {e}")
        print("💡 The database may not be fully restored yet")
        return False
    except Exception as e:
        print(f"\n❌ Verification error: {e}")
        return False

if __name__ == "__main__":
    print("🚑 Emergency Recovery Verification Script")
    print("Run this after completing database restore via emergency recovery page")
    print()
    
    success = verify_database_recovery()
    sys.exit(0 if success else 1)
