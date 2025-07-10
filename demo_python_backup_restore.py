#!/usr/bin/env python3
"""
Simple demonstration of Python backup and restore scripts
Shows how to use the existing backup.py and restore.py scripts
"""

import os
import sys
import subprocess
import time
from datetime import datetime

def run_command(command, description, timeout=120):
    """Run a command and return the result"""
    print(f"\n🔄 {description}")
    print(f"Command: {' '.join(command)}")
    
    try:
        start_time = time.time()
        result = subprocess.run(command, capture_output=True, text=True, timeout=timeout)
        duration = time.time() - start_time
        
        if result.returncode == 0:
            print(f"✅ Success ({duration:.2f}s)")
            if result.stdout.strip():
                print(f"Output: {result.stdout}")
            return True, result.stdout
        else:
            print(f"❌ Failed ({duration:.2f}s)")
            if result.stderr.strip():
                print(f"Error: {result.stderr}")
            return False, result.stderr
            
    except subprocess.TimeoutExpired:
        print(f"⏰ Command timed out after {timeout}s")
        return False, "Timeout"
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False, str(e)

def check_python_scripts():
    """Check if the Python backup/restore scripts exist"""
    backup_script = os.path.join("db", "backup.py")
    restore_script = os.path.join("db", "restore.py")
    
    print("🔍 Checking for Python backup/restore scripts...")
    
    if os.path.exists(backup_script):
        print(f"✅ Found backup script: {backup_script}")
    else:
        print(f"❌ Missing backup script: {backup_script}")
        return False
        
    if os.path.exists(restore_script):
        print(f"✅ Found restore script: {restore_script}")
    else:
        print(f"❌ Missing restore script: {restore_script}")
        return False
    
    return True

def demo_backup_script():
    """Demonstrate the backup.py script"""
    print(f"\n{'='*60}")
    print("📦 DEMONSTRATING PYTHON BACKUP SCRIPT")
    print("="*60)
    
    backup_script = os.path.join("db", "backup.py")
    
    # Try to get help/usage
    success, output = run_command([
        sys.executable, backup_script, "--help"
    ], "Getting backup script help", timeout=30)
    
    if not success:
        # Try running without arguments to see what happens
        success, output = run_command([
            sys.executable, backup_script
        ], "Running backup script (default behavior)", timeout=60)
    
    # Try a simple backup
    print(f"\n📝 Attempting to create a backup...")
    success, output = run_command([
        sys.executable, backup_script, "--type", "complete"
    ], "Creating complete backup", timeout=120)
    
    if not success:
        # Try alternative approach
        print(f"\n🔄 Trying alternative backup approach...")
        success, output = run_command([
            sys.executable, backup_script
        ], "Running backup with default settings", timeout=120)

def demo_restore_script():
    """Demonstrate the restore.py script"""
    print(f"\n{'='*60}")
    print("🔄 DEMONSTRATING PYTHON RESTORE SCRIPT")
    print("="*60)
    
    restore_script = os.path.join("db", "restore.py")
    
    # Try to get help/usage
    success, output = run_command([
        sys.executable, restore_script, "--help"
    ], "Getting restore script help", timeout=30)
    
    if not success:
        # Try listing available backups
        success, output = run_command([
            sys.executable, restore_script, "--list"
        ], "Listing available backups", timeout=30)
    
    if not success:
        # Try running without arguments
        success, output = run_command([
            sys.executable, restore_script
        ], "Running restore script (default behavior)", timeout=30)

def show_available_backups():
    """Show available backup files"""
    print(f"\n{'='*60}")
    print("📁 AVAILABLE BACKUP FILES")
    print("="*60)
    
    backups_dir = "backups"
    if os.path.exists(backups_dir):
        backup_files = [f for f in os.listdir(backups_dir) if f.endswith('.sql')]
        
        if backup_files:
            print(f"Found {len(backup_files)} backup files:")
            # Sort by modification time (newest first)
            backup_files.sort(key=lambda x: os.path.getmtime(os.path.join(backups_dir, x)), reverse=True)
            
            for i, filename in enumerate(backup_files[:10], 1):  # Show top 10
                filepath = os.path.join(backups_dir, filename)
                size = os.path.getsize(filepath)
                mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
                
                print(f"  {i:2d}. {filename}")
                print(f"      Size: {size/1024/1024:.2f} MB")
                print(f"      Date: {mtime.strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            print("No backup files found in the backups directory")
    else:
        print(f"Backups directory '{backups_dir}' does not exist")

def check_vs_code_tasks():
    """Check if VS Code tasks are available for backup/restore"""
    print(f"\n{'='*60}")
    print("⚙️ VS CODE TASKS")
    print("="*60)
    
    tasks_file = os.path.join(".vscode", "tasks.json")
    if os.path.exists(tasks_file):
        print("✅ VS Code tasks.json found")
        print("Available tasks for backup/restore:")
        print("  - Database Backup (Ctrl+Shift+P → Tasks: Run Task → Database Backup)")
        print("  - Generate Sample Data")
        
        # Read and show relevant tasks
        try:
            with open(tasks_file, 'r') as f:
                content = f.read()
                if 'backup' in content.lower():
                    print("  ✅ Backup task found in tasks.json")
                if 'restore' in content.lower():
                    print("  ✅ Restore task found in tasks.json")
        except Exception as e:
            print(f"  ⚠️ Could not read tasks.json: {e}")
    else:
        print("❌ No VS Code tasks.json found")

def main():
    """Main demonstration function"""
    print("🐍 PYTHON BACKUP & RESTORE SCRIPTS DEMONSTRATION")
    print("="*60)
    print("This script demonstrates the existing Python backup and restore functionality")
    print("="*60)
    
    # Check if scripts exist
    if not check_python_scripts():
        print("\n❌ Required Python scripts not found. Cannot proceed.")
        return
    
    # Show available backups
    show_available_backups()
    
    # Check VS Code tasks
    check_vs_code_tasks()
    
    # Ask user what to demonstrate
    print(f"\n{'='*60}")
    print("What would you like to demonstrate?")
    print("1. Backup script (backup.py)")
    print("2. Restore script (restore.py)")
    print("3. Both scripts")
    print("4. Just show information (no execution)")
    
    try:
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == "1":
            demo_backup_script()
        elif choice == "2":
            demo_restore_script()
        elif choice == "3":
            demo_backup_script()
            demo_restore_script()
        elif choice == "4":
            print("\n✅ Information displayed above. No scripts executed.")
        else:
            print("Invalid choice. Showing information only.")
    
    except KeyboardInterrupt:
        print("\n\n⏹️ Demonstration cancelled by user.")
    
    print(f"\n{'='*60}")
    print("📋 SUMMARY")
    print("="*60)
    print("Python backup and restore scripts are available:")
    print("  • db/backup.py - Creates database backups")
    print("  • db/restore.py - Restores database from backups")
    print("  • Both scripts can be run directly from command line")
    print("  • VS Code tasks may also be available for GUI access")
    print("  • The web interface also provides backup/restore functionality")

if __name__ == "__main__":
    main()
