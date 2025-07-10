#!/usr/bin/env python3
"""
Backup File User Counter
Analyzes backup files to count how many users they contain
"""

import os
import sys
import re

def count_users_in_backup(backup_file):
    """Count users in a backup file"""
    backup_path = os.path.join('backups', backup_file)
    
    if not os.path.exists(backup_path):
        print(f"❌ File not found: {backup_path}")
        return None
    
    print(f"📁 Analyzing: {backup_file}")
    
    try:
        with open(backup_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Count INSERT statements for users
        insert_pattern = r'INSERT\s+INTO\s+(?:public\.)?users'
        insert_matches = re.findall(insert_pattern, content, re.IGNORECASE)
        insert_count = len(insert_matches)
        
        # Count COPY data lines for users
        copy_count = 0
        copy_pattern = r'COPY\s+(?:public\.)?users\s+.*?\n(.*?)\\\.'
        copy_matches = re.findall(copy_pattern, content, re.IGNORECASE | re.DOTALL)
        
        for copy_block in copy_matches:
            # Count non-empty, non-comment lines
            lines = copy_block.split('\n')
            data_lines = [line for line in lines if line.strip() and not line.strip().startswith('--')]
            copy_count += len(data_lines)
        
        total_users = insert_count + copy_count
        
        # Get file size
        file_size = os.path.getsize(backup_path)
        size_mb = file_size / (1024 * 1024)
        
        print(f"   📊 File size: {size_mb:.2f} MB")
        print(f"   👥 INSERT statements: {insert_count}")
        print(f"   📋 COPY data lines: {copy_count}")
        print(f"   🔢 Total users: {total_users}")
        
        return {
            'filename': backup_file,
            'size_mb': size_mb,
            'insert_count': insert_count,
            'copy_count': copy_count,
            'total_users': total_users
        }
        
    except Exception as e:
        print(f"❌ Error analyzing {backup_file}: {e}")
        return None

def analyze_all_backups():
    """Analyze all backup files in the backups directory"""
    print("🔍 BACKUP FILE USER ANALYSIS")
    print("=" * 50)
    
    backups_dir = 'backups'
    if not os.path.exists(backups_dir):
        print(f"❌ Backups directory not found: {backups_dir}")
        return
    
    # Get all SQL backup files
    backup_files = [f for f in os.listdir(backups_dir) if f.endswith('.sql')]
    backup_files.sort(reverse=True)  # Newest first
    
    if not backup_files:
        print("❌ No backup files found")
        return
    
    print(f"📁 Found {len(backup_files)} backup files\n")
    
    results = []
    for backup_file in backup_files:
        result = count_users_in_backup(backup_file)
        if result:
            results.append(result)
        print()  # Empty line between files
    
    # Summary
    print("=" * 50)
    print("📊 SUMMARY")
    print("=" * 50)
    
    if results:
        # Find backups with most users
        max_users = max(r['total_users'] for r in results)
        large_backups = [r for r in results if r['total_users'] > 1000]
        
        print(f"📈 Largest backup: {max_users} users")
        
        if large_backups:
            print(f"🎯 Backups with 1000+ users:")
            for backup in large_backups:
                print(f"   • {backup['filename']}: {backup['total_users']} users ({backup['size_mb']:.1f} MB)")
        else:
            print("⚠️  No backups found with 1000+ users")
            print("   This might explain why restore only shows 4 users")
        
        # Show files by user count
        sorted_results = sorted(results, key=lambda x: x['total_users'], reverse=True)
        print(f"\n📋 All backups by user count:")
        for result in sorted_results[:10]:  # Top 10
            print(f"   {result['total_users']:>6} users - {result['filename']} ({result['size_mb']:.1f} MB)")

def analyze_specific_file(filename):
    """Analyze a specific backup file"""
    print(f"🔍 ANALYZING SPECIFIC FILE: {filename}")
    print("=" * 50)
    
    result = count_users_in_backup(filename)
    if result:
        print("\n✅ Analysis complete!")
        if result['total_users'] == 10003:
            print("🎉 This file contains 10,003 users as expected!")
        elif result['total_users'] < 100:
            print("⚠️  This file contains very few users")
            print("   It was likely created when the database only had a few users")
        else:
            print(f"ℹ️  This file contains {result['total_users']} users")

def main():
    """Main function"""
    if len(sys.argv) > 1:
        # Analyze specific file
        filename = sys.argv[1]
        analyze_specific_file(filename)
    else:
        # Analyze all files
        analyze_all_backups()

if __name__ == "__main__":
    main()
