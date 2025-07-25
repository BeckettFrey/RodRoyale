#!/usr/bin/env python3
"""
Debug script to compare browser vs iOS simulator requests for catch creation
"""
import requests
import json
import tempfile
from PIL import Image
import urllib3

# Disable SSL warnings for self-signed certificates in development
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Try HTTPS first, fallback to HTTP
BASE_URLs = [
    "https://localhost:8000/api/v1",  # HTTPS (preferred)
    "http://localhost:8000/api/v1"   # HTTP (fallback)
]

def get_working_base_url():
    """Find which base URL is working (HTTPS or HTTP)"""
    for base_url in BASE_URLs:
        try:
            # Test with SSL verification disabled for self-signed certs
            response = requests.get(
                base_url.replace('/api/v1', '/health'), 
                timeout=2, 
                verify=False
            )
            if response.status_code == 200:
                print(f"✅ Using: {base_url}")
                return base_url
        except Exception:
            continue
    
    print("❌ No working base URL found")
    return BASE_URLs[1]  # Default to HTTP

BASE_URL = get_working_base_url()

def create_test_image():
    """Create a test image file for upload"""
    img = Image.new('RGB', (800, 600), color='lightblue')
    temp_file = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
    img.save(temp_file.name, 'JPEG')
    temp_file.close()
    return temp_file.name

def get_auth_token():
    """Get authentication token"""
    print("🔑 Getting authentication token...")
    login_data = {
        "email": "test@Rod Royale.com",
        "password": "testpassword123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data, verify=False)
        if response.status_code == 200:
            auth_response = response.json()
            token = auth_response['token']['access_token']
            print("✅ Authentication successful")
            return token
        else:
            print(f"❌ Authentication failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Authentication error: {e}")
        return None

def test_browser_style_request(token):
    """Test catch creation like a browser would do it"""
    print("\n🌐 Testing Browser-style Request")
    print("=" * 40)
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    catch_data = {
        "species": "Browser Test Bass",
        "weight": 2.5,
        "photo_url": "https://example.com/test-image.jpg",
        "location": {
            "lat": 43.054013,
            "lng": -89.450452
        },
        "shared_with_followers": True
    }
    
    print(f"   Request URL: {BASE_URL}/catches/")
    print(f"   Headers: {json.dumps(headers, indent=4)}")
    print(f"   Data: {json.dumps(catch_data, indent=4)}")
    
    try:
        response = requests.post(f"{BASE_URL}/catches/", json=catch_data, headers=headers, verify=False)
        print(f"   Status Code: {response.status_code}")
        print(f"   Response Headers: {dict(response.headers)}")
        
        if response.status_code == 201:
            result = response.json()
            print("✅ Browser request successful!")
            print(f"   Created catch ID: {result.get('_id', 'N/A')}")
            return True
        else:
            print("❌ Browser request failed!")
            try:
                error = response.json()
                print(f"   Error: {json.dumps(error, indent=4)}")
            except Exception:
                print(f"   Error text: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Browser request error: {e}")
        return False

def test_ios_style_request(token):
    """Test catch creation like iOS simulator would do it"""
    print("\n📱 Testing iOS Simulator-style Request")
    print("=" * 40)
    
    # iOS simulatore often uses different User-Agent and may have different header formatting
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "User-Agent": "Rod RoyaleApp/1.0 (iOS 17.0; iPhone Simulator)",
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive"
    }
    
    catch_data = {
        "species": "iOS Test Bass",
        "weight": 3.2,
        "photo_url": "http://172.20.10.7:8000/uploads/test-ios.jpg",  # Local network IP common in simulators
        "location": {
            "lat": 43.054013,
            "lng": -89.450452
        },
        "shared_with_followers": True
    }
    
    print(f"   Request URL: {BASE_URL}/catches/")
    print(f"   Headers: {json.dumps(headers, indent=4)}")
    print(f"   Data: {json.dumps(catch_data, indent=4)}")
    
    try:
        response = requests.post(f"{BASE_URL}/catches/", json=catch_data, headers=headers, verify=False)
        print(f"   Status Code: {response.status_code}")
        print(f"   Response Headers: {dict(response.headers)}")
        
        if response.status_code == 201:
            result = response.json()
            print("✅ iOS request successful!")
            print(f"   Created catch ID: {result.get('_id', 'N/A')}")
            return True
        else:
            print("❌ iOS request failed!")
            try:
                error = response.json()
                print(f"   Error: {json.dumps(error, indent=4)}")
            except Exception:
                print(f"   Error text: {response.text}")
            return False
    except Exception as e:
        print(f"❌ iOS request error: {e}")
        return False

