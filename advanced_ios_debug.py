#!/usr/bin/env python3
"""
Advanced iOS debugging - test specific scenarios that commonly fail on iOS
"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def get_auth_token():
    """Get authentication token"""
    login_data = {"email": "test@Rod Royale.com", "password": "testpassword123"}
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    if response.status_code == 200:
        return response.json()['token']['access_token']
    return None

def test_cors_preflight():
    """Test CORS preflight requests (OPTIONS)"""
    print("🌐 Testing CORS Preflight (OPTIONS request)")
    print("=" * 50)
    
    headers = {
        "Origin": "http://localhost:3000",  # Common frontend origin
        "Access-Control-Request-Method": "POST",
        "Access-Control-Request-Headers": "Authorization, Content-Type"
    }
    
    try:
        response = requests.options(f"{BASE_URL}/catches/", headers=headers)
        print(f"   Status Code: {response.status_code}")
        print("   Response Headers:")
        for key, value in response.headers.items():
            if 'access-control' in key.lower() or 'cors' in key.lower():
                print(f"     {key}: {value}")
        
        if response.status_code == 200:
            print("✅ CORS preflight successful")
            return True
        else:
            print("❌ CORS preflight failed")
            return False
    except Exception as e:
        print(f"❌ CORS preflight error: {e}")
        return False

def test_malformed_json():
    """Test with slightly malformed JSON that might be sent by iOS"""
    print("\n📱 Testing Potential iOS JSON Issues")
    print("=" * 40)
    
    token = get_auth_token()
    if not token:
        print("❌ Cannot get auth token")
        return False
    
    # Test with trailing comma (sometimes iOS SDKs add these)
    test_cases = [
        {
            "name": "Extra whitespace in JSON",
            "data": '''
            {
                "species"  :  "Test Bass"  ,
                "weight"   :  2.5  ,
                "photo_url": "https://example.com/test.jpg"  ,
                "location" : {
                    "lat"  : 43.054013  ,
                    "lng"  : -89.450452
                }  ,
                "shared_with_followers": true
            }
            '''
        },
        {
            "name": "Numbers as strings",
            "data": {
                "species": "String Number Test Bass",
                "weight": "2.5",  # Sometimes iOS sends numbers as strings
                "photo_url": "https://example.com/test.jpg",
                "location": {
                    "lat": "43.054013",
                    "lng": "-89.450452"
                },
                "shared_with_followers": True
            }
        }
    ]
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "User-Agent": "Rod RoyaleApp/1.0 (iOS 17.0; iPhone Simulator)"
    }
    
    results = []
    for test_case in test_cases:
        print(f"\n   Testing: {test_case['name']}")
        
        try:
            if isinstance(test_case['data'], str):
                # Raw JSON string
                response = requests.post(
                    f"{BASE_URL}/catches/",
                    data=test_case['data'],
                    headers=headers
                )
            else:
                # Dict to be JSON encoded
                response = requests.post(
                    f"{BASE_URL}/catches/",
                    json=test_case['data'],
                    headers=headers
                )
            
            if response.status_code == 201:
                print(f"   ✅ {test_case['name']}: SUCCESS")
                results.append(True)
            else:
                print(f"   ❌ {test_case['name']}: FAILED ({response.status_code})")
                try:
                    error = response.json()
                    print(f"      Error: {error.get('detail', 'Unknown error')}")
                except:
                    print(f"      Error text: {response.text[:200]}...")
                results.append(False)
                
        except Exception as e:
            print(f"   ❌ {test_case['name']}: ERROR - {e}")
            results.append(False)
    
    return all(results)

def test_network_conditions():
    """Test network conditions that might affect iOS"""
    print("\n📶 Testing Network Conditions")
    print("=" * 35)
    
    token = get_auth_token()
    if not token:
        print("❌ Cannot get auth token")
        return False
    
    # Test with very short timeout (iOS might timeout faster)
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "User-Agent": "Rod RoyaleApp/1.0 (iOS 17.0; iPhone Simulator)"
    }
    
    catch_data = {
        "species": "Timeout Test Bass",
        "weight": 2.0,
        "photo_url": "https://example.com/test.jpg",
        "location": {"lat": 43.054013, "lng": -89.450452},
        "shared_with_followers": True
    }
    
    # Test with very short timeout
    try:
        print("   Testing with 1 second timeout...")
        response = requests.post(
            f"{BASE_URL}/catches/",
            json=catch_data,
            headers=headers,
            timeout=1
        )
        if response.status_code == 201:
            print("   ✅ Short timeout: SUCCESS")
            return True
        else:
            print(f"   ❌ Short timeout: FAILED ({response.status_code})")
            return False
    except requests.exceptions.Timeout:
        print("   ⚠️  Request timed out - this might be your iOS issue!")
        return False
    except Exception as e:
        print(f"   ❌ Network test error: {e}")
        return False

def test_ssl_certificate():
    """Test SSL certificate issues"""
    print("\n🔐 Testing SSL/HTTPS Issues")
    print("=" * 32)
    
    # Test HTTPS endpoint if available
    https_url = BASE_URL.replace('http://', 'https://')
    
    try:
        response = requests.get(f"{https_url}/", timeout=5)
        if response.status_code == 200:
            print("   ✅ HTTPS endpoint accessible")
            return True
        else:
            print(f"   ❌ HTTPS endpoint returned: {response.status_code}")
            return False
    except requests.exceptions.SSLError as e:
        print(f"   ❌ SSL Error: {e}")
        print("   💡 iOS might be rejecting invalid SSL certificates")
        return False
    except requests.exceptions.ConnectionError:
        print("   ℹ️  HTTPS not configured (using HTTP)")
        return True  # Not an error if HTTPS isn't set up
    except Exception as e:
        print(f"   ❌ HTTPS test error: {e}")
        return False

def test_content_length():
    """Test Content-Length header issues"""
    print("\n📏 Testing Content-Length Header")
    print("=" * 35)
    
    token = get_auth_token()
    if not token:
        return False
    
    catch_data = {
        "species": "Content Length Test Bass",
        "weight": 2.0,
        "photo_url": "https://example.com/test.jpg",
        "location": {"lat": 43.054013, "lng": -89.450452},
        "shared_with_followers": True
    }
    
    json_data = json.dumps(catch_data)
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Content-Length": str(len(json_data)),
        "User-Agent": "Rod RoyaleApp/1.0 (iOS 17.0; iPhone Simulator)"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/catches/",
            data=json_data,
            headers=headers
        )
        
        if response.status_code == 201:
            print("   ✅ Explicit Content-Length: SUCCESS")
            return True
        else:
            print(f"   ❌ Explicit Content-Length: FAILED ({response.status_code})")
            return False
    except Exception as e:
        print(f"   ❌ Content-Length test error: {e}")
        return False

def main():
    print("🔍 Advanced iOS Debugging - Common Mobile Issues")
    print("=" * 60)
    
    tests = [
        ("CORS Preflight", test_cors_preflight),
        ("JSON Formatting", test_malformed_json),
        ("Network Timeout", test_network_conditions),
        ("SSL/HTTPS", test_ssl_certificate),
        ("Content-Length", test_content_length)
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results[test_name] = False
    
    print("\n📊 Advanced Test Results")
    print("=" * 30)
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"   {test_name}: {status}")
    
    # Provide specific guidance
    failed_tests = [name for name, passed in results.items() if not passed]
    if failed_tests:
        print(f"\n🔍 Failed Tests: {', '.join(failed_tests)}")
        print("\n💡 Common iOS Issues & Solutions:")
        
        if "CORS Preflight" in failed_tests:
            print("   • CORS: Check frontend origin in CORS settings")
            print("     - Ensure your iOS app's URL is in BACKEND_CORS_ORIGINS")
        
        if "Network Timeout" in failed_tests:
            print("   • Timeout: iOS might have stricter network timeouts")
            print("     - Increase timeout values in your iOS HTTP client")
        
        if "SSL/HTTPS" in failed_tests:
            print("   • SSL: iOS rejects invalid certificates in production")
            print("     - Use valid SSL certificates or allow insecure connections in dev")
        
        if "JSON Formatting" in failed_tests:
            print("   • JSON: Check your JSON serialization in iOS")
            print("     - Ensure numbers are sent as numbers, not strings")
        
        print("\n🛠️  Next Steps:")
        print("   1. Check iOS network logs in Xcode")
        print("   2. Verify the exact request being sent by iOS")
        print("   3. Compare iOS request headers with working browser requests")
        print("   4. Check for any iOS-specific networking libraries/settings")
    else:
        print("\n✅ All backend tests pass - issue is likely in iOS app code")
        print("\n💡 Check your iOS app for:")
        print("   • Correct API endpoint URLs")
        print("   • Proper JWT token handling")
        print("   • Correct HTTP method (POST)")
        print("   • Proper Content-Type headers")
        print("   • Network reachability")

if __name__ == "__main__":
    main()
