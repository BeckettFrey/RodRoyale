#!/usr/bin/env python3
"""
Test the combined image upload and catch creation endpoint
"""

import requests
import os
from PIL import Image
import tempfile

BASE_URL = "http://localhost:8000/api/v1"

def create_test_image():
    """Create a test image file for upload"""
    # Create a simple test image
    img = Image.new('RGB', (800, 600), color='lightblue')
    
    # Save to temporary file
    temp_file = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
    img.save(temp_file.name, 'JPEG')
    temp_file.close()
    
    return temp_file.name

def test_combined_upload():
    """Test the combined upload and catch creation endpoint"""
    print("🎣 Testing Combined Image Upload + Catch Creation")
    print("=" * 55)
    
    # Note: This test requires a valid JWT token
    print("⚠️  This endpoint requires authentication!")
    print("📝 To get a token:")
    print("   1. Register: POST /api/v1/auth/register")
    print("   2. Login: POST /api/v1/auth/login") 
    print("   3. Use the access_token in Authorization header")
    print()
    
    # Create test image
    test_image_path = create_test_image()
    print(f"📸 Created test image: {test_image_path}")
    
    try:
        # Test data
        catch_data = {
            'species': 'Test Bass',
            'weight': 3.5,
            'lat': 28.5383,
            'lng': -81.3792,
            'shared_with_followers': True
        }
        
        # Test file upload
        with open(test_image_path, 'rb') as f:
            files = {'file': ('test_catch.jpg', f, 'image/jpeg')}
            
            print("📤 Testing upload endpoint (without auth - should fail):")
            response = requests.post(
                f"{BASE_URL}/catches/upload-with-image",
                data=catch_data,
                files=files
            )
            
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.json()}")
            
            if response.status_code == 403:
                print("   ✅ Correctly requires authentication")
            else:
                print("   ⚠️  Unexpected response")
        
        # Show example curl command
        print("\n💡 Example usage with curl (with auth token):")
        print(f"""
curl -X POST "{BASE_URL}/catches/upload-with-image" \\
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \\
  -F "file=@{test_image_path}" \\
  -F "species=Largemouth Bass" \\
  -F "weight=4.2" \\
  -F "lat=28.5383" \\
  -F "lng=-81.3792" \\
  -F "shared_with_followers=true"
        """)
        
        print("\n🔄 Complete workflow example:")
        print("""
# 1. Register a user
curl -X POST "http://localhost:8000/api/v1/auth/register" \\
  -H "Content-Type: application/json" \\
  -d '{
    "username": "test_angler",
    "email": "test@example.com",
    "password": "securepass123",
    "bio": "Test angler"
  }'

# 2. Login to get token
curl -X POST "http://localhost:8000/api/v1/auth/login" \\
  -H "Content-Type: application/json" \\
  -d '{
    "email": "test@example.com",
    "password": "securepass123"
  }'

# 3. Upload catch with image (use token from step 2)
curl -X POST "http://localhost:8000/api/v1/catches/upload-with-image" \\
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \\
  -F "file=@your_fish_photo.jpg" \\
  -F "species=Largemouth Bass" \\
  -F "weight=4.2" \\
  -F "lat=28.5383" \\
  -F "lng=-81.3792" \\
  -F "shared_with_followers=true"
        """)
        
    finally:
        # Clean up test image
        if os.path.exists(test_image_path):
            os.unlink(test_image_path)
            print(f"🧹 Cleaned up test image: {test_image_path}")

def show_endpoint_features():
    """Show what the combined endpoint does"""
    print("\n🚀 Combined Upload Endpoint Features:")
    print("=" * 45)
    print("✅ Single API call for complete catch creation")
    print("✅ Handles multipart/form-data file upload")
    print("✅ Uploads image to Cloudinary automatically")
    print("✅ Generates optimized URLs (thumbnail, secure_url)")
    print("✅ Stores catch data in MongoDB")
    print("✅ Returns complete Catch object with image URLs")
    print("✅ Validates input data (weight > 0, species required)")
    print("✅ Requires JWT authentication")
    print("✅ Respects privacy settings (shared_with_followers)")
    print()
    
    print("📋 Request Format:")
    print("   - Method: POST")
    print("   - Content-Type: multipart/form-data")
    print("   - Authentication: Bearer token required")
    print()
    
    print("📊 Form Fields:")
    print("   - file: Image file (required)")
    print("   - species: Fish species name (required)")
    print("   - weight: Weight in pounds (required, > 0)")
    print("   - lat: Latitude coordinate (required)")
    print("   - lng: Longitude coordinate (required)")
    print("   - shared_with_followers: Privacy setting (optional, default: false)")
    print()
    
    print("📤 Response:")
    print("   - Complete Catch object with:")
    print("     • Generated catch ID")
    print("     • User ID (from JWT token)")
    print("     • Cloudinary image URLs")
    print("     • Timestamp")
    print("     • All form data")

if __name__ == "__main__":
    show_endpoint_features()
    test_combined_upload()
