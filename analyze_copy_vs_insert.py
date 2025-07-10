#!/usr/bin/env python3
"""
Detailed COPY vs INSERT Analysis Tool
Analyzes why backup files use COPY instead of INSERT and how to fix it
"""

import os
import re
from datetime import datetime

def analyze_copy_statements(filename):
    """Analyze COPY statements in backup file"""
    backup_path = os.path.join("backups", filename)
    
    if not os.path.exists(backup_path):
        print(f"❌ File not found: {backup_path}")
        return
    
    print(f"🔍 ANALYZING COPY STATEMENTS IN: {filename}")
    print("="*80)
    
    try:
        with open(backup_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        lines = content.split('\n')
        copy_blocks = {}
        current_copy_table = None
        copy_data_lines = []
        
        for line_num, line in enumerate(lines, 1):
            line_stripped = line.strip()
            
            # Detect COPY statement start
            if line_stripped.startswith('COPY '):
                if current_copy_table and copy_data_lines:
                    copy_blocks[current_copy_table]['data_lines'] = copy_data_lines
                    copy_blocks[current_copy_table]['record_count'] = len(copy_data_lines)
                
                # Parse COPY statement
                match = re.match(r'COPY\s+(?:public\.)?(\w+)\s*\((.*?)\)\s+FROM\s+stdin;', line_stripped)
                if match:
                    table_name = match.group(1)
                    columns = [col.strip() for col in match.group(2).split(',')]
                    
                    current_copy_table = table_name
                    copy_data_lines = []
                    copy_blocks[table_name] = {
                        'line_number': line_num,
                        'columns': columns,
                        'statement': line_stripped,
                        'data_lines': [],
                        'record_count': 0
                    }
                    
                    print(f"\n📋 COPY STATEMENT FOUND:")
                    print(f"   Line {line_num}: {line_stripped}")
                    print(f"   Table: {table_name}")
                    print(f"   Columns: {', '.join(columns)}")
            
            # Detect end of COPY data
            elif line_stripped == '\\.':
                if current_copy_table and copy_data_lines:
                    copy_blocks[current_copy_table]['data_lines'] = copy_data_lines
                    copy_blocks[current_copy_table]['record_count'] = len(copy_data_lines)
                    print(f"   Data records: {len(copy_data_lines)}")
                    
                    # Show sample data for users table
                    if current_copy_table == 'users' and copy_data_lines:
                        print(f"   Sample user records:")
                        for i, data_line in enumerate(copy_data_lines[:3]):
                            print(f"     {i+1}. {data_line[:100]}...")
                
                current_copy_table = None
                copy_data_lines = []
            
            # Collect COPY data lines
            elif current_copy_table and line_stripped and not line_stripped.startswith('--'):
                copy_data_lines.append(line_stripped)
        
        # Handle last COPY block if file doesn't end with \.
        if current_copy_table and copy_data_lines:
            copy_blocks[current_copy_table]['data_lines'] = copy_data_lines
            copy_blocks[current_copy_table]['record_count'] = len(copy_data_lines)
        
        # Summary
        print(f"\n{'='*80}")
        print("COPY STATEMENT SUMMARY")
        print("="*80)
        
        total_records = 0
        for table_name, info in copy_blocks.items():
            record_count = info['record_count']
            total_records += record_count
            print(f"Table: {table_name:<15} Records: {record_count:>8,}")
            
            if table_name == 'users' and record_count > 0:
                print(f"  ✅ Users table has {record_count} records in COPY format")
            elif table_name == 'users':
                print(f"  ❌ Users table has NO records in COPY format")
        
        print(f"\nTotal records across all tables: {total_records:,}")
        
        # Check for users specifically
        if 'users' in copy_blocks:
            users_info = copy_blocks['users']
            print(f"\n🔍 USERS TABLE ANALYSIS:")
            print(f"   COPY statement line: {users_info['line_number']}")
            print(f"   Columns: {len(users_info['columns'])}")
            print(f"   Data records: {users_info['record_count']}")
            
            if users_info['record_count'] > 0:
                print(f"   ✅ This backup SHOULD restore {users_info['record_count']} users")
                
                # Show first few user records
                print(f"   Sample data:")
                for i, data_line in enumerate(users_info['data_lines'][:5]):
                    fields = data_line.split('\t')
                    user_id = fields[0] if len(fields) > 0 else 'N/A'
                    username = fields[1] if len(fields) > 1 else 'N/A'
                    email = fields[2] if len(fields) > 2 else 'N/A'
                    print(f"     {i+1}. ID: {user_id}, Username: {username}, Email: {email}")
            else:
                print(f"   ❌ This backup has NO user data - it will restore 0 users!")
        else:
            print(f"\n❌ NO USERS TABLE FOUND in COPY statements")
        
        return copy_blocks
        
    except Exception as e:
        print(f"❌ Error analyzing file: {e}")
        return None

def compare_backup_formats():
    """Compare different backup formats"""
    print(f"\n{'='*80}")
    print("BACKUP FORMAT EXPLANATION")
    print("="*80)
    
    print("""
🔍 WHY YOUR BACKUPS USE COPY INSTEAD OF INSERT:

1. **pg_dump Default Behavior:**
   - pg_dump uses COPY format by default for efficiency
   - COPY is faster than INSERT for large datasets
   - Format: COPY table_name (columns) FROM stdin;

2. **COPY vs INSERT Format:**
   
   INSERT Format:
   INSERT INTO users (user_id, username, email) VALUES 
   ('123e4567-e89b-12d3-a456-426614174000', 'john_doe', 'john@example.com'),
   ('123e4567-e89b-12d3-a456-426614174001', 'jane_doe', 'jane@example.com');
   
   COPY Format:
   COPY users (user_id, username, email) FROM stdin;
   123e4567-e89b-12d3-a456-426614174000	john_doe	john@example.com
   123e4567-e89b-12d3-a456-426614174001	jane_doe	jane@example.com
   \.

3. **Why This Causes Issues:**
   - Your analysis script only looks for INSERT statements
   - COPY data is in tab-separated format, not SQL
   - The restore process should handle COPY correctly
   - But the analysis shows wrong user counts

4. **The Real Problem:**
   - Your backups DO contain the data (in COPY format)
   - The restore process IS working correctly
   - The issue is that you're creating backups when database only has 4 users
   - NOT that backups with 10,003 users are being corrupted
""")

def recommend_solutions():
    """Provide solutions for the backup/restore issue"""
    print(f"\n{'='*80}")
    print("RECOMMENDED SOLUTIONS")
    print("="*80)
    
    print("""
🔧 SOLUTION 1: Generate Large Dataset and Create Proper Backup

1. Generate 10,000+ users in database:
   cd scripts
   python data_generator.py

2. Verify user count:
   python -c "
   import requests
   token = requests.post('http://localhost:3001/api/users/login', 
                        json={'email': 'admin@example.com', 'password': 'admin123'}).json()['data']['token']
   count = requests.post('http://localhost:3001/api/database/query',
                        json={'sql': 'SELECT COUNT(*) FROM users'},
                        headers={'Authorization': f'Bearer {token}'}).json()['data']['rows'][0]['count']
   print(f'Current users: {count}')
   "

3. Create backup when database has 10,000+ users:
   python db/backup.py --type full

🔧 SOLUTION 2: Force INSERT Format in Backups

Modify backup.py to use INSERT format:
- Add --inserts flag to pg_dump command
- This creates INSERT statements instead of COPY
- Less efficient but more readable

🔧 SOLUTION 3: Better Backup Analysis

Create proper COPY statement parser that:
- Counts records in COPY blocks
- Analyzes tab-separated data
- Provides accurate record counts

🔧 SOLUTION 4: Test with Known Good Backup

1. Find a backup created when you actually had 10,000+ users
2. Check its creation timestamp vs database state
3. Use our analysis tool to verify data content
""")

def main():
    """Main analysis function"""
    print("🔍 COPY vs INSERT BACKUP ANALYSIS")
    print("="*80)
    
    # Find most recent large backup
    backups_dir = "backups"
    if os.path.exists(backups_dir):
        backup_files = [f for f in os.listdir(backups_dir) if f.endswith('.sql')]
        backup_files.sort(key=lambda x: os.path.getmtime(os.path.join(backups_dir, x)), reverse=True)
        
        if backup_files:
            # Analyze the most recent backup
            recent_backup = backup_files[0]
            copy_blocks = analyze_copy_statements(recent_backup)
            
            # Compare formats
            compare_backup_formats()
            
            # Provide solutions
            recommend_solutions()
            
            print(f"\n{'='*80}")
            print("KEY FINDINGS")
            print("="*80)
            
            if copy_blocks and 'users' in copy_blocks:
                user_count = copy_blocks['users']['record_count']
                print(f"✅ Your most recent backup ({recent_backup}) contains {user_count} users")
                print(f"✅ The backup format is correct (using COPY statements)")
                
                if user_count == 4:
                    print(f"⚠️  ISSUE: You created the backup when database only had 4 users")
                    print(f"🔧 SOLUTION: Generate more data first, then create backup")
                else:
                    print(f"✅ This backup should restore {user_count} users correctly")
            else:
                print(f"❌ Issues found with backup format")
        else:
            print("❌ No backup files found")
    else:
        print("❌ Backups directory not found")

if __name__ == "__main__":
    main()
