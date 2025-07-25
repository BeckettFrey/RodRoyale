#!/usr/bin/env python3
"""
User Posts Retrieval Example & Test
Shows how clients can retrieve user's catches (posts) with proper authentication
"""

import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000/api/v1"
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2ODgzMTY4YWJiOTE5MmY1ODE5YTIwNWQiLCJleHAiOjE3NTM0NzQxMTEsInR5cGUiOiJhY2Nlc3MifQ.YG7YCfJBCtmOuSgjoei0Hl0EwBdG1i4-jlruyvdWRko"

# Test user ID (replace with actual user ID)
USER_ID = "6883168abb9192f5819a205d"

def make_api_request(method, endpoint, data=None):
    """Make authenticated API request"""
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }
    
    url = f"{BASE_URL}{endpoint}"
    print(f"\n🌐 {method} {url}")
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data)
        
        print(f"📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Success!")
            data = response.json()
            return data
        else:
            print(f"❌ Error: {response.status_code}")
            try:
                error_data = response.json()
                print(f"📄 Error details: {json.dumps(error_data, indent=2)}")
            except:
                print(f"📄 Error response: {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return None

def create_sample_catch():
    """Create a sample catch for testing"""
    print("🎣 Creating a sample catch for testing...")
    
    sample_catch = {
        "species": "Rainbow Trout",
        "weight": 2.5,
        "photo_url": "https://example.com/trout.jpg",
        "location": {
            "lat": 40.7128,
            "lng": -74.0060
        },
        "shared_with_followers": True,
        "add_to_map": False
    }
    
    return make_api_request("POST", "/catches/", sample_catch)

def get_my_posts():
    """Get current user's own posts (catches)"""
    print("\n📱 CLIENT EXAMPLE: Getting my own posts")
    print("=" * 50)
    
    # Method 1: Get my catches (recommended for own posts)
    my_catches = make_api_request("GET", "/catches/me?limit=5")
    
    if my_catches:
        print(f"📊 Found {len(my_catches)} of my catches:")
        for i, catch in enumerate(my_catches, 1):
            print(f"\n🎣 Catch #{i}:")
            print(f"   🐟 Species: {catch.get('species')}")
            print(f"   ⚖️  Weight: {catch.get('weight')} lbs")
            print(f"   📅 Date: {catch.get('created_at', 'Unknown')}")
            print(f"   👥 Shared: {catch.get('shared_with_followers', False)}")
            print(f"   🗺️  On Map: {catch.get('add_to_map', False)}")
    
    return my_catches

def get_user_posts(user_id):
    """Get another user's posts (catches)"""
    print(f"\n👤 CLIENT EXAMPLE: Getting user {user_id}'s posts")
    print("=" * 50)
    
    # Method 2: Get specific user's catches (with access control)
    user_catches = make_api_request("GET", f"/users/{user_id}/catches?limit=5")
    
    if user_catches:
        print(f"📊 Found {len(user_catches)} public/shared catches:")
        for i, catch in enumerate(user_catches, 1):
            print(f"\n🎣 Catch #{i}:")
            print(f"   🐟 Species: {catch.get('species')}")
            print(f"   ⚖️  Weight: {catch.get('weight')} lbs")
            print(f"   📅 Date: {catch.get('created_at', 'Unknown')}")
            print(f"   👥 Shared: {catch.get('shared_with_followers', False)}")
    else:
        print("❌ No catches found or access denied")
    
    return user_catches

def show_pagination_example():
    """Show how to use pagination"""
    print("\n📄 CLIENT EXAMPLE: Pagination")
    print("=" * 50)
    
    # Get first page
    print("Getting first 3 catches...")
    page1 = make_api_request("GET", "/catches/me?limit=3&skip=0")
    
    if page1:
        print(f"📊 Page 1: {len(page1)} catches")
        
        # Get second page
        print("\nGetting next 3 catches...")
        page2 = make_api_request("GET", "/catches/me?limit=3&skip=3")
        
        if page2:
            print(f"📊 Page 2: {len(page2)} catches")

def show_curl_examples():
    """Show curl command examples"""
    print("\n🌐 CURL COMMAND EXAMPLES:")
    print("=" * 60)
    
    print("\n1️⃣  Get your own catches:")
    print(f"curl -X GET \"{BASE_URL}/catches/me\" \\")
    print(f"  -H \"Authorization: Bearer {TOKEN}\"")
    
    print("\n2️⃣  Get your catches with pagination:")
    print(f"curl -X GET \"{BASE_URL}/catches/me?limit=10&skip=0\" \\")
    print(f"  -H \"Authorization: Bearer {TOKEN}\"")
    
    print("\n3️⃣  Get another user's catches:")
    print(f"curl -X GET \"{BASE_URL}/users/{USER_ID}/catches\" \\")
    print(f"  -H \"Authorization: Bearer {TOKEN}\"")
    
    print("\n4️⃣  Get another user's catches with pagination:")
    print(f"curl -X GET \"{BASE_URL}/users/{USER_ID}/catches?limit=5&skip=0\" \\")
    print(f"  -H \"Authorization: Bearer {TOKEN}\"")

def main():
    """Main test function"""
    print("🎣 Rod Royale API - User Posts Retrieval Test")
    print("=" * 60)
    print(f"⏰ Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("⚠️  Make sure your API server is running on localhost:8000")
    
    # Create a sample catch first
    sample_catch = create_sample_catch()
    if sample_catch:
        print("✅ Sample catch created successfully!")
    
    # Test getting own posts
    my_catches = get_my_posts()
    
    # Test getting another user's posts
    user_catches = get_user_posts(USER_ID)
    
    # Show pagination example
    if my_catches and len(my_catches) > 0:
        show_pagination_example()
    
    # Show curl examples
    show_curl_examples()
    
    print(f"\n✅ Test completed at: {datetime.now().strftime('%H:%M:%S')}")
    print("\n💡 KEY POINTS:")
    print("   • Use /catches/me for your own posts (sees all)")
    print("   • Use /users/{id}/catches for others (respects privacy)")
    print("   • Both support pagination with ?limit=X&skip=Y")
    print("   • Authentication required for all endpoints")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️  Test cancelled by user")
    except Exception as e:
        print(f"\n💥 Error: {e}")
