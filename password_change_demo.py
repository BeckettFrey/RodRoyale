#!/usr/bin/env python3
"""
Simple demo script showing how to use the password change endpoint
"""

import requests
import urllib3
import uuid
import json

# Disable SSL warnings for demo
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_URL = "https://localhost:8000/api/v1"
AUTH_URL = f"{BASE_URL}/auth"

def demo_password_change():
    print("🔐 Rod Royale Password Change Demo")
    print("=" * 50)
    
    # Step 1: Create a test user
    unique_id = uuid.uuid4().hex[:8]
    user_data = {
        "username": f"demo_user_{unique_id}",
        "email": f"demo_{unique_id}@example.com",
        "password": "my_old_password123"
    }
    
    print(f"1. Creating test user: {user_data['username']}")
    
    # Register user
    reg_response = requests.post(f"{AUTH_URL}/register", json=user_data, verify=False)
    if reg_response.status_code != 201:
        print(f"❌ Registration failed: {reg_response.json()}")
        return
    
    print("✅ User created successfully!")
    
    # Get access token from registration response
    access_token = reg_response.json()["token"]["access_token"]
    
    # Step 2: Change password
    print(f"\n2. Changing password from '{user_data['password']}' to 'my_new_secure_password456'")
    
    headers = {"Authorization": f"Bearer {access_token}"}
    change_data = {
        "current_password": user_data["password"],
        "new_password": "my_new_secure_password456"
    }
    
    change_response = requests.post(f"{AUTH_URL}/change-password", json=change_data, headers=headers, verify=False)
    
    if change_response.status_code == 200:
        result = change_response.json()
        print("✅ Password changed successfully!")
        print(f"   Message: {result['message']}")
        print(f"   Detail: {result['detail']}")
    else:
        print(f"❌ Password change failed: {change_response.json()}")
        return
    
    # Step 3: Verify old password no longer works
    print("\n3. Verifying old password no longer works...")
    
    old_login_data = {
        "email": user_data["email"],
        "password": user_data["password"]  # Old password
    }
    
    old_login_response = requests.post(f"{AUTH_URL}/login", json=old_login_data, verify=False)
    
    if old_login_response.status_code == 401:
        print("✅ Old password correctly rejected")
    else:
        print("❌ Security issue: Old password still works!")
        return
    
    # Step 4: Verify new password works
    print("\n4. Verifying new password works...")
    
    new_login_data = {
        "email": user_data["email"],
        "password": "my_new_secure_password456"  # New password
    }
    
    new_login_response = requests.post(f"{AUTH_URL}/login", json=new_login_data, verify=False)
    
    if new_login_response.status_code == 200:
        print("✅ New password works correctly!")
        new_user_data = new_login_response.json()["user"]
        print(f"   Logged in as: {new_user_data['username']}")
    else:
        print(f"❌ New password login failed: {new_login_response.json()}")
        return
    
    print("\n🎉 Password change demo completed successfully!")
    print("\n📖 Summary:")
    print(f"   • User '{user_data['username']}' was created")
    print("   • Password was successfully changed")
    print("   • Old password was properly invalidated")
    print("   • New password authentication works")
    print("\n🔧 How to use in your app:")
    print(f"   1. POST {AUTH_URL}/change-password")
    print("   2. Headers: Authorization: Bearer <access_token>")
    print(f"   3. Body: {json.dumps({'current_password': 'old_pwd', 'new_password': 'new_pwd'}, indent=6)}")
    print(f"   4. Response: {json.dumps({'message': 'Password changed successfully'}, indent=13)}")

if __name__ == "__main__":
    try:
        demo_password_change()
    except KeyboardInterrupt:
        print("\n\n👋 Demo interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()
