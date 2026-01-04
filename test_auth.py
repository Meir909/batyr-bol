import requests
import json

# Test server endpoints
BASE_URL = "http://localhost:8000"

def test_registration():
    """Test user registration"""
    print("Testing user registration...")
    
    # Test data
    user_data = {
        "name": "Тестовый Пользователь",
        "email": "test@example.com",
        "password": "testpassword123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/register", json=user_data)
        print(f"Registration response: {response.status_code}")
        print(f"Response data: {response.json()}")
        return response.json()
    except Exception as e:
        print(f"Error during registration: {e}")
        return None

def test_login():
    """Test user login"""
    print("\nTesting user login...")
    
    # Test data
    login_data = {
        "email": "test@example.com",
        "password": "testpassword123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/login", json=login_data)
        print(f"Login response: {response.status_code}")
        print(f"Response data: {response.json()}")
        return response.json()
    except Exception as e:
        print(f"Error during login: {e}")
        return None

def test_profile_update():
    """Test profile update"""
    print("\nTesting profile update...")
    
    # Test data
    update_data = {
        "email": "test@example.com",
        "name": "Обновленный Пользователь",
        "new_email": "updated@example.com",
        "password": "newpassword123"
    }
    
    try:
        response = requests.put(f"{BASE_URL}/api/profile", json=update_data)
        print(f"Profile update response: {response.status_code}")
        print(f"Response data: {response.json()}")
        return response.json()
    except Exception as e:
        print(f"Error during profile update: {e}")
        return None

if __name__ == "__main__":
    print("Running authentication tests...")
    
    # Test registration
    reg_result = test_registration()
    
    if reg_result and reg_result.get("success"):
        # Test login
        login_result = test_login()
        
        if login_result and login_result.get("success"):
            # Test profile update
            update_result = test_profile_update()
            
            print("\nAll tests completed!")
        else:
            print("Login failed, skipping profile update test")
    else:
        print("Registration failed, skipping other tests")