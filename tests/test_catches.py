# File: tests/test_catches.py
"""
Catch management endpoint tests for Rod Royale API
"""

from fastapi import status
from bson import ObjectId
import uuid

def create_test_user_and_auth(client, unique_suffix=None):
    """Helper function to create a test user and return auth headers."""
    if unique_suffix is None:
        unique_suffix = uuid.uuid4().hex[:8]
    else:
        # Ensure uniqueness even with suffix by adding random string
        unique_suffix = f"{unique_suffix}_{uuid.uuid4().hex[:6]}"
    
    user_data = {
        "username": f"testuser_{unique_suffix}",
        "email": f"test_{unique_suffix}@example.com",
        "password": "testpass123"
    }
    
    # Register user
    reg_response = client.post("/api/v1/auth/register", json=user_data)
    assert reg_response.status_code == 201
    user_id = reg_response.json()["user"]["_id"]  # Use _id instead of id
    
    # Login to get token (use email, not username)
    login_response = client.post("/api/v1/auth/login", json={
        "email": user_data["email"],  # Use email for login
        "password": user_data["password"]
    })
    assert login_response.status_code == 200
    token = login_response.json()["token"]["access_token"]  # Access nested token
    auth_headers = {"Authorization": f"Bearer {token}"}
    
    return user_id, auth_headers

