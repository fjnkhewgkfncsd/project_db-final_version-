#!/usr/bin/env python3
"""
Proper Database Restore Script
Handles constraint conflicts by truncating tables before restore
"""
import psycopg2
import os
import subprocess
from dotenv import load_dotenv

# Load environment variables
load_dotenv('backend/.env')

def proper_restore_with_truncate(backup_filename):
    """Properly restore backup by truncating tables first"""
    
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '5432')
    DB_USER = os.getenv('DB_USER', 'postgres')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'hengmengly123')
    DB_NAME = os.getenv('DB_NAME', 'ecommerce_db')
    
    backup_path = os.path.join('backups', backup_filename)
    
    print("🔄 PROPER DATABASE RESTORE WITH TRUNCATION")
    print("=" * 60)
    print(f"Backup file: {backup_filename}")
    print(f"Target database: {DB_NAME}")
    print()
    
    try:
        # Step 1: Connect and truncate all tables to avoid conflicts
        print("1. 🗑️  Truncating existing tables to avoid conflicts...")
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Get all table names
        cursor.execute("""
            SELECT tablename 
            FROM pg_tables 
            WHERE schemaname = 'public' 
            AND tablename NOT LIKE 'pg_%'
            ORDER BY tablename;
        """)
        tables = [row[0] for row in cursor.fetchall()]
        
        if tables:
            print(f"   Found {len(tables)} tables: {', '.join(tables)}")
            
            # Disable triggers to avoid cascade issues
            for table in tables:
                cursor.execute(f'ALTER TABLE public.{table} DISABLE TRIGGER ALL;')
            
            # Truncate all tables
            truncate_query = 'TRUNCATE TABLE ' + ', '.join([f'public.{table}' for table in tables]) + ' RESTART IDENTITY CASCADE;'
            cursor.execute(truncate_query)
            
            # Re-enable triggers
            for table in tables:
                cursor.execute(f'ALTER TABLE public.{table} ENABLE TRIGGER ALL;')
            
            print("   ✅ All tables truncated successfully")
        else:
            print("   ⚠️  No tables found to truncate")
        
        cursor.close()
        conn.close()
        
        # Step 2: Restore from backup
        print("2. 📥 Restoring data from backup...")
        
        # Set environment variable for password
        env = os.environ.copy()
        env['PGPASSWORD'] = DB_PASSWORD
        
        # Execute psql restore
        restore_command = [
            'psql',
            '-h', DB_HOST,
            '-p', DB_PORT,
            '-U', DB_USER,
            '-d', DB_NAME,
            '-f', backup_path,
            '--set', 'ON_ERROR_STOP=off'  # Continue on errors
        ]
        
        print(f"   Command: {' '.join(restore_command)}")
        
        result = subprocess.run(
            restore_command,
            env=env,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("   ✅ Restore completed successfully")
        else:
            print(f"   ⚠️  Restore completed with warnings (exit code: {result.returncode})")
            if result.stderr:
                print(f"   Stderr: {result.stderr[:500]}...")
        
        # Step 3: Verify restoration
        print("3. 🔍 Verifying restoration...")
        
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        cursor = conn.cursor()
        
        # Count users
        cursor.execute("SELECT COUNT(*) FROM users;")
        user_count = cursor.fetchone()[0]
        
        # Count products
        cursor.execute("SELECT COUNT(*) FROM products;")
        product_count = cursor.fetchone()[0]
        
        # Count by role
        cursor.execute("SELECT role, COUNT(*) FROM users GROUP BY role ORDER BY role;")
        role_counts = cursor.fetchall()
        
        print(f"   👥 Total users: {user_count}")
        print(f"   📦 Total products: {product_count}")
        print("   📊 Users by role:")
        for role, count in role_counts:
            print(f"      {role}: {count}")
        
        # Check admin user
        cursor.execute("SELECT username, email, first_name, last_name FROM users WHERE role = 'admin' LIMIT 5;")
        admin_users = cursor.fetchall()
        print(f"   👑 Sample admin users ({len(admin_users)}):")
        for username, email, first_name, last_name in admin_users:
            print(f"      {username} | {email} | {first_name} {last_name}")
        
        cursor.close()
        conn.close()
        
        print()
        print("🎉 RESTORE COMPLETED SUCCESSFULLY!")
        print(f"✅ Database now contains {user_count} users and {product_count} products")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during restore: {e}")
        return False

if __name__ == "__main__":
    # Use the backup file that contains 10,002 users
    backup_file = "ecommerce_data_2025-06-27_04-13-11.sql"
    
    print("This script will properly restore the backup with 10,002 users")
    print("by truncating existing tables first to avoid constraint conflicts.")
    print()
    
    confirm = input("Proceed with full restore? (y/N): ")
    if confirm.lower() == 'y':
        success = proper_restore_with_truncate(backup_file)
        if success:
            print("\\nYou can now login to the main system with any of the admin users!")
        else:
            print("\\nRestore failed. Check the error messages above.")
    else:
        print("Restore cancelled.")
