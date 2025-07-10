#!/usr/bin/env python3

import requests
import json

def test_frontend_api():
    """Test the frontend API connectivity"""
    frontend_url = "http://localhost:3000"
    backend_url = "http://localhost:3001"
    
    print("🧪 Testing Frontend API Connectivity...")
    
    # Test direct backend connection
    try:
        print("\n1. Testing direct backend connection...")
        response = requests.get(f"{backend_url}/api/analytics/system-status")
        print(f"Backend status: {response.status_code}")
        
        # Test frontend connection to backend via proxy
        print("\n2. Testing frontend proxy to backend...")
        # This should proxy through to the backend
        response = requests.get(f"{frontend_url}/api/analytics/system-status")
        print(f"Frontend proxy status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Frontend proxy is working correctly")
        else:
            print("❌ Frontend proxy may have issues")
            
    except requests.exceptions.ConnectionError as e:
        print(f"❌ Connection error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_frontend_api()
