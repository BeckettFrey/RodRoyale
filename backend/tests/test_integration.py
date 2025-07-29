# File: tests/test_integration.py
"""
Integration tests for Rod Royale API
Tests complex workflows and cross-endpoint interactions
"""

from fastapi import status


def create_test_user_and_auth(client, base_suffix=""):
    """Helper function to create a test user and return user_id and auth headers."""
    import random
    import string
    
    # Always generate a unique suffix to avoid conflicts
    unique_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    if base_suffix:
        full_suffix = f"{base_suffix}_{unique_suffix}"
    else:
        full_suffix = unique_suffix
    
    user_data = {
        "username": f"testuser_{full_suffix}",
        "email": f"test_{full_suffix}@example.com",
        "password": "testpassword123",
        "bio": f"Test user {full_suffix}"
    }
    
    # Register user
    register_response = client.post("/api/v1/auth/register", json=user_data)
    assert register_response.status_code == 201
    register_data = register_response.json()
    
    access_token = register_data["token"]["access_token"]
    auth_headers = {"Authorization": f"Bearer {access_token}"}
    
    # Get user ID from /me endpoint
    me_response = client.get("/api/v1/auth/me", headers=auth_headers)
    assert me_response.status_code == 200
    user_id = str(me_response.json()["_id"])
    
    return user_id, auth_headers


def create_test_catch(client, auth_headers, species="Test Bass", weight=5.0, add_to_map=False, shared_with_followers=False):
    """Helper function to create a test catch and return the catch data with normalized ID."""
    catch_data = {
        "species": species,
        "weight": weight,
        "photo_url": "https://example.com/test_fish.jpg",
        "location": {
            "lat": 42.3601,
            "lng": -71.0589
        },
        "shared_with_followers": shared_with_followers,
        "add_to_map": add_to_map
    }
    
    response = client.post("/api/v1/catches/", json=catch_data, headers=auth_headers)
    assert response.status_code == 201
    catch_response = response.json()
    
    # Normalize the ID field - ensure it's available as 'id' for consistent access
    if "_id" in catch_response and "id" not in catch_response:
        catch_response["id"] = catch_response["_id"]
    elif "id" in catch_response and "_id" not in catch_response:
        catch_response["_id"] = catch_response["id"]
    
    return catch_response


class TestUserRegistrationFlow:
    """Test complete user registration and profile setup flow."""
    
    def test_complete_registration_flow(self, client):
        """Test user registration, login, and profile access."""
        import random
        import string
        
        # Generate unique suffix to avoid username conflicts
        unique_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
        
        # Step 1: Register new user
        user_data = {
            "username": f"integration_user_{unique_suffix}",
            "email": f"integration_{unique_suffix}@example.com",
            "password": "secure_password123",
            "bio": "Testing integration flows"
        }
        
        register_response = client.post("/api/v1/auth/register", json=user_data)
        assert register_response.status_code == status.HTTP_201_CREATED
        
        register_data = register_response.json()
        access_token = register_data["token"]["access_token"]
        
        # Step 2: Use token to access protected endpoint
        headers = {"Authorization": f"Bearer {access_token}"}
        profile_response = client.get("/api/v1/auth/me", headers=headers)
        
        assert profile_response.status_code == status.HTTP_200_OK
        profile_data = profile_response.json()
        user_id = str(profile_data["_id"])
        assert profile_data["username"] == user_data["username"]
        assert profile_data["email"] == user_data["email"]
        
        # Step 3: Update profile
        update_data = {"bio": "Updated integration bio"}
        update_response = client.put(f"/api/v1/users/{user_id}", json=update_data, headers=headers)
        
        assert update_response.status_code == status.HTTP_200_OK
        assert update_response.json()["bio"] == update_data["bio"]
        
        # Step 4: Verify changes persist
        verify_response = client.get("/api/v1/auth/me", headers=headers)
        assert verify_response.status_code == status.HTTP_200_OK
        assert verify_response.json()["bio"] == update_data["bio"]

