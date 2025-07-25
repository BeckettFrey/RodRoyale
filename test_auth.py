#!/usr/bin/env python3
"""
Test script for authentication endpoints
"""
import requests

BASE_URL = "http://localhost:8000/api/v1"

def test_auth():
    print("🔐 Testing Authentication System")
    print("=" * 40)
    
    # Test health endpoint first
    try:
        response = requests.get("http://localhost:8000/health")
        if response.json().get("status") == "healthy":
            print("✅ API is healthy")
        else:
            print("❌ API health check failed")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API. Make sure the server is running on http://localhost:8000")
        return False
    
    # Test user registration
    print("\n1. Testing user registration...")
    user_data = {
        "username": "test_angler",
        "email": "test@Rod Royale.com",
        "bio": "Test user for authentication",
        "password": "testpassword123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/register", json=user_data)
        if response.status_code == 201:
            auth_response = response.json()
            print(f"✅ User registered successfully: {auth_response['user']['username']}")
            print(f"   Access token received: {auth_response['token']['access_token'][:50]}...")
            
            # Store tokens for further testing
            access_token = auth_response['token']['access_token']
            refresh_token = auth_response['token']['refresh_token']
            user_id = auth_response['user']['_id']
            
        else:
            print(f"⚠️  Registration failed: {response.status_code} - {response.text}")
            # If user already exists, try to login
            print("   Trying to login with existing credentials...")
            
            login_data = {
                "email": user_data["email"],
                "password": user_data["password"]
            }
            
            response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
            if response.status_code == 200:
                auth_response = response.json()
                print(f"✅ Logged in successfully: {auth_response['user']['username']}")
                access_token = auth_response['token']['access_token']
                refresh_token = auth_response['token']['refresh_token']
                user_id = auth_response['user']['_id']
            else:
                print(f"❌ Login failed: {response.status_code} - {response.text}")
                return False
    except Exception as e:
        print(f"❌ Error during registration/login: {e}")
        return False
    
    # Test accessing protected endpoint
    print("\n2. Testing protected endpoint access...")
    headers = {"Authorization": f"Bearer {access_token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
        if response.status_code == 200:
            user_profile = response.json()
            print(f"✅ Protected endpoint accessed: {user_profile['username']}")
        else:
            print(f"❌ Failed to access protected endpoint: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Error accessing protected endpoint: {e}")
    
    # Test token refresh
    print("\n3. Testing token refresh...")
    try:
        refresh_data = {"refresh_token": refresh_token}
        response = requests.post(f"{BASE_URL}/auth/refresh", json=refresh_data)
        if response.status_code == 200:
            new_tokens = response.json()
            print("✅ Token refreshed successfully")
            print(f"   New access token: {new_tokens['access_token'][:50]}...")
            access_token = new_tokens['access_token']  # Update token
        else:
            print(f"❌ Token refresh failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Error refreshing token: {e}")
    
    # Test user profile update with authentication
    print("\n4. Testing authenticated user profile update...")
    headers = {"Authorization": f"Bearer {access_token}"}
    update_data = {
        "bio": "Updated bio with authentication!"
    }
    
    try:
        response = requests.put(f"{BASE_URL}/users/{user_id}", json=update_data, headers=headers)
        if response.status_code == 200:
            updated_user = response.json()
            print(f"✅ Profile updated successfully: {updated_user['bio']}")
        else:
            print(f"❌ Profile update failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Error updating profile: {e}")
    
    # Test accessing endpoint without token
    print("\n5. Testing endpoint access without token...")
    try:
        response = requests.get(f"{BASE_URL}/auth/me")  # No Authorization header
        if response.status_code == 401:
            print("✅ Correctly rejected access without token")
        else:
            print(f"⚠️  Expected 401, got {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing unauthorized access: {e}")
    
    # Test login with wrong credentials
    print("\n6. Testing login with wrong credentials...")
    wrong_login = {
        "email": user_data["email"],
        "password": "wrongpassword"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=wrong_login)
        if response.status_code == 401:
            print("✅ Correctly rejected wrong credentials")
        else:
            print(f"⚠️  Expected 401, got {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing wrong credentials: {e}")
    
    # Test logout
    print("\n7. Testing logout...")
    try:
        response = requests.post(f"{BASE_URL}/auth/logout", headers=headers)
        if response.status_code == 200:
            logout_response = response.json()
            print(f"✅ Logout successful: {logout_response['message']}")
        else:
            print(f"❌ Logout failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Error during logout: {e}")
    
    # Test catch creation with JWT authentication
    print("\n8. Testing catch creation with JWT authentication...")
    catch_data = {
        "species": "Test Bass",
        "weight": 2.5,
        "photo_url": "https://example.com/test.jpg",
        "location": {"lat": 40.7128, "lng": -74.0060},
        "shared_with_followers": False
    }
    
    try:
        response = requests.post(f"{BASE_URL}/catches", json=catch_data, headers=headers)
        if response.status_code == 201:
            catch_response = response.json()
            print(f"✅ Catch created successfully: {catch_response['species']}")
            
            # Test getting user's catches
            print("   Testing get current user's catches...")
            response = requests.get(f"{BASE_URL}/catches/me", headers=headers)
            if response.status_code == 200:
                catches = response.json()
                print(f"   ✅ Retrieved {len(catches)} catches for current user")
            else:
                print(f"   ❌ Failed to get user catches: {response.status_code} - {response.text}")
        else:
            print(f"❌ Catch creation failed: {response.status_code} - {response.text}")
            if response.status_code == 401:
                print("   ⚠️  This indicates JWT authentication is not working properly")
    except Exception as e:
        print(f"❌ Error testing catch creation: {e}")
    
    print("\n" + "=" * 40)
    print("🔐 Authentication Test Complete!")
    print("📚 Visit http://localhost:8000/docs for interactive API documentation")
    return True

if __name__ == "__main__":
    success = test_auth()
    exit(0 if success else 1)
