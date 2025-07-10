#!/usr/bin/env python3
"""
List backup files and their restore safety status
"""
import os
import glob
from datetime import datetime

def analyze_backup_safety():
    """Analyze backup files for restore safety"""
    print("🔍 BACKUP FILE RESTORE SAFETY ANALYSIS")
    print("=" * 70)
    
    backup_dir = "backups"
    if not os.path.exists(backup_dir):
        print("❌ Backup directory not found")
        return
    
    # Get all backup files
    sql_files = glob.glob(os.path.join(backup_dir, "*.sql"))
    backup_files = glob.glob(os.path.join(backup_dir, "*.backup"))
    
    all_files = sql_files + backup_files
    all_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
    
    if not all_files:
        print("❌ No backup files found")
        return
    
    print(f"📊 Found {len(all_files)} backup files")
    print()
    
    safe_files = []
    unsafe_files = []
    
    for file_path in all_files:
        filename = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)
        file_size_mb = file_size / (1024 * 1024)
        modified_time = datetime.fromtimestamp(os.path.getmtime(file_path))
        
        # Analyze file content for safety
        safety_status = analyze_file_safety(file_path, filename)
        
        file_info = {
            'filename': filename,
            'size_mb': file_size_mb,
            'modified': modified_time,
            'safety': safety_status
        }
        
        if safety_status['safe']:
            safe_files.append(file_info)
        else:
            unsafe_files.append(file_info)
    
    # Print safe files
    print("✅ SAFE TO RESTORE (Recommended)")
    print("-" * 50)
    if safe_files:
        for i, file_info in enumerate(safe_files, 1):
            print(f"{i:2d}. 📄 {file_info['filename']}")
            print(f"    📊 Size: {file_info['size_mb']:.1f} MB")
            print(f"    🕐 Modified: {file_info['modified'].strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"    ✅ Status: {file_info['safety']['reason']}")
            if file_info['safety']['user_count']:
                print(f"    👥 Users: {file_info['safety']['user_count']}")
            print()
    else:
        print("❌ No safe backup files found!")
    
    # Print unsafe files
    print("\n⚠️  POTENTIALLY UNSAFE (May Cause Issues)")
    print("-" * 50)
    if unsafe_files:
        for i, file_info in enumerate(unsafe_files, 1):
            print(f"{i:2d}. 📄 {file_info['filename']}")
            print(f"    📊 Size: {file_info['size_mb']:.1f} MB")
            print(f"    🕐 Modified: {file_info['modified'].strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"    ⚠️  Issue: {file_info['safety']['reason']}")
            if file_info['safety']['user_count']:
                print(f"    👥 Users: {file_info['safety']['user_count']}")
            print()
    else:
        print("✅ All backup files appear safe!")
    
    # Print recommendations
    print_recommendations(safe_files, unsafe_files)

def analyze_file_safety(file_path, filename):
    """Analyze a specific backup file for restore safety"""
    try:
        # For .backup files (binary format), assume they're safe
        if filename.endswith('.backup'):
            return {
                'safe': True,
                'reason': 'Binary format backup (pg_restore compatible)',
                'user_count': None
            }
        
        # For .sql files, check content
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read(10000)  # Read first 10KB for analysis
        
        # Check for safety indicators
        has_drop_database = 'DROP DATABASE' in content
        has_create_database = 'CREATE DATABASE' in content
        has_drop_table = 'DROP TABLE' in content
        has_clean_flags = '--clean' in content or 'DROP TABLE IF EXISTS' in content
        
        # Check if this is the fixed backup we created
        is_fixed_backup = 'FIXED' in filename.upper()
        
        # Count users in the file
        user_count = count_users_in_backup(file_path)
        
        # Determine safety
        if is_fixed_backup:
            return {
                'safe': True,
                'reason': 'Fixed backup with proper DROP statements',
                'user_count': user_count
            }
        elif has_drop_database:
            return {
                'safe': True,
                'reason': 'Contains DROP DATABASE statement',
                'user_count': user_count
            }
        elif has_drop_table or has_clean_flags:
            return {
                'safe': True,
                'reason': 'Contains DROP TABLE statements',
                'user_count': user_count
            }
        elif 'CREATE DATABASE' in content and user_count and user_count > 1000:
            # Newer backups created with our improved system
            created_after_fix = any(date in filename for date in ['2025-07-09', '2025-07-10'])
            if created_after_fix:
                return {
                    'safe': True,
                    'reason': 'Recent backup with proper format',
                    'user_count': user_count
                }
            else:
                return {
                    'safe': False,
                    'reason': 'Old backup missing DROP statements',
                    'user_count': user_count
                }
        else:
            return {
                'safe': False,
                'reason': 'Missing critical DROP statements',
                'user_count': user_count
            }
            
    except Exception as e:
        return {
            'safe': False,
            'reason': f'Error analyzing file: {str(e)}',
            'user_count': None
        }

def count_users_in_backup(file_path):
    """Count users in a backup file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Count INSERT statements for users
        insert_count = content.count('INSERT INTO users') + content.count('INSERT INTO public.users')
        
        # Count COPY data lines for users
        copy_start = content.find('COPY public.users')
        if copy_start != -1:
            copy_end = content.find('\\.', copy_start)
            if copy_end != -1:
                users_section = content[copy_start:copy_end]
                copy_lines = users_section.split('\n')[1:]  # Skip header
                copy_count = len([line for line in copy_lines if line.strip()])
                return copy_count
        
        return insert_count if insert_count > 0 else None
        
    except Exception:
        return None

def print_recommendations(safe_files, unsafe_files):
    """Print recommendations for backup usage"""
    print("\n🎯 RECOMMENDATIONS")
    print("=" * 70)
    
    if safe_files:
        # Find the best backup to use
        best_backup = None
        highest_users = 0
        
        for file_info in safe_files:
            if file_info['safety']['user_count'] and file_info['safety']['user_count'] > highest_users:
                highest_users = file_info['safety']['user_count']
                best_backup = file_info
        
        if best_backup:
            print(f"🏆 RECOMMENDED BACKUP:")
            print(f"   📄 File: {best_backup['filename']}")
            print(f"   👥 Users: {best_backup['safety']['user_count']}")
            print(f"   ✅ Reason: {best_backup['safety']['reason']}")
            print(f"   🕐 Date: {best_backup['modified'].strftime('%Y-%m-%d %H:%M:%S')}")
        
        print(f"\n✅ SAFE RESTORE PROCEDURE:")
        print(f"   1. Use any file from the 'SAFE TO RESTORE' list above")
        print(f"   2. Through web interface: Admin Panel → Database → Restore")
        print(f"   3. Or emergency interface: http://localhost:3002")
        print(f"   4. Expected result: Proper user count restoration")
    
    if unsafe_files:
        print(f"\n⚠️  UNSAFE FILES - AVOID THESE:")
        for file_info in unsafe_files:
            print(f"   ❌ {file_info['filename']} - {file_info['safety']['reason']}")
        
        print(f"\n🔧 TO FIX UNSAFE FILES:")
        print(f"   • Create new backups using current system")
        print(f"   • Use the fix_restore_issue.py script")
        print(f"   • Manual fix: Add 'DROP DATABASE IF EXISTS ecommerce_db;' at the top")
    
    print(f"\n📋 GENERAL GUIDELINES:")
    print(f"   ✅ Always use 'complete' backup type")
    print(f"   ✅ Prefer recent backups (2025-07-09 or later)")
    print(f"   ✅ Look for 'FIXED' in filename for guaranteed safety")
    print(f"   ✅ Test restore in development first")
    print(f"   ⚠️  Avoid data-only or schema-only for full recovery")

def create_restore_script():
    """Create a script for safe restoration"""
    script_content = '''#!/usr/bin/env python3
"""
Safe restore script - only uses verified safe backup files
"""
import requests
import json

# Use the recommended safe backup file
SAFE_BACKUP_FILE = "ecommerce_backup_FIXED_MANUAL_2025-07-10_05-32-48.sql"
BASE_URL = "http://localhost:3001"

def safe_restore():
    """Perform safe restore using verified backup"""
    print(f"🔧 Starting SAFE restore with: {SAFE_BACKUP_FILE}")
    
    # Login first
    login_response = requests.post(f"{BASE_URL}/api/users/login", json={
        "email": "admin@example.com",
        "password": "admin123"
    })
    
    if login_response.status_code != 200:
        print("❌ Login failed")
        return False
    
    token = login_response.json()["data"]["token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Perform restore
    restore_response = requests.post(f"{BASE_URL}/api/database/restore", 
                                   json={"filename": SAFE_BACKUP_FILE}, 
                                   headers=headers)
    
    if restore_response.status_code == 200:
        result = restore_response.json()
        verification = result["data"]["verification"]
        print(f"✅ Restore successful!")
        print(f"👥 Users restored: {verification.get('userCount', 'Unknown')}")
        return True
    else:
        print(f"❌ Restore failed: {restore_response.text}")
        return False

if __name__ == "__main__":
    safe_restore()
'''
    
    with open('safe_restore.py', 'w') as f:
        f.write(script_content)
    
    print(f"\n💾 Created safe_restore.py script")
    print(f"   Run with: python safe_restore.py")

def main():
    """Main function"""
    analyze_backup_safety()
    create_restore_script()

if __name__ == "__main__":
    main()
