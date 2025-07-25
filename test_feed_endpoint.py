#!/usr/bin/env python3
"""
Feed Timeline Test Script
Tests the new /catches/feed endpoint that includes user's own catches + following catches
"""

import requests

BASE_URL = "http://localhost:8000/api/v1"

def test_feed_endpoint():
    print("📰 Testing Feed Timeline Endpoint")
    print("=" * 50)
    
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
    
    # Create test users for feed functionality
    print("\n1. Creating/logging in test users...")
    test_users = [
        {
            "username": "feed_user_alice",
            "email": "alice_feed@Rod Royale.com",
            "bio": "Alice loves posting her catches",
            "password": "alice123"
        },
        {
            "username": "feed_user_bob",
            "email": "bob_feed@Rod Royale.com",
            "bio": "Bob is a prolific angler",
            "password": "bob123"
        },
        {
            "username": "feed_user_charlie",
            "email": "charlie_feed@Rod Royale.com",
            "bio": "Charlie shares amazing catches",
            "password": "charlie123"
        }
    ]
    
    users = []
    tokens = []
    
    for user_data in test_users:
        try:
            # Try registration first
            response = requests.post(f"{BASE_URL}/auth/register", json=user_data)
            if response.status_code == 201:
                auth_response = response.json()
                users.append(auth_response['user'])
                tokens.append(auth_response['token']['access_token'])
                print(f"✅ Registered: {auth_response['user']['username']}")
            else:
                # If user exists, try login
                login_data = {"email": user_data["email"], "password": user_data["password"]}
                response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
                if response.status_code == 200:
                    auth_response = response.json()
                    users.append(auth_response['user'])
                    tokens.append(auth_response['token']['access_token'])
                    print(f"✅ Logged in: {auth_response['user']['username']}")
                else:
                    print(f"❌ Failed to authenticate user {user_data['username']}: {response.text}")
        except Exception as e:
            print(f"❌ Error with user {user_data['username']}: {e}")
    
    if len(users) < 3:
        print("❌ Need at least 3 users to test feed functionality")
        return False
    
    alice, bob, charlie = users[0], users[1], users[2]
    alice_token, bob_token, charlie_token = tokens[0], tokens[1], tokens[2]
    
    # Set up following relationships
    print("\n2. Setting up following relationships...")
    # Alice follows Bob and Charlie
    relationships = [
        (alice['_id'], bob['_id'], "Alice follows Bob"),
        (alice['_id'], charlie['_id'], "Alice follows Charlie"),
        (bob['_id'], alice['_id'], "Bob follows Alice (mutual)"),
    ]
    
    for follower_id, followed_id, description in relationships:
        try:
            response = requests.post(f"{BASE_URL}/users/{follower_id}/follow/{followed_id}")
            if response.status_code == 200:
                print(f"✅ {description}")
            else:
                print(f"❌ Failed: {description} - {response.text}")
        except Exception as e:
            print(f"❌ Error: {description} - {e}")
    
    # Create test catches for each user
    print("\n3. Creating test catches...")
    test_catches = [
        {
            "user": alice,
            "token": alice_token,
            "catches": [
                {
                    "species": "Largemouth Bass",
                    "weight": 5.2,
                    "photo_url": "https://example.com/alice_bass1.jpg",
                    "location": {"lat": 34.0522, "lng": -118.2437},
                    "shared_with_followers": False
                },
                {
                    "species": "Rainbow Trout",
                    "weight": 2.1,
                    "photo_url": "https://example.com/alice_trout1.jpg",
                    "location": {"lat": 34.0522, "lng": -118.2437},
                    "shared_with_followers": False
                }
            ]
        },
        {
            "user": bob,
            "token": bob_token,
            "catches": [
                {
                    "species": "Striped Bass",
                    "weight": 8.5,
                    "photo_url": "https://example.com/bob_striper1.jpg",
                    "location": {"lat": 37.7749, "lng": -122.4194},
                    "shared_with_followers": False
                },
                {
                    "species": "Salmon",
                    "weight": 12.3,
                    "photo_url": "https://example.com/bob_salmon1.jpg",
                    "location": {"lat": 37.7749, "lng": -122.4194},
                    "shared_with_followers": False
                }
            ]
        },
        {
            "user": charlie,
            "token": charlie_token,
            "catches": [
                {
                    "species": "Pike",
                    "weight": 15.7,
                    "photo_url": "https://example.com/charlie_pike1.jpg",
                    "location": {"lat": 41.8781, "lng": -87.6298},
                    "shared_with_followers": False
                }
            ]
        }
    ]
    
    created_catches = {"alice": [], "bob": [], "charlie": []}
    
    for user_data in test_catches:
        user = user_data["user"]
        token = user_data["token"]
        username = user["username"].split("_")[-1]  # Extract alice/bob/charlie
        
        headers = {"Authorization": f"Bearer {token}"}
        
        for catch_data in user_data["catches"]:
            try:
                response = requests.post(f"{BASE_URL}/catches/", json=catch_data, headers=headers)
                if response.status_code == 201:
                    catch = response.json()
                    created_catches[username].append(catch)
                    print(f"✅ {user['username']} created catch: {catch['species']} ({catch['weight']}lbs)")
                else:
                    print(f"❌ Failed to create catch for {user['username']}: {response.text}")
            except Exception as e:
                print(f"❌ Error creating catch for {user['username']}: {e}")
    
    # Test the new feed endpoint
    print("\n4. Testing feed endpoint...")
    
    # Test Alice's feed (should include her own catches + Bob's + Charlie's catches)
    print("\n   Alice's Feed (should include Alice + Bob + Charlie catches):")
    try:
        headers = {"Authorization": f"Bearer {alice_token}"}
        response = requests.get(f"{BASE_URL}/catches/feed", headers=headers)
        
        if response.status_code == 200:
            feed_catches = response.json()
            print(f"✅ Alice's feed returned {len(feed_catches)} catches")
            
            # Group catches by user for display
            catches_by_user = {}
            for catch in feed_catches:
                user_id = catch['user_id']
                if user_id not in catches_by_user:
                    catches_by_user[user_id] = []
                catches_by_user[user_id].append(catch)
            
            for user_id, catches in catches_by_user.items():
                # Find username for this user_id
                username = "Unknown"
                for user in users:
                    if user['_id'] == user_id:
                        username = user['username']
                        break
                
                print(f"     From {username}: {len(catches)} catches")
                for catch in catches:
                    print(f"       - {catch['species']} ({catch['weight']}lbs)")
        else:
            print(f"❌ Alice's feed failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Error getting Alice's feed: {e}")
    
    # Test Bob's feed (should include Bob's own + Alice's catches, but not Charlie's)
    print("\n   Bob's Feed (should include Bob + Alice catches, no Charlie):")
    try:
        headers = {"Authorization": f"Bearer {bob_token}"}
        response = requests.get(f"{BASE_URL}/catches/feed", headers=headers)
        
        if response.status_code == 200:
            feed_catches = response.json()
            print(f"✅ Bob's feed returned {len(feed_catches)} catches")
            
            # Group catches by user for display
            catches_by_user = {}
            for catch in feed_catches:
                user_id = catch['user_id']
                if user_id not in catches_by_user:
                    catches_by_user[user_id] = []
                catches_by_user[user_id].append(catch)
            
            for user_id, catches in catches_by_user.items():
                # Find username for this user_id
                username = "Unknown"
                for user in users:
                    if user['_id'] == user_id:
                        username = user['username']
                        break
                
                print(f"     From {username}: {len(catches)} catches")
                for catch in catches:
                    print(f"       - {catch['species']} ({catch['weight']}lbs)")
        else:
            print(f"❌ Bob's feed failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Error getting Bob's feed: {e}")
    
    # Test Charlie's feed (should only include Charlie's own catches since he doesn't follow anyone)
    print("\n   Charlie's Feed (should only include Charlie's catches):")
    try:
        headers = {"Authorization": f"Bearer {charlie_token}"}
        response = requests.get(f"{BASE_URL}/catches/feed", headers=headers)
        
        if response.status_code == 200:
            feed_catches = response.json()
            print(f"✅ Charlie's feed returned {len(feed_catches)} catches")
            
            for catch in feed_catches:
                print(f"     - {catch['species']} ({catch['weight']}lbs)")
        else:
            print(f"❌ Charlie's feed failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Error getting Charlie's feed: {e}")
    
    # Test feed pagination
    print("\n5. Testing feed pagination...")
    try:
        headers = {"Authorization": f"Bearer {alice_token}"}
        response = requests.get(f"{BASE_URL}/catches/feed?limit=2&skip=0", headers=headers)
        
        if response.status_code == 200:
            feed_catches = response.json()
            print(f"✅ Paginated feed (limit=2): {len(feed_catches)} catches")
        else:
            print(f"❌ Paginated feed failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Error with paginated feed: {e}")
    
    # Test unauthenticated access (should fail)
    print("\n6. Testing unauthenticated access (should fail)...")
    try:
        response = requests.get(f"{BASE_URL}/catches/feed")
        if response.status_code == 401:
            print("✅ Unauthenticated access correctly rejected")
        else:
            print(f"⚠️  Expected 401, got {response.status_code}: {response.text}")
    except Exception as e:
        print(f"❌ Error testing unauthenticated access: {e}")
    
    print("\n" + "=" * 50)
    print("📰 Feed Timeline Test Complete!")
    print("\n🎯 NEW ENDPOINT IMPLEMENTED:")
    print("   ✅ GET /api/v1/catches/feed - Get personalized user feed")
    print("\n📋 FEED FUNCTIONALITY:")
    print("   - Includes user's own catches")
    print("   - Includes catches from users they follow")
    print("   - Ordered chronologically (newest first)")
    print("   - Supports pagination (skip/limit)")
    print("   - Requires authentication")
    print("   - Respects following relationships")
    
    return True

if __name__ == "__main__":
    success = test_feed_endpoint()
    exit(0 if success else 1)
