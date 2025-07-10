#!/usr/bin/env python3
"""
Analyze backup files to find one with exactly 4 users
"""
import os
import re

def count_users_in_backup(filename):
    """Count users in a backup file"""
    backup_path = os.path.join('backups', filename)
    
    if not os.path.exists(backup_path):
        return 0, "File not found"
    
    try:
        with open(backup_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Look for different patterns that might indicate user data
        patterns = [
            # COPY statement for users table
            r'COPY public\.users.*?FROM stdin;(.*?)\\.',
            # INSERT statements for users
            r'INSERT INTO (?:public\.)?users.*?VALUES.*?;',
            # Look for user data after COPY statement
            r'-- Data for Name: users.*?\n(.*?)(?=-- Data for Name:|\Z)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
            if match:
                if 'COPY' in pattern:
                    # Count lines in COPY block
                    user_data = match.group(1).strip()
                    if user_data:
                        lines = [line.strip() for line in user_data.split('\n') if line.strip() and not line.startswith('--')]
                        return len(lines), "COPY format"
                elif 'INSERT' in pattern:
                    # Count INSERT statements
                    inserts = re.findall(r'INSERT INTO (?:public\.)?users.*?VALUES.*?;', content, re.IGNORECASE)
                    return len(inserts), "INSERT format"
                else:
                    # Count lines in data section
                    user_data = match.group(1).strip()
                    if user_data:
                        lines = [line.strip() for line in user_data.split('\n') if line.strip() and not line.startswith('--')]
                        return len(lines), "Data section"
        
        # Check if it's a schema-only file
        if 'CREATE TABLE' in content and 'COPY' not in content and 'INSERT' not in content:
            return 0, "Schema only (no data)"
        
        return 0, "No user data found"
        
    except Exception as e:
        return 0, f"Error: {e}"

def main():
    backup_dir = 'backups'
    
    print("🔍 ANALYZING BACKUP FILES FOR USER COUNT")
    print("=" * 60)
    print(f"{'Filename':<40} {'Users':<8} {'Type'}")
    print("-" * 60)
    
    files_with_4_users = []
    
    for filename in sorted(os.listdir(backup_dir)):
        if filename.endswith('.sql'):
            user_count, file_type = count_users_in_backup(filename)
            print(f"{filename:<40} {user_count:<8} {file_type}")
            
            if user_count == 4:
                files_with_4_users.append(filename)
    
    print("\n" + "=" * 60)
    
    if files_with_4_users:
        print(f"✅ Found {len(files_with_4_users)} backup file(s) with exactly 4 users:")
        for filename in files_with_4_users:
            print(f"   📁 {filename}")
        
        print(f"\n📋 RECOMMENDED FILE FOR TESTING:")
        recommended = files_with_4_users[0]  # Pick the first one
        print(f"   🎯 {recommended}")
        
        # Show detailed info about the recommended file
        print(f"\n🔍 DETAILED ANALYSIS OF {recommended}:")
        backup_path = os.path.join('backups', recommended)
        
        try:
            with open(backup_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check file size
            file_size = os.path.getsize(backup_path)
            print(f"   📊 File size: {file_size:,} bytes ({file_size/1024:.1f} KB)")
            
            # Check for CREATE statements (full backup vs data-only)
            has_creates = 'CREATE DATABASE' in content or 'CREATE TABLE' in content
            has_drops = 'DROP DATABASE' in content or 'DROP TABLE' in content
            
            print(f"   🏗️  Contains CREATE statements: {'Yes' if has_creates else 'No'}")
            print(f"   🗑️  Contains DROP statements: {'Yes' if has_drops else 'No'}")
            
            if has_creates and has_drops:
                backup_type = "Full backup (schema + data)"
            elif has_creates:
                backup_type = "Schema + data backup"
            else:
                backup_type = "Data-only backup"
            
            print(f"   📝 Backup type: {backup_type}")
            
            # Look for user data sample
            user_match = re.search(r'COPY public\.users.*?FROM stdin;\n(.*?)\n.*?\n.*?\n.*?\n.*?\\\.', content, re.DOTALL)
            if user_match:
                user_lines = user_match.group(1).strip().split('\n')[:4]  # First 4 lines
                print(f"   👥 Sample users:")
                for i, line in enumerate(user_lines, 1):
                    if line.strip():
                        parts = line.split('\t')
                        if len(parts) >= 3:
                            username = parts[1] if len(parts) > 1 else 'N/A'
                            email = parts[2] if len(parts) > 2 else 'N/A'
                            role = parts[12] if len(parts) > 12 else 'N/A'
                            print(f"      {i}. {username} | {email} | {role}")
            
        except Exception as e:
            print(f"   ❌ Error analyzing file: {e}")
        
    else:
        print("❌ No backup files found with exactly 4 users")
        print("💡 Suggestion: Look for files with small user counts that you can use for testing")

if __name__ == "__main__":
    main()
