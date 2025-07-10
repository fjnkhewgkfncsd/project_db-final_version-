#!/usr/bin/env python3
"""
Backup and Restore Issue Diagnosis Tool
Diagnoses why backups with 10,003 users restore to only 4 users
"""

import os
import sys
import time
import subprocess
import requests
from datetime import datetime

# Configuration
BACKEND_URL = "http://localhost:3001"
ADMIN_EMAIL = "admin@example.com"
ADMIN_PASSWORD = "admin123"

def log_step(step, message, status="INFO"):
    """Log with timestamp and status"""
    timestamp = datetime.now().strftime('%H:%M:%S')
    icons = {"INFO": "ℹ️", "SUCCESS": "✅", "ERROR": "❌", "WARNING": "⚠️"}
    icon = icons.get(status, "📝")
    print(f"[{timestamp}] {icon} {step}: {message}")

def analyze_backup_file(filename):
    """Analyze backup file content to understand what's actually in it"""
    backup_path = os.path.join("backups", filename)
    
    if not os.path.exists(backup_path):
        log_step("ANALYSIS", f"Backup file not found: {backup_path}", "ERROR")
        return None
    
    log_step("ANALYSIS", f"Analyzing backup file: {filename}")
    
    try:
        with open(backup_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        analysis = {
            'filename': filename,
            'size_mb': os.path.getsize(backup_path) / 1024 / 1024,
            'total_lines': len(content.split('\n')),
            'drop_statements': [],
            'create_statements': [],
            'insert_statements': [],
            'user_inserts': [],
            'copy_statements': [],
            'database_creation': False
        }
        
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            line_upper = line.strip().upper()
            
            # Check for DROP statements
            if line_upper.startswith('DROP'):
                analysis['drop_statements'].append(f"Line {line_num}: {line.strip()[:80]}")
            
            # Check for CREATE statements
            elif line_upper.startswith('CREATE'):
                analysis['create_statements'].append(f"Line {line_num}: {line.strip()[:80]}")
                if 'DATABASE' in line_upper:
                    analysis['database_creation'] = True
            
            # Check for INSERT statements
            elif line_upper.startswith('INSERT'):
                analysis['insert_statements'].append(f"Line {line_num}: {line.strip()[:80]}")
                if 'INTO USERS' in line_upper or 'INTO PUBLIC.USERS' in line_upper:
                    analysis['user_inserts'].append(f"Line {line_num}: {line.strip()[:100]}")
            
            # Check for COPY statements (alternative to INSERT)
            elif line_upper.startswith('COPY'):
                analysis['copy_statements'].append(f"Line {line_num}: {line.strip()[:80]}")
        
        # Count actual user records in INSERT statements
        user_record_count = 0
        for insert in analysis['user_inserts']:
            # Count comma-separated value groups in INSERT statements
            if 'VALUES' in insert.upper():
                # This is a rough count - each opening parenthesis represents a record
                user_record_count += insert.count('(')
        
        analysis['estimated_user_records'] = user_record_count
        
        return analysis
        
    except Exception as e:
        log_step("ANALYSIS", f"Error analyzing backup: {e}", "ERROR")
        return None

def get_auth_token():
    """Get authentication token"""
    try:
        response = requests.post(f"{BACKEND_URL}/api/users/login", 
                               json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD})
        
        if response.status_code == 200:
            return response.json()['data']['token']
        else:
            log_step("AUTH", f"Login failed: {response.text}", "ERROR")
            return None
    except Exception as e:
        log_step("AUTH", f"Login error: {e}", "ERROR")
        return None

def check_current_user_count(token):
    """Check current user count via API"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.post(f"{BACKEND_URL}/api/database/query", 
                               json={"sql": "SELECT COUNT(*) as count FROM users"}, 
                               headers=headers)
        
        if response.status_code == 200:
            count = response.json()['data']['rows'][0]['count']
            return int(count)
        else:
            log_step("CHECK", f"Query failed: {response.text}", "ERROR")
            return None
    except Exception as e:
        log_step("CHECK", f"Query error: {e}", "ERROR")
        return None

def get_user_samples(token, limit=10):
    """Get sample users to see what's in the database"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.post(f"{BACKEND_URL}/api/database/query", 
                               json={"sql": f"SELECT user_id, username, email, created_at FROM users ORDER BY user_id LIMIT {limit}"}, 
                               headers=headers)
        
        if response.status_code == 200:
            return response.json()['data']['rows']
        else:
            log_step("SAMPLE", f"Query failed: {response.text}", "ERROR")
            return None
    except Exception as e:
        log_step("SAMPLE", f"Query error: {e}", "ERROR")
        return None

