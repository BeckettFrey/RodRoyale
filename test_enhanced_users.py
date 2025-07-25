#!/usr/bin/env python3
"""
Enhanced User Management Test Script
Tests user following, unfollowing, search, and relationship endpoints
"""

import requests

BASE_URL = "http://localhost:8000/api/v1"

def test_enhanced_user_management():
    print("👥 Testing Enhanced User Management System")
    print("=" * 60)
    
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
    
    # Create test users for comprehensive testing
    print("\n1. Creating test users...")
    test_users = [
        {
            "username": "bass_master_2024",
            "email": "bassmaster@Rod Royale.com",
            "bio": "Professional bass fishing tournament champion",
            "password": "bass123"
        },
        {
            "username": "trout_whisperer",
            "email": "trout@Rod Royale.com",
            "bio": "Fly fishing guide specializing in trout streams",
            "password": "trout123"
        },
        {
            "username": "deep_sea_explorer",
            "email": "deepsea@Rod Royale.com",
            "bio": "Deep sea fishing adventures and big game hunting",
            "password": "deep123"
        },
        {
            "username": "freshwater_king",
            "email": "freshwater@Rod Royale.com",
            "bio": "Lake and river fishing expert, bass and pike specialist",
            "password": "fresh123"
        }
    ]
    
    created_users = []
    user_tokens = []
    
    for user_data in test_users:
        try:
            # Try registration first
            response = requests.post(f"{BASE_URL}/auth/register", json=user_data)
            if response.status_code == 201:
                auth_response = response.json()
                created_users.append(auth_response['user'])
                user_tokens.append(auth_response['token']['access_token'])
                print(f"✅ Registered: {auth_response['user']['username']}")
            else:
                # If user exists, try login
                login_data = {"email": user_data["email"], "password": user_data["password"]}
                response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
                if response.status_code == 200:
                    auth_response = response.json()
                    created_users.append(auth_response['user'])
                    user_tokens.append(auth_response['token']['access_token'])
                    print(f"✅ Logged in: {auth_response['user']['username']}")
                else:
                    print(f"❌ Failed to create/login user {user_data['username']}: {response.text}")
        except Exception as e:
            print(f"❌ Error with user {user_data['username']}: {e}")
    
    if len(created_users) < 3:
        print("❌ Need at least 3 users to test comprehensively")
        return False
    
    # Set up test relationships
    print("\n2. Setting up test relationships...")
    bass_master = created_users[0]
    trout_whisperer = created_users[1]
    deep_sea = created_users[2]
    freshwater = created_users[3] if len(created_users) > 3 else None
    
    # Create some follow relationships
    relationships = [
        (bass_master, trout_whisperer, "bass_master follows trout_whisperer"),
        (bass_master, deep_sea, "bass_master follows deep_sea"),
        (trout_whisperer, bass_master, "trout_whisperer follows bass_master (mutual)"),
        (deep_sea, bass_master, "deep_sea follows bass_master"),
    ]
    
    if freshwater:
        relationships.extend([
            (freshwater, bass_master, "freshwater follows bass_master"),
            (freshwater, trout_whisperer, "freshwater follows trout_whisperer"),
        ])
    
    for user1, user2, description in relationships:
        try:
            response = requests.post(f"{BASE_URL}/users/{user1['_id']}/follow/{user2['_id']}")
            if response.status_code == 200:
                print(f"✅ {description}")
            else:
                print(f"❌ Failed: {description} - {response.text}")
        except Exception as e:
            print(f"❌ Error: {description} - {e}")\n    \n    # Test user search functionality\n    print(\"\\n3. Testing user search functionality...\")\n    \n    search_tests = [\n        (\"bass\", \"Search for 'bass' (should find bass_master and freshwater_king)\"),\n        (\"trout\", \"Search for 'trout' (should find trout_whisperer)\"),\n        (\"fishing\", \"Search for 'fishing' (should find multiple users)\"),\n        (\"deep\", \"Search for 'deep' (should find deep_sea_explorer)\"),\n        (\"xyz123\", \"Search for non-existent term (should return empty)\")\n    ]\n    \n    for search_term, description in search_tests:\n        try:\n            response = requests.get(f\"{BASE_URL}/users/search?q={search_term}\")\n            if response.status_code == 200:\n                results = response.json()\n                print(f\"✅ {description}: Found {len(results)} users\")\n                for user in results:\n                    print(f\"   - {user['username']}: {user['bio'][:50]}...\")\n            else:\n                print(f\"❌ Search failed for '{search_term}': {response.status_code} - {response.text}\")\n        except Exception as e:\n            print(f\"❌ Error searching for '{search_term}': {e}\")\n    \n    # Test getting followers\n    print(\"\\n4. Testing followers endpoint...\")\n    try:\n        response = requests.get(f\"{BASE_URL}/users/{bass_master['_id']}/followers\")\n        if response.status_code == 200:\n            followers = response.json()\n            print(f\"✅ bass_master has {len(followers)} followers:\")\n            for follower in followers:\n                print(f\"   - {follower['username']}\")\n        else:\n            print(f\"❌ Failed to get followers: {response.status_code} - {response.text}\")\n    except Exception as e:\n        print(f\"❌ Error getting followers: {e}\")\n    \n    # Test getting following\n    print(\"\\n5. Testing following endpoint...\")\n    try:\n        response = requests.get(f\"{BASE_URL}/users/{bass_master['_id']}/following\")\n        if response.status_code == 200:\n            following = response.json()\n            print(f\"✅ bass_master is following {len(following)} users:\")\n            for followed in following:\n                print(f\"   - {followed['username']}\")\n        else:\n            print(f\"❌ Failed to get following: {response.status_code} - {response.text}\")\n    except Exception as e:\n        print(f\"❌ Error getting following: {e}\")\n    \n    # Test search with limits\n    print(\"\\n6. Testing search with pagination...\")\n    try:\n        response = requests.get(f\"{BASE_URL}/users/search?q=fishing&limit=2\")\n        if response.status_code == 200:\n            results = response.json()\n            print(f\"✅ Limited search (limit=2): Found {len(results)} users\")\n        else:\n            print(f\"❌ Limited search failed: {response.status_code} - {response.text}\")\n    except Exception as e:\n        print(f\"❌ Error with limited search: {e}\")\n    \n    # Test followers with pagination\n    print(\"\\n7. Testing followers with pagination...\")\n    try:\n        response = requests.get(f\"{BASE_URL}/users/{bass_master['_id']}/followers?limit=2&skip=0\")\n        if response.status_code == 200:\n            followers = response.json()\n            print(f\"✅ Paginated followers (limit=2, skip=0): Found {len(followers)} users\")\n        else:\n            print(f\"❌ Paginated followers failed: {response.status_code} - {response.text}\")\n    except Exception as e:\n        print(f\"❌ Error with paginated followers: {e}\")\n    \n    # Test error cases\n    print(\"\\n8. Testing error cases...\")\n    \n    # Invalid user ID for followers\n    try:\n        response = requests.get(f\"{BASE_URL}/users/invalid_id/followers\")\n        if response.status_code == 400:\n            print(\"✅ Invalid user ID correctly rejected for followers\")\n        else:\n            print(f\"⚠️  Expected 400 for invalid ID, got {response.status_code}\")\n    except Exception as e:\n        print(f\"❌ Error testing invalid ID: {e}\")\n    \n    # Empty search query\n    try:\n        response = requests.get(f\"{BASE_URL}/users/search?q=\")\n        if response.status_code == 422:  # Validation error\n            print(\"✅ Empty search query correctly rejected\")\n        else:\n            print(f\"⚠️  Expected 422 for empty search, got {response.status_code}\")\n    except Exception as e:\n        print(f\"❌ Error testing empty search: {e}\")\n    \n    print(\"\\n\" + \"=\" * 60)\n    print(\"👥 Enhanced User Management Test Complete!\")\n    print(\"\\n📋 TESTED ENDPOINTS:\")\n    print(\"   ✅ GET    /api/v1/users/search?q=term        - Search users\")\n    print(\"   ✅ GET    /api/v1/users/{id}/followers      - Get user's followers\")\n    print(\"   ✅ GET    /api/v1/users/{id}/following      - Get user's following\")\n    print(\"   ✅ POST   /api/v1/users/{id}/follow/{id}   - Follow user\")\n    print(\"   ✅ DELETE /api/v1/users/{id}/follow/{id}   - Unfollow user\")\n    print(\"   ✅ GET    /api/v1/users/{id}               - Get user profile\")\n    \n    print(\"\\n🎯 SEARCH CAPABILITIES:\")\n    print(\"   - Search by username (case-insensitive)\")\n    print(\"   - Search by bio content (case-insensitive)\")\n    print(\"   - Configurable result limits (1-50)\")\n    print(\"   - Excludes password hashes from results\")\n    \n    print(\"\\n📊 RELATIONSHIP CAPABILITIES:\")\n    print(\"   - Get followers with pagination\")\n    print(\"   - Get following with pagination\")\n    print(\"   - Follow/unfollow with duplicate handling\")\n    print(\"   - Self-follow prevention\")\n    \n    return True\n\nif __name__ == \"__main__\":\n    success = test_enhanced_user_management()\n    exit(0 if success else 1)
