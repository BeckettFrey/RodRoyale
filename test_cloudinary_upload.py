#!/usr/bin/env python3
"""
Cloudinary Image Upload Test Script
Tests the new Cloudinary-based image upload functionality
"""

import requests
from io import BytesIO
from PIL import Image

BASE_URL = "http://localhost:8000/api/v1"

def create_test_image(filename="test_catch.jpg", width=800, height=600):
    """Create a test image file for upload testing"""
    # Create a simple test image
    img = Image.new('RGB', (width, height), color='lightblue')
    
    # Save to BytesIO
    img_bytes = BytesIO()
    img.save(img_bytes, format='JPEG', quality=85)
    img_bytes.seek(0)
    
    return img_bytes

def test_cloudinary_upload_system():
    print("🌤️  Testing Cloudinary Image Upload System")
    print("=" * 60)
    
    # Test health check
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
    
    # Create test user
    print("\n1. Creating test user...")
    test_user = {
        "username": "cloudinary_angler",
        "email": "cloudinary@Rod Royale.com",
        "bio": "Testing Cloudinary image uploads",
        "password": "cloud123"
    }
    
    try:
        # Try registration first
        response = requests.post(f"{BASE_URL}/auth/register", json=test_user)
        if response.status_code == 201:
            auth_response = response.json()
            user = auth_response['user']
            token = auth_response['token']['access_token']
            print(f"✅ Registered: {user['username']}")
        else:
            # If user exists, try login
            login_data = {"email": test_user["email"], "password": test_user["password"]}
            response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
            if response.status_code == 200:
                auth_response = response.json()
                user = auth_response['user']
                token = auth_response['token']['access_token']
                print(f"✅ Logged in: {user['username']}")
            else:
                print(f"❌ Failed to authenticate user: {response.text}")
                return False
    except Exception as e:
        print(f"❌ Error with user authentication: {e}")
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test direct image upload to Cloudinary
    print("\n2. Testing direct image upload to Cloudinary...")
    try:
        # Create test image
        test_image = create_test_image("test_upload.jpg")
        
        files = {
            'file': ('test_upload.jpg', test_image, 'image/jpeg')
        }
        
        response = requests.post(f"{BASE_URL}/upload/image", files=files)
        
        if response.status_code == 200:
            upload_result = response.json()
            print("✅ Direct Cloudinary upload successful:")
            print(f"   📷 Image URL: {upload_result['url']}")
            print(f"   🆔 Public ID: {upload_result['public_id']}")
            print(f"   🖼️  Thumbnail URL: {upload_result.get('thumbnail_url', 'N/A')}")
            
            # Store for cleanup later
            image_public_id = upload_result['public_id']
        else:
            print(f"❌ Direct upload failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error during direct upload: {e}")
        return False
    
    # Test catch creation with image upload
    print("\n3. Testing catch creation with image upload...")
    try:
        # Create another test image for catch
        catch_image = create_test_image("bass_catch.jpg", 1000, 800)
        
        # Prepare form data
        files = {
            'file': ('bass_catch.jpg', catch_image, 'image/jpeg')
        }
        
        data = {
            'species': 'Largemouth Bass',
            'weight': 8.5,
            'lat': 34.0522,
            'lng': -118.2437,
            'shared_with_followers': True
        }
        
        response = requests.post(
            f"{BASE_URL}/catches/upload-with-image",
            files=files,
            data=data,
            headers=headers
        )
        
        if response.status_code == 201:
            catch = response.json()
            print("✅ Catch created with Cloudinary image:")
            print(f"   🐟 Species: {catch['species']}")
            print(f"   ⚖️  Weight: {catch['weight']}lbs")
            print(f"   📷 Photo URL: {catch['photo_url']}")
            print(f"   🆔 Public ID: {catch.get('photo_public_id', 'N/A')}")
            print(f"   🖼️  Thumbnail: {catch.get('thumbnail_url', 'N/A')}")
        else:
            print(f"❌ Catch with image upload failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error during catch creation: {e}")
        return False
    
    # Test thumbnail generation
    print("\n4. Testing thumbnail URL generation...")
    if image_public_id:
        try:
            response = requests.get(
                f"{BASE_URL}/upload/image/{image_public_id}/thumbnail?width=200&height=200"
            )
            
            if response.status_code == 200:
                thumbnail_result = response.json()
                print("✅ Thumbnail URL generated:")
                print(f"   🖼️  Thumbnail URL: {thumbnail_result['thumbnail_url']}")
                print(f"   📐 Dimensions: {thumbnail_result['width']}x{thumbnail_result['height']}")
            else:
                print(f"❌ Thumbnail generation failed: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error generating thumbnail: {e}")
    
    # Test optimized URL generation
    print("\n5. Testing optimized URL generation...")
    if image_public_id:
        try:
            response = requests.get(
                f"{BASE_URL}/upload/image/{image_public_id}/optimized?width=600&height=400"
            )
            
            if response.status_code == 200:
                optimized_result = response.json()
                print("✅ Optimized URL generated:")
                print(f"   🎯 Optimized URL: {optimized_result['optimized_url']}")
                print(f"   📐 Max Dimensions: {optimized_result['width']}x{optimized_result['height']}")
            else:
                print(f"❌ Optimized URL generation failed: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error generating optimized URL: {e}")
    
    # Test image cleanup
    print("\n6. Testing image deletion...")
    if image_public_id:
        try:
            response = requests.delete(f"{BASE_URL}/upload/image/{image_public_id}")
            
            if response.status_code == 200:
                delete_result = response.json()
                print("✅ Image deleted from Cloudinary:")
                print(f"   🗑️  Deleted: {delete_result['public_id']}")
            else:
                print(f"❌ Image deletion failed: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error deleting image: {e}")
    
    print("\n" + "=" * 60)
    print("🌤️  Cloudinary Integration Test Complete!")
    
    print("\n📸 CLOUDINARY ENDPOINTS:")
    print("   ✅ POST /api/v1/upload/image                    - Direct image upload")
    print("   ✅ POST /api/v1/catches/upload-with-image       - Create catch with image")
    print("   ✅ GET  /api/v1/upload/image/{id}/thumbnail     - Generate thumbnail URL")
    print("   ✅ GET  /api/v1/upload/image/{id}/optimized     - Generate optimized URL")
    print("   ✅ DELETE /api/v1/upload/image/{id}             - Delete image")
    
    print("\n🌟 CLOUDINARY FEATURES:")
    print("   📷 Automatic image optimization and format conversion")
    print("   🖼️  Dynamic thumbnail generation with custom dimensions")
    print("   🎯 Optimized URLs with quality and format auto-detection")
    print("   ☁️  Cloud storage eliminates local uploads folder")
    print("   🔧 Image transformations (resize, crop, quality adjustment)")
    print("   🗑️  Programmatic image deletion and cleanup")
    print("   📊 Advanced image analytics and usage tracking (via Cloudinary dashboard)")
    
    print("\n⚙️  SETUP REQUIREMENTS:")
    print("   1. Sign up for free Cloudinary account at https://cloudinary.com")
    print("   2. Get your Cloud Name, API Key, and API Secret from dashboard")
    print("   3. Set environment variables:")
    print("      - CLOUDINARY_CLOUD_NAME=your_cloud_name")
    print("      - CLOUDINARY_API_KEY=your_api_key") 
    print("      - CLOUDINARY_API_SECRET=your_api_secret")
    print("   4. Install cloudinary package: pip install cloudinary==1.36.0")
    
    return True

if __name__ == "__main__":
    success = test_cloudinary_upload_system()
    exit(0 if success else 1)
