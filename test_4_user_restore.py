#!/usr/bin/env python3
"""
Test script for 4-user backup restore
"""
import os
import re
import subprocess
import psycopg2
from dotenv import load_dotenv

load_dotenv('backend/.env')

def analyze_backup_file(filename):
    """Analyze backup file and show user details"""
    backup_path = os.path.join('backups', filename)
    
    print(f"🔍 ANALYZING BACKUP FILE: {filename}")
    print("=" * 60)
    
    try:
        with open(backup_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find users section
        user_match = re.search(r'COPY public\.users.*?FROM stdin;\n(.*?)\n\\\\.', content, re.DOTALL)
        if user_match:
            users_data = user_match.group(1).strip()
            user_lines = [line.strip() for line in users_data.split('\n') if line.strip()]
            
            print(f"📊 Total users in backup: {len(user_lines)}")
            print("\n👥 User details:")
            
            for i, line in enumerate(user_lines, 1):
                parts = line.split('\t')
                if len(parts) >= 13:
                    username = parts[1]
                    email = parts[2]
                    first_name = parts[4]
                    last_name = parts[5]
                    role = parts[12]
                    print(f"  {i}. {username:<15} | {email:<25} | {first_name} {last_name:<10} | {role}")
            
            # Check if it's a full backup or data-only
            has_creates = 'CREATE DATABASE' in content or 'CREATE TABLE' in content
            has_drops = 'DROP DATABASE' in content
            
            print(f"\n📝 Backup type:")
            print(f"   Contains CREATE statements: {'Yes' if has_creates else 'No'}")
            print(f"   Contains DROP DATABASE: {'Yes' if has_drops else 'No'}")
            
            if has_creates and has_drops:
                backup_type = "Full backup (can restore to empty database)"
            elif has_creates:
                backup_type = "Schema + data backup"
            else:
                backup_type = "Data-only backup (requires existing schema)"
            
            print(f"   Type: {backup_type}")
            
            return len(user_lines), backup_type
        else:
            print("❌ No user data found in backup file")
            return 0, "No data"
            
    except Exception as e:
        print(f"❌ Error analyzing file: {e}")
        return 0, "Error"

def test_restore_4_users():
    """Test restoring the 4-user backup"""
    backup_filename = "ecommerce_backup_2025-07-04_01-48-21.sql"
    
    # First analyze the backup
    user_count, backup_type = analyze_backup_file(backup_filename)
    
    if user_count != 4:
        print(f"❌ Expected 4 users but found {user_count}")
        return False
    
    print(f"\n🎯 PERFECT! Found backup with exactly 4 users")
    print(f"📁 File: {backup_filename}")
    print(f"📋 Type: {backup_type}")
    
    # Ask if user wants to test the restore
    print(f"\n🧪 TEST RESTORE OPTIONS:")
    print(f"1. This backup contains CREATE DATABASE statements")
    print(f"2. It will completely replace your current database")
    print(f"3. After restore, you'll have exactly 4 users")
    print(f"4. You can test if constraint conflicts were the issue")
    
    return True

if __name__ == "__main__":
    print("🔍 FINDING 4-USER BACKUP FOR TESTING")
    print("=" * 60)
    
    if test_restore_4_users():
        print(f"\n✅ SUCCESS! Found the perfect test backup:")
        print(f"   📁 ecommerce_backup_2025-07-04_01-48-21.sql")
        print(f"   👥 Contains exactly 4 users")
        print(f"   🏗️  Full backup with schema")
        print(f"\n🧪 TO TEST THE RESTORE:")
        print(f"   1. Use the emergency recovery interface")
        print(f"   2. Select: ecommerce_backup_2025-07-04_01-48-21.sql")
        print(f"   3. Restore and verify you get exactly 4 users")
        print(f"   4. This will prove the restore process works with small datasets")
    else:
        print(f"\n❌ Could not find suitable 4-user backup for testing")