def create_test_backup(token, description="Test backup"):
    """Create a backup of current database state for testing"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.post(f"{BACKEND_URL}/api/database/backup", 
                               json={"backupType": "complete"}, 
                               headers=headers, timeout=120)
        
        if response.status_code == 200:
            data = response.json()['data']
            log_step("BACKUP", f"Test backup created: {data['filename']} ({data['size']})", "SUCCESS")
            return data['filename']
        else:
            log_step("BACKUP", f"Backup failed: {response.text}", "ERROR")
            return None
    except Exception as e:
        log_step("BACKUP", f"Backup error: {e}", "ERROR")
        return None

def test_restore_with_api(token, filename):
    """Test restore using the API"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        start_time = time.time()
        
        response = requests.post(f"{BACKEND_URL}/api/database/restore", 
                               json={"filename": filename, "force": True}, 
                               headers=headers, timeout=120)
        
        duration = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()['data']
            verification = data.get('verification', {})
            user_count = verification.get('users_count', 'unknown')
            
            log_step("API-RESTORE", f"Success - {user_count} users restored in {duration:.2f}s", "SUCCESS")
            return int(user_count) if str(user_count).isdigit() else 0
        else:
            log_step("API-RESTORE", f"Failed: {response.text}", "ERROR")
            return None
    except Exception as e:
        log_step("API-RESTORE", f"Error: {e}", "ERROR")
        return None

def test_restore_with_python(filename):
    """Test restore using Python script"""
    try:
        start_time = time.time()
        
        result = subprocess.run([
            sys.executable, 
            os.path.join("db", "restore.py"),
            f"backups/{filename}",
            "--force"
        ], capture_output=True, text=True, timeout=120)
        
        duration = time.time() - start_time
        
        if result.returncode == 0:
            # Parse output for user count
            user_count = "unknown"
            for line in result.stdout.split('\n'):
                if "users;" in line and "->" in line:
                    try:
                        user_count = line.split("->")[-1].strip()
                    except:
                        pass
            
            log_step("PY-RESTORE", f"Success - {user_count} users restored in {duration:.2f}s", "SUCCESS")
            return int(user_count) if str(user_count).isdigit() else 0
        else:
            log_step("PY-RESTORE", f"Failed: {result.stderr}", "ERROR")
            return None
    except Exception as e:
        log_step("PY-RESTORE", f"Error: {e}", "ERROR")
        return None

