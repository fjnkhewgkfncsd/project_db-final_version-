#!/usr/bin/env python3
"""
Manual Database Drop Script for Disaster Recovery Testing
Safely drops the ecommerce database to test emergency recovery
"""
import psycopg2
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('backend/.env')

def drop_database():
    """Drop the ecommerce database"""
    
    # Database connection parameters
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '5432')
    DB_USER = os.getenv('DB_USER', 'postgres')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'hengmengly123')
    DB_NAME = os.getenv('DB_NAME', 'ecommerce_db')
    
    print("🚨 DATABASE DROP SIMULATION")
    print("=" * 50)
    print(f"Target Database: {DB_NAME}")
    print(f"Host: {DB_HOST}:{DB_PORT}")
    print(f"User: {DB_USER}")
    print()
    
    # Confirm operation
    confirmation = input("⚠️  This will DROP the entire database! Type 'DROP DATABASE' to confirm: ")
    if confirmation != "DROP DATABASE":
        print("❌ Operation cancelled")
        return False
    
    try:
        # Connect to PostgreSQL (to default 'postgres' database)
        print("🔌 Connecting to PostgreSQL...")
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database='postgres'  # Connect to default database
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        # First, terminate any active connections to the target database
        print(f"🔄 Terminating active connections to {DB_NAME}...")
        cursor.execute(f"""
            SELECT pg_terminate_backend(pid)
            FROM pg_stat_activity
            WHERE datname = '{DB_NAME}' AND pid <> pg_backend_pid();
        """)
        
        # Check if database exists
        cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{DB_NAME}';")
        if not cursor.fetchone():
            print(f"ℹ️  Database '{DB_NAME}' does not exist")
            return False
        
        # Drop the database
        print(f"💥 Dropping database '{DB_NAME}'...")
        cursor.execute(f'DROP DATABASE "{DB_NAME}";')
        
        # Verify deletion
        cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{DB_NAME}';")
        if cursor.fetchone():
            print("❌ Database drop failed - database still exists")
            return False
        
        print("✅ Database successfully dropped!")
        print()
        print("📋 NEXT STEPS:")
        print("1. Open http://localhost:3002 in your browser")
        print("2. Login with emergency credentials:")
        print("   - Username: emergency_admin")
        print("   - Password: EmergencyRestore2025!")
        print("3. Select a backup file to restore")
        print("4. Confirm the restore operation")
        print("5. Verify the restoration was successful")
        print()
        
        cursor.close()
        conn.close()
        return True
        
    except psycopg2.Error as e:
        print(f"❌ PostgreSQL Error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def verify_database_deleted():
    """Verify that the database has been deleted"""
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '5432')
    DB_USER = os.getenv('DB_USER', 'postgres')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'hengmengly123')
    DB_NAME = os.getenv('DB_NAME', 'ecommerce_db')
    
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database='postgres'
        )
        cursor = conn.cursor()
        
        cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{DB_NAME}';")
        exists = cursor.fetchone() is not None
        
        cursor.close()
        conn.close()
        
        if exists:
            print(f"🟢 Database '{DB_NAME}' still exists")
        else:
            print(f"🔴 Database '{DB_NAME}' does not exist - DISASTER SCENARIO CONFIRMED")
        
        return not exists
        
    except Exception as e:
        print(f"❌ Error checking database: {e}")
        return False

if __name__ == "__main__":
    print("Starting manual database drop for disaster recovery testing...")
    print()
    
    # First verify current state
    print("🔍 Checking current database state...")
    if not verify_database_deleted():
        # Database exists, proceed with drop
        if drop_database():
            print("\n🎯 Disaster scenario created successfully!")
            print("Database has been dropped - you can now test emergency recovery.")
        else:
            print("\n❌ Failed to create disaster scenario")
    else:
        print("ℹ️  Database is already deleted - disaster scenario already active")
        print("You can proceed with emergency recovery testing.")