class TestCatchAndPinFlow:
    """Test catch creation with automatic pin generation."""
    
    def test_catch_creation_with_pin(self, client):
        """Test catch creation automatically creates pin when add_to_map is true."""
        # Create test user
        user_id, auth_headers = create_test_user_and_auth(client, "pin_flow")
        
        # Create catch with add_to_map=True
        catch_data = create_test_catch(
            client, 
            auth_headers, 
            species="Integration Bass", 
            weight=6.5, 
            add_to_map=True, 
            shared_with_followers=True
        )
        catch_id = catch_data["id"]
        
        # Verify catch was created by fetching it
        catch_response = client.get(f"/api/v1/catches/{catch_id}", headers=auth_headers)
        assert catch_response.status_code == status.HTTP_200_OK
        catch_result = catch_response.json()
        assert catch_result["species"] == "Integration Bass"
        assert catch_result["weight"] == 6.5
        
        # Verify pin was automatically created by checking pins endpoint
        pins_response = client.get("/api/v1/pins/", headers=auth_headers)
        assert pins_response.status_code == status.HTTP_200_OK
        
        pins_data = pins_response.json()
        # Find pin associated with our catch
        catch_pins = [pin for pin in pins_data if pin.get("catch_id") == catch_id]
        assert len(catch_pins) == 1
        
        pin = catch_pins[0]
        assert pin["location"]["lat"] == 42.3601
        assert pin["location"]["lng"] == -71.0589

class TestSocialFeatures:
    """Test follow/unfollow and feed integration."""
    
    def test_follow_and_feed_integration(self, client):
        """Test following user affects feed content."""
        # Create two test users
        user_id, auth_headers = create_test_user_and_auth(client, "follower")
        target_user_id, user2_headers = create_test_user_and_auth(client, "followed")
        
        # Step 1: Create catch as second user
        catch_data = create_test_catch(
            client,
            user2_headers,
            species="Followed User Bass",
            weight=7.2,
            shared_with_followers=True
        )
        catch_id = catch_data["_id"]
        
        # Step 2: Check feed before following (should not include catch)
        feed_before = client.get("/api/v1/catches/feed", headers=auth_headers)
        assert feed_before.status_code == status.HTTP_200_OK
        
        before_catch_ids = [catch["id"] for catch in feed_before.json()]
        assert catch_id not in before_catch_ids
        
        # Step 3: Follow the second user
        follow_response = client.post(
            f"/api/v1/users/{user_id}/follow/{target_user_id}",
            headers=auth_headers
        )
        assert follow_response.status_code == status.HTTP_200_OK
        
        # Step 4: Check feed after following (should include catch)
        feed_after = client.get("/api/v1/catches/feed", headers=auth_headers)
        assert feed_after.status_code == status.HTTP_200_OK
        
        after_catch_ids = [catch["_id"] for catch in feed_after.json()]
        assert catch_id in after_catch_ids
        
        # Step 5: Unfollow and verify catch disappears from feed
        unfollow_response = client.delete(
            f"/api/v1/users/{user_id}/follow/{target_user_id}",
            headers=auth_headers
        )
        assert unfollow_response.status_code == status.HTTP_200_OK
        
        feed_after_unfollow = client.get("/api/v1/catches/feed", headers=auth_headers)
        assert feed_after_unfollow.status_code == status.HTTP_200_OK
        
        final_catch_ids = [catch["id"] for catch in feed_after_unfollow.json()]
        assert catch_id not in final_catch_ids
        
        final_catch_ids = [catch["id"] for catch in feed_after_unfollow.json()]
        assert catch_id not in final_catch_ids

