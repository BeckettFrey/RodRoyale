#!/usr/bin/env python3
"""
Password Reset Flow Demo for Rod Royale API
Demonstrates the complete password reset process
"""

import requests
import urllib3
import uuid

# Disable SSL warnings for demo
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_URL = "https://localhost:8000/api/v1"
AUTH_URL = f"{BASE_URL}/auth"

def demo_password_reset_flow():
    print("🔐 Rod Royale Password Reset Flow Demo")
    print("=" * 60)
    
    # Step 1: Create a test user
    unique_id = uuid.uuid4().hex[:8]
    user_data = {
        "username": f"reset_demo_user_{unique_id}",
        "email": f"reset_demo_{unique_id}@example.com",
        "password": "original_password_123"
    }
    
    print(f"1. Creating test user: {user_data['username']}")
    print(f"   Email: {user_data['email']}")
    print(f"   Original password: {user_data['password']}")
    
    # Register user
    reg_response = requests.post(f"{AUTH_URL}/register", json=user_data, verify=False)
    if reg_response.status_code != 201:
        print(f"❌ Registration failed: {reg_response.json()}")
        return
    
    print("✅ User created successfully!")
    
    # Step 2: Simulate forgetting password and request reset
    print("\n2. User forgot password - requesting reset")
    
    reset_request_data = {
        "email": user_data["email"]
    }
    
    forgot_response = requests.post(f"{AUTH_URL}/forgot-password", json=reset_request_data, verify=False)
    
    if forgot_response.status_code == 200:
        forgot_result = forgot_response.json()
        print("✅ Password reset requested successfully!")
        print(f"   Message: {forgot_result['message']}")
        
        # In demo mode, we get the token back (in production this would be emailed)
        reset_token = forgot_result.get("reset_token")
        if reset_token:
            print(f"   Reset token: {reset_token[:50]}...")
            print(f"   Note: {forgot_result.get('note', '')}")
        else:
            print("❌ No reset token received")
            return
    else:
        print(f"❌ Password reset request failed: {forgot_response.json()}")
        return
    
    # Step 3: Verify old password no longer works (simulate user trying to login)
    print("\n3. Verifying user can't login with old password...")
    
    old_login_data = {
        "email": user_data["email"],
        "password": user_data["password"]
    }
    
    old_login_response = requests.post(f"{AUTH_URL}/login", json=old_login_data, verify=False)
    
    if old_login_response.status_code == 200:
        print("✅ User can still login with old password (this is expected)")
    else:
        print(f"❌ Unexpected: User can't login with original password: {old_login_response.json()}")
    
    # Step 4: Use reset token to set new password
    print("\n4. Using reset token to set new password")
    
    new_password = "new_secure_password_456"
    reset_data = {
        "token": reset_token,
        "new_password": new_password
    }
    
    reset_response = requests.post(f"{AUTH_URL}/reset-password", json=reset_data, verify=False)
    
    if reset_response.status_code == 200:
        reset_result = reset_response.json()
        print("✅ Password reset successfully!")
        print(f"   Message: {reset_result['message']}")
        print(f"   Detail: {reset_result['detail']}")
    else:
        print(f"❌ Password reset failed: {reset_response.json()}")
        return
    
    # Step 5: Verify old password no longer works
    print("\n5. Verifying old password no longer works...")
    
    old_login_response2 = requests.post(f"{AUTH_URL}/login", json=old_login_data, verify=False)
    
    if old_login_response2.status_code == 401:
        print("✅ Old password correctly rejected")
    else:
        print(f"❌ Security issue: Old password still works! {old_login_response2.json()}")
        return
    
    # Step 6: Verify new password works
    print("\n6. Verifying new password works...")
    
    new_login_data = {
        "email": user_data["email"],
        "password": new_password
    }
    
    new_login_response = requests.post(f"{AUTH_URL}/login", json=new_login_data, verify=False)
    
    if new_login_response.status_code == 200:
        new_login_result = new_login_response.json()
        print("✅ New password works correctly!")
        print(f"   Logged in as: {new_login_result['user']['username']}")
    else:
        print(f"❌ New password login failed: {new_login_response.json()}")
        return
    
    # Step 7: Test security - try to reuse the reset token
    print("\n7. Testing security - trying to reuse reset token...")
    
    reuse_data = {
        "token": reset_token,
        "new_password": "another_password_789"
    }
    
    reuse_response = requests.post(f"{AUTH_URL}/reset-password", json=reuse_data, verify=False)
    
    if reuse_response.status_code == 400:
        print("✅ Reset token correctly rejected (can't be reused)")
    else:
        print(f"❌ Security issue: Reset token was reused! {reuse_response.json()}")
    
    print("\n🎉 Password reset flow demo completed successfully!")
    
    # Summary
    print("\n📖 Complete Password Reset Flow Summary:")
    print("   1. User requests password reset with email")
    print("   2. System generates secure reset token (sent via email in production)")
    print("   3. User clicks reset link with token")
    print("   4. User enters new password")
    print("   5. System validates token and updates password")
    print("   6. Old password is invalidated")
    print("   7. Reset token becomes invalid after use")
    
    print("\n🔧 API Endpoints:")
    print(f"   POST {AUTH_URL}/forgot-password")
    print(f"   POST {AUTH_URL}/reset-password")

def test_error_scenarios():
    """Test various error scenarios"""
    print("\n🔍 Testing Error Scenarios:")
    print("=" * 40)
    
    # Test 1: Non-existent email
    print("\n   Test 1: Non-existent email")
    non_existent_data = {"email": "nonexistent@example.com"}
    response = requests.post(f"{AUTH_URL}/forgot-password", json=non_existent_data, verify=False)
    print(f"   Status: {response.status_code} (should be 200 for security)")
    
    # Test 2: Invalid reset token
    print("\n   Test 2: Invalid reset token")
    invalid_data = {"token": "invalid_token", "new_password": "newpass123"}
    response = requests.post(f"{AUTH_URL}/reset-password", json=invalid_data, verify=False)
    print(f"   Status: {response.status_code} (should be 400)")
    
    # Test 3: Password too short
    print("\n   Test 3: Password too short")
    # First get a valid token
    unique_id = uuid.uuid4().hex[:8]
    user_data = {
        "username": f"test_user_{unique_id}",
        "email": f"test_{unique_id}@example.com",
        "password": "testpass123"
    }
    requests.post(f"{AUTH_URL}/register", json=user_data, verify=False)
    
    reset_req = requests.post(f"{AUTH_URL}/forgot-password", json={"email": user_data["email"]}, verify=False)
    if reset_req.status_code == 200:
        token = reset_req.json().get("reset_token")
        if token:
            short_pass_data = {"token": token, "new_password": "123"}  # Too short
            response = requests.post(f"{AUTH_URL}/reset-password", json=short_pass_data, verify=False)
            print(f"   Status: {response.status_code} (should be 422 for validation error)")

if __name__ == "__main__":
    try:
        demo_password_reset_flow()
        test_error_scenarios()
    except KeyboardInterrupt:
        print("\n\n👋 Demo interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()
