#!/usr/bin/env python3
"""
Complete Python vs JavaScript Backup/Restore Comparison
Tests and compares all available backup/restore methods
"""

import os
import sys
import time
import requests
import subprocess
from datetime import datetime

# Configuration
BACKEND_URL = "http://localhost:3001"
ADMIN_EMAIL = "admin@example.com"
ADMIN_PASSWORD = "admin123"

def log_step(category, message, status="INFO"):
    """Log a step with timestamp and status"""
    timestamp = datetime.now().strftime('%H:%M:%S')
    icons = {
        "INFO": "ℹ️",
        "SUCCESS": "✅",
        "ERROR": "❌",
        "WARNING": "⚠️"
    }
    icon = icons.get(status, "📝")
    print(f"[{timestamp}] {icon} {category}: {message}")

def get_auth_token():
    """Get authentication token for API calls"""
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
    """Check current user count in database via API"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.post(f"{BACKEND_URL}/api/database/query", 
                               json={"sql": "SELECT COUNT(*) as count FROM users"}, 
                               headers=headers)
        
        if response.status_code == 200:
            count = response.json()['data']['rows'][0]['count']
            log_step("CHECK", f"Current user count: {count}", "SUCCESS")
            return count
        else:
            log_step("CHECK", f"Query failed: {response.text}", "ERROR")
            return None
    except Exception as e:
        log_step("CHECK", f"Query error: {e}", "ERROR")
        return None

def test_javascript_api_backup(token):
    """Test JavaScript/API backup functionality"""
    log_step("JS-BACKUP", "Testing JavaScript API backup")
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        start_time = time.time()
        
        response = requests.post(f"{BACKEND_URL}/api/database/backup", 
                               json={"backupType": "complete"}, 
                               headers=headers, timeout=120)
        
        duration = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()['data']
            log_step("JS-BACKUP", f"Success - {data['filename']} ({data['size']})", "SUCCESS")
            log_step("JS-BACKUP", f"Duration: {duration:.2f}s", "INFO")
            return data['filename']
        else:
            log_step("JS-BACKUP", f"Failed: {response.text}", "ERROR")
            return None
            
    except Exception as e:
        log_step("JS-BACKUP", f"Error: {e}", "ERROR")
        return None

def test_javascript_api_restore(token, filename):
    """Test JavaScript/API restore functionality"""
    log_step("JS-RESTORE", f"Testing JavaScript API restore with {filename}")
    
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
            
            log_step("JS-RESTORE", f"Success - {user_count} users restored", "SUCCESS")
            log_step("JS-RESTORE", f"Duration: {duration:.2f}s", "INFO")
            return user_count
        else:
            log_step("JS-RESTORE", f"Failed: {response.text}", "ERROR")
            return None
            
    except Exception as e:
        log_step("JS-RESTORE", f"Error: {e}", "ERROR")
        return None

def test_python_restore(filename):
    """Test Python restore script"""
    log_step("PY-RESTORE", f"Testing Python restore with {filename}")
    
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
            # Parse output to find user count
            output = result.stdout
            user_count = "unknown"
            
            for line in output.split('\n'):
                if "users;" in line and "->" in line:
                    try:
                        user_count = line.split("->")[-1].strip()
                    except:
                        pass
            
            log_step("PY-RESTORE", f"Success - {user_count} users restored", "SUCCESS")
            log_step("PY-RESTORE", f"Duration: {duration:.2f}s", "INFO")
            return user_count
        else:
            log_step("PY-RESTORE", f"Failed: {result.stderr}", "ERROR")
            return None
            
    except subprocess.TimeoutExpired:
        log_step("PY-RESTORE", "Timed out", "ERROR")
        return None
    except Exception as e:
        log_step("PY-RESTORE", f"Error: {e}", "ERROR")
        return None

def list_available_backups():
    """List available backup files"""
    log_step("BACKUPS", "Listing available backup files")
    
    backups_dir = "backups"
    if os.path.exists(backups_dir):
        backup_files = [f for f in os.listdir(backups_dir) if f.endswith('.sql')]
        backup_files.sort(key=lambda x: os.path.getmtime(os.path.join(backups_dir, x)), reverse=True)
        
        log_step("BACKUPS", f"Found {len(backup_files)} backup files", "SUCCESS")
        
        # Show top 5 most recent
        for i, filename in enumerate(backup_files[:5], 1):
            filepath = os.path.join(backups_dir, filename)
            size = os.path.getsize(filepath) / 1024 / 1024  # MB
            mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
            log_step("BACKUPS", f"  {i}. {filename} ({size:.2f} MB, {mtime.strftime('%Y-%m-%d %H:%M')})")
        
        return backup_files
    else:
        log_step("BACKUPS", "Backups directory not found", "ERROR")
        return []

def test_python_backup():
    """Test Python backup script"""
    log_step("PY-BACKUP", "Testing Python backup script")
    
    try:
        start_time = time.time()
        
        # Try using environment variables for authentication
        env = os.environ.copy()
        env['PGPASSWORD'] = 'hengmengly123'  # Set password for pg_dump
        
        result = subprocess.run([
            sys.executable, 
            os.path.join("db", "backup.py"),
            "--type", "full"
        ], capture_output=True, text=True, timeout=120, env=env)
        
        duration = time.time() - start_time
        
        if result.returncode == 0:
            log_step("PY-BACKUP", f"Success", "SUCCESS")
            log_step("PY-BACKUP", f"Duration: {duration:.2f}s", "INFO")
            return True
        else:
            log_step("PY-BACKUP", f"Failed: {result.stderr}", "ERROR")
            # Try alternative - SQL format backup
            log_step("PY-BACKUP", "Trying alternative backup method...", "WARNING")
            return False
            
    except subprocess.TimeoutExpired:
        log_step("PY-BACKUP", "Timed out", "ERROR")
        return False
    except Exception as e:
        log_step("PY-BACKUP", f"Error: {e}", "ERROR")
        return False

def main():
    """Main comparison test"""
    print("🔄 COMPLETE BACKUP & RESTORE COMPARISON TEST")
    print("="*80)
    print("Testing both Python scripts and JavaScript API methods")
    print("="*80)
    
    # Get authentication token
    token = get_auth_token()
    if not token:
        print("❌ Cannot proceed without authentication")
        return
    
    log_step("INIT", "Authentication successful", "SUCCESS")
    
    # Check initial state
    initial_users = check_current_user_count(token)
    
    # List available backups
    backup_files = list_available_backups()
    
    if not backup_files:
        print("❌ No backup files available for testing")
        return
    
    # Use the most recent backup for testing
    test_backup = backup_files[0]
    log_step("TEST", f"Using backup file: {test_backup}", "INFO")
    
    print(f"\n{'-'*60}")
    print("🧪 TESTING JAVASCRIPT API METHODS")
    print(f"{'-'*60}")
    
    # Test JavaScript API backup
    new_backup = test_javascript_api_backup(token)
    
    # Test JavaScript API restore
    js_restore_result = test_javascript_api_restore(token, test_backup)
    
    print(f"\n{'-'*60}")
    print("🐍 TESTING PYTHON SCRIPT METHODS")
    print(f"{'-'*60}")
    
    # Test Python backup
    py_backup_result = test_python_backup()
    
    # Test Python restore
    py_restore_result = test_python_restore(test_backup)
    
    # Final verification
    final_users = check_current_user_count(token)
    
    print(f"\n{'='*80}")
    print("📊 COMPARISON RESULTS")
    print("="*80)
    
    print(f"Initial user count: {initial_users}")
    print(f"Final user count: {final_users}")
    print("")
    
    print("JavaScript API Methods:")
    print(f"  Backup: {'✅ Success' if new_backup else '❌ Failed'}")
    print(f"  Restore: {'✅ Success' if js_restore_result else '❌ Failed'}")
    if js_restore_result:
        print(f"    Users restored: {js_restore_result}")
    
    print("")
    print("Python Script Methods:")
    print(f"  Backup: {'✅ Success' if py_backup_result else '❌ Failed'}")
    print(f"  Restore: {'✅ Success' if py_restore_result else '❌ Failed'}")
    if py_restore_result:
        print(f"    Users restored: {py_restore_result}")
    
    print(f"\n{'='*80}")
    print("🎯 CONCLUSION")
    print("="*80)
    
    if js_restore_result and py_restore_result:
        print("✅ Both JavaScript API and Python scripts work for restore")
        print("✅ You have multiple backup/restore options available:")
        print("   • Web interface (Database Tools tab)")
        print("   • JavaScript API endpoints")
        print("   • Python command-line scripts")
        print("   • Emergency recovery server")
    else:
        print("⚠️ Some methods may need configuration adjustments")
        print("📝 Check the logs above for specific issues")
    
    print(f"{'='*80}")

if __name__ == "__main__":
    main()
