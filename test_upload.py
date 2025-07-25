#!/usr/bin/env python3
"""
Test script for the image upload endpoint
"""
import requests
from PIL import Image
import io

def create_test_image():
    """Create a simple test image"""
    # Create a simple 100x100 red image
    img = Image.new('RGB', (100, 100), color='red')
    
    # Save to bytes
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='JPEG')
    img_bytes.seek(0)
    
    return img_bytes

def test_image_upload():
    """Test the image upload endpoint"""
    base_url = "http://localhost:8000"
    upload_url = f"{base_url}/api/v1/upload/image"
    
    # Create test image
    test_image = create_test_image()
    
    # Prepare the file for upload
    files = {
        'file': ('test_image.jpg', test_image, 'image/jpeg')
    }
    
    try:
        # Make the upload request
        response = requests.post(upload_url, files=files)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Upload successful!")
            print(f"Image URL: {result['url']}")
            
            # Test accessing the uploaded image
            image_url = f"{base_url}{result['url']}"
            img_response = requests.get(image_url)
            
            if img_response.status_code == 200:
                print("✅ Image access successful!")
                print(f"Image accessible at: {image_url}")
            else:
                print(f"❌ Failed to access image: {img_response.status_code}")
                
        else:
            print(f"❌ Upload failed: {response.status_code}")
            print(f"Error: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed. Make sure the FastAPI server is running on localhost:8000")
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")

if __name__ == "__main__":
    print("Testing image upload endpoint...")
    test_image_upload()
