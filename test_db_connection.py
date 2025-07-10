#!/usr/bin/env python3
"""
Test database connection and verify restore prerequisites
"""

import psycopg2
import os
import sys
from datetime import datetime

def test_db_connection():
    """Test if we can connect to the database"""
    try:
        # Database credentials from .env
        connection = psycopg2.connect(
            host="localhost",
            port="5432",
            database="ecommerce_db",
            user="postgres",
            password="hengmengly123"
        )
        
        cursor = connection.cursor()
        
        # Test basic query
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"✅ Database connected successfully!")
        print(f"PostgreSQL version: {version[0]}")
        
        # Check if database has tables
        cursor.execute("""
            SELECT COUNT(*) 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        table_count = cursor.fetchone()[0]
        print(f"📊 Number of tables in database: {table_count}")
        
        # Check if we have some sample data
        if table_count > 0:
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                ORDER BY table_name
            """)
            tables = cursor.fetchall()
            print(f"📋 Tables: {[t[0] for t in tables]}")
            
            # Check users table specifically
            try:
                cursor.execute("SELECT COUNT(*) FROM users")
                user_count = cursor.fetchone()[0]
                print(f"👥 Users in database: {user_count}")
            except:
                print("⚠️  Users table not found or inaccessible")
        
        cursor.close()
        connection.close()
        return True
        
    except psycopg2.Error as e:
        print(f"❌ Database connection failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def check_backup_files():
    """Check if we have backup files available"""
    backup_dir = "backups"
    if not os.path.exists(backup_dir):
        print(f"❌ Backup directory '{backup_dir}' not found")
        return False
    
    sql_files = [f for f in os.listdir(backup_dir) if f.endswith('.sql')]
    if not sql_files:
        print(f"❌ No .sql backup files found in '{backup_dir}'")
        return False
    
    print(f"✅ Found {len(sql_files)} backup files:")
    for i, file in enumerate(sorted(sql_files)[-5:], 1):  # Show last 5
        file_path = os.path.join(backup_dir, file)
        size = os.path.getsize(file_path) / 1024 / 1024  # MB
        print(f"  {i}. {file} ({size:.2f} MB)")
    
    return True

def test_restore_prerequisites():
    """Test if all prerequisites for restore are met"""
    print("🔍 Testing Database Restore Prerequisites")
    print("=" * 50)
    
    # Test 1: Database connection
    print("\n1. Testing database connection...")
    db_ok = test_db_connection()
    
    # Test 2: Backup files
    print("\n2. Checking backup files...")
    backup_ok = check_backup_files()
    
    # Test 3: Python dependencies
    print("\n3. Checking Python dependencies...")
    try:
        import psycopg2
        print("✅ psycopg2 available")
        deps_ok = True
    except ImportError:
        print("❌ psycopg2 not installed")
        deps_ok = False
    
    # Summary
    print("\n" + "=" * 50)
    print("SUMMARY:")
    print(f"Database Connection: {'✅ OK' if db_ok else '❌ FAILED'}")
    print(f"Backup Files:       {'✅ OK' if backup_ok else '❌ FAILED'}")
    print(f"Dependencies:       {'✅ OK' if deps_ok else '❌ FAILED'}")
    
    if db_ok and backup_ok and deps_ok:
        print("\n🎉 All prerequisites met! Ready for restore testing.")
        return True
    else:
        print("\n⚠️  Some prerequisites failed. Please fix before testing restore.")
        return False

if __name__ == "__main__":
    success = test_restore_prerequisites()
    sys.exit(0 if success else 1)
