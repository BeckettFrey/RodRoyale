#!/usr/bin/env python3
"""
Test cases for the password change endpoint
"""

import requests
import uuid
import urllib3

# Disable SSL warnings for testing
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def create_test_user_and_auth(username=None, email=None, password=None):
    """Helper function to create a test user and return auth token."""
    if not username:
        unique_suffix = uuid.uuid4().hex[:8]
        username = f"testuser_{unique_suffix}"
    if not email:
        unique_suffix = uuid.uuid4().hex[:8]
        email = f"test_{unique_suffix}@example.com"
    if not password:
        password = "testpass123"
    
    user_data = {
        "username": username,
        "email": email,
        "password": password
    }
    
    # Register user
    reg_response = requests.post("https://localhost:8000/api/v1/auth/register", json=user_data, verify=False)
    if reg_response.status_code != 201:
        print(f"Registration failed! Expected 201, got {reg_response.status_code}")
        return None, None
    user_id = reg_response.json()["user"]["_id"]
    
    # Login to get token
    login_response = requests.post("https://localhost:8000/api/v1/auth/login", json={
        "email": email,
        "password": password
    }, verify=False)
    assert login_response.status_code == 200
    token = login_response.json()["token"]["access_token"]
    
    return user_data, token

class TestPasswordChange:
    def setup_method(self):
        """Setup for each test method"""
        self.base_url = "https://localhost:8000"
        self.auth_url = f"{self.base_url}/api/v1/auth"
    
    def test_successful_password_change(self):
        """Test successful password change with valid credentials"""
        # Create test user and get auth token
        unique_suffix = uuid.uuid4().hex[:8]
        username = f"password_test_user_{unique_suffix}"
        email = f"password_test_{unique_suffix}@example.com"
        old_password = "oldpassword123"
        new_password = "newpassword456"
        
        user_data, auth_token = create_test_user_and_auth(
            username=username,
            email=email,
            password=old_password
        )
        
        if not auth_token:
            print("❌ Failed to create test user")
            return
        
        # Change password
        headers = {"Authorization": f"Bearer {auth_token}"}
        change_data = {
            "current_password": old_password,
            "new_password": new_password
        }
        
        response = requests.post(f"{self.auth_url}/change-password", json=change_data, headers=headers, verify=False)
        assert response.status_code == 200
        
        result = response.json()
        assert result["message"] == "Password changed successfully"
        assert "Please log in again" in result["detail"]
        
        # Verify old password no longer works
        login_data = {"email": email, "password": old_password}
        old_login_response = requests.post(f"{self.auth_url}/login", json=login_data, verify=False)
        assert old_login_response.status_code == 401
        
        # Verify new password works
        new_login_data = {"email": email, "password": new_password}
        new_login_response = requests.post(f"{self.auth_url}/login", json=new_login_data, verify=False)
        assert new_login_response.status_code == 200
    
    def test_wrong_current_password(self):
        """Test password change with incorrect current password"""
        # Create test user and get auth token
        unique_suffix = uuid.uuid4().hex[:8]
        username = f"password_test_user2_{unique_suffix}"
        email = f"password_test2_{unique_suffix}@example.com"
        password = "testpassword123"
        
        user_data, auth_token = create_test_user_and_auth(
            username=username,
            email=email,
            password=password
        )
        
        # Try to change password with wrong current password
        headers = {"Authorization": f"Bearer {auth_token}"}
        change_data = {
            "current_password": "wrongpassword",
            "new_password": "newpassword456"
        }
        
        response = requests.post(f"{self.auth_url}/change-password", json=change_data, headers=headers, verify=False)
        assert response.status_code == 400
        
        result = response.json()
        assert "Current password is incorrect" in result["detail"]
    
    def test_same_password_rejection(self):
        """Test that using the same password as new password is rejected"""
        # Create test user and get auth token
        unique_suffix = uuid.uuid4().hex[:8]
        username = f"password_test_user3_{unique_suffix}"
        email = f"password_test3_{unique_suffix}@example.com"
        password = "testpassword123"
        
        user_data, auth_token = create_test_user_and_auth(
            username=username,
            email=email,
            password=password
        )
        
        # Try to change password to the same password
        headers = {"Authorization": f"Bearer {auth_token}"}
        change_data = {
            "current_password": password,
            "new_password": password
        }
        
        response = requests.post(f"{self.auth_url}/change-password", json=change_data, headers=headers, verify=False)
        assert response.status_code == 400
        
        result = response.json()
        assert "New password must be different from current password" in result["detail"]
    
    def test_unauthenticated_request(self):
        """Test password change without authentication token"""
        change_data = {
            "current_password": "oldpassword",
            "new_password": "newpassword"
        }
        
        response = requests.post(f"{self.auth_url}/change-password", json=change_data, verify=False)
        assert response.status_code == 403
    
    def test_invalid_token(self):
        """Test password change with invalid authentication token"""
        headers = {"Authorization": "Bearer invalid_token"}
        change_data = {
            "current_password": "oldpassword",
            "new_password": "newpassword"
        }
        
        response = requests.post(f"{self.auth_url}/change-password", json=change_data, headers=headers, verify=False)
        assert response.status_code == 403
    
    def test_password_validation(self):
        """Test password change with invalid new password (too short)"""
        # Create test user and get auth token
        unique_suffix = uuid.uuid4().hex[:8]
        username = f"password_test_user4_{unique_suffix}"
        email = f"password_test4_{unique_suffix}@example.com"
        password = "testpassword123"
        
        user_data, auth_token = create_test_user_and_auth(
            username=username,
            email=email,
            password=password
        )
        
        # Try to change to password that's too short
        headers = {"Authorization": f"Bearer {auth_token}"}
        change_data = {
            "current_password": password,
            "new_password": "123"  # Too short (less than 6 characters)
        }
        
        response = requests.post(f"{self.auth_url}/change-password", json=change_data, headers=headers, verify=False)
        assert response.status_code == 422  # Validation error

if __name__ == "__main__":
    # Run a simple demo
    test_instance = TestPasswordChange()
    test_instance.setup_method()
    
    print("🔐 Testing Password Change Endpoint")
    print("=" * 40)
    
    try:
        test_instance.test_successful_password_change()
        print("✅ Successful password change test passed")
    except Exception as e:
        print(f"❌ Successful password change test failed: {e}")
        import traceback
        traceback.print_exc()
    
    try:
        test_instance.test_wrong_current_password()
        print("✅ Wrong current password test passed")
    except Exception as e:
        print(f"❌ Wrong current password test failed: {e}")
        import traceback
        traceback.print_exc()
    
    try:
        test_instance.test_same_password_rejection()
        print("✅ Same password rejection test passed")
    except Exception as e:
        print(f"❌ Same password rejection test failed: {e}")
        import traceback
        traceback.print_exc()
    
    try:
        test_instance.test_unauthenticated_request()
        print("✅ Unauthenticated request test passed")
    except Exception as e:
        print(f"❌ Unauthenticated request test failed: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n🎉 Password change endpoint testing completed!")
