#!/usr/bin/env python3
"""
Catchy Backend API Test Script
Demonstrates basic API functionality with sample data
"""

import requests
import sys

BASE_URL = "http://localhost:8000/api/v1"

def test_api():
    print("🎣 Testing Catchy Backend API")
    print("=" * 40)
    
    # Test health endpoint
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
    
    # Test user creation
    print("\n1. Creating test users...")
    users_data = [
        {
            "username": "angler_mike",
            "email": "mike@catchy.com",
            "bio": "Bass fishing enthusiast from Texas"
        },
        {
            "username": "fisher_sarah",
            "email": "sarah@catchy.com", 
            "bio": "Fly fishing guide in Colorado"
        }
    ]
    
    created_users = []
    for user_data in users_data:
        try:
            response = requests.post(f"{BASE_URL}/users", json=user_data)
            if response.status_code == 201:
                user = response.json()
                created_users.append(user)
                print(f"✅ Created user: {user['username']} (ID: {user['_id']})")
            else:
                print(f"⚠️  User {user_data['username']} might already exist")
                # Try to find existing user
                response = requests.get(f"{BASE_URL}/users")
        except Exception as e:
            print(f"❌ Error creating user {user_data['username']}: {e}")
    
    if len(created_users) < 1:
        print("❌ Need at least one user to continue testing")
        return False
    
    user1 = created_users[0]
    print(user1)
    user1_id = user1['_id']
    
    # Test following functionality if we have multiple users
    if len(created_users) >= 2:
        user2 = created_users[1]
        user2_id = user2['_id']
        
        print("\n2. Testing follow functionality...")
        try:
            response = requests.post(f"{BASE_URL}/users/{user1_id}/follow/{user2_id}")
            if response.status_code == 200:
                print(f"✅ {user1['username']} now follows {user2['username']}")
            else:
                print(f"⚠️  Follow request failed: {response.text}")
        except Exception as e:
            print(f"❌ Error following user: {e}")
    
    # Test catch creation
    print(f"\n3. Creating test catches for {user1['username']}...")
    catches_data = [
        {
            "species": "Largemouth Bass",
            "weight": 3.5,
            "photo_url": "https://example.com/bass1.jpg",
            "location": {"lat": 30.2672, "lng": -97.7431},
            "shared_with_followers": False
        },
        {
            "species": "Rainbow Trout", 
            "weight": 1.2,
            "photo_url": "https://example.com/trout1.jpg", 
            "location": {"lat": 39.7392, "lng": -104.9903},
            "shared_with_followers": True
        }
    ]
    
    created_catches = []
    for catch_data in catches_data:
        try:
            response = requests.post(f"{BASE_URL}/catches?user_id={user1_id}", json=catch_data)
            if response.status_code == 201:
                catch = response.json()
                created_catches.append(catch)
                print(f"✅ Created catch: {catch['species']} - {catch['weight']}lbs")
            else:
                print(f"❌ Error creating catch: {response.text}")
        except Exception as e:
            print(f"❌ Error creating catch: {e}")
    
    if not created_catches:
        print("❌ No catches created, skipping pin tests")
        return True
    
    # Test pin creation
    print("\n4. Creating map pins...")
    catch1 = created_catches[0]
    pin_data = {
        "catch_id": catch1['_id'],
        "location": catch1['location'],
        "visibility": "public"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/pins?user_id={user1_id}", json=pin_data)
        if response.status_code == 201:
            print(f"✅ Created pin for {catch1['species']} catch")
            
            # Test retrieving pins
            print("\n5. Retrieving map pins...")
            response = requests.get(f"{BASE_URL}/pins?viewer_id={user1_id}")
            if response.status_code == 200:
                pins = response.json()
                print(f"✅ Retrieved {len(pins)} pins from map")
                if pins:
                    print(f"   First pin: {pins[0]['catch_info']['species']} by {pins[0]['owner_info']['username']}")
            else:
                print(f"❌ Error retrieving pins: {response.text}")
                
        else:
            print(f"❌ Error creating pin: {response.text}")
    except Exception as e:
        print(f"❌ Error with pins: {e}")
    
    # Test getting user catches
    print("\n6. Retrieving user catches...")
    try:
        response = requests.get(f"{BASE_URL}/catches/users/{user1_id}/catches?viewer_id={user1_id}")
        if response.status_code == 200:
            catches = response.json()
            print(f"✅ Retrieved {len(catches)} catches for {user1['username']}")
        else:
            print(f"❌ Error retrieving catches: {response.text}")
    except Exception as e:
        print(f"❌ Error retrieving catches: {e}")
    
    print("\n" + "=" * 40)
    print("🎣 API Test Complete!")
    print("📚 Visit http://localhost:8000/docs for interactive API documentation")
    return True

if __name__ == "__main__":
    success = test_api()
    sys.exit(0 if success else 1)
