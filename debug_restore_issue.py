#!/usr/bin/env python3
"""
Debug the restore issue - why 10,006 users backup restores to only 10,003 users
"""
import subprocess
import os
import time
import sys

def run_psql_command(sql_command, database='ecommerce_db'):
    """Run a PostgreSQL command and return the result"""
    env = {
        **os.environ,
        'PGPASSWORD': os.getenv('DB_PASSWORD', 'hengmengly123')
    }
    
    cmd = [
        'psql',
        '-h', os.getenv('DB_HOST', 'localhost'),
        '-p', os.getenv('DB_PORT', '5432'),
        '-U', os.getenv('DB_USER', 'postgres'),
        '-d', database,
        '-t',  # tuples only
        '-c', sql_command
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, env=env)
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            return f"ERROR: {result.stderr}"
    except Exception as e:
        return f"EXCEPTION: {e}"

def count_users_in_db():
    """Count current users in database"""
    result = run_psql_command("SELECT COUNT(*) FROM users;")
    try:
        return int(result)
    except:
        return f"Error counting users: {result}"

def get_max_user_id():
    """Get the highest user ID in database"""
    result = run_psql_command("SELECT MAX(user_id) FROM users;")
    try:
        return int(result) if result and result != 'ERROR' else 0
    except:
        return f"Error getting max ID: {result}"

def get_user_id_range():
    """Get the range of user IDs"""
    min_result = run_psql_command("SELECT MIN(user_id) FROM users;")
    max_result = run_psql_command("SELECT MAX(user_id) FROM users;")
    try:
        min_id = int(min_result)
        max_id = int(max_result)
        return min_id, max_id
    except:
        return f"Error: {min_result}, {max_result}"

def test_manual_restore():
    """Test the restore process manually step by step"""
    print("🧪 MANUAL RESTORE TEST")
    print("=" * 50)
    
    backup_file = "backups/ecommerce_backup_2025-07-09_05-01-55.sql"
    
    if not os.path.exists(backup_file):
        print(f"❌ Backup file not found: {backup_file}")
        return False
    
    print(f"📁 Using backup file: {backup_file}")
    
    # Step 1: Check current state
    print("\n📊 Step 1: Current Database State")
    current_users = count_users_in_db()
    print(f"   👥 Current users: {current_users}")
    
    min_id, max_id = get_user_id_range()
    print(f"   🔢 User ID range: {min_id} to {max_id}")
    
    # Step 2: Check what's in the backup file
    print("\n📄 Step 2: Analyzing Backup File")
    try:
        with open(backup_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Look for DROP/TRUNCATE statements
        drop_users = content.count('DROP TABLE users') + content.count('DROP TABLE public.users')
        truncate_users = content.count('TRUNCATE users') + content.count('TRUNCATE public.users')
        delete_users = content.count('DELETE FROM users') + content.count('DELETE FROM public.users')
        
        print(f"   🗑️  DROP TABLE statements: {drop_users}")
        print(f"   🧹 TRUNCATE statements: {truncate_users}")
        print(f"   ❌ DELETE statements: {delete_users}")
        
        # Check for CREATE DATABASE
        create_db = content.count('CREATE DATABASE')
        print(f"   🏗️  CREATE DATABASE statements: {create_db}")
        
        # Find the users COPY section
        copy_start = content.find('COPY public.users')
        if copy_start != -1:
            copy_end = content.find('\\.', copy_start)
            if copy_end != -1:
                users_section = content[copy_start:copy_end]
                user_lines = users_section.split('\n')[1:]  # Skip header line
                user_count = len([line for line in user_lines if line.strip()])
                print(f"   📋 Users in backup COPY section: {user_count}")
            else:
                print("   ⚠️  Could not find end of COPY section")
        else:
            print("   ⚠️  No COPY public.users section found")
            
    except Exception as e:
        print(f"   ❌ Error reading backup file: {e}")
    
    # Step 3: Manual restore test
    print(f"\n🔄 Step 3: Testing Manual Restore")
    print("   ⚠️  This will actually restore the database!")
    
    response = input("   Continue with restore test? (y/N): ")
    if response.lower() != 'y':
        print("   ❌ Restore test cancelled")
        return False
    
    # Execute the restore
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
        '-f', backup_file
    ]
    
    print(f"   🚀 Executing: {' '.join(cmd)}")
    start_time = time.time()
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, env=env)
        duration = time.time() - start_time
        
        print(f"   ⏱️  Restore completed in {duration:.2f} seconds")
        print(f"   🔢 Exit code: {result.returncode}")
        
        if result.stdout:
            stdout_lines = result.stdout.split('\n')
            print(f"   📤 STDOUT ({len(stdout_lines)} lines):")
            for line in stdout_lines[-10:]:  # Show last 10 lines
                if line.strip():
                    print(f"      {line}")
        
        if result.stderr:
            stderr_lines = result.stderr.split('\n')
            print(f"   📥 STDERR ({len(stderr_lines)} lines):")
            for line in stderr_lines[-10:]:  # Show last 10 lines
                if line.strip():
                    print(f"      {line}")
                    
    except Exception as e:
        print(f"   ❌ Restore command failed: {e}")
        return False
    
    # Step 4: Check result
    print(f"\n📊 Step 4: Post-Restore Database State")
    time.sleep(2)  # Give database time to settle
    
    new_users = count_users_in_db()
    print(f"   👥 Users after restore: {new_users}")
    
    new_min_id, new_max_id = get_user_id_range()
    print(f"   🔢 New user ID range: {new_min_id} to {new_max_id}")
    
    # Compare results
    print(f"\n📈 Step 5: Results Analysis")
    if isinstance(current_users, int) and isinstance(new_users, int):
        difference = new_users - current_users
        print(f"   📊 User count change: {current_users} → {new_users} ({difference:+d})")
        
        if new_users == 10006:
            print("   ✅ SUCCESS! Restore worked correctly!")
        elif new_users == current_users:
            print("   ❌ PROBLEM: User count unchanged - restore didn't work")
        else:
            print(f"   ⚠️  PARTIAL: User count changed but not to expected 10,006")
    else:
        print(f"   ❌ Error comparing results: {current_users} vs {new_users}")
    
    return True

