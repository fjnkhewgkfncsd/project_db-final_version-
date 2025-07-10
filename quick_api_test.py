#!/usr/bin/env python3
"""
Quick test for emergency recovery endpoints
"""

import requests
import json

def quick_test():
    base_url = "http://localhost:3002"
    
    # Login
    print("🔐 Testing login...")
    response = requests.post(f"{base_url}/api/emergency/login", json={
        "username": "emergency_admin",
        "password": "EmergencyRestore2025!"
    })
    
    print(f"Login response: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        token = data.get('data', {}).get('token')
        print(f"Token: {token}")
        
        # Test backups
        print("\n📋 Testing backups...")
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{base_url}/api/emergency/backups", headers=headers)
        print(f"Backups response: {response.status_code}")
        print(f"Response content: {response.text}")
        
        # Test status  
        print("\n📊 Testing status...")
        response = requests.get(f"{base_url}/api/emergency/status", headers=headers)
        print(f"Status response: {response.status_code}")
        print(f"Response content: {response.text}")
    
if __name__ == "__main__":
    quick_test()
