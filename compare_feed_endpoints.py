#!/usr/bin/env python3
"""
Feed vs My Catches Comparison Script
Demonstrates the difference between /catches/me and /catches/feed endpoints
"""

import requests

BASE_URL = "http://localhost:8000/api/v1"

def compare_endpoints():
    print("📊 Feed vs My Catches Comparison")
    print("=" * 50)
    
    # Get or create a test user
    user_data = {
        "username": "comparison_user",
        "email": "comparison@Rod Royale.com",
        "bio": "Testing feed comparison",
        "password": "test123"
    }
    
    # Try to login first, if that fails try to register
    try:
        login_response = requests.post(f"{BASE_URL}/auth/login", json={
            "email": user_data["email"],
            "password": user_data["password"]
        })
        
        if login_response.status_code == 200:
            auth_data = login_response.json()
            print(f"✅ Logged in as: {auth_data['user']['username']}")
        else:
            # Try registration
            register_response = requests.post(f"{BASE_URL}/auth/register", json=user_data)
            if register_response.status_code == 201:
                auth_data = register_response.json()
                print(f"✅ Registered as: {auth_data['user']['username']}")
            else:
                print("❌ Failed to authenticate")
                return
        
        token = auth_data['token']['access_token']
        headers = {"Authorization": f"Bearer {token}"}
        
        print("\n1. Testing /catches/me endpoint...")
        my_catches_response = requests.get(f"{BASE_URL}/catches/me", headers=headers)
        if my_catches_response.status_code == 200:
            my_catches = my_catches_response.json()
            print(f"✅ /catches/me returned {len(my_catches)} catches")
            print("   📝 This endpoint shows ONLY your own catches")
        else:
            print(f"❌ /catches/me failed: {my_catches_response.status_code}")
        
        print("\n2. Testing /catches/feed endpoint...")
        feed_response = requests.get(f"{BASE_URL}/catches/feed", headers=headers)
        if feed_response.status_code == 200:
            feed_catches = feed_response.json()
            print(f"✅ /catches/feed returned {len(feed_catches)} catches")
            print("   📝 This endpoint shows your catches + catches from users you follow")
        else:
            print(f"❌ /catches/feed failed: {feed_response.status_code}")
        
        print("\n" + "=" * 50)
        print("📊 ENDPOINT COMPARISON SUMMARY")
        print("")
        print("🔸 /catches/me:")
        print("   Purpose: Get only the current user's catches")
        print("   Use case: Profile page, personal catch history")
        print("   Returns: Your catches only")
        print("")
        print("🔸 /catches/feed:")
        print("   Purpose: Get personalized feed of catches")
        print("   Use case: Home page, social feed, timeline")
        print("   Returns: Your catches + catches from users you follow")
        print("")
        print("Both endpoints:")
        print("   - Require authentication")
        print("   - Support pagination (skip/limit)")
        print("   - Order by creation date (newest first)")
        print("   - Return full catch objects with all details")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    compare_endpoints()
