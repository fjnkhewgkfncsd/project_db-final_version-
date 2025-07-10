#!/usr/bin/env python3
"""
Database Deletion Script for Emergency Recovery Testing
This script will completely drop the ecommerce_db database to test emergency recovery
"""

import psycopg2
import sys
from datetime import datetime

# Database configuration (connect to postgres DB to drop ecommerce_db)
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'user': 'postgres',
    'password': 'hengmengly123',
    'database': 'postgres'  # Connect to postgres DB to manage ecommerce_db
}

ECOMMERCE_DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'user': 'postgres',
    'password': 'hengmengly123',
    'database': 'ecommerce_db'
}

def check_current_database_state():
    """Check current database state before deletion"""
    print("📊 Checking current database state...")
    
    try:
        conn = psycopg2.connect(**ECOMMERCE_DB_CONFIG)
        cursor = conn.cursor()
        
        # Get table counts
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM products")
        product_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM orders")
        order_count = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        print(f"✅ Current database state:")
        print(f"   Users: {user_count}")
        print(f"   Products: {product_count}")
        print(f"   Orders: {order_count}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error checking database state: {e}")
        return False

def drop_ecommerce_database():
    """Completely drop the ecommerce database"""
    print("\n🗑️ DROPPING ECOMMERCE DATABASE...")
    print("⚠️ This will completely remove the ecommerce_db database!")
    
    try:
        # Connect to postgres database to drop ecommerce_db
        conn = psycopg2.connect(**DB_CONFIG)
        conn.autocommit = True
        cursor = conn.cursor()
        
        print("   Terminating existing connections...")
        # Terminate all connections to the target database
        cursor.execute("""
            SELECT pg_terminate_backend(pid)
            FROM pg_stat_activity
            WHERE datname = 'ecommerce_db' AND pid <> pg_backend_pid()
        """)
        
        print("   Dropping database...")
        # Drop the database
        cursor.execute("DROP DATABASE IF EXISTS ecommerce_db")
        
        cursor.close()
        conn.close()
        
        print("💥 DATABASE SUCCESSFULLY DROPPED!")
        print("   The ecommerce_db database has been completely removed")
        
        return True
        
    except Exception as e:
        print(f"❌ Error dropping database: {e}")
        return False

def verify_database_is_gone():
    """Verify that the database is actually gone"""
    print("\n🔍 Verifying database deletion...")
    
    try:
        # Try to connect to the deleted database
        conn = psycopg2.connect(**ECOMMERCE_DB_CONFIG)
        print("❌ ERROR: Database still exists! Deletion failed.")
        conn.close()
        return False
        
    except psycopg2.OperationalError as e:
        if "does not exist" in str(e) or "database" in str(e).lower():
            print("✅ CONFIRMED: Database successfully deleted")
            print("   Connection failed as expected - database no longer exists")
            return True
        else:
            print(f"❌ Unexpected error: {e}")
            return False
    except Exception as e:
        print(f"❌ Unexpected error verifying deletion: {e}")
        return False

def main():
    """Main function to drop database for testing"""
    print("🧪 DATABASE DELETION FOR EMERGENCY RECOVERY TESTING")
    print("=" * 70)
    print("⚠️ WARNING: This will COMPLETELY DELETE the ecommerce_db database!")
    print("=" * 70)
    print(f"🕒 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Step 1: Check current state
    print("📊 Step 1: Checking current database state...")
    if not check_current_database_state():
        print("❌ Cannot access current database. It may already be deleted.")
        return 1
    
    # Step 2: Final confirmation
    print("\n🚨 FINAL CONFIRMATION 🚨")
    print("You are about to:")
    print("• COMPLETELY DELETE the ecommerce_db database")
    print("• ALL data will be PERMANENTLY LOST")
    print("• You will need to use the emergency recovery page to restore")
    print()
    print("After deletion, you should:")
    print("1. Go to http://localhost:3002 (Emergency Recovery Page)")
    print("2. Login with: emergency_admin / EmergencyRestore2025!")
    print("3. Select a backup file to restore")
    print("4. Execute the restore operation")
    print()
    
    # For manual testing, ask for confirmation
    confirm = input("Type 'DELETE' to proceed with database deletion: ")
    
    if confirm.upper() != 'DELETE':
        print("❌ Operation cancelled. Database not deleted.")
        return 1
    
    # Step 3: Drop the database
    print("\n💥 Step 3: Dropping database...")
    deletion_success = drop_ecommerce_database()
    
    if not deletion_success:
        print("❌ Failed to drop database")
        return 1
    
    # Step 4: Verify deletion
    print("\n🔍 Step 4: Verifying deletion...")
    deletion_verified = verify_database_is_gone()
    
    if not deletion_verified:
        print("❌ Database deletion could not be verified")
        return 1
    
    # Step 5: Instructions for recovery
    print("\n" + "=" * 70)
    print("✅ DATABASE SUCCESSFULLY DELETED!")
    print("=" * 70)
    print()
    print("🚑 NEXT STEPS - EMERGENCY RECOVERY:")
    print()
    print("1. 🌐 Open Emergency Recovery Page:")
    print("   http://localhost:3002")
    print()
    print("2. 🔐 Login with Emergency Credentials:")
    print("   Username: emergency_admin")
    print("   Password: EmergencyRestore2025!")
    print()
    print("3. 📁 Select a Backup File:")
    print("   - Choose from available backup files")
    print("   - Recommend using the latest complete backup")
    print()
    print("4. 🔧 Execute Restore:")
    print("   - Click 'Restore Database'")
    print("   - Wait for restore to complete")
    print("   - Verify restoration success")
    print()
    print("🎯 This tests the REAL emergency scenario!")
    print("   Database is completely gone and needs emergency recovery")
    print()
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    print(f"\n🏁 Database deletion completed with exit code: {exit_code}")
    sys.exit(exit_code)
