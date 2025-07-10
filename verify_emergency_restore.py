#!/usr/bin/env python3
"""
Emergency Database Restore Verification Script
Verifies that the database restoration was successful
"""
import psycopg2
import os
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv('backend/.env')

def verify_database_restoration():
    """Verify that the database has been successfully restored"""
    
    # Database connection parameters
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '5432')
    DB_USER = os.getenv('DB_USER', 'postgres')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'hengmengly123')
    DB_NAME = os.getenv('DB_NAME', 'ecommerce_db')
    
    print("🔍 EMERGENCY RESTORE VERIFICATION")
    print("=" * 50)
    print(f"Target Database: {DB_NAME}")
    print(f"Host: {DB_HOST}:{DB_PORT}")
    print(f"User: {DB_USER}")
    print()
    
    verification_results = {
        'database_exists': False,
        'can_connect': False,
        'tables_exist': False,
        'data_present': False,
        'users_count': 0,
        'products_count': 0,
        'orders_count': 0,
        'overall_success': False
    }
    
    try:
        # Step 1: Check if database exists
        print("1. 🔍 Checking if database exists...")
        conn_postgres = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database='postgres'
        )
        cursor_postgres = conn_postgres.cursor()
        
        cursor_postgres.execute(f"SELECT 1 FROM pg_database WHERE datname = '{DB_NAME}';")
        if cursor_postgres.fetchone():
            verification_results['database_exists'] = True
            print("   ✅ Database exists")
        else:
            print("   ❌ Database does not exist")
            cursor_postgres.close()
            conn_postgres.close()
            return verification_results
        
        cursor_postgres.close()
        conn_postgres.close()
        
        # Step 2: Try to connect to the target database
        print("2. 🔗 Testing database connection...")
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        cursor = conn.cursor()
        verification_results['can_connect'] = True
        print("   ✅ Successfully connected to database")
        
        # Step 3: Check if main tables exist
        print("3. 📊 Checking table structure...")
        expected_tables = ['users', 'products', 'orders', 'order_items', 'categories']
        existing_tables = []
        
        for table in expected_tables:
            cursor.execute(f"""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = '{table}'
                );
            """)
            if cursor.fetchone()[0]:
                existing_tables.append(table)
        
        if len(existing_tables) >= 3:  # At least 3 main tables should exist
            verification_results['tables_exist'] = True
            print(f"   ✅ Found {len(existing_tables)} tables: {', '.join(existing_tables)}")
        else:
            print(f"   ⚠️  Only found {len(existing_tables)} tables: {', '.join(existing_tables)}")
        
        # Step 4: Check data presence
        print("4. 📈 Checking data integrity...")
        
        # Count users
        try:
            cursor.execute("SELECT COUNT(*) FROM users;")
            verification_results['users_count'] = cursor.fetchone()[0]
            print(f"   👥 Users: {verification_results['users_count']}")
        except Exception as e:
            print(f"   ❌ Error counting users: {e}")
        
        # Count products
        try:
            cursor.execute("SELECT COUNT(*) FROM products;")
            verification_results['products_count'] = cursor.fetchone()[0]
            print(f"   📦 Products: {verification_results['products_count']}")
        except Exception as e:
            print(f"   ❌ Error counting products: {e}")
        
        # Count orders
        try:
            cursor.execute("SELECT COUNT(*) FROM orders;")
            verification_results['orders_count'] = cursor.fetchone()[0]
            print(f"   🛒 Orders: {verification_results['orders_count']}")
        except Exception as e:
            print(f"   ❌ Error counting orders: {e}")
        
        # Check if we have meaningful data
        if (verification_results['users_count'] > 0 and 
            verification_results['products_count'] > 0):
            verification_results['data_present'] = True
            print("   ✅ Database contains meaningful data")
        else:
            print("   ⚠️  Database appears to be empty or has minimal data")
        
        # Step 5: Test some basic queries
        print("5. 🧪 Testing basic database operations...")
        
        try:
            # Test a simple join query
            cursor.execute("""
                SELECT u.username, COUNT(o.id) as order_count
                FROM users u
                LEFT JOIN orders o ON u.user_id = o.user_id
                GROUP BY u.user_id, u.username
                LIMIT 5;
            """)
            sample_data = cursor.fetchall()
            print(f"   ✅ Join queries working - sample users: {len(sample_data)}")
            
            # Show some sample data
            if sample_data:
                print("   📋 Sample user data:")
                for username, order_count in sample_data[:3]:
                    print(f"      - {username}: {order_count} orders")
        
        except Exception as e:
            print(f"   ❌ Error testing queries: {e}")
        
        cursor.close()
        conn.close()
        
        # Overall assessment
        verification_results['overall_success'] = (
            verification_results['database_exists'] and
            verification_results['can_connect'] and
            verification_results['tables_exist'] and
            verification_results['data_present']
        )
        
    except psycopg2.Error as e:
        print(f"❌ PostgreSQL Error: {e}")
        return verification_results
    except Exception as e:
        print(f"❌ Error: {e}")
        return verification_results
    
    return verification_results

def print_final_report(results):
    """Print the final verification report"""
    print("\n" + "=" * 50)
    print("📋 FINAL VERIFICATION REPORT")
    print("=" * 50)
    
    if results['overall_success']:
        print("🎉 RESTORATION SUCCESSFUL!")
        print("✅ Database has been successfully restored from backup")
    else:
        print("⚠️  RESTORATION ISSUES DETECTED")
        print("❌ Some verification checks failed")
    
    print("\n📊 Detailed Results:")
    print(f"   Database Exists: {'✅' if results['database_exists'] else '❌'}")
    print(f"   Can Connect: {'✅' if results['can_connect'] else '❌'}")
    print(f"   Tables Present: {'✅' if results['tables_exist'] else '❌'}")
    print(f"   Data Available: {'✅' if results['data_present'] else '❌'}")
    
    print(f"\n📈 Data Summary:")
    print(f"   Users: {results['users_count']}")
    print(f"   Products: {results['products_count']}")
    print(f"   Orders: {results['orders_count']}")
    
    if results['overall_success']:
        print("\n🎯 Next Steps:")
        print("   1. Test application functionality")
        print("   2. Verify user login capabilities")
        print("   3. Check data integrity in detail")
        print("   4. Resume normal operations")
    else:
        print("\n🛠️  Recommended Actions:")
        print("   1. Check the restore process logs")
        print("   2. Try restoring from a different backup")
        print("   3. Verify database permissions")
        print("   4. Contact database administrator")
    
    print("\n" + "=" * 50)

if __name__ == "__main__":
    print("Starting emergency database restore verification...")
    print()
    
    # Wait a moment for any ongoing processes
    time.sleep(1)
    
    # Run verification
    results = verify_database_restoration()
    
    # Print final report
    print_final_report(results)
    
    # Exit with appropriate code
    exit(0 if results['overall_success'] else 1)