def test_multipart_upload(token):
    """Test the multipart upload endpoint (used by mobile apps for image upload)"""
    print("\n📤 Testing Multipart Upload Endpoint")
    print("=" * 40)
    
    test_image_path = create_test_image()
    print(f"   Created test image: {test_image_path}")
    
    # iOS-style headers for multipart upload
    headers = {
        "Authorization": f"Bearer {token}",
        "User-Agent": "Rod RoyaleApp/1.0 (iOS 17.0; iPhone Simulator)",
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive"
        # Note: Content-Type will be set automatically by requests for multipart
    }
    
    form_data = {
        'species': 'Multipart Bass',
        'weight': 4.1,
        'lat': 43.054013,
        'lng': -89.450452,
        'shared_with_followers': True
    }
    
    try:
        with open(test_image_path, 'rb') as f:
            files = {'file': ('catch.jpg', f, 'image/jpeg')}
            
            print(f"   Request URL: {BASE_URL}/catches/upload-with-image")
            print(f"   Headers: {json.dumps(headers, indent=4)}")
            print(f"   Form data: {form_data}")
            
            response = requests.post(
                f"{BASE_URL}/catches/upload-with-image",
                data=form_data,
                files=files,
                headers=headers,
                verify=False
            )
            
            print(f"   Status Code: {response.status_code}")
            print(f"   Response Headers: {dict(response.headers)}")
            
            if response.status_code == 201:
                result = response.json()
                print("✅ Multipart upload successful!")
                print(f"   Created catch ID: {result.get('_id', 'N/A')}")
                print(f"   Photo URL: {result.get('photo_url', 'N/A')}")
                return True
            else:
                print("❌ Multipart upload failed!")
                try:
                    error = response.json()
                    print(f"   Error: {json.dumps(error, indent=4)}")
                except:
                    print(f"   Error text: {response.text}")
                return False
    except Exception as e:
        print(f"❌ Multipart upload error: {e}")
        return False
    finally:
        import os
        if os.path.exists(test_image_path):
            os.unlink(test_image_path)

def check_server_logs():
    """Display information about checking server logs"""
    print("\n📋 Server Log Analysis")
    print("=" * 30)
    print("To check server logs for differences:")
    print("1. Monitor the uvicorn server output while making requests")
    print("2. Look for differences in:")
    print("   - Request headers")
    print("   - Content-Type handling")
    print("   - JWT token validation")
    print("   - CORS preflight requests")
    print("   - Error messages")
    
def main():
    print("🐟 Rod Royale iOS vs Browser Debug Tool")
    print("=" * 50)
    
    # Get authentication token
    token = get_auth_token()
    if not token:
        print("❌ Cannot proceed without authentication token")
        print("\n💡 Make sure you have a test user registered:")
        print("   Email: test@Rod Royale.com")
        print("   Password: testpassword123")
        return
    
    # Run tests
    browser_success = test_browser_style_request(token)
    ios_success = test_ios_style_request(token)
    multipart_success = test_multipart_upload(token)
    
    # Summary
    print("\n📊 Test Results Summary")
    print("=" * 30)
    print(f"   Browser-style request: {'✅ PASS' if browser_success else '❌ FAIL'}")
    print(f"   iOS-style request: {'✅ PASS' if ios_success else '❌ FAIL'}")
    print(f"   Multipart upload: {'✅ PASS' if multipart_success else '❌ FAIL'}")
    
    if not ios_success and browser_success:
        print("\n🔍 Potential Issues to Investigate:")
        print("   1. JWT token format differences")
        print("   2. Content-Type header handling")
        print("   3. CORS preflight request handling")
        print("   4. User-Agent based filtering")
        print("   5. Network connectivity (simulator vs browser)")
        print("   6. SSL/TLS certificate issues")
    
    check_server_logs()

if __name__ == "__main__":
    main()
