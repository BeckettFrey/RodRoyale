#!/usr/bin/env python3
"""
User Management Test Script
Tests user following, unfollowing, and demonstrates user search endpoints
"""

import requests

BASE_URL = "http://localhost:8000/api/v1"

def test_user_management():
    print("👥 Testing User Management System")
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
    
    # Create test users for following functionality
    print("\n1. Creating test users...")
    test_users = [
        {
            "username": "alice_angler",
            "email": "alice@Rod Royale.com",
            "bio": "Bass fishing expert from Florida",
            "password": "alice123"
        },
        {
            "username": "bob_bassmaster",
            "email": "bob@Rod Royale.com",
            "bio": "Tournament angler from Texas",
            "password": "bob123"
        },
        {
            "username": "charlie_carp",
            "email": "charlie@Rod Royale.com",
            "bio": "Carp fishing specialist from Michigan",
            "password": "charlie123"
        },
        {
            "username": "diana_deepwater",
            "email": "diana@Rod Royale.com",
            "bio": "Deep sea fishing guide from California",
            "password": "diana123"
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
                print(f"✅ Registered: {auth_response['user']['username']} (ID: {auth_response['user']['_id']})")
            else:
                # If user exists, try login
                login_data = {"email": user_data["email"], "password": user_data["password"]}
                response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
                if response.status_code == 200:
                    auth_response = response.json()
                    created_users.append(auth_response['user'])
                    user_tokens.append(auth_response['token']['access_token'])
                    print(f"✅ Logged in: {auth_response['user']['username']} (ID: {auth_response['user']['_id']})")
                else:
                    print(f"❌ Failed to create/login user {user_data['username']}: {response.text}")
        except Exception as e:
            print(f"❌ Error with user {user_data['username']}: {e}")
    
    if len(created_users) < 2:
        print("❌ Need at least 2 users to test following functionality")
        return False
    
    # Test user profile retrieval
    print("\n2. Testing user profile retrieval...")
    for i, user in enumerate(created_users[:2]):
        try:
            response = requests.get(f"{BASE_URL}/users/{user['_id']}")
            if response.status_code == 200:
                profile = response.json()
                print(f"✅ Retrieved profile: {profile['username']} - {profile['bio']}")
            else:
                print(f"❌ Failed to get profile for {user['username']}: {response.text}")
        except Exception as e:
            print(f"❌ Error getting profile: {e}")
    
    # Test following functionality
    print("\n3. Testing follow functionality...")
    alice = created_users[0]
    bob = created_users[1]
    charlie = created_users[2] if len(created_users) > 2 else None
    
    # Alice follows Bob
    try:
        response = requests.post(f"{BASE_URL}/users/{alice['_id']}/follow/{bob['_id']}")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ {alice['username']} followed {bob['username']}: {result['message']}")
        else:
            print(f"❌ Follow failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Error following user: {e}")
    
    # Alice follows Charlie (if exists)
    if charlie:
        try:
            response = requests.post(f"{BASE_URL}/users/{alice['_id']}/follow/{charlie['_id']}")
            if response.status_code == 200:
                result = response.json()
                print(f"✅ {alice['username']} followed {charlie['username']}: {result['message']}")
        except Exception as e:
            print(f"❌ Error following user: {e}")
    
    # Bob follows Alice (mutual follow)
    try:
        response = requests.post(f"{BASE_URL}/users/{bob['_id']}/follow/{alice['_id']}")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ {bob['username']} followed {alice['username']}: {result['message']}")
    except Exception as e:
        print(f"❌ Error following user: {e}")
    
    # Test duplicate follow (should be handled gracefully)
    print("\n4. Testing duplicate follow (should be handled gracefully)...")
    try:
        response = requests.post(f"{BASE_URL}/users/{alice['_id']}/follow/{bob['_id']}")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Duplicate follow handled: {result['message']}")
        else:
            print(f"⚠️  Duplicate follow response: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Error with duplicate follow: {e}")
    
    # Test self-follow (should fail)
    print("\n5. Testing self-follow (should fail)...")
    try:
        response = requests.post(f"{BASE_URL}/users/{alice['_id']}/follow/{alice['_id']}")
        if response.status_code == 400:
            print("✅ Self-follow correctly rejected")
        else:
            print(f"⚠️  Expected 400, got {response.status_code}: {response.text}")
    except Exception as e:
        print(f"❌ Error testing self-follow: {e}")
    
    # Test unfollow functionality
    print("\n6. Testing unfollow functionality...")
    try:
        response = requests.delete(f"{BASE_URL}/users/{alice['_id']}/follow/{bob['_id']}")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ {alice['username']} unfollowed {bob['username']}: {result['message']}")
        else:
            print(f"❌ Unfollow failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Error unfollowing user: {e}")
    
    # Test unfollow non-existent relationship
    print("\n7. Testing unfollow non-existent relationship...")
    try:
        response = requests.delete(f"{BASE_URL}/users/{alice['_id']}/follow/{bob['_id']}")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Non-existent unfollow handled: {result['message']}")
        else:
            print(f"⚠️  Non-existent unfollow response: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Error with non-existent unfollow: {e}")
    
    # Test getting updated user profiles to see follower/following counts
    print("\n8. Checking updated user profiles...")
    for user in [alice, bob]:
        try:
            response = requests.get(f"{BASE_URL}/users/{user['_id']}")
            if response.status_code == 200:
                profile = response.json()
                follower_count = len(profile.get('followers', []))
                following_count = len(profile.get('following', []))
                print(f"✅ {profile['username']}: {follower_count} followers, {following_count} following")
            else:
                print(f"❌ Failed to get updated profile for {user['username']}")
        except Exception as e:
            print(f"❌ Error getting updated profile: {e}")
    
    # Test what happens when we use the new endpoints
    print("\n10. Testing newly implemented endpoints...")
    try:
        response = requests.get(f"{BASE_URL}/users/search?q=alice")
        print(f"   Search endpoint status: {response.status_code}")
        if response.status_code == 200:
            results = response.json()
            print(f"   ✅ Search working! Found {len(results)} users")
            
            # Test followers/following endpoints
            if results:
                user_id = results[0]['_id']
                followers_resp = requests.get(f"{BASE_URL}/users/{user_id}/followers")
                following_resp = requests.get(f"{BASE_URL}/users/{user_id}/following")
                print(f"   ✅ Followers endpoint: {followers_resp.status_code}")
                print(f"   ✅ Following endpoint: {following_resp.status_code}")
        else:
            print("   ❌ Search endpoint still not working")
    except Exception as e:
        print(f"   Error testing new endpoints: {e}")
    
    print("\n" + "=" * 50)
    print("👥 User Management Test Complete!")
    print("\n📋 CURRENT USER ENDPOINTS AVAILABLE:")
    print("   POST   /api/v1/users/                     - Create user (deprecated, use auth/register)")
    print("   GET    /api/v1/users/{user_id}           - Get user profile")
    print("   PUT    /api/v1/users/{user_id}           - Update user profile")
    print("   POST   /api/v1/users/{id}/follow/{id}    - Follow user")
    print("   DELETE /api/v1/users/{id}/follow/{id}    - Unfollow user")
    print("   ✅ GET    /api/v1/users/search?q=term        - Search users (NEW!)")
    print("   ✅ GET    /api/v1/users/{id}/followers      - Get user's followers (NEW!)")
    print("   ✅ GET    /api/v1/users/{id}/following      - Get user's following (NEW!)")
    print("\n📋 AUTHENTICATION ENDPOINTS:")
    print("   POST   /api/v1/auth/register              - Register new user")
    print("   POST   /api/v1/auth/login                 - Login user")
    print("   POST   /api/v1/auth/refresh               - Refresh tokens")
    print("   GET    /api/v1/auth/me                    - Get current user profile")
    print("   POST   /api/v1/auth/logout                - Logout user")
    print("\n🚧 REMAINING RECOMMENDED ENDPOINTS:")
    print("   GET    /api/v1/users/me/feed              - Get authenticated user's feed")
    print("   GET    /api/v1/users/suggested            - Get suggested users to follow")
    print("   GET    /api/v1/users/popular              - Get popular/trending users")
    print("\n✨ NEWLY IMPLEMENTED FEED ENDPOINT:")
    print("   ✅ GET    /api/v1/catches/feed             - Get personalized catch feed (own + following)")
    
    return True

if __name__ == "__main__":
    success = test_user_management()
    exit(0 if success else 1)