def check_database_constraints():
    """Check for constraints that might prevent restore"""
    print("\n🔍 CONSTRAINT CHECK")
    print("=" * 50)
    
    # Check for foreign key constraints
    fk_query = """
    SELECT tc.constraint_name, tc.table_name, kcu.column_name, 
           ccu.table_name AS foreign_table_name,
           ccu.column_name AS foreign_column_name 
    FROM information_schema.table_constraints AS tc 
    JOIN information_schema.key_column_usage AS kcu
      ON tc.constraint_name = kcu.constraint_name
    JOIN information_schema.constraint_column_usage AS ccu
      ON ccu.constraint_name = tc.constraint_name
    WHERE constraint_type = 'FOREIGN KEY' AND tc.table_name='users';
    """
    
    print("🔗 Foreign key constraints on users table:")
    fk_result = run_psql_command(fk_query)
    if fk_result.strip():
        print(f"   {fk_result}")
    else:
        print("   ✅ No foreign key constraints found")
    
    # Check for triggers
    trigger_query = """
    SELECT trigger_name, event_manipulation, action_statement
    FROM information_schema.triggers 
    WHERE event_object_table = 'users';
    """
    
    print("\n⚡ Triggers on users table:")
    trigger_result = run_psql_command(trigger_query)
    if trigger_result.strip():
        print(f"   {trigger_result}")
    else:
        print("   ✅ No triggers found")

def main():
    """Main diagnostic function"""
    print("🔍 RESTORE DEBUGGING TOOL")
    print("=" * 50)
    print("This tool will help diagnose why your restore isn't working correctly.")
    print()
    
    # Basic checks
    check_database_constraints()
    
    # Main test
    if test_manual_restore():
        print("\n✅ Diagnostic complete!")
    else:
        print("\n❌ Diagnostic failed!")

if __name__ == "__main__":
    main()
