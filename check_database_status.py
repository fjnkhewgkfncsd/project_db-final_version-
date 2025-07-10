#!/usr/bin/env python3
"""
Quick Database Status Check
Checks if the database exists and is operational
"""
import psycopg2
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('backend/.env')

def check_database_status():
    """Check current database status"""
    
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '5432')
    DB_USER = os.getenv('DB_USER', 'postgres')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'hengmengly123')
    DB_NAME = os.getenv('DB_NAME', 'ecommerce_db')
    
    print("🔍 QUICK DATABASE STATUS CHECK")
    print("=" * 40)
    print(f"Database: {DB_NAME}")
    print(f"Host: {DB_HOST}:{DB_PORT}")
    print()
    
    try:
        # Check if database exists
        conn_postgres = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database='postgres'
        )
        cursor_postgres = conn_postgres.cursor()
        
        cursor_postgres.execute(f"SELECT 1 FROM pg_database WHERE datname = '{DB_NAME}';")
        db_exists = cursor_postgres.fetchone() is not None
        
        cursor_postgres.close()
        conn_postgres.close()
        
        if not db_exists:
            print("🔴 DATABASE NOT FOUND - DISASTER SCENARIO ACTIVE")
            print("   The database does not exist - perfect for testing emergency recovery!")
            print()
            print("📋 TO RESTORE:")
            print("   1. Open http://localhost:3002")
            print("   2. Login with emergency credentials")
            print("   3. Select a backup file")
            print("   4. Restore the database")
            return False
        
        # Try to connect to the database
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        cursor = conn.cursor()
        
        # Quick data check
        cursor.execute("SELECT COUNT(*) FROM users;")
        user_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM products;")
        product_count = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        print("🟢 DATABASE IS OPERATIONAL")
        print(f"   Users: {user_count}")
        print(f"   Products: {product_count}")
        print()
        print("✅ Database appears to be working normally")
        return True
        
    except psycopg2.Error as e:
        print(f"🔴 DATABASE ERROR: {e}")
        print("   The database may be corrupted or inaccessible")
        print()
        print("📋 TO RESTORE:")
        print("   1. Open http://localhost:3002")
        print("   2. Login with emergency credentials")
        print("   3. Select a backup file")
        print("   4. Restore the database")
        return False
    
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

if __name__ == "__main__":
    check_database_status()
