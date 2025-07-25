#!/usr/bin/env python3
"""
Rod Royale Backend API Test Script
Demonstrates basic API functionality with sample data
"""

import requests
import sys
import io
from PIL import Image

BASE_URL = "http://localhost:8000/api/v1"

def test_api():
    print("🎣 Testing Rod Royale Backend API")
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
    print("\n1. Creating test users with authentication...")
    users_data = [
        {
            "username": "angler_mike",
            "email": "mike@Rod Royale.com",
            "bio": "Bass fishing enthusiast from Texas",
            "password": "password123"
        },
        {
            "username": "fisher_sarah",
            "email": "sarah@Rod Royale.com", 
            "bio": "Fly fishing guide in Colorado",
            "password": "password456"
        }
    ]
    
    created_users = []
    user_tokens = []
    for user_data in users_data:
        try:
            # Try registration first
            response = requests.post(f"{BASE_URL}/auth/register", json=user_data)
            if response.status_code == 201:
                auth_response = response.json()
                created_users.append(auth_response['user'])
                user_tokens.append(auth_response['token']['access_token'])
                print(f"✅ Registered user: {auth_response['user']['username']} (ID: {auth_response['user']['_id']})")
            else:
                # If registration fails (user exists), try login
                login_data = {"email": user_data["email"], "password": user_data["password"]}
                response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
                if response.status_code == 200:
                    auth_response = response.json()
                    created_users.append(auth_response['user'])
                    user_tokens.append(auth_response['token']['access_token'])
                    print(f"✅ Logged in user: {auth_response['user']['username']} (ID: {auth_response['user']['_id']})")
                else:
                    print(f"❌ Failed to create/login user {user_data['username']}: {response.text}")
        except Exception as e:
            print(f"❌ Error with user {user_data['username']}: {e}")
    
    if len(created_users) < 1:
        print("❌ Need at least one user to continue testing")
        return False
    
    user1 = created_users[0]
    user1_token = user_tokens[0]
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
    headers = {"Authorization": f"Bearer {user_tokens[0]}"}  # Use first user's token
    
    for catch_data in catches_data:
        try:
            response = requests.post(f"{BASE_URL}/catches", json=catch_data, headers=headers)
            if response.status_code == 201:
                catch = response.json()
                created_catches.append(catch)
                print(f"✅ Created catch: {catch['species']} - {catch['weight']}lbs")
            else:
                print(f"❌ Error creating catch: {response.status_code} - {response.text}")
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
        response = requests.post(f"{BASE_URL}/pins", json=pin_data, headers=headers)
        if response.status_code == 201:
            print(f"✅ Created pin for {catch1['species']} catch")
            
            # Test retrieving pins
            print("\n5. Retrieving map pins...")
            response = requests.get(f"{BASE_URL}/pins")  # No need for viewer_id with JWT
            if response.status_code == 200:
                pins = response.json()
                print(f"✅ Retrieved {len(pins)} pins from map")
                if pins:
                    print(f"   First pin: {pins[0]['catch_info']['species']} by {pins[0]['owner_info']['username']}")
            else:
                print(f"❌ Error retrieving pins: {response.status_code} - {response.text}")
                
        else:
            print(f"❌ Error creating pin: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Error with pins: {e}")
    
    # Test getting user catches
    print("\n6. Retrieving user catches...")
    try:
        # Test getting current user's catches (easier with JWT)
        response = requests.get(f"{BASE_URL}/catches/me", headers=headers)
        if response.status_code == 200:
            catches = response.json()
            print(f"✅ Retrieved {len(catches)} catches for authenticated user")
        else:
            print(f"❌ Error retrieving catches: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Error retrieving catches: {e}")
    
    # Test image upload
    print("\n7. Testing image upload...")
    try:
        # Create a simple test image
        img = Image.new('RGB', (100, 100), color='blue')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='JPEG')
        img_bytes.seek(0)
        
        files = {
            'file': ('test_image.jpg', img_bytes, 'image/jpeg')
        }
        
        response = requests.post(f"{BASE_URL}/upload/image", files=files)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Image uploaded successfully: {result['url']}")
            
            # Test accessing the uploaded image
            image_url = f"http://localhost:8000{result['url']}"
            img_response = requests.get(image_url)
            if img_response.status_code == 200:
                print("✅ Uploaded image is accessible")
            else:
                print(f"❌ Cannot access uploaded image: {img_response.status_code}")
        else:
            print(f"❌ Image upload failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Error testing image upload: {e}")
    
    print("\n" + "=" * 40)
    print("🎣 API Test Complete!")
    print("📚 Visit http://localhost:8000/docs for interactive API documentation")
    return True

if __name__ == "__main__":
    success = test_api()
    sys.exit(0 if success else 1)
