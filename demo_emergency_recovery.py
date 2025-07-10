#!/usr/bin/env python3
"""
Emergency Recovery System Demonstration
Starts the emergency recovery server and demonstrates its functionality
"""

import subprocess
import time
import requests
import json
import os
import sys
from datetime import datetime

def start_emergency_recovery_server():
    """Start the emergency recovery server"""
    print("🚨 Starting Emergency Recovery Server...")
    
    try:
        # Change to project directory
        project_dir = r"d:\year2\year2_term3\DatabaseAdmin\project_db(v2)"
        os.chdir(project_dir)
        
        # Start emergency recovery server
        process = subprocess.Popen(
            ["node", "backend/emergency-recovery-server.js"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Give it time to start
        time.sleep(3)
        
        # Check if it's running
        try:
            response = requests.get("http://localhost:3002/health", timeout=5)
            if response.status_code == 200:
                print("✅ Emergency Recovery Server started successfully on port 3002")
                return process
            else:
                print(f"❌ Server responded with status {response.status_code}")
                return None
        except requests.exceptions.RequestException:
            print("❌ Server is not responding")
            return None
            
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        return None

def test_emergency_system():
    """Test the emergency recovery system"""
    print("\n🔍 Testing Emergency Recovery System...")
    
    # Emergency credentials
    credentials = {
        "username": "emergency_admin",
        "password": "EmergencyRestore2025!"
    }
    
    try:
        # Test authentication
        print("🔐 Testing authentication...")
        response = requests.post("http://localhost:3002/api/emergency/login", json=credentials)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ Authentication successful")
                token = data['data']['token']
                
                # Test backup listing
                print("📁 Testing backup file listing...")
                headers = {"Authorization": f"Bearer {token}"}
                backup_response = requests.get("http://localhost:3002/api/emergency/backups", headers=headers)
                
                if backup_response.status_code == 200:
                    backup_data = backup_response.json()
                    if backup_data.get('success'):
                        backups = backup_data['data']['backups']
                        print(f"✅ Found {len(backups)} backup files")
                        
                        if backups:
                            latest = backups[0]
                            print(f"   Latest backup: {latest['filename']}")
                            print(f"   Size: {latest['sizeFormatted']}")
                            print(f"   Type: {latest['type']}")
                            print(f"   Modified: {latest['modified']}")
                        
                        return True
                    else:
                        print(f"❌ Backup listing failed: {backup_data.get('message')}")
                        return False
                else:
                    print(f"❌ Backup request failed: {backup_response.status_code}")
                    return False
            else:
                print(f"❌ Authentication failed: {data.get('message')}")
                return False
        else:
            print(f"❌ Authentication request failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Test error: {e}")
        return False

def demonstrate_features():
    """Demonstrate emergency recovery features"""
    print("\n🎯 Emergency Recovery System Features:")
    print("=" * 60)
    
    features = [
        "🔐 Independent Authentication System",
        "📁 Backup File Management and Listing", 
        "🔄 Database Status Monitoring",
        "💾 Safe Database Restoration",
        "📝 Comprehensive Recovery Logging",
        "🚨 Emergency-Only Access Control",
        "🛡️ Security Validation and Checks",
        "🔧 Standalone Operation (No DB Dependency)"
    ]
    
    for feature in features:
        print(f"   ✅ {feature}")
    
    print("\n🌐 Access Points:")
    print("   • Emergency Recovery Interface: http://localhost:3002")
    print("   • Emergency API Base: http://localhost:3002/api/emergency")
    print("   • Health Check: http://localhost:3002/health")
    
    print("\n🔑 Emergency Credentials:")
    print("   • Username: emergency_admin")
    print("   • Password: EmergencyRestore2025!")
    
    print("\n📋 Usage Scenarios:")
    scenarios = [
        "Database server completely down",
        "Main application cannot connect to database", 
        "Database corruption or data loss",
        "Failed database migration or update",
        "Emergency disaster recovery situation"
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"   {i}. {scenario}")

def main():
    """Main demonstration function"""
    print("🚨 EMERGENCY DATABASE RECOVERY SYSTEM DEMONSTRATION")
    print("=" * 70)
    print(f"🕒 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Start emergency recovery server
    server_process = start_emergency_recovery_server()
    
    if not server_process:
        print("❌ Failed to start emergency recovery server")
        print("Please check that Node.js is installed and port 3002 is available")
        return 1
    
    try:
        # Test the system
        test_success = test_emergency_system()
        
        # Demonstrate features
        demonstrate_features()
        
        print("\n" + "=" * 70)
        print("📋 DEMONSTRATION SUMMARY")
        print("=" * 70)
        
        if test_success:
            print("✅ Emergency Recovery System is FULLY OPERATIONAL")
            print("\n🎯 System Status:")
            print("   • Server: Running on port 3002")
            print("   • Authentication: Working")
            print("   • Backup Access: Functional")
            print("   • API Endpoints: Responsive")
            
            print("\n💡 Next Steps:")
            print("   1. Open http://localhost:3002 in your browser")
            print("   2. Use the emergency credentials to log in")
            print("   3. Explore the backup files and recovery options")
            print("   4. Test the database status monitoring")
            
            print("\n⚠️ IMPORTANT NOTES:")
            print("   • This system is for EMERGENCY USE ONLY")
            print("   • Always create backups before restoration")
            print("   • Verify database connections after recovery")
            print("   • Monitor logs for recovery operation details")
            
        else:
            print("❌ Emergency Recovery System has issues")
            print("   Check the logs and ensure all dependencies are available")
        
        print(f"\n🚨 Emergency Recovery Server will continue running...")
        print("   Press Ctrl+C to stop the server")
        
        # Keep the server running
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\n🛑 Stopping Emergency Recovery Server...")
            server_process.terminate()
            server_process.wait()
            print("✅ Server stopped")
            
        return 0 if test_success else 1
        
    except Exception as e:
        print(f"❌ Demonstration error: {e}")
        if server_process:
            server_process.terminate()
        return 1

if __name__ == "__main__":
    sys.exit(main())
