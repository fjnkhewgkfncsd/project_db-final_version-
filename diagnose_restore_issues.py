#!/usr/bin/env python3
"""
Diagnose common restore issues and provide solutions
"""
import os
import subprocess
import json
import requests
from pathlib import Path

def check_environment():
    """Check if environment is properly set up for restore"""
    print("🔍 Checking Environment Setup")
    print("-" * 40)
    
    issues = []
    
    # Check if PostgreSQL tools are available
    try:
        result = subprocess.run(['psql', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ PostgreSQL psql: {result.stdout.strip()}")
        else:
            issues.append("❌ psql command not found in PATH")
    except FileNotFoundError:
        issues.append("❌ psql command not found - PostgreSQL client tools not installed")
    
    try:
        result = subprocess.run(['pg_restore', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ PostgreSQL pg_restore: {result.stdout.strip()}")
        else:
            issues.append("❌ pg_restore command not found")
    except FileNotFoundError:
        issues.append("❌ pg_restore command not found - PostgreSQL client tools not installed")
    
    # Check backup directory
    backup_dir = Path("backups")
    if backup_dir.exists():
        backup_files = list(backup_dir.glob("*.sql"))
        print(f"✅ Backup directory exists with {len(backup_files)} SQL files")
        
        if backup_files:
            # Check a sample backup file
            sample_backup = backup_files[0]
            try:
                with open(sample_backup, 'r', encoding='utf-8') as f:
                    content = f.read(1000)  # Read first 1KB
                
                if 'CREATE' in content or 'INSERT' in content or 'COPY' in content:
                    print(f"✅ Sample backup file ({sample_backup.name}) appears valid")
                else:
                    issues.append(f"❌ Sample backup file ({sample_backup.name}) may be invalid")
            except Exception as e:
                issues.append(f"❌ Cannot read backup file: {e}")
        else:
            issues.append("⚠️  No SQL backup files found")
    else:
        issues.append("❌ Backup directory not found")
    
    # Check Docker if used
    try:
        result = subprocess.run(['docker', 'ps'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Docker is running")
            # Check if postgres container is running
            if 'postgres' in result.stdout:
                print("✅ PostgreSQL container appears to be running")
            else:
                issues.append("⚠️  PostgreSQL container may not be running")
        else:
            print("ℹ️  Docker not available (may be using local PostgreSQL)")
    except FileNotFoundError:
        print("ℹ️  Docker not found (may be using local PostgreSQL)")
    
    return issues

def check_database_connectivity():
    """Test database connectivity"""
    print("\n🔗 Checking Database Connectivity")
    print("-" * 40)
    
    issues = []
    
    # Test connection to PostgreSQL
    env_vars = {
        'PGPASSWORD': os.getenv('DB_PASSWORD', 'hengmengly123'),
        'PGHOST': os.getenv('DB_HOST', 'localhost'),
        'PGPORT': os.getenv('DB_PORT', '5432'),
        'PGUSER': os.getenv('DB_USER', 'postgres')
    }
    
    # Test connection to postgres database
    try:
        cmd = ['psql', '-h', env_vars['PGHOST'], '-p', env_vars['PGPORT'], 
               '-U', env_vars['PGUSER'], '-d', 'postgres', '-c', 'SELECT 1;']
        
        env = {**os.environ, **env_vars}
        result = subprocess.run(cmd, capture_output=True, text=True, env=env)
        
        if result.returncode == 0:
            print("✅ Can connect to PostgreSQL (postgres database)")
        else:
            issues.append(f"❌ Cannot connect to PostgreSQL: {result.stderr}")
    except Exception as e:
        issues.append(f"❌ Database connection test failed: {e}")
    
    # Test connection to target database
    target_db = os.getenv('DB_NAME', 'ecommerce_db')
    try:
        cmd = ['psql', '-h', env_vars['PGHOST'], '-p', env_vars['PGPORT'], 
               '-U', env_vars['PGUSER'], '-d', target_db, '-c', 'SELECT COUNT(*) FROM users;']
        
        env = {**os.environ, **env_vars}
        result = subprocess.run(cmd, capture_output=True, text=True, env=env)
        
        if result.returncode == 0:
            print(f"✅ Can connect to target database ({target_db})")
            # Extract user count from output
            output_lines = result.stdout.strip().split('\n')
            for line in output_lines:
                if line.strip().isdigit():
                    print(f"👥 Current user count: {line.strip()}")
                    break
        else:
            print(f"⚠️  Cannot query target database ({target_db}): {result.stderr}")
            print("   This is normal if database doesn't exist yet")
    except Exception as e:
        issues.append(f"❌ Target database test failed: {e}")
    
    return issues

def check_backend_api():
    """Test backend API connectivity"""
    print("\n🌐 Checking Backend API")
    print("-" * 40)
    
    issues = []
    base_url = 'http://localhost:3001'
    
    # Test basic connectivity
    try:
        response = requests.get(f'{base_url}/api/health', timeout=5)
        if response.status_code == 200:
            print("✅ Backend API is responding")
        else:
            issues.append(f"❌ Backend API returned status {response.status_code}")
    except requests.exceptions.ConnectionError:
        issues.append("❌ Cannot connect to backend API - is the server running?")
    except requests.exceptions.Timeout:
        issues.append("❌ Backend API timeout - server may be overloaded")
    except Exception as e:
        issues.append(f"❌ Backend API test failed: {e}")
    
    # Test admin login
    try:
        login_data = {'email': 'admin@example.com', 'password': 'admin123'}
        response = requests.post(f'{base_url}/api/users/login', json=login_data, timeout=10)
        if response.status_code == 200:
            print("✅ Admin login successful")
            token = response.json().get('data', {}).get('token')
            if token:
                print("✅ Authentication token received")
                
                # Test backup list endpoint
                headers = {'Authorization': f'Bearer {token}'}
                response = requests.get(f'{base_url}/api/admin/database/backups', 
                                      headers=headers, timeout=10)
                if response.status_code == 200:
                    backup_count = len(response.json().get('data', {}).get('backups', []))
                    print(f"✅ Backup list endpoint working ({backup_count} backups found)")
                else:
                    issues.append(f"❌ Backup list endpoint failed: {response.status_code}")
            else:
                issues.append("❌ No authentication token in login response")
        else:
            issues.append(f"❌ Admin login failed: {response.status_code}")
    except Exception as e:
        issues.append(f"❌ API authentication test failed: {e}")
    
    return issues

def analyze_common_restore_failures():
    """Analyze common patterns that cause restore failures"""
    print("\n🔍 Common Restore Failure Patterns")
    print("-" * 40)
    
    solutions = []
    
    # Check for common file issues
    backup_dir = Path("backups")
    if backup_dir.exists():
        sql_files = list(backup_dir.glob("*.sql"))
        
        for backup_file in sql_files[:3]:  # Check first 3 files
            try:
                with open(backup_file, 'r', encoding='utf-8') as f:
                    content = f.read(5000)  # Read first 5KB
                
                # Check for common issues
                if len(content) < 100:
                    solutions.append(f"⚠️  {backup_file.name} is very small - may be empty or incomplete")
                
                if 'CREATE DATABASE' not in content and 'CREATE TABLE' not in content:
                    solutions.append(f"⚠️  {backup_file.name} may be data-only backup (no schema)")
                
                if 'INSERT' not in content and 'COPY' not in content:
                    solutions.append(f"⚠️  {backup_file.name} may be schema-only backup (no data)")
                
                # Count potential user records
                user_lines = content.count('INSERT INTO users') + content.count('COPY public.users')
                if user_lines == 0:
                    solutions.append(f"⚠️  {backup_file.name} may not contain user data")
                
            except Exception as e:
                solutions.append(f"❌ Cannot analyze {backup_file.name}: {e}")
    
    # Common solutions
    print("💡 Common Solutions:")
    print("   1. Ensure backup file is complete (not truncated)")
    print("   2. Use 'complete' backup type for full restore")
    print("   3. Check PostgreSQL logs for detailed error messages")
    print("   4. Verify database permissions and roles")
    print("   5. Ensure target database can be dropped/recreated")
    
    return solutions

def main():
    """Run comprehensive restore diagnostics"""
    print("🏥 Database Restore Diagnostics")
    print("=" * 50)
    
    all_issues = []
    
    # Run all checks
    all_issues.extend(check_environment())
    all_issues.extend(check_database_connectivity())
    all_issues.extend(check_backend_api())
    all_issues.extend(analyze_common_restore_failures())
    
    # Summary
    print(f"\n📋 Diagnostic Summary")
    print("=" * 50)
    
    if not all_issues:
        print("✅ No issues detected! Your restore setup appears to be working correctly.")
    else:
        print(f"⚠️  Found {len(all_issues)} potential issues:")
        for i, issue in enumerate(all_issues, 1):
            print(f"   {i}. {issue}")
        
        print("\n🔧 Recommended Actions:")
        print("   1. Address the issues listed above")
        print("   2. Test restore with a small backup file first")
        print("   3. Check PostgreSQL logs for detailed error messages")
        print("   4. Ensure all required environment variables are set")
        print("   5. Test with both .sql and .backup format files")

if __name__ == "__main__":
    main()
