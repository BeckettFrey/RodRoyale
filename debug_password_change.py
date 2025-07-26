#!/usr/bin/env python3
"""
Debug script to test password change endpoint with detailed logging
"""

import requests
import urllib3
import uuid

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_URL = "https://localhost:8000/api/v1"
AUTH_URL = f"{BASE_URL}/auth"

def test_password_change_debug():
    print("🔐 Debug: Password Change Test")
    print("=" * 50)
    
    # Step 1: Create a test user
    unique_id = uuid.uuid4().hex[:8]
    user_data = {
        "username": f"debug_user_{unique_id}",
        "email": f"debug_{unique_id}@example.com",
        "password": "debug_password_123"
    }
    
    print(f"1. Creating test user: {user_data['username']}")
    
    # Register user
    reg_response = requests.post(f"{AUTH_URL}/register", json=user_data, verify=False)
    if reg_response.status_code != 201:
        print(f"❌ Registration failed: {reg_response.status_code}")
        print(f"   Response: {reg_response.text}")
        return
    
    print("✅ User created successfully!")
    
    # Get access token from registration response
    reg_data = reg_response.json()
    access_token = reg_data["token"]["access_token"]
    user_id = reg_data["user"]["_id"]
    
    print(f"   User ID: {user_id}")
    print(f"   Token: {access_token[:50]}...")
    
    # Step 2: Try to change password with CORRECT current password
    print("\n2. Attempting password change with CORRECT current password")
    
    headers = {"Authorization": f"Bearer {access_token}"}
    change_data = {
        "current_password": user_data["password"],  # This should be correct
        "new_password": "new_debug_password_456"
    }
    
    print(f"   Current password: '{change_data['current_password']}'")
    print(f"   New password: '{change_data['new_password']}'")
    
    change_response = requests.post(f"{AUTH_URL}/change-password", json=change_data, headers=headers, verify=False)
    
    print(f"   Response Status: {change_response.status_code}")
    print(f"   Response Body: {change_response.text}")
    
    if change_response.status_code == 200:
        print("✅ Password change succeeded!")
    else:
        print("❌ Password change failed!")
        
        # Step 3: Try to change password with WRONG current password to see the difference
        print("\n3. Testing with WRONG current password for comparison")
        
        wrong_change_data = {
            "current_password": "definitely_wrong_password",
            "new_password": "new_debug_password_789"
        }
        
        wrong_response = requests.post(f"{AUTH_URL}/change-password", json=wrong_change_data, headers=headers, verify=False)
        print(f"   Wrong password response: {wrong_response.status_code}")
        print(f"   Wrong password body: {wrong_response.text}")

if __name__ == "__main__":
    test_password_change_debug()
