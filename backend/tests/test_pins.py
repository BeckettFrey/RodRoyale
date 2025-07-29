# File: tests/test_pins.py
"""
Pin management endpoint tests for Rod Royale API - Converted to synchronous API-based tests
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
    register_response = client.post("/api/v1/auth/register", json=user_data)
    assert register_response.status_code == status.HTTP_201_CREATED
    user_id = register_response.json()["user"]["_id"]  # Get user_id from registration
    
    # Login to get token
    login_data = {
        "email": user_data["email"],
        "password": user_data["password"]
    }
    
    login_response = client.post("/api/v1/auth/login", json=login_data)
    assert login_response.status_code == status.HTTP_200_OK
    
    login_result = login_response.json()
    token = login_result["token"]["access_token"]
    
    return user_id, {"Authorization": f"Bearer {token}"}

def create_test_catch(client, auth_headers, shared_with_followers=False):
    """Helper function to create a test catch for pin testing"""
    catch_data = {
        "species": "Bass",
        "weight": 2.5,
        "photo_url": "https://example.com/bass.jpg",
        "location": {"lat": 40.7128, "lng": -74.0060},
        "shared_with_followers": shared_with_followers,
        "add_to_map": False
    }
    
    response = client.post("/api/v1/catches/", json=catch_data, headers=auth_headers)
    assert response.status_code == status.HTTP_201_CREATED
    
    catch_response = response.json()
    return catch_response["_id"] if "_id" in catch_response else catch_response["id"]

class TestPinEndpoints:
    """Test pin management endpoints."""
    
    def test_create_pin_success(self, client):
        """Test successful pin creation."""
        user_id, auth_headers = create_test_user_and_auth(client, "create_pin")
        catch_id = create_test_catch(client, auth_headers)
        
        pin_data = {
            "catch_id": catch_id,
            "location": {
                "lat": 40.7128,
                "lng": -74.0060
            },
            "visibility": "public"
        }
        
        response = client.post("/api/v1/pins/", json=pin_data, headers=auth_headers)
        assert response.status_code == status.HTTP_201_CREATED
        
        response_data = response.json()
        assert response_data["location"]["lat"] == pin_data["location"]["lat"]
        assert response_data["location"]["lng"] == pin_data["location"]["lng"]
        assert response_data["visibility"] == pin_data["visibility"]
        assert response_data["catch_id"] == catch_id
        # Check for either id or _id field
        assert ("id" in response_data) or ("_id" in response_data)
    
    def test_create_pin_unauthorized(self, client):
        """Test pin creation without authentication."""
        user_id, auth_headers = create_test_user_and_auth(client, "unauthorized_test")
        catch_id = create_test_catch(client, auth_headers)
        
        pin_data = {
            "catch_id": catch_id,
            "location": {
                "lat": 40.7128,
                "lng": -74.0060
            },
            "visibility": "public"
        }
        
        response = client.post("/api/v1/pins/", json=pin_data)
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_create_pin_missing_fields(self, client):
        """Test pin creation with missing required fields."""
        user_id, auth_headers = create_test_user_and_auth(client, "missing_fields")
        
        pin_data = {
            "location": {
                "lat": 40.7128,
                "lng": -74.0060
            }
            # Missing catch_id and visibility
        }
        
        response = client.post("/api/v1/pins/", json=pin_data, headers=auth_headers)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_create_pin_invalid_location(self, client):
        """Test pin creation with invalid location coordinates."""
        user_id, auth_headers = create_test_user_and_auth(client, "invalid_location")
        catch_id = create_test_catch(client, auth_headers)
        
        pin_data = {
            "catch_id": catch_id,
            "location": {
                "lat": 91.0,  # Invalid latitude (> 90)
                "lng": -74.0060
            },
            "visibility": "public"
        }
        
        response = client.post("/api/v1/pins/", json=pin_data, headers=auth_headers)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_get_pins_success(self, client):
        """Test successful pin retrieval."""
        user_id, auth_headers = create_test_user_and_auth(client, "get_pins")
        catch_id = create_test_catch(client, auth_headers)
        
        pin_data = {
            "catch_id": catch_id,
            "location": {
                "lat": 40.7128,
                "lng": -74.0060
            },
            "visibility": "public"
        }
        
        # Create a pin first
        create_response = client.post("/api/v1/pins/", json=pin_data, headers=auth_headers)
        assert create_response.status_code == status.HTTP_201_CREATED
        
        # Get pins
        response = client.get("/api/v1/pins/", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        
        pins = response.json()
        assert isinstance(pins, list)
        assert len(pins) >= 1
        
        # Check the created pin is in the response
        pin_found = False
        for pin in pins:
            if pin["catch_id"] == catch_id:
                pin_found = True
                assert pin["location"]["lat"] == pin_data["location"]["lat"]
                assert pin["location"]["lng"] == pin_data["location"]["lng"]
                assert pin["visibility"] == pin_data["visibility"]
                break
        assert pin_found, "Created pin not found in pins list"
    
    def test_get_pins_unauthorized(self, client):
        """Test pin retrieval without authentication."""
        response = client.get("/api/v1/pins/")
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_get_pins_with_multiple_visibilities(self, client):
        """Test pin retrieval shows correct visibility for user's own pins."""
        user_id, auth_headers = create_test_user_and_auth(client, "visibility_filter")
        
        # Create catches for pins
        catch1_id = create_test_catch(client, auth_headers)
        catch2_id = create_test_catch(client, auth_headers)
        
        # Create public pin
        public_pin_data = {
            "catch_id": catch1_id,
            "location": {"lat": 40.7128, "lng": -74.0060},
            "visibility": "public"
        }
        
        # Create private pin
        private_pin_data = {
            "catch_id": catch2_id,
            "location": {"lat": 41.7128, "lng": -75.0060},
            "visibility": "private"
        }
        
        # Create both pins
        client.post("/api/v1/pins/", json=public_pin_data, headers=auth_headers)
        client.post("/api/v1/pins/", json=private_pin_data, headers=auth_headers)
        
        # Get all pins (user should see their own pins regardless of visibility)
        response = client.get("/api/v1/pins/", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        
        pins = response.json()
        assert isinstance(pins, list)
        assert len(pins) >= 2
        
        # Check that both pins are returned (user can see their own private pins)
        found_pins = {}
        for pin in pins:
            if pin["catch_id"] in [catch1_id, catch2_id]:
                found_pins[pin["catch_id"]] = pin["visibility"]
        
        assert catch1_id in found_pins
        assert catch2_id in found_pins
        assert found_pins[catch1_id] == "public"
        assert found_pins[catch2_id] == "private"
    
    def test_update_pin_success(self, client):
        """Test successful pin update."""
        user_id, auth_headers = create_test_user_and_auth(client, "update_pin")
        catch_id = create_test_catch(client, auth_headers)
        
        pin_data = {
            "catch_id": catch_id,
            "location": {"lat": 40.7128, "lng": -74.0060},
            "visibility": "public"
        }
        
        # Create pin
        create_response = client.post("/api/v1/pins/", json=pin_data, headers=auth_headers)
        assert create_response.status_code == status.HTTP_201_CREATED
        pin = create_response.json()
        pin_id = pin.get("id", pin.get("_id"))
        
        # Update pin
        update_data = {
            "visibility": "private",
            "location": {"lat": 41.7128, "lng": -75.0060}
        }
        
        response = client.put(f"/api/v1/pins/{pin_id}", json=update_data, headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        
        updated_pin = response.json()
        assert updated_pin["visibility"] == "private"
        assert updated_pin["location"]["lat"] == 41.7128
        assert updated_pin["location"]["lng"] == -75.0060
    
    def test_update_pin_unauthorized(self, client):
        """Test pin update without authentication."""
        user_id, auth_headers = create_test_user_and_auth(client, "update_unauthorized")
        catch_id = create_test_catch(client, auth_headers)
        
        pin_data = {
            "catch_id": catch_id,
            "location": {"lat": 40.7128, "lng": -74.0060},
            "visibility": "public"
        }
        
        # Create pin
        create_response = client.post("/api/v1/pins/", json=pin_data, headers=auth_headers)
        assert create_response.status_code == status.HTTP_201_CREATED
        pin = create_response.json()
        pin_id = pin.get("id", pin.get("_id"))
        update_data = {"visibility": "private"}
        
        response = client.put(f"/api/v1/pins/{pin_id}", json=update_data)
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_update_pin_not_found(self, client):
        """Test updating non-existent pin."""
        user_id, auth_headers = create_test_user_and_auth(client, "update_not_found")
        fake_id = str(ObjectId())
        update_data = {"visibility": "private"}
        
        response = client.put(f"/api/v1/pins/{fake_id}", json=update_data, headers=auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_update_other_user_pin_forbidden(self, client):
        """Test updating another user's pin."""
        user_id1, auth_headers1 = create_test_user_and_auth(client, "update_owner")
        user_id2, auth_headers2 = create_test_user_and_auth(client, "update_other")
        catch_id = create_test_catch(client, auth_headers1)
        
        pin_data = {
            "catch_id": catch_id,
            "location": {"lat": 40.7128, "lng": -74.0060},
            "visibility": "public"
        }
        
        # User 1 creates pin
        create_response = client.post("/api/v1/pins/", json=pin_data, headers=auth_headers1)
        assert create_response.status_code == status.HTTP_201_CREATED
        pin = create_response.json()
        pin_id = pin.get("id", pin.get("_id"))
        
        # User 2 tries to update pin
        update_data = {"visibility": "private"}
        response = client.put(f"/api/v1/pins/{pin_id}", json=update_data, headers=auth_headers2)
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_delete_pin_success(self, client):
        """Test successful pin deletion."""
        user_id, auth_headers = create_test_user_and_auth(client, "delete_pin")
        catch_id = create_test_catch(client, auth_headers)
        
        pin_data = {
            "catch_id": catch_id,
            "location": {"lat": 40.7128, "lng": -74.0060},
            "visibility": "public"
        }
        
        # Create pin
        create_response = client.post("/api/v1/pins/", json=pin_data, headers=auth_headers)
        assert create_response.status_code == status.HTTP_201_CREATED
        pin = create_response.json()
        pin_id = pin.get("id", pin.get("_id"))
        
        # Delete pin
        response = client.delete(f"/api/v1/pins/{pin_id}", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        
        # Verify pin is deleted by checking it's not in the pins list
        get_response = client.get("/api/v1/pins/", headers=auth_headers)
        assert get_response.status_code == status.HTTP_200_OK
        pins = get_response.json()
        
        # Check that the deleted pin is not in the list
        pin_found = False
        for pin in pins:
            if pin.get("id") == pin_id or pin.get("_id") == pin_id:
                pin_found = True
                break
        assert not pin_found, "Deleted pin should not appear in pins list"
    
    def test_delete_pin_unauthorized(self, client):
        """Test pin deletion without authentication."""
        user_id, auth_headers = create_test_user_and_auth(client, "delete_unauthorized")
        catch_id = create_test_catch(client, auth_headers)
        
        pin_data = {
            "catch_id": catch_id,
            "location": {"lat": 40.7128, "lng": -74.0060},
            "visibility": "public"
        }
        
        # Create pin
        create_response = client.post("/api/v1/pins/", json=pin_data, headers=auth_headers)
        assert create_response.status_code == status.HTTP_201_CREATED
        pin = create_response.json()
        pin_id = pin.get("id", pin.get("_id"))
        response = client.delete(f"/api/v1/pins/{pin_id}")
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_delete_pin_not_found(self, client):
        """Test deleting non-existent pin."""
        user_id, auth_headers = create_test_user_and_auth(client, "delete_not_found")
        fake_id = str(ObjectId())
        
        response = client.delete(f"/api/v1/pins/{fake_id}", headers=auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_delete_other_user_pin_forbidden(self, client):
        """Test deleting another user's pin."""
        user_id1, auth_headers1 = create_test_user_and_auth(client, "delete_owner")
        user_id2, auth_headers2 = create_test_user_and_auth(client, "delete_other")
        catch_id = create_test_catch(client, auth_headers1)
        
        pin_data = {
            "catch_id": catch_id,
            "location": {"lat": 40.7128, "lng": -74.0060},
            "visibility": "public"
        }
        
        # User 1 creates pin
        create_response = client.post("/api/v1/pins/", json=pin_data, headers=auth_headers1)
        assert create_response.status_code == status.HTTP_201_CREATED
        pin = create_response.json()
        pin_id = pin.get("id", pin.get("_id"))
        
        # User 2 tries to delete pin
        response = client.delete(f"/api/v1/pins/{pin_id}", headers=auth_headers2)
        assert response.status_code == status.HTTP_403_FORBIDDEN

class TestPinVisibility:
    """Test pin visibility and access controls."""
    
    def test_public_pins_visible_to_all(self, client):
        """Test that public pins are visible to all authenticated users."""
        user_id1, auth_headers1 = create_test_user_and_auth(client, "public_owner")
        user_id2, auth_headers2 = create_test_user_and_auth(client, "public_viewer")
        catch_id = create_test_catch(client, auth_headers1, shared_with_followers=False)  # Make catch publicly accessible
        
        pin_data = {
            "catch_id": catch_id,
            "location": {"lat": 40.7128, "lng": -74.0060},
            "visibility": "public"
        }
        
        # User 1 creates public pin
        create_response = client.post("/api/v1/pins/", json=pin_data, headers=auth_headers1)
        assert create_response.status_code == status.HTTP_201_CREATED
        
        # User 2 should see the public pin
        response = client.get("/api/v1/pins/", headers=auth_headers2)
        assert response.status_code == status.HTTP_200_OK
        
        pins = response.json()
        public_pin_found = False
        for pin in pins:
            if pin["catch_id"] == catch_id and pin["visibility"] == "public":
                public_pin_found = True
                break
        assert public_pin_found, "Public pin should be visible to other users"
    
    def test_private_pins_only_visible_to_owner(self, client):
        """Test that private pins are only visible to the owner."""
        user_id1, auth_headers1 = create_test_user_and_auth(client, "private_owner")
        user_id2, auth_headers2 = create_test_user_and_auth(client, "private_viewer")
        catch_id = create_test_catch(client, auth_headers1)
        
        pin_data = {
            "catch_id": catch_id,
            "location": {"lat": 40.7128, "lng": -74.0060},
            "visibility": "private"
        }
        
        # User 1 creates private pin
        create_response = client.post("/api/v1/pins/", json=pin_data, headers=auth_headers1)
        assert create_response.status_code == status.HTTP_201_CREATED
        
        # User 1 should see their own private pin
        response1 = client.get("/api/v1/pins/", headers=auth_headers1)
        assert response1.status_code == status.HTTP_200_OK
        pins1 = response1.json()
        
        private_pin_found_owner = False
        for pin in pins1:
            if pin["catch_id"] == catch_id and pin["visibility"] == "private":
                private_pin_found_owner = True
                break
        assert private_pin_found_owner, "Owner should see their own private pin"
        
        # User 2 should not see the private pin
        response2 = client.get("/api/v1/pins/", headers=auth_headers2)
        assert response2.status_code == status.HTTP_200_OK
        pins2 = response2.json()
        
        private_pin_found_other = False
        for pin in pins2:
            if pin["catch_id"] == catch_id and pin["visibility"] == "private":
                private_pin_found_other = True
                break
        assert not private_pin_found_other, "Private pin should not be visible to other users"

class TestPinValidation:
    """Test pin data validation."""
    
    def test_invalid_visibility_value(self, client):
        """Test pin creation with invalid visibility value."""
        user_id, auth_headers = create_test_user_and_auth(client, "invalid_visibility")
        catch_id = create_test_catch(client, auth_headers)
        
        pin_data = {
            "catch_id": catch_id,
            "location": {"lat": 40.7128, "lng": -74.0060},
            "visibility": "invalid_value"
        }
        
        response = client.post("/api/v1/pins/", json=pin_data, headers=auth_headers)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_latitude_bounds_validation(self, client):
        """Test latitude bounds validation."""
        user_id, auth_headers = create_test_user_and_auth(client, "invalid_lat")
        catch_id = create_test_catch(client, auth_headers)
        
        # Test latitude > 90
        pin_data = {
            "catch_id": catch_id,
            "location": {"lat": 91.0, "lng": -74.0060},
            "visibility": "public"
        }
        
        response = client.post("/api/v1/pins/", json=pin_data, headers=auth_headers)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_longitude_bounds_validation(self, client):
        """Test longitude bounds validation."""
        user_id, auth_headers = create_test_user_and_auth(client, "invalid_lng")
        catch_id = create_test_catch(client, auth_headers)
        
        # Test longitude > 180
        pin_data = {
            "catch_id": catch_id,
            "location": {"lat": 40.7128, "lng": 181.0},
            "visibility": "public"
        }
        
        response = client.post("/api/v1/pins/", json=pin_data, headers=auth_headers)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
