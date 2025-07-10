#!/usr/bin/env python3
"""
Comprehensive Python Backup and Restore Testing Script
Tests both backup.py and restore.py functionality
"""

import os
import sys
import time
import subprocess
import json
from datetime import datetime
from pathlib import Path

# Add the db directory to Python path to import modules
sys.path.append(os.path.join(os.path.dirname(__file__), 'db'))

try:
    from backup import DatabaseBackup
    from restore import DatabaseRestore
except ImportError as e:
    print(f"❌ Error importing backup/restore modules: {e}")
    print("Make sure backup.py and restore.py are in the db/ directory")
    sys.exit(1)

class BackupRestoreTestSuite:
    def __init__(self):
        self.test_results = {
            'backup_tests': [],
            'restore_tests': [],
            'performance_metrics': {}
        }
        
    def log_step(self, step, message, status="INFO"):
        """Log a test step with timestamp"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        status_icon = {
            "INFO": "ℹ️",
            "SUCCESS": "✅", 
            "ERROR": "❌",
            "WARNING": "⚠️"
        }.get(status, "📝")
        
        print(f"[{timestamp}] {status_icon} {step}: {message}")
        
    def test_backup_functionality(self):
        """Test the Python backup script functionality"""
        self.log_step("BACKUP TEST", "Starting backup functionality tests")
        
        try:
            # Initialize backup class
            backup_system = DatabaseBackup()
            
            # Test 1: Schema-only backup
            self.log_step("BACKUP", "Testing schema-only backup")
            start_time = time.time()
            
            schema_backup = backup_system.create_backup(
                backup_type='schema',
                description='Test schema backup'
            )
            
            schema_time = time.time() - start_time
            
            if schema_backup:
                self.log_step("BACKUP", f"Schema backup created: {schema_backup}", "SUCCESS")
                self.test_results['backup_tests'].append({
                    'type': 'schema',
                    'success': True,
                    'filename': schema_backup,
                    'duration': schema_time
                })
            else:
                self.log_step("BACKUP", "Schema backup failed", "ERROR")
                self.test_results['backup_tests'].append({
                    'type': 'schema',
                    'success': False,
                    'duration': schema_time
                })
            
            # Test 2: Data-only backup
            self.log_step("BACKUP", "Testing data-only backup")
            start_time = time.time()
            
            data_backup = backup_system.create_backup(
                backup_type='data',
                description='Test data backup'
            )
            
            data_time = time.time() - start_time
            
            if data_backup:
                self.log_step("BACKUP", f"Data backup created: {data_backup}", "SUCCESS")
                self.test_results['backup_tests'].append({
                    'type': 'data',
                    'success': True,
                    'filename': data_backup,
                    'duration': data_time
                })
            else:
                self.log_step("BACKUP", "Data backup failed", "ERROR")
                self.test_results['backup_tests'].append({
                    'type': 'data',
                    'success': False,
                    'duration': data_time
                })
            
            # Test 3: Complete backup
            self.log_step("BACKUP", "Testing complete backup")
            start_time = time.time()
            
            complete_backup = backup_system.create_backup(
                backup_type='complete',
                description='Test complete backup'
            )
            
            complete_time = time.time() - start_time
            
            if complete_backup:
                self.log_step("BACKUP", f"Complete backup created: {complete_backup}", "SUCCESS")
                self.test_results['backup_tests'].append({
                    'type': 'complete',
                    'success': True,
                    'filename': complete_backup,
                    'duration': complete_time
                })
                return complete_backup  # Return for restore testing
            else:
                self.log_step("BACKUP", "Complete backup failed", "ERROR")
                self.test_results['backup_tests'].append({
                    'type': 'complete',
                    'success': False,
                    'duration': complete_time
                })
                return None
                
        except Exception as e:
            self.log_step("BACKUP", f"Backup testing failed: {e}", "ERROR")
            return None
    
    def test_restore_functionality(self, backup_filename=None):
        """Test the Python restore script functionality"""
        self.log_step("RESTORE TEST", "Starting restore functionality tests")
        
        if not backup_filename:
            # Find the latest backup file
            backups_dir = Path("backups")
            if backups_dir.exists():
                backup_files = list(backups_dir.glob("*.sql"))
                if backup_files:
                    backup_filename = str(max(backup_files, key=os.path.getctime))
                    self.log_step("RESTORE", f"Using latest backup: {backup_filename}")
                else:
                    self.log_step("RESTORE", "No backup files found", "ERROR")
                    return False
            else:
                self.log_step("RESTORE", "Backups directory not found", "ERROR")
                return False
        
        try:
            # Initialize restore class
            restore_system = DatabaseRestore()
            
            # Test 1: Verify backup file
            self.log_step("RESTORE", f"Verifying backup file: {backup_filename}")
            
            if restore_system.verify_backup(backup_filename):
                self.log_step("RESTORE", "Backup file verification passed", "SUCCESS")
            else:
                self.log_step("RESTORE", "Backup file verification failed", "WARNING")
            
            # Test 2: Get current database stats before restore
            self.log_step("RESTORE", "Getting pre-restore database statistics")
            pre_stats = restore_system.get_database_stats()
            
            if pre_stats:
                self.log_step("RESTORE", f"Pre-restore user count: {pre_stats.get('users', 'unknown')}")
            
            # Test 3: Perform restore
            self.log_step("RESTORE", "Performing database restore")
            start_time = time.time()
            
            restore_result = restore_system.restore_database(
                backup_filename,
                create_backup=False,  # Skip pre-restore backup for testing
                verify=True
            )
            
            restore_time = time.time() - start_time
            
            if restore_result:
                self.log_step("RESTORE", f"Restore completed successfully in {restore_time:.2f}s", "SUCCESS")
                
                # Test 4: Verify restore
                self.log_step("RESTORE", "Verifying restore results")
                post_stats = restore_system.get_database_stats()
                
                if post_stats:
                    self.log_step("RESTORE", f"Post-restore user count: {post_stats.get('users', 'unknown')}")
                
                self.test_results['restore_tests'].append({
                    'success': True,
                    'filename': backup_filename,
                    'duration': restore_time,
                    'pre_stats': pre_stats,
                    'post_stats': post_stats
                })
                
                return True
            else:
                self.log_step("RESTORE", "Restore failed", "ERROR")
                self.test_results['restore_tests'].append({
                    'success': False,
                    'filename': backup_filename,
                    'duration': restore_time
                })
                return False
                
        except Exception as e:
            self.log_step("RESTORE", f"Restore testing failed: {e}", "ERROR")
            return False
    
    def test_python_scripts_directly(self):
        """Test backup and restore scripts by running them directly"""
        self.log_step("DIRECT TEST", "Testing Python scripts directly via command line")
        
        # Test backup script
        try:
            self.log_step("DIRECT", "Running backup.py script")
            result = subprocess.run([
                sys.executable, 
                os.path.join("db", "backup.py"),
                "--type", "complete",
                "--description", "Direct script test"
            ], capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                self.log_step("DIRECT", "backup.py executed successfully", "SUCCESS")
                print(f"Output: {result.stdout}")
            else:
                self.log_step("DIRECT", f"backup.py failed: {result.stderr}", "ERROR")
                
        except subprocess.TimeoutExpired:
            self.log_step("DIRECT", "backup.py timed out", "WARNING")
        except Exception as e:
            self.log_step("DIRECT", f"Error running backup.py: {e}", "ERROR")
        
        # Test restore script
        try:
            self.log_step("DIRECT", "Running restore.py script (list backups)")
            result = subprocess.run([
                sys.executable, 
                os.path.join("db", "restore.py"),
                "--list"
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                self.log_step("DIRECT", "restore.py list executed successfully", "SUCCESS")
                print(f"Available backups: {result.stdout}")
            else:
                self.log_step("DIRECT", f"restore.py list failed: {result.stderr}", "ERROR")
                
        except subprocess.TimeoutExpired:
            self.log_step("DIRECT", "restore.py timed out", "WARNING")
        except Exception as e:
            self.log_step("DIRECT", f"Error running restore.py: {e}", "ERROR")
    
    def generate_report(self):
        """Generate a comprehensive test report"""
        print(f"\n{'='*80}")
        print("PYTHON BACKUP & RESTORE TEST REPORT")
        print(f"{'='*80}")
        
        # Backup Tests Summary
        print("\n📦 BACKUP TESTS:")
        backup_success_count = sum(1 for test in self.test_results['backup_tests'] if test['success'])
        backup_total = len(self.test_results['backup_tests'])
        
        print(f"   Total Tests: {backup_total}")
        print(f"   Successful: {backup_success_count}")
        print(f"   Failed: {backup_total - backup_success_count}")
        
        for test in self.test_results['backup_tests']:
            status = "✅" if test['success'] else "❌"
            print(f"   {status} {test['type'].title()} backup: {test['duration']:.2f}s")
            if test['success'] and 'filename' in test:
                print(f"      File: {test['filename']}")
        
        # Restore Tests Summary
        print("\n🔄 RESTORE TESTS:")
        restore_success_count = sum(1 for test in self.test_results['restore_tests'] if test['success'])
        restore_total = len(self.test_results['restore_tests'])
        
        print(f"   Total Tests: {restore_total}")
        print(f"   Successful: {restore_success_count}")
        print(f"   Failed: {restore_total - restore_success_count}")
        
        for test in self.test_results['restore_tests']:
            status = "✅" if test['success'] else "❌"
            print(f"   {status} Restore: {test['duration']:.2f}s")
            if test['success']:
                pre_users = test.get('pre_stats', {}).get('users', 'unknown')
                post_users = test.get('post_stats', {}).get('users', 'unknown')
                print(f"      Users: {pre_users} → {post_users}")
        
        # Overall Status
        print(f"\n{'='*80}")
        overall_success = (backup_success_count == backup_total and 
                          restore_success_count == restore_total)
        
        if overall_success:
            print("🎉 ALL TESTS PASSED - Python backup and restore scripts are working!")
        else:
            print("⚠️ SOME TESTS FAILED - Check the logs above for details")
        
        print(f"{'='*80}")
    
    def run_comprehensive_test(self):
        """Run the complete test suite"""
        print("🧪 PYTHON BACKUP & RESTORE COMPREHENSIVE TEST SUITE")
        print("="*80)
        
        # Test backup functionality
        latest_backup = self.test_backup_functionality()
        
        print(f"\n{'-'*40}")
        
        # Test restore functionality
        self.test_restore_functionality(latest_backup)
        
        print(f"\n{'-'*40}")
        
        # Test scripts directly
        self.test_python_scripts_directly()
        
        # Generate final report
        self.generate_report()

def main():
    """Main test execution"""
    print("🐍 Python Backup & Restore Script Tester")
    print("="*50)
    
    # Check if required scripts exist
    backup_script = os.path.join("db", "backup.py")
    restore_script = os.path.join("db", "restore.py")
    
    if not os.path.exists(backup_script):
        print(f"❌ backup.py not found at {backup_script}")
        return
        
    if not os.path.exists(restore_script):
        print(f"❌ restore.py not found at {restore_script}")
        return
    
    print("✅ Both backup.py and restore.py found")
    
    # Run the test suite
    test_suite = BackupRestoreTestSuite()
    test_suite.run_comprehensive_test()

if __name__ == "__main__":
    main()