class TestAccountDeletionIntegration:
    """Test account deletion cascades properly."""
    
    def test_account_deletion_cascade(self, client):
        """Test account deletion removes all associated data and relationships."""
        # Create two test users
        user_id, auth_headers = create_test_user_and_auth(client, "to_delete")
        target_user_id, target_auth_headers = create_test_user_and_auth(client, "target")
        
        # Step 1: Create follow relationship
        follow_response = client.post(
            f"/api/v1/users/{user_id}/follow/{target_user_id}",
            headers=auth_headers
        )
        assert follow_response.status_code == status.HTTP_204_NO_CONTENT

        # Step 2: Create catch with pin
        catch_data = create_test_catch(
            client, 
            auth_headers, 
            species="Deletion Test Bass", 
            weight=4.8, 
            add_to_map=True, 
            shared_with_followers=True
        )
        catch_id = catch_data["id"]
        
        # Step 3: Verify data exists before deletion
        # Check user profile
        profile_response = client.get("/api/v1/auth/me", headers=auth_headers)
        assert profile_response.status_code == status.HTTP_200_OK
        
        # Check catch exists
        catch_response = client.get(f"/api/v1/catches/{catch_id}", headers=auth_headers)
        assert catch_response.status_code == status.HTTP_200_OK
        
        # Check pins exist
        pins_response = client.get("/api/v1/pins/", headers=auth_headers)
        assert pins_response.status_code == status.HTTP_200_OK
        pins_before = pins_response.json()
        user_pins = [pin for pin in pins_before if pin.get("catch_id") == catch_id]
        assert len(user_pins) > 0
        
        # Step 4: Delete account
        delete_response = client.delete("/api/v1/users/me", headers=auth_headers)
        assert delete_response.status_code == status.HTTP_200_OK
        
        # Step 5: Verify user can no longer access their data
        profile_after = client.get("/api/v1/auth/me", headers=auth_headers)
        assert profile_after.status_code == status.HTTP_403_FORBIDDEN
        
        # Verify catch is no longer accessible 
        catch_after = client.get(f"/api/v1/catches/{catch_id}", headers=target_auth_headers)
        assert catch_after.status_code in [status.HTTP_404_NOT_FOUND, status.HTTP_403_FORBIDDEN]

class TestLeaderboardIntegration:
    """Test leaderboard updates with catch creation."""
    
    def test_leaderboard_updates_with_catches(self, client):
        """Test that creating catches updates leaderboard stats."""
        # Create test user
        user_id, auth_headers = create_test_user_and_auth(client, "leaderboard")
        
        # Step 1: Get initial stats (corrected field names)
        initial_stats = client.get("/api/v1/leaderboard/my-stats", headers=auth_headers)
        assert initial_stats.status_code == status.HTTP_200_OK
        initial_data = initial_stats.json()
        initial_count = initial_data["catches_this_month"]
        initial_weight = initial_data["all_time_weight"]
        
        # Step 2: Create new catch
        create_test_catch(
            client, 
            auth_headers, 
            species="Leaderboard Bass", 
            weight=8.5, 
            shared_with_followers=True
        )
        
        # Step 3: Verify stats updated
        updated_stats = client.get("/api/v1/leaderboard/my-stats", headers=auth_headers)
        assert updated_stats.status_code == status.HTTP_200_OK
        updated_data = updated_stats.json()
        
        assert updated_data["catches_this_month"] == initial_count + 1
        assert abs(updated_data["all_time_weight"] - (initial_weight + 8.5)) < 0.01
        
        # Step 4: Verify appears in global leaderboard
        global_board = client.get("/api/v1/leaderboard/global", headers=auth_headers)
        assert global_board.status_code == status.HTTP_200_OK
        
        global_data = global_board.json()
        # Global leaderboard has nested structure
        assert "leaderboard" in global_data
        leaderboard = global_data["leaderboard"]
        
        user_entries = [entry for entry in leaderboard if entry["user_id"] == user_id]
        assert len(user_entries) == 1
        
        user_entry = user_entries[0]
        assert user_entry["catches_this_month"] == initial_count + 1
        assert abs(user_entry["all_time_weight"] - (initial_weight + 8.5)) < 0.01

