import requests
import json
import time
import subprocess
import sys
import os

def end_to_end_test():
    """End-to-end test of the complete BATYR BOL system"""
    print("=== BATYR BOL End-to-End Test ===\n")
    
    base_url = "http://localhost:8000"
    
    try:
        # Step 1: Test web interface accessibility
        print("Step 1: Testing web interface accessibility...")
        response = requests.get(base_url)
        assert response.status_code == 200
        assert "BATYR BOL" in response.text
        print("   ✓ Landing page accessible")
        
        response = requests.get(f"{base_url}/game")
        assert response.status_code == 200
        assert "BATYR BOL" in response.text
        print("   ✓ Game page accessible")
        
        # Step 2: Test user registration
        print("\nStep 2: Testing user registration...")
        email = f"e2e_test_{int(time.time())}@example.com"
        reg_data = {
            "name": "E2E Test User",
            "email": email,
            "password": "e2epassword123"
        }
        
        response = requests.post(f"{base_url}/api/register", json=reg_data)
        assert response.status_code == 200
        result = response.json()
        assert result["success"] == True
        user_id = result["user"]["id"]
        print("   ✓ User registration successful")
        
        # Step 3: Test user login
        print("\nStep 3: Testing user login...")
        login_data = {
            "email": email,
            "password": "e2epassword123"
        }
        
        response = requests.post(f"{base_url}/api/login", json=login_data)
        assert response.status_code == 200
        result = response.json()
        assert result["success"] == True
        assert result["user"]["email"] == email
        print("   ✓ User login successful")
        
        # Step 4: Test profile update
        print("\nStep 4: Testing profile update...")
        update_data = {
            "email": email,
            "name": "Updated E2E Test User",
            "new_email": f"updated_{email}"
        }
        
        response = requests.put(f"{base_url}/api/profile", json=update_data)
        assert response.status_code == 200
        result = response.json()
        assert result["success"] == True
        assert result["user"]["name"] == "Updated E2E Test User"
        print("   ✓ Profile update successful")
        
        # Step 5: Test static files
        print("\nStep 5: Testing static file serving...")
        response = requests.get(f"{base_url}/game_integration.js")
        assert response.status_code == 200
        assert "GameIntegration" in response.text
        print("   ✓ JavaScript file served correctly")
        
        # Step 6: Test data persistence
        print("\nStep 6: Testing data persistence...")
        # Check if user data was saved to file
        if os.path.exists("users_data.json"):
            with open("users_data.json", "r", encoding="utf-8") as f:
                users_data = json.load(f)
                updated_email = f"updated_{email}"
                assert updated_email in users_data
                assert users_data[updated_email]["name"] == "Updated E2E Test User"
            print("   ✓ User data persisted to file")
        else:
            print("   ⚠ users_data.json file not found")
        
        print("\n🎉 All end-to-end tests passed!")
        print("🎉 BATYR BOL system is working correctly!")
        return True
        
    except Exception as e:
        print(f"\n❌ End-to-end test failed: {e}")
        return False

if __name__ == "__main__":
    success = end_to_end_test()
    exit(0 if success else 1)