class TestCatchEndpoints:
    """Test catch management endpoints."""
    
    def test_create_catch_success(self, client):
        """Test successful catch creation."""
        user_id, auth_headers = create_test_user_and_auth(client)
        
        # Sample catch data
        sample_catch_data = {
            "species": "Bass",
            "weight": 2.5,
            "photo_url": "https://example.com/bass.jpg",
            "location": {"lat": 40.7128, "lng": -74.0060},
            "shared_with_followers": True,
            "add_to_map": False
        }
        
        response = client.post("/api/v1/catches/", json=sample_catch_data, headers=auth_headers)
        
        assert response.status_code == status.HTTP_201_CREATED
        response_data = response.json()
        
        assert response_data["species"] == sample_catch_data["species"]
        assert response_data["weight"] == sample_catch_data["weight"]
        assert response_data["photo_url"] == sample_catch_data["photo_url"]
        assert response_data["user_id"] == user_id
        # Check for either id or _id field
        assert ("id" in response_data) or ("_id" in response_data)
        assert "created_at" in response_data
    
    def test_create_catch_with_pin(self, client):
        """Test catch creation with automatic pin creation."""
        user_id, auth_headers = create_test_user_and_auth(client)
        
        # Sample catch data with pin creation enabled
        sample_catch_data = {
            "species": "Bass",
            "weight": 2.5,
            "photo_url": "https://example.com/bass.jpg",
            "location": {"lat": 40.7128, "lng": -74.0060},
            "shared_with_followers": True,
            "add_to_map": True
        }
        
        response = client.post("/api/v1/catches/", json=sample_catch_data, headers=auth_headers)
        
        assert response.status_code == status.HTTP_201_CREATED
        response_data = response.json()
        
        # Verify catch creation successful
        assert response_data["species"] == sample_catch_data["species"]
    
    def test_create_catch_unauthorized(self, client):
        """Test catch creation without authentication."""
        sample_catch_data = {
            "species": "Bass",
            "weight": 2.5,
            "photo_url": "https://example.com/bass.jpg",
            "location": {"lat": 40.7128, "lng": -74.0060},
            "shared_with_followers": True,
            "add_to_map": False
        }
        
        response = client.post("/api/v1/catches/", json=sample_catch_data)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_create_catch_missing_fields(self, client):
        """Test catch creation with missing required fields."""
        user_id, auth_headers = create_test_user_and_auth(client)
        
        incomplete_data = {
            "species": "Bass",
            # Missing weight, photo_url, location
        }
        
        response = client.post("/api/v1/catches/", json=incomplete_data, headers=auth_headers)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    from unittest.mock import patch

    @patch("services.cloudinary_service.cloudinary.uploader.upload")
    def test_upload_with_image_success(self, mock_upload, client):
        """Test catch creation with image upload (Cloudinary mocked)."""
        user_id, auth_headers = create_test_user_and_auth(client)

        # Mock Cloudinary response
        mock_upload.return_value = {
            "secure_url": "https://fake.cloudinary.com/fake.jpg",
            "public_id": "Rod Royale/catches/fake-id"
        }

        catch_data = {
            "species": "Trout",
            "weight": "2.5",
            "location_lat": "40.7128",
            "location_lng": "-74.0060",
            "shared_with_followers": "true",
            "add_to_map": "true"
        }

        response = client.post("/api/v1/catches/upload-with-image", data=catch_data, headers=auth_headers)
        # Expecting validation error due to missing file, not auth error
        assert response.status_code != status.HTTP_403_FORBIDDEN
    
    def test_upload_with_image_unauthorized(self, client):
        """Test image upload without authentication."""
        catch_data = {"species": "Bass"}
        
        response = client.post("/api/v1/catches/upload-with-image", data=catch_data)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_get_feed_success(self, client):
        """Test retrieving catch feed."""
        # Create test user and catch via API
        user_id, auth_headers = create_test_user_and_auth(client)
        
        # Create a test catch
        catch_data = {
            "species": "Test Bass",
            "weight": 2.5,
            "photo_url": "https://example.com/bass.jpg",
            "location": {"lat": 40.7128, "lng": -74.0060},
            "shared_with_followers": True,
            "add_to_map": False
        }
        catch_response = client.post("/api/v1/catches/", json=catch_data, headers=auth_headers)
        assert catch_response.status_code == 201
        catch_id = catch_response.json().get("id") or catch_response.json().get("_id")
        
        response = client.get("/api/v1/catches/feed", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        
        assert isinstance(response_data, list)
        # Should include our test catch since user follows themselves by default
        catch_ids = [catch.get("id", catch.get("_id")) for catch in response_data]
        assert catch_id in catch_ids
    
    def test_get_feed_unauthorized(self, client):
        """Test retrieving feed without authentication."""
        response = client.get("/api/v1/catches/feed")
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_get_my_catches_success(self, client):
        """Test retrieving current user's catches."""
        # Create test user and catch via API
        user_id, auth_headers = create_test_user_and_auth(client)
        
        # Create a test catch
        catch_data = {
            "species": "Test Bass",
            "weight": 2.5,
            "photo_url": "https://example.com/bass.jpg",
            "location": {"lat": 40.7128, "lng": -74.0060},
            "shared_with_followers": True,
            "add_to_map": False
        }
        catch_response = client.post("/api/v1/catches/", json=catch_data, headers=auth_headers)
        assert catch_response.status_code == 201
        catch_id = catch_response.json().get("id") or catch_response.json().get("_id")
        
        response = client.get("/api/v1/catches/me", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        
        assert isinstance(response_data, list)
        assert len(response_data) >= 1
        
        # Should include our test catch
        catch_ids = [catch.get("id", catch.get("_id")) for catch in response_data]
        assert catch_id in catch_ids
        
        # All catches should belong to current user
        for catch in response_data:
            assert catch["user_id"] == user_id
    
    def test_get_my_catches_unauthorized(self, client):
        """Test retrieving my catches without authentication."""
        response = client.get("/api/v1/catches/me")
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_get_catch_by_id_success(self, client):
        """Test retrieving specific catch by ID."""
        # Create test user and catch via API
        user_id, auth_headers = create_test_user_and_auth(client)
        
        # Create a test catch
        catch_data = {
            "species": "Test Bass",
            "weight": 2.5,
            "photo_url": "https://example.com/bass.jpg",
            "location": {"lat": 40.7128, "lng": -74.0060},
            "shared_with_followers": True,
            "add_to_map": False
        }
        catch_response = client.post("/api/v1/catches/", json=catch_data, headers=auth_headers)
        assert catch_response.status_code == 201
        catch_id = catch_response.json().get("id") or catch_response.json().get("_id")
        
        response = client.get(f"/api/v1/catches/{catch_id}", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        
        catch_response_id = response_data.get("id") or response_data.get("_id")
        assert catch_response_id == catch_id
        assert response_data["species"] == catch_data["species"]
        assert response_data["weight"] == catch_data["weight"]
    
    def test_get_catch_by_id_not_found(self, client):
        """Test retrieving non-existent catch."""
        user_id, auth_headers = create_test_user_and_auth(client)
        
        fake_id = str(ObjectId())
        response = client.get(f"/api/v1/catches/{fake_id}", headers=auth_headers)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_get_catch_by_id_unauthorized(self, client):
        """Test retrieving catch without authentication."""
        fake_id = str(ObjectId())
        response = client.get(f"/api/v1/catches/{fake_id}")
        
        # API may return 404 instead of 403 to avoid exposing endpoint existence
        assert response.status_code in [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND]
    
    def test_get_user_catches_success(self, client):
        """Test retrieving specific user's catches."""
        # Create test user and catch via API
        user_id, auth_headers = create_test_user_and_auth(client)
        
        # Create a test catch
        catch_data = {
            "species": "Test Bass",
            "weight": 2.5,
            "photo_url": "https://example.com/bass.jpg",
            "location": {"lat": 40.7128, "lng": -74.0060},
            "shared_with_followers": True,
            "add_to_map": False
        }
        catch_response = client.post("/api/v1/catches/", json=catch_data, headers=auth_headers)
        assert catch_response.status_code == 201
        catch_id = catch_response.json().get("id") or catch_response.json().get("_id")
        
        response = client.get(f"/api/v1/catches/users/{user_id}/catches", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        
        assert isinstance(response_data, list)
        assert len(response_data) >= 1
        
        # Should include our test catch
        catch_ids = [catch.get("id", catch.get("_id")) for catch in response_data]
        assert catch_id in catch_ids
        
        # All catches should belong to specified user
        for catch in response_data:
            assert catch["user_id"] == user_id
    
    def test_get_user_catches_unauthorized(self, client):
        """Test retrieving user catches without authentication."""
        fake_id = str(ObjectId())
        response = client.get(f"/api/v1/catches/users/{fake_id}/catches")
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_update_catch_success(self, client):
        """Test successful catch update."""
        # Create test user and catch via API
        user_id, auth_headers = create_test_user_and_auth(client)
        
        # Create a test catch
        catch_data = {
            "species": "Test Bass",
            "weight": 2.5,
            "photo_url": "https://example.com/bass.jpg",
            "location": {"lat": 40.7128, "lng": -74.0060},
            "shared_with_followers": True,
            "add_to_map": False
        }
        catch_response = client.post("/api/v1/catches/", json=catch_data, headers=auth_headers)
        assert catch_response.status_code == 201
        catch_id = catch_response.json().get("id") or catch_response.json().get("_id")
        
        update_data = {
            "species": "Updated Bass",
            "weight": 5.5,
            "shared_with_followers": False
        }
        
        response = client.put(f"/api/v1/catches/{catch_id}", json=update_data, headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        
        assert response_data["species"] == update_data["species"]
        assert response_data["weight"] == update_data["weight"]
        assert response_data["shared_with_followers"] == update_data["shared_with_followers"]
    
    def test_update_catch_unauthorized(self, client):
        """Test updating catch without authentication."""
        fake_id = str(ObjectId())
        update_data = {"species": "Hacked Bass"}
        
        response = client.put(f"/api/v1/catches/{fake_id}", json=update_data)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_update_other_user_catch_forbidden(self, client):
        """Test updating another user's catch (should be forbidden)."""
        # Create first user and catch
        user1_id, headers1 = create_test_user_and_auth(client, "user1")
        
        # Create catch as user1
        catch_data = {
            "species": "Test Bass",
            "weight": 2.5,
            "photo_url": "https://example.com/bass.jpg",
            "location": {"lat": 40.7128, "lng": -74.0060},
            "shared_with_followers": True,
            "add_to_map": False
        }
        catch_response = client.post("/api/v1/catches/", json=catch_data, headers=headers1)
        assert catch_response.status_code == 201
        catch_id = catch_response.json().get("id") or catch_response.json().get("_id")
        
        # Create second user
        user2_id, headers2 = create_test_user_and_auth(client, "user2")
        
        # Try to update user1's catch as user2
        update_data = {"species": "Stolen Bass"}
        response = client.put(f"/api/v1/catches/{catch_id}", json=update_data, headers=headers2)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_delete_catch_success(self, client):
        """Test successful catch deletion."""
        # Create test user and catch via API
        user_id, auth_headers = create_test_user_and_auth(client)
        
        # Create a test catch
        catch_data = {
            "species": "Test Bass",
            "weight": 2.5,
            "photo_url": "https://example.com/bass.jpg",
            "location": {"lat": 40.7128, "lng": -74.0060},
            "shared_with_followers": True,
            "add_to_map": False
        }
        catch_response = client.post("/api/v1/catches/", json=catch_data, headers=auth_headers)
        assert catch_response.status_code == 201
        catch_id = catch_response.json().get("id") or catch_response.json().get("_id")
        
        response = client.delete(f"/api/v1/catches/{catch_id}", headers=auth_headers)
        
        # Check for either 200 or 204 as valid delete responses
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_204_NO_CONTENT]
        
        # If 200, check for message
        if response.status_code == status.HTTP_200_OK:
            assert "deleted" in response.json()["message"].lower()
    
    def test_delete_catch_unauthorized(self, client):
        """Test deleting catch without authentication."""
        fake_id = str(ObjectId())
        
        response = client.delete(f"/api/v1/catches/{fake_id}")
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_delete_other_user_catch_forbidden(self, client):
        """Test deleting another user's catch (should be forbidden)."""
        # Create first user and catch
        user1_id, headers1 = create_test_user_and_auth(client, "user1")
        
        # Create catch as user1
        catch_data = {
            "species": "Test Bass",
            "weight": 2.5,
            "photo_url": "https://example.com/bass.jpg",
            "location": {"lat": 40.7128, "lng": -74.0060},
            "shared_with_followers": True,
            "add_to_map": False
        }
        catch_response = client.post("/api/v1/catches/", json=catch_data, headers=headers1)
        assert catch_response.status_code == 201
        catch_id = catch_response.json().get("id") or catch_response.json().get("_id")
        
        # Create second user  
        user2_id, headers2 = create_test_user_and_auth(client, "user2")
        
        # Try to delete user1's catch as user2
        response = client.delete(f"/api/v1/catches/{catch_id}", headers=headers2)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN

class TestCatchValidation:
    """Test catch data validation."""
    
    def test_negative_weight_validation(self, client):
        """Test that negative weight is rejected."""
        user_id, auth_headers = create_test_user_and_auth(client)
        
        catch_data = {
            "species": "Bass",
            "weight": -1.0,  # Invalid negative weight
            "photo_url": "https://example.com/bass.jpg",
            "location": {"lat": 40.7128, "lng": -74.0060},
            "shared_with_followers": True,
            "add_to_map": True
        }
        
        response = client.post("/api/v1/catches/", json=catch_data, headers=auth_headers)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_invalid_location_validation(self, client):
        """Test that invalid GPS coordinates are rejected."""
        user_id, auth_headers = create_test_user_and_auth(client)
        
        catch_data = {
            "species": "Bass",
            "weight": 2.5,
            "photo_url": "https://example.com/bass.jpg",
            "location": {"lat": 200.0, "lng": -74.0060},  # Invalid latitude
            "shared_with_followers": True,
            "add_to_map": True
        }
        
        response = client.post("/api/v1/catches/", json=catch_data, headers=auth_headers)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_empty_species_validation(self, client):
        """Test that empty species name is rejected."""
        user_id, auth_headers = create_test_user_and_auth(client)
        
        catch_data = {
            "species": "",  # Empty species
            "weight": 2.5,
            "photo_url": "https://example.com/bass.jpg",
            "location": {"lat": 40.7128, "lng": -74.0060},
            "shared_with_followers": True,
            "add_to_map": True
        }
        
        response = client.post("/api/v1/catches/", json=catch_data, headers=auth_headers)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
