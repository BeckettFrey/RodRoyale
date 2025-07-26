#!/usr/bin/env python3
"""
Test script demonstrating the password change endpoint functionality
"""

import requests
from typing import Optional

# Configuration
BASE_URL = "http://localhost:8000"
AUTH_ENDPOINT = f"{BASE_URL}/auth"

class PasswordChangeDemo:
    def __init__(self):
        self.access_token: Optional[str] = None
        
    def register_test_user(self, username: str, email: str, password: str) -> bool:
        """Register a test user"""
        print(f"\n1. Registering test user: {username}")
        
        data = {
            "username": username,
            "email": email,
            "password": password
        }
        
        try:
            response = requests.post(f"{AUTH_ENDPOINT}/register", json=data)
            if response.status_code == 201:
                result = response.json()
                self.access_token = result["token"]["access_token"]
                print("✅ User registered successfully")
                print(f"   Username: {result['user']['username']}")
                print(f"   Email: {result['user']['email']}")
                return True
            else:
                print(f"❌ Registration failed: {response.status_code}")
                print(f"   Error: {response.json().get('detail', 'Unknown error')}")
                return False
        except Exception as e:
            print(f"❌ Registration error: {e}")
            return False
    
    def login_user(self, email: str, password: str) -> bool:
        """Login user and get access token"""
        print(f"\n2. Logging in user: {email}")
        
        data = {
            "email": email,
            "password": password
        }
        
        try:
            response = requests.post(f"{AUTH_ENDPOINT}/login", json=data)
            if response.status_code == 200:
                result = response.json()
                self.access_token = result["token"]["access_token"]
                print("✅ Login successful")
                print(f"   User: {result['user']['username']}")
                return True
            else:
                print(f"❌ Login failed: {response.status_code}")
                print(f"   Error: {response.json().get('detail', 'Unknown error')}")
                return False
        except Exception as e:
            print(f"❌ Login error: {e}")
            return False
    
    def change_password(self, current_password: str, new_password: str) -> bool:
        """Change user password"""
        print("\n3. Changing password")
        
        if not self.access_token:
            print("❌ No access token available. Please login first.")
            return False
        
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        data = {
            "current_password": current_password,
            "new_password": new_password
        }
        
        try:
            response = requests.post(f"{AUTH_ENDPOINT}/change-password", json=data, headers=headers)
            if response.status_code == 200:
                result = response.json()
                print("✅ Password changed successfully")
                print(f"   Message: {result['message']}")
                print(f"   Detail: {result['detail']}")
                return True
            else:
                print(f"❌ Password change failed: {response.status_code}")
                error_detail = response.json().get('detail', 'Unknown error')
                print(f"   Error: {error_detail}")
                return False
        except Exception as e:
            print(f"❌ Password change error: {e}")
            return False
    
    def verify_new_password(self, email: str, new_password: str) -> bool:
        """Verify the new password works by logging in"""
        print("\n4. Verifying new password by logging in")
        
        return self.login_user(email, new_password)
    
    def test_security_scenarios(self, email: str, old_password: str, new_password: str):
        """Test various security scenarios"""
        print("\n🔒 Testing Security Scenarios:")
        
        # Test 1: Wrong current password
        print("\n   Test 1: Wrong current password")
        headers = {"Authorization": f"Bearer {self.access_token}"}
        data = {
            "current_password": "wrong_password",
            "new_password": new_password + "_test"
        }
        response = requests.post(f"{AUTH_ENDPOINT}/change-password", json=data, headers=headers)
        if response.status_code == 400:
            print("   ✅ Correctly rejected wrong current password")
        else:
            print("   ❌ Security issue: Wrong password was accepted")
        
        # Test 2: Same password as new password
        print("\n   Test 2: Same password as new password")
        data = {
            "current_password": new_password,  # Using new password since we changed it
            "new_password": new_password
        }
        response = requests.post(f"{AUTH_ENDPOINT}/change-password", json=data, headers=headers)
        if response.status_code == 400:
            print("   ✅ Correctly rejected same password")
        else:
            print("   ❌ Security issue: Same password was accepted")
        
        # Test 3: No authentication token
        print("\n   Test 3: No authentication token")
        data = {
            "current_password": new_password,
            "new_password": new_password + "_test2"
        }
        response = requests.post(f"{AUTH_ENDPOINT}/change-password", json=data)
        if response.status_code == 401:
            print("   ✅ Correctly rejected unauthenticated request")
        else:
            print("   ❌ Security issue: Unauthenticated request was accepted")

def main():
    print("🔐 Password Change Endpoint Demo")
    print("=" * 50)
    
    demo = PasswordChangeDemo()
    
    # Test user credentials
    test_email = "testuser@example.com"
    test_username = "testuser_password_demo"
    old_password = "oldpassword123"
    new_password = "newpassword456"
    
    # Step 1: Register or login
    if not demo.register_test_user(test_username, test_email, old_password):
        # If registration fails (user might exist), try to login
        if not demo.login_user(test_email, old_password):
            print("❌ Could not register or login. Exiting.")
            return
    
    # Step 2: Change password
    if demo.change_password(old_password, new_password):
        # Step 3: Verify new password works
        demo.verify_new_password(test_email, new_password)
        
        # Step 4: Test security scenarios
        demo.test_security_scenarios(test_email, old_password, new_password)
    
    print("\n🎉 Demo completed!")
    print("\n📋 How to use the password change endpoint:")
    print("   1. POST /auth/change-password")
    print("   2. Headers: Authorization: Bearer <your_access_token>")
    print("   3. Body: {'current_password': 'old', 'new_password': 'new'}")
    print("   4. Response: {'message': 'Password changed successfully'}")

if __name__ == "__main__":
    main()
