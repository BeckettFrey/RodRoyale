#!/usr/bin/env python3
"""
Client Example: How to Retrieve User Posts (Catches)
Shows the exact code clients should use to get user's fishing posts
"""

# 📱 CLIENT CODE EXAMPLES

def get_my_posts(api_client, token):
    """Get current user's own posts/catches"""
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get all my catches with pagination
    response = api_client.get(
        "/api/v1/catches/me?limit=20&skip=0", 
        headers=headers
    )
    
    if response.status_code == 200:
        catches = response.json()
        print(f"📊 Found {len(catches)} of your catches")
        return catches
    else:
        print(f"❌ Error: {response.status_code}")
        return None

def get_user_posts(api_client, token, user_id):
    """Get another user's public/shared posts"""
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get user's catches (respects privacy settings)
    response = api_client.get(
        f"/api/v1/users/{user_id}/catches?limit=20&skip=0",
        headers=headers
    )
    
    if response.status_code == 200:
        catches = response.json()
        print(f"📊 Found {len(catches)} public catches from user")
        return catches
    else:
        print(f"❌ Error: {response.status_code}")
        return None

# 🧪 MOCK TEST DATA (What the API would return)

def mock_api_response():
    """Mock API response showing what clients will receive"""
    return [
        {
            "id": "67890abc123def456789",
            "species": "Largemouth Bass",
            "weight": 4.2,
            "photo_url": "https://cloudinary.com/Rod Royale/bass_001.jpg",
            "thumbnail_url": "https://cloudinary.com/Rod Royale/bass_001_thumb.jpg",
            "location": {
                "lat": 40.7128,
                "lng": -74.0060
            },
            "created_at": "2025-07-25T15:30:00",
            "shared_with_followers": True,
            "add_to_map": True,
            "user_id": "6883168abb9192f5819a205d"
        },
        {
            "id": "12345def789abc456123",
            "species": "Rainbow Trout", 
            "weight": 2.8,
            "photo_url": "https://cloudinary.com/Rod Royale/trout_002.jpg",
            "thumbnail_url": "https://cloudinary.com/Rod Royale/trout_002_thumb.jpg",
            "location": {
                "lat": 41.8781,
                "lng": -87.6298
            },
            "created_at": "2025-07-24T10:15:00",
            "shared_with_followers": False,
            "add_to_map": False,
            "user_id": "6883168abb9192f5819a205d"
        }
    ]

def display_catches(catches):
    """Display catches in a user-friendly format"""
    print("\n🎣 USER'S FISHING POSTS:")
    print("=" * 50)
    
    for i, catch in enumerate(catches, 1):
        print(f"\n📸 Post #{i}:")
        print(f"   🐟 Species: {catch['species']}")
        print(f"   ⚖️  Weight: {catch['weight']} lbs")
        print(f"   📅 Caught: {catch['created_at']}")
        print(f"   📍 Location: {catch['location']['lat']}, {catch['location']['lng']}")
        print(f"   🖼️  Photo: {catch['photo_url']}")
        print(f"   👥 Shared with followers: {'Yes' if catch['shared_with_followers'] else 'No'}")
        print(f"   🗺️  On map: {'Yes' if catch['add_to_map'] else 'No'}")

def test_with_mock_data():
    """Test the display with mock data"""
    print("🎣 Client Example: Retrieving User Posts")
    print("=" * 60)
    
    # Simulate API response
    mock_catches = mock_api_response()
    
    # Display the catches
    display_catches(mock_catches)
    
    print(f"\n✅ Successfully retrieved {len(mock_catches)} posts!")

# 📋 IMPLEMENTATION GUIDE

def show_implementation_guide():
    """Show how clients should implement this"""
    print("\n📋 CLIENT IMPLEMENTATION GUIDE:")
    print("=" * 60)
    
    print("\n🔐 AUTHENTICATION:")
    print("   • All endpoints require JWT token")
    print("   • Include: Authorization: Bearer <token>")
    print("   • Token should be stored securely")
    
    print("\n📱 ENDPOINTS:")
    print("   • GET /api/v1/catches/me - Your own posts (sees all)")
    print("   • GET /api/v1/users/{id}/catches - Other user's posts (respects privacy)")
    
    print("\n🔄 PRIVACY RULES:")
    print("   • Own posts: See everything")
    print("   • Others' posts: Only public + shared (if following)")
    print("   • Not following: Only public posts")
    
    print("\n📄 PAGINATION:")
    print("   • ?limit=20 - Number of posts per page (max 100)")
    print("   • ?skip=0 - Skip first N posts")
    print("   • Example: ?limit=10&skip=20 for page 3")
    
    print("\n📊 RESPONSE FORMAT:")
    print("   • Array of catch objects")
    print("   • Sorted by created_at (newest first)")
    print("   • Includes all photo URLs (original, thumbnail, etc.)")

# 🌐 CURL EXAMPLES

def show_curl_examples():
    """Production-ready curl examples"""
    print("\n🌐 CURL EXAMPLES:")
    print("=" * 60)
    
    token = "YOUR_JWT_TOKEN_HERE"
    base_url = "https://api.Rod Royale.app"  # Your production URL
    
    print("\n1️⃣  Get your own posts:")
    print(f"curl -X GET \"{base_url}/api/v1/catches/me?limit=20\" \\")
    print(f"  -H \"Authorization: Bearer {token}\" \\")
    print("  -H \"Accept: application/json\"")
    
    print("\n2️⃣  Get another user's posts:")
    print(f"curl -X GET \"{base_url}/api/v1/users/USER_ID_HERE/catches?limit=20\" \\")
    print(f"  -H \"Authorization: Bearer {token}\" \\")
    print("  -H \"Accept: application/json\"")
    
    print("\n3️⃣  Get posts with pagination (page 2):")
    print(f"curl -X GET \"{base_url}/api/v1/catches/me?limit=10&skip=10\" \\")
    print(f"  -H \"Authorization: Bearer {token}\" \\")
    print("  -H \"Accept: application/json\"")

# 🏃‍♂️ RUN THE DEMO

if __name__ == "__main__":
    print("🎣 Rod Royale API - User Posts Retrieval Guide")
    print("=" * 60)
    
    # Show mock data example
    test_with_mock_data()
    
    # Show implementation guide
    show_implementation_guide()
    
    # Show curl examples
    show_curl_examples()
    
    print("\n🎉 Ready to implement user post retrieval!")
    print("💡 This shows exactly what your API returns and how clients should use it.")
