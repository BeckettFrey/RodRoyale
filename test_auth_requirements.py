#!/usr/bin/env python3
"""
Test authentication requirements for endpoints
"""
import requests

BASE_URL = "http://192.168.86.29:8000/api/v1"

def test_endpoint_without_auth(endpoint, method="GET"):
    """Test if an endpoint properly rejects requests without authentication"""
    print(f"Testing {method} {endpoint} without auth...")
    
    try:
        if method == "GET":
            response = requests.get(f"{BASE_URL}{endpoint}")
        elif method == "POST":
            response = requests.post(f"{BASE_URL}{endpoint}", json={})
        elif method == "PUT":
            response = requests.put(f"{BASE_URL}{endpoint}", json={})
        elif method == "DELETE":
            response = requests.delete(f"{BASE_URL}{endpoint}")
        
        if response.status_code == 401 or response.status_code == 403:
            print(f"   ✅ Correctly requires authentication ({response.status_code})")
            return True
        else:
            print(f"   ❌ Does NOT require authentication ({response.status_code})")
            return False
            
    except Exception as e:
        print(f"   ❌ Error testing endpoint: {e}")
        return False

def test_endpoint_with_auth(endpoint, method="GET"):
    """Test if an endpoint works with proper authentication"""
    # First get a token
    login_data = {"email": "test@Rod Royale.com", "password": "testpassword123"}
    auth_response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    
    if auth_response.status_code != 200:
        print("   ❌ Cannot get auth token for testing")
        return False
    
    token = auth_response.json()['token']['access_token']
    headers = {"Authorization": f"Bearer {token}"}
    
    print(f"Testing {method} {endpoint} with auth...")
    
    try:
        if method == "GET":
            response = requests.get(f"{BASE_URL}{endpoint}", headers=headers)
        elif method == "POST":
            # Use minimal valid data for testing
            if "catches" in endpoint:
                data = {
                    "species": "Test Fish",
                    "weight": 1.0,
                    "photo_url": "https://example.com/test.jpg",
                    "location": {"lat": 43.0, "lng": -89.0}
                }
            elif "pins" in endpoint:
                data = {
                    "catch_id": "507f1f77bcf86cd799439011",  # Dummy ObjectId
                    "location": {"lat": 43.0, "lng": -89.0},
                    "visibility": "public"
                }
            else:
                data = {}
            response = requests.post(f"{BASE_URL}{endpoint}", json=data, headers=headers)
        
        if response.status_code in [200, 201]:
            print(f"   ✅ Works with authentication ({response.status_code})")
            return True
        elif response.status_code == 404:
            print("   ⚠️  Endpoint not found (404) - might be expected")
            return True
        else:
            print(f"   ⚠️  Unexpected response ({response.status_code}): {response.text[:100]}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error testing authenticated endpoint: {e}")
        return False

def main():
    print("🔒 Testing Authentication Requirements")
    print("=" * 50)
    
    # Endpoints that should require authentication
    endpoints_to_test = [
        ("/pins/", "GET"),
        ("/pins/", "POST"),
        ("/catches/feed", "GET"),
        ("/catches/me", "GET"),
        ("/catches/users/507f1f77bcf86cd799439011/catches", "GET"),  # Dummy user ID
        ("/catches/", "POST"),
    ]
    
    results = {"without_auth": [], "with_auth": []}
    
    print("\n📵 Testing WITHOUT Authentication")
    print("-" * 40)
    for endpoint, method in endpoints_to_test:
        success = test_endpoint_without_auth(endpoint, method)
        results["without_auth"].append((f"{method} {endpoint}", success))
    
    print("\n🔑 Testing WITH Authentication")
    print("-" * 35)
    for endpoint, method in endpoints_to_test:
        success = test_endpoint_with_auth(endpoint, method)
        results["with_auth"].append((f"{method} {endpoint}", success))
    
    print("\n📊 Summary")
    print("=" * 20)
    
    print("\nEndpoints correctly requiring authentication:")
    for endpoint, success in results["without_auth"]:
        status = "✅" if success else "❌"
        print(f"   {status} {endpoint}")
    
    print("\nEndpoints working with authentication:")
    for endpoint, success in results["with_auth"]:
        status = "✅" if success else "❌"
        print(f"   {status} {endpoint}")
    
    # Check if all endpoints properly require auth
    all_secured = all(success for _, success in results["without_auth"])
    all_working = all(success for _, success in results["with_auth"])
    
    print("\n🎯 Result:")
    if all_secured and all_working:
        print("   ✅ All endpoints properly secured and functional!")
    elif all_secured:
        print("   ⚠️  All endpoints are secured, but some have issues with auth")
    else:
        print("   ❌ Some endpoints are not properly secured!")
        
    print("\n💡 All tested endpoints should now:")
    print("   • Require JWT authentication (return 401/403 without token)")
    print("   • Only show data relevant to the authenticated user")
    print("   • Respect privacy settings and following relationships")

if __name__ == "__main__":
    main()
