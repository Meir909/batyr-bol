#!/usr/bin/env python3
"""
Test script for profile editing functionality
"""

import requests
import json
import time

def test_profile_editing():
    """Test the profile editing functionality"""
    base_url = "http://localhost:8000"
    
    print("Testing profile editing functionality...")
    
    # First, register a test user
    print("\n1. Registering test user...")
    register_data = {
        "name": "Test User",
        "email": "test@example.com",
        "password": "testpassword"
    }
    
    try:
        response = requests.post(f"{base_url}/api/register", json=register_data)
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ Registration successful")
                user_data = result.get('user', {})
                print(f"   User ID: {user_data.get('id')}")
                print(f"   Name: {user_data.get('name')}")
                print(f"   Email: {user_data.get('email')}")
            else:
                print(f"❌ Registration failed: {result.get('message')}")
        else:
            print(f"❌ Registration failed with status {response.status_code}")
    except Exception as e:
        print(f"❌ Registration error: {e}")
        return
    
    # Wait a moment
    time.sleep(1)
    
    # Login with the test user
    print("\n2. Logging in...")
    login_data = {
        "email": "test@example.com",
        "password": "testpassword"
    }
    
    try:
        response = requests.post(f"{base_url}/api/login", json=login_data)
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ Login successful")
                user_data = result.get('user', {})
                print(f"   User ID: {user_data.get('id')}")
                print(f"   Name: {user_data.get('name')}")
                print(f"   Email: {user_data.get('email')}")
            else:
                print(f"❌ Login failed: {result.get('message')}")
        else:
            print(f"❌ Login failed with status {response.status_code}")
    except Exception as e:
        print(f"❌ Login error: {e}")
        return
    
    # Wait a moment
    time.sleep(1)
    
    # Update the profile
    print("\n3. Updating profile...")
    update_data = {
        "email": "test@example.com",  # Required for authentication
        "name": "Updated Test User",
        "new_email": "updated_test@example.com"
    }
    
    try:
        response = requests.put(f"{base_url}/api/profile", json=update_data)
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ Profile update successful")
                user_data = result.get('user', {})
                print(f"   Updated Name: {user_data.get('name')}")
                print(f"   Updated Email: {user_data.get('email')}")
            else:
                print(f"❌ Profile update failed: {result.get('message')}")
        else:
            print(f"❌ Profile update failed with status {response.status_code}")
    except Exception as e:
        print(f"❌ Profile update error: {e}")
        return
    
    print("\n🎉 All tests completed!")

if __name__ == "__main__":
    test_profile_editing()