def diagnose_backup_restore_issue():
    """Main diagnosis function"""
    print("🔍 BACKUP & RESTORE ISSUE DIAGNOSIS")
    print("="*80)
    print("This tool will help diagnose why backups with 10,003 users restore to only 4 users")
    print("="*80)
    
    # Step 1: Get authentication
    token = get_auth_token()
    if not token:
        print("❌ Cannot proceed without authentication")
        return
    
    # Step 2: Check current database state
    log_step("INITIAL", "Checking current database state")
    current_users = check_current_user_count(token)
    
    if current_users:
        log_step("INITIAL", f"Current database has {current_users} users")
        
        # Get sample users
        user_samples = get_user_samples(token, 5)
        if user_samples:
            log_step("INITIAL", "Sample users in current database:")
            for user in user_samples:
                log_step("INITIAL", f"  - ID: {user['user_id']}, Username: {user['username']}, Email: {user['email']}")
    
    # Step 3: List and analyze available backups
    log_step("DISCOVERY", "Analyzing available backup files")
    
    backups_dir = "backups"
    if os.path.exists(backups_dir):
        backup_files = [f for f in os.listdir(backups_dir) if f.endswith('.sql')]
        backup_files.sort(key=lambda x: os.path.getmtime(os.path.join(backups_dir, x)), reverse=True)
        
        log_step("DISCOVERY", f"Found {len(backup_files)} backup files")
        
        # Analyze top 5 backups
        print(f"\n{'='*60}")
        print("BACKUP FILE ANALYSIS")
        print("="*60)
        
        analyzed_backups = []
        for i, filename in enumerate(backup_files[:5], 1):
            analysis = analyze_backup_file(filename)
            if analysis:
                analyzed_backups.append(analysis)
                
                print(f"\n{i}. {filename}")
                print(f"   Size: {analysis['size_mb']:.2f} MB")
                print(f"   Total lines: {analysis['total_lines']:,}")
                print(f"   DROP statements: {len(analysis['drop_statements'])}")
                print(f"   CREATE statements: {len(analysis['create_statements'])}")
                print(f"   INSERT statements: {len(analysis['insert_statements'])}")
                print(f"   User INSERT statements: {len(analysis['user_inserts'])}")
                print(f"   COPY statements: {len(analysis['copy_statements'])}")
                print(f"   Database creation: {analysis['database_creation']}")
                print(f"   Estimated user records: {analysis['estimated_user_records']}")
                
                # Show sample user INSERT if available
                if analysis['user_inserts']:
                    print(f"   Sample user INSERT: {analysis['user_inserts'][0][:80]}...")
        
        # Step 4: Test backup creation with current state
        print(f"\n{'='*60}")
        print("CREATING TEST BACKUP")
        print("="*60)
        
        test_backup_name = create_test_backup(token, f"Diagnosis test - {current_users} users")
        
        if test_backup_name:
            # Analyze the test backup
            test_analysis = analyze_backup_file(test_backup_name)
            if test_analysis:
                print(f"\nTest backup analysis:")
                print(f"   Filename: {test_analysis['filename']}")
                print(f"   Size: {test_analysis['size_mb']:.2f} MB")
                print(f"   User INSERT statements: {len(test_analysis['user_inserts'])}")
                print(f"   Estimated user records: {test_analysis['estimated_user_records']}")
        
        # Step 5: Test restore with suspect backup
        if analyzed_backups:
            print(f"\n{'='*60}")
            print("TESTING RESTORE WITH SUSPECT BACKUP")
            print("="*60)
            
            # Find a backup that should have many users (large size)
            large_backup = None
            for backup in analyzed_backups:
                if backup['size_mb'] > 10:  # Large backup likely has many users
                    large_backup = backup
                    break
            
            if large_backup:
                log_step("TEST", f"Testing restore with large backup: {large_backup['filename']}")
                
                # Test with API
                api_result = test_restore_with_api(token, large_backup['filename'])
                
                # Check result
                final_count = check_current_user_count(token)
                
                print(f"\n{'='*60}")
                print("DIAGNOSIS RESULTS")
                print("="*60)
                
                print(f"Expected users (from backup analysis): {large_backup['estimated_user_records']}")
                print(f"API restore result: {api_result}")
                print(f"Final database count: {final_count}")
                
                if api_result and final_count:
                    if api_result != final_count:
                        print("❌ ISSUE DETECTED: API reports different count than actual database")
                    elif final_count < large_backup['estimated_user_records']:
                        print("❌ ISSUE DETECTED: Backup contains more users than restored")
                        print("\nPossible causes:")
                        print("1. Backup file is corrupted or truncated")
                        print("2. Restore process is not processing all data")
                        print("3. Database constraints preventing some inserts")
                        print("4. Transaction rollback occurring")
                        print("5. Backup created during data generation (partial state)")
                    else:
                        print("✅ Restore appears to be working correctly")
                
                # Show current users after restore
                final_samples = get_user_samples(token, 5)
                if final_samples:
                    print(f"\nCurrent users after restore:")
                    for user in final_samples:
                        print(f"  - ID: {user['user_id']}, Username: {user['username']}")
            else:
                print("⚠️ No large backup files found for testing")
    else:
        print("❌ Backups directory not found")

if __name__ == "__main__":
    diagnose_backup_restore_issue()
