import requests
import json
import time

def test_basic_functionality():
    """Test basic functionality of the BATYR BOL application"""
    print("Testing BATYR BOL application...")
    
    base_url = "http://localhost:8000"
    
    try:
        # Test 1: Check if landing page loads
        print("\n1. Testing landing page...")
        response = requests.get(base_url)
        assert response.status_code == 200
        assert "BATYR BOL" in response.text
        print("   ✓ Landing page loads correctly")
        
        # Test 2: Check if game page loads
        print("\n2. Testing game page...")
        response = requests.get(f"{base_url}/game")
        assert response.status_code == 200
        assert "BATYR BOL" in response.text
        print("   ✓ Game page loads correctly")
        
        # Test 3: Check if JavaScript file is served
        print("\n3. Testing JavaScript file...")
        response = requests.get(f"{base_url}/game_integration.js")
        assert response.status_code == 200
        assert "GameIntegration" in response.text
        print("   ✓ JavaScript file served correctly")
        
        # Test 4: Test user registration
        print("\n4. Testing user registration...")
        email = f"test_{int(time.time())}@example.com"
        reg_data = {
            "name": "Test User",
            "email": email,
            "password": "testpassword123"
        }
        
        response = requests.post(f"{base_url}/api/register", json=reg_data)
        assert response.status_code == 200
        result = response.json()
        assert result["success"] == True
        print("   ✓ User registration works")
        
        # Test 5: Test user login
        print("\n5. Testing user login...")
        login_data = {
            "email": email,
            "password": "testpassword123"
        }
        
        response = requests.post(f"{base_url}/api/login", json=login_data)
        assert response.status_code == 200
        result = response.json()
        assert result["success"] == True
        print("   ✓ User login works")
        
        # Test 6: Test profile update
        print("\n6. Testing profile update...")
        update_data = {
            "email": email,
            "name": "Updated Test User"
        }
        
        response = requests.put(f"{base_url}/api/profile", json=update_data)
        assert response.status_code == 200
        result = response.json()
        assert result["success"] == True
        assert result["user"]["name"] == "Updated Test User"
        print("   ✓ Profile update works")
        
        print("\n🎉 All tests passed! BATYR BOL application is working correctly.")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_basic_functionality()
    exit(0 if success else 1)