class TestPermissionsIntegration:
    """Test permission checks across different endpoints."""
    
    def test_user_can_only_modify_own_content(self, client):
        """Test that users can only modify their own catches and pins."""
        # Create two users
        user_id1, user1_headers = create_test_user_and_auth(client, "owner")
        user_id2, user2_headers = create_test_user_and_auth(client, "other")
        
        # User 1 creates a catch with pin
        catch_data = create_test_catch(
            client, 
            user1_headers, 
            species="Permission Test Bass", 
            weight=5.0, 
            add_to_map=True
        )
        catch_id = catch_data["id"]
        
        # Get the pin created with the catch
        pins_response = client.get("/api/v1/pins/", headers=user1_headers)
        assert pins_response.status_code == status.HTTP_200_OK
        pins = pins_response.json()
        user_pins = [pin for pin in pins if pin.get("catch_id") == catch_id]
        assert len(user_pins) == 1
        pin_id = user_pins[0]["id"]
        
        # User 1 should be able to modify their own content
        catch_update = client.put(f"/api/v1/catches/{catch_id}", 
                                json={"species": "Updated Bass"}, 
                                headers=user1_headers)
        assert catch_update.status_code == status.HTTP_200_OK
        
        pin_update = client.put(f"/api/v1/pins/{pin_id}", 
                              json={"visibility": "private"}, 
                              headers=user1_headers)
        assert pin_update.status_code == status.HTTP_200_OK
        
        # User 2 should NOT be able to modify user 1's content
        catch_hack = client.put(f"/api/v1/catches/{catch_id}", 
                              json={"species": "Hacked Bass"}, 
                              headers=user2_headers)
        assert catch_hack.status_code == status.HTTP_403_FORBIDDEN
        
        pin_hack = client.put(f"/api/v1/pins/{pin_id}", 
                            json={"visibility": "public"}, 
                            headers=user2_headers)
        assert pin_hack.status_code == status.HTTP_403_FORBIDDEN
        
        # User 2 should NOT be able to delete user 1's content
        catch_delete = client.delete(f"/api/v1/catches/{catch_id}", headers=user2_headers)
        assert catch_delete.status_code == status.HTTP_403_FORBIDDEN
        
        pin_delete = client.delete(f"/api/v1/pins/{pin_id}", headers=user2_headers)
        assert pin_delete.status_code == status.HTTP_403_FORBIDDEN

class TestDataConsistency:
    """Test data consistency across operations."""
    
    def test_catch_deletion_removes_associated_pin(self, client):
        """Test that deleting a catch also removes its associated pin."""
        # Create test user
        user_id, auth_headers = create_test_user_and_auth(client, "consistency")
        
        # Create catch with pin
        catch_data = create_test_catch(
            client, 
            auth_headers, 
            species="Consistency Bass", 
            weight=5.2, 
            add_to_map=True, 
            shared_with_followers=True
        )
        catch_id = catch_data["id"]
        
        # Verify pin was created
        pins_before = client.get("/api/v1/pins/", headers=auth_headers)
        assert pins_before.status_code == status.HTTP_200_OK
        pins_before_data = pins_before.json()
        catch_pins_before = [pin for pin in pins_before_data if pin.get("catch_id") == catch_id]
        assert len(catch_pins_before) == 1
        
        # Delete catch
        delete_response = client.delete(f"/api/v1/catches/{catch_id}", headers=auth_headers)
        assert delete_response.status_code == status.HTTP_200_OK
        
        # Verify pin was also deleted  
        pins_after = client.get("/api/v1/pins/", headers=auth_headers)
        assert pins_after.status_code == status.HTTP_200_OK
        pins_after_data = pins_after.json()
        catch_pins_after = [pin for pin in pins_after_data if pin.get("catch_id") == catch_id]
        assert len(catch_pins_after) == 0
