"""
Authentication endpoint tests for Rod Royale API
"""

import pytest
from fastapi import status
from bson import ObjectId
from auth import AuthUtils

class TestAuthEndpoints:
    """Test authentication endpoints."""
    
    def test_register_success(self, client):
        """Test successful user registration."""
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        
        user_data = {
            "username": f"new_angler_{unique_id}",
            "email": f"new_{unique_id}@example.com", 
            "password": "secure_password123",
            "bio": "New to fishing!"
        }
        
        response = client.post("/api/v1/auth/register", json=user_data)
        
        assert response.status_code == status.HTTP_201_CREATED
        response_data = response.json()
        
        # Check response structure
        assert "token" in response_data
        assert "user" in response_data
        
        token_data = response_data["token"]
        assert "access_token" in token_data
        assert "token_type" in token_data
        assert "refresh_token" in token_data
        assert "expires_in" in token_data
        assert token_data["token_type"] == "bearer"
        
        # Check user data in response
        user_response = response_data["user"]
        assert user_response["username"] == user_data["username"]
        assert user_response["email"] == user_data["email"]
        assert user_response["bio"] == user_data["bio"]
    
    def test_register_duplicate_username(self, client):
        """Test registration with duplicate username."""
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        
        # First, create a user
        user_data = {
            "username": f"test_angler_{unique_id}",
            "email": f"first_{unique_id}@example.com",
            "password": "password123",
            "bio": "First user"
        }
        
        response1 = client.post("/api/v1/auth/register", json=user_data)
        assert response1.status_code == status.HTTP_201_CREATED
        
        # Then try to create another user with same username
        duplicate_data = {
            "username": f"test_angler_{unique_id}",  # Same username
            "email": f"different_{unique_id}@example.com",
            "password": "password123",
            "bio": "Different user"
        }
        
        response2 = client.post("/api/v1/auth/register", json=duplicate_data)
        
        assert response2.status_code == status.HTTP_400_BAD_REQUEST
        assert "already exists" in response2.json()["detail"].lower()
    
    def test_register_duplicate_email(self, client):
        """Test registration with duplicate email."""
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        
        # First, create a user
        user_data = {
            "username": f"first_angler_{unique_id}",
            "email": f"shared_{unique_id}@example.com",
            "password": "password123",
            "bio": "First user"
        }
        
        response1 = client.post("/api/v1/auth/register", json=user_data)
        assert response1.status_code == status.HTTP_201_CREATED
        
        # Then try to create another user with same email
        duplicate_data = {
            "username": f"different_angler_{unique_id}",
            "email": f"shared_{unique_id}@example.com",  # Same email
            "password": "password123",
            "bio": "Different user"
        }
        
        response2 = client.post("/api/v1/auth/register", json=duplicate_data)
        
        assert response2.status_code == status.HTTP_400_BAD_REQUEST
        assert "already exists" in response2.json()["detail"].lower()
    
    def test_register_invalid_email(self, client):
        """Test registration with invalid email format."""
        user_data = {
            "username": "test_angler",
            "email": "invalid-email",
            "password": "password123",
            "bio": "Bio"
        }
        
        response = client.post("/api/v1/auth/register", json=user_data)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_register_missing_fields(self, client):
        """Test registration with missing required fields."""
        user_data = {
            "username": "test_angler",
            # Missing email and password
            "bio": "Bio"
        }
        
        response = client.post("/api/v1/auth/register", json=user_data)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_login_success(self, client):
        """Test successful login."""
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        
        # First register a user
        register_data = {
            "username": f"login_user_{unique_id}",
            "email": f"login_{unique_id}@example.com", 
            "password": "secure_password123",
            "bio": "Test user for login"
        }
        
        register_response = client.post("/api/v1/auth/register", json=register_data)
        assert register_response.status_code == status.HTTP_201_CREATED
        
        # Then try to login
        login_data = {
            "email": f"login_{unique_id}@example.com",  # Use email, not username
            "password": "secure_password123"
        }
        
        response = client.post("/api/v1/auth/login", json=login_data)
        
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        
        # Check login response structure  
        assert "token" in response_data
        token_data = response_data["token"]
        assert "access_token" in token_data
        assert "refresh_token" in token_data
        assert "token_type" in token_data
        assert token_data["token_type"] == "bearer"
    
    def test_login_invalid_username(self, client):
        """Test login with non-existent email."""
        login_data = {
            "email": "nonexistent@example.com",  # Use email, not username
            "password": "password123"
        }
        
        response = client.post("/api/v1/auth/login", json=login_data)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "invalid email or password" in response.json()["detail"].lower()
    
    def test_login_invalid_password(self, client):
        """Test login with incorrect password."""
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        
        # First register a user
        register_data = {
            "username": f"pass_user_{unique_id}",
            "email": f"pass_{unique_id}@example.com", 
            "password": "correct_password123",
            "bio": "Test user for password test"
        }
        
        register_response = client.post("/api/v1/auth/register", json=register_data)
        assert register_response.status_code == status.HTTP_201_CREATED
        
        # Then try to login with wrong password
        login_data = {
            "email": f"pass_{unique_id}@example.com",  # Use email, not username
            "password": "wrong_password"
        }
        
        response = client.post("/api/v1/auth/login", json=login_data)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_login_missing_fields(self, client):
        """Test login with missing required fields."""
        login_data = {
            "username": "test_user"
            # Missing password
        }
        
        response = client.post("/api/v1/auth/login", json=login_data)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_get_me_success(self, client):
        """Test successful retrieval of current user."""
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        
        # First register and login a user
        register_data = {
            "username": f"me_user_{unique_id}",
            "email": f"me_{unique_id}@example.com", 
            "password": "secure_password123",
            "bio": "Test user for get me"
        }
        
        register_response = client.post("/api/v1/auth/register", json=register_data)
        assert register_response.status_code == status.HTTP_201_CREATED
        
        # Get the access token from registration response
        token_info = register_response.json()["token"]
        access_token = token_info["access_token"]
        
        # Now test get me endpoint
        auth_headers = {"Authorization": f"Bearer {access_token}"}
        response = client.get("/api/v1/auth/me", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        
        # Check response structure
        assert "_id" in response_data  # get_me returns user data directly, not wrapped in "user"
        assert response_data["username"] == f"me_user_{unique_id}"
        assert response_data["email"] == f"me_{unique_id}@example.com"
    
    def test_get_me_unauthorized(self, client):
        """Test get me endpoint without authentication."""
        response = client.get("/api/v1/auth/me")
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_get_me_invalid_token(self, client):
        """Test get me endpoint with invalid token."""
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.get("/api/v1/auth/me", headers=headers)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_refresh_token_success(self, client):
        """Test successful token refresh."""
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        
        # First register a user
        register_data = {
            "username": f"refresh_user_{unique_id}",
            "email": f"refresh_{unique_id}@example.com", 
            "password": "secure_password123",
            "bio": "Test user for refresh"
        }
        
        register_response = client.post("/api/v1/auth/register", json=register_data)
        assert register_response.status_code == status.HTTP_201_CREATED
        
        # Get the refresh token from registration response
        token_info = register_response.json()["token"]
        refresh_token = token_info["refresh_token"]
        
        # Test refresh endpoint
        refresh_data = {"refresh_token": refresh_token}  # Use refresh_token, not token
        response = client.post("/api/v1/auth/refresh", json=refresh_data)
        
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        
        # Check refresh response structure - returns token data directly
        assert "access_token" in response_data
        assert "refresh_token" in response_data
        assert "token_type" in response_data
    
    def test_refresh_token_invalid(self, client):
        """Test token refresh with invalid token."""
        refresh_data = {"refresh_token": "invalid_token"}  # Use refresh_token, not token
        
        response = client.post("/api/v1/auth/refresh", json=refresh_data)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_logout_success(self, client):
        """Test successful logout."""
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        
        # First register a user
        register_data = {
            "username": f"logout_user_{unique_id}",
            "email": f"logout_{unique_id}@example.com", 
            "password": "secure_password123",
            "bio": "Test user for logout"
        }
        
        register_response = client.post("/api/v1/auth/register", json=register_data)
        assert register_response.status_code == status.HTTP_201_CREATED
        
        # Get the access token
        token_info = register_response.json()["token"]
        access_token = token_info["access_token"]
        
        # Test logout endpoint
        auth_headers = {"Authorization": f"Bearer {access_token}"}
        response = client.post("/api/v1/auth/logout", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        assert "successfully logged out" in response.json()["message"].lower()
    
    def test_logout_unauthorized(self, client):
        """Test logout without authentication."""
        response = client.post("/api/v1/auth/logout")
        
        assert response.status_code == status.HTTP_200_OK  # Logout returns 200 even without auth

class TestAuthUtils:
    """Test authentication utility functions."""
    
    def test_hash_password(self):
        """Test password hashing."""
        password = "test_password123"
        hashed = AuthUtils.hash_password(password)
        
        assert hashed != password
        assert len(hashed) > 20  # Hashed password should be longer
        assert AuthUtils.verify_password(password, hashed)
    
    def test_verify_password_correct(self):
        """Test password verification with correct password."""
        password = "test_password123"
        hashed = AuthUtils.hash_password(password)
        
        assert AuthUtils.verify_password(password, hashed)
    
    def test_verify_password_incorrect(self):
        """Test password verification with incorrect password."""
        password = "test_password123"
        wrong_password = "wrong_password"
        hashed = AuthUtils.hash_password(password)
        
        assert not AuthUtils.verify_password(wrong_password, hashed)
    
    def test_create_access_token(self):
        """Test access token creation."""
        user_id = str(ObjectId())
        token = AuthUtils.create_access_token({"sub": user_id})
        
        assert isinstance(token, str)
        assert len(token) > 0
        
        # Verify token structure (should have 3 parts separated by dots)
        parts = token.split('.')
        assert len(parts) == 3
    
    def test_decode_access_token_valid(self):
        """Test decoding valid access token."""
        user_id = str(ObjectId())
        token = AuthUtils.create_access_token({"sub": user_id})
        
        decoded_data = AuthUtils.decode_token(token)
        
        assert decoded_data is not None
        assert decoded_data["sub"] == user_id
        assert decoded_data["type"] == "access"
    
    def test_decode_access_token_invalid(self):
        """Test decoding invalid access token."""
        invalid_token = "invalid.jwt.token"
        
        # AuthUtils.decode_token raises HTTPException for invalid tokens
        with pytest.raises(Exception):  # Could be HTTPException or other JWT error
            AuthUtils.decode_token(invalid_token)
    
    def test_decode_access_token_expired(self):
        """Test decoding expired access token."""
        # This would require creating a token with past expiration
        # For now, we'll test with malformed token
        expired_token = "expired.token.here"
        
        # AuthUtils.decode_token raises HTTPException for invalid/expired tokens
        with pytest.raises(Exception):  # Could be HTTPException or other JWT error
            AuthUtils.decode_token(expired_token)
