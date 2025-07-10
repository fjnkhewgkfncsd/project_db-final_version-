#!/usr/bin/env python3
"""
Fix the restore issue by creating a proper backup with DROP statements
"""
import subprocess
import os
import time
from datetime import datetime

def create_proper_backup():
    """Create a backup with proper DROP statements"""
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    backup_filename = f"ecommerce_backup_FIXED_{timestamp}.sql"
    backup_path = f"backups/{backup_filename}"
    
    print("🔧 Creating FIXED backup with proper DROP statements...")
    
    env = {
        **os.environ,
        'PGPASSWORD': os.getenv('DB_PASSWORD', 'hengmengly123')
    }
    
    # Use pg_dump with --clean and --if-exists flags
    cmd = [
        'pg_dump',
        '-h', os.getenv('DB_HOST', 'localhost'),
        '-p', os.getenv('DB_PORT', '5432'),
        '-U', os.getenv('DB_USER', 'postgres'),
        '-d', os.getenv('DB_NAME', 'ecommerce_db'),
        '--verbose',
        '--clean',           # Add DROP statements
        '--if-exists',       # Add IF EXISTS to DROP statements
        '--create',          # Add CREATE DATABASE statement
        '-f', backup_path
    ]
    
    print(f"🚀 Running: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, env=env)
        
        if result.returncode == 0:
            # Check file size
            file_size = os.path.getsize(backup_path) / (1024 * 1024)
            print(f"✅ FIXED backup created successfully!")
            print(f"   📄 File: {backup_filename}")
            print(f"   📊 Size: {file_size:.2f} MB")
            
            # Verify it has DROP statements
            with open(backup_path, 'r', encoding='utf-8') as f:
                content = f.read(5000)  # Read first 5KB
            
            drop_count = content.count('DROP TABLE')
            if drop_count > 0:
                print(f"   ✅ Contains {drop_count} DROP TABLE statements")
            else:
                print("   ⚠️  Warning: No DROP TABLE statements found")
            
            return backup_filename
            
        else:
            print(f"❌ Backup failed: {result.stderr}")
            return None
            
    except Exception as e:
        print(f"❌ Error creating backup: {e}")
        return None

def test_fixed_restore(backup_filename):
    """Test restore with the fixed backup file"""
    print(f"\n🧪 Testing restore with FIXED backup: {backup_filename}")
    
    # Get current user count
    current_users = get_user_count()
    print(f"   👥 Current users before restore: {current_users}")
    
    # Perform restore
    backup_path = f"backups/{backup_filename}"
    
    env = {
        **os.environ,
        'PGPASSWORD': os.getenv('DB_PASSWORD', 'hengmengly123')
    }
    
    cmd = [
        'psql',
        '-h', os.getenv('DB_HOST', 'localhost'),
        '-p', os.getenv('DB_PORT', '5432'),
        '-U', os.getenv('DB_USER', 'postgres'),
        '-d', 'postgres',  # Connect to postgres database
        '-f', backup_path
    ]
    
    print(f"   🔄 Restoring...")
    start_time = time.time()
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, env=env)
        duration = time.time() - start_time
        
        print(f"   ⏱️  Restore took {duration:.2f} seconds")
        print(f"   🔢 Exit code: {result.returncode}")
        
        if result.returncode == 0:
            print("   ✅ Restore command completed successfully")
            
            # Check user count after restore
            time.sleep(2)  # Give database time to settle
            new_users = get_user_count()
            print(f"   👥 Users after restore: {new_users}")
            
            if isinstance(current_users, int) and isinstance(new_users, int):
                if new_users == current_users:
                    print("   ❌ User count unchanged - restore still not working")
                else:
                    print(f"   ✅ User count changed: {current_users} → {new_users}")
            
        else:
            print(f"   ❌ Restore failed: {result.stderr}")
            
    except Exception as e:
        print(f"   ❌ Restore error: {e}")

def get_user_count():
    """Get current user count from database"""
    env = {
        **os.environ,
        'PGPASSWORD': os.getenv('DB_PASSWORD', 'hengmengly123')
    }
    
    cmd = [
        'psql',
        '-h', os.getenv('DB_HOST', 'localhost'),
        '-p', os.getenv('DB_PORT', '5432'),
        '-U', os.getenv('DB_USER', 'postgres'),
        '-d', os.getenv('DB_NAME', 'ecommerce_db'),
        '-t',
        '-c', 'SELECT COUNT(*) FROM users;'
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, env=env)
        if result.returncode == 0:
            return int(result.stdout.strip())
        else:
            return f"Error: {result.stderr}"
    except Exception as e:
        return f"Exception: {e}"

def fix_existing_backup():
    """Fix an existing backup by adding proper DROP statements"""
    original_backup = "backups/ecommerce_backup_2025-07-09_05-01-55.sql"
    
    if not os.path.exists(original_backup):
        print(f"❌ Original backup not found: {original_backup}")
        return None
    
    print(f"🔧 Fixing existing backup: {original_backup}")
    
    # Read the original backup
    with open(original_backup, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Create fixed version
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    fixed_backup = f"backups/ecommerce_backup_FIXED_MANUAL_{timestamp}.sql"
    
    # Add DROP statements before CREATE statements
    fixed_content = []
    
    # Add header
    fixed_content.append("-- FIXED BACKUP FILE WITH PROPER DROP STATEMENTS")
    fixed_content.append("-- Generated automatically to fix restore issues")
    fixed_content.append("")
    
    # Add DROP statements
    drop_statements = [
        "DROP DATABASE IF EXISTS ecommerce_db;",
        "",
        "-- Now proceed with original backup content",
        ""
    ]
    
    fixed_content.extend(drop_statements)
    fixed_content.append(content)
    
    # Write fixed backup
    with open(fixed_backup, 'w', encoding='utf-8') as f:
        f.write('\n'.join(fixed_content))
    
    file_size = os.path.getsize(fixed_backup) / (1024 * 1024)
    print(f"✅ Fixed backup created: {os.path.basename(fixed_backup)}")
    print(f"   📊 Size: {file_size:.2f} MB")
    
    return os.path.basename(fixed_backup)

def main():
    """Main function to fix restore issues"""
    print("🔧 RESTORE ISSUE FIX TOOL")
    print("=" * 50)
    print("This tool will create a proper backup with DROP statements")
    print("that should fix your restore issue.")
    print()
    
    print("Choose an option:")
    print("1. Create new backup with proper DROP statements")
    print("2. Fix existing backup by adding DROP statements")
    print("3. Test restore with current 10006-user backup")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice == '1':
        backup_filename = create_proper_backup()
        if backup_filename:
            response = input(f"\nTest restore with new backup? (y/N): ")
            if response.lower() == 'y':
                test_fixed_restore(backup_filename)
    
    elif choice == '2':
        backup_filename = fix_existing_backup()
        if backup_filename:
            response = input(f"\nTest restore with fixed backup? (y/N): ")
            if response.lower() == 'y':
                test_fixed_restore(backup_filename)
    
    elif choice == '3':
        print("\n🧪 Testing restore with existing 10006-user backup...")
        test_fixed_restore("ecommerce_backup_2025-07-09_05-01-55.sql")
    
    else:
        print("❌ Invalid choice")

if __name__ == "__main__":
    main()
