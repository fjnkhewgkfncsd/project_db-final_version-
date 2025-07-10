#!/usr/bin/env python3
"""
Direct backup file analysis - no API needed
"""

import os

def analyze_backup_file_users(filename):
    """Analyze backup file to count users"""
    filepath = os.path.join('backups', filename)
    
    if not os.path.exists(filepath):
        return None
        
    user_count = 0
    file_size = os.path.getsize(filepath)
    
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            in_users_copy = False
            copy_line = ""
            
            for line_num, line in enumerate(f, 1):
                # Look for COPY statement for users table
                if 'COPY public.users' in line:
                    in_users_copy = True
                    copy_line = line.strip()
                    print(f"   Found users COPY at line {line_num}: {copy_line}")
                    continue
                
                # Count data lines in the COPY block
                elif in_users_copy:
                    if line.strip() == '\\.' or line.strip() == '\\.':
                        print(f"   End of COPY block at line {line_num}")
                        break
                    elif line.strip() and not line.startswith('--'):
                        user_count += 1
                        if user_count <= 3:  # Show first few users
                            print(f"   User {user_count}: {line.strip()[:80]}...")
        
        return {
            'user_count': user_count,
            'file_size_mb': file_size / (1024 * 1024),
            'file_exists': True
        }
        
    except Exception as e:
        print(f"   Error reading file: {e}")
        return None

def main():
    """Analyze backup files directly"""
    print("🔍 DIRECT BACKUP FILE ANALYSIS")
    print("=" * 40)
    
    backup_dir = 'backups'
    if not os.path.exists(backup_dir):
        print(f"❌ Backup directory not found: {backup_dir}")
        return
    
    # Get all backup files
    backup_files = []
    for filename in os.listdir(backup_dir):
        if filename.startswith('ecommerce_backup_') and filename.endswith('.sql'):
            backup_files.append(filename)
    
    # Sort by modification time (newest first)
    backup_files.sort(key=lambda x: os.path.getmtime(os.path.join(backup_dir, x)), reverse=True)
    
    print(f"\n📁 Found {len(backup_files)} backup files")
    
    large_backups = []
    
    # Analyze each backup
    for i, filename in enumerate(backup_files[:15]):  # Check first 15 files
        print(f"\n📄 {i+1}. {filename}")
        
        analysis = analyze_backup_file_users(filename)
        
        if analysis:
            print(f"   File size: {analysis['file_size_mb']:.1f} MB")
            print(f"   Users: {analysis['user_count']}")
            
            if analysis['user_count'] > 1000:
                large_backups.append({
                    'filename': filename,
                    'users': analysis['user_count'],
                    'size_mb': analysis['file_size_mb']
                })
                print(f"   🎯 LARGE BACKUP FOUND!")
        else:
            print(f"   ❌ Could not analyze file")
    
    # Summary
    print(f"\n" + "=" * 40)
    print("📊 ANALYSIS SUMMARY")
    print("=" * 40)
    
    if large_backups:
        print(f"✅ Found {len(large_backups)} backup(s) with >1000 users:")
        for backup in large_backups:
            print(f"   📄 {backup['filename']}")
            print(f"      Users: {backup['users']:,}")
            print(f"      Size: {backup['size_mb']:.1f} MB")
    else:
        print("⚠️  No backups found with >1000 users")
        print("   All analyzed backups contain small amounts of data")
        print("   This means:")
        print("   - The backups were created when database had few users")
        print("   - OR the backup files are corrupted")
        print("   - OR the COPY format is different than expected")

if __name__ == "__main__":
    main()
