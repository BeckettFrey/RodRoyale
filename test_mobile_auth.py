#!/usr/bin/env python3
"""
Test script to mimic mobile app behavior for debugging JWT authentication
"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def test_mobile_auth_flow():
    print("📱 Testing Mobile App Authentication Flow")
    print("=" * 50)
    
    # Step 1: Login to get token
    print("\n1. Logging in to get JWT token...")
    login_data = {
        "email": "test@Rod Royale.com",
        "password": "testpassword123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        if response.status_code == 200:
            auth_response = response.json()
            access_token = auth_response['token']['access_token']
            print("✅ Login successful!")
            print(f"   Token: {access_token[:50]}...")
        else:
            print(f"❌ Login failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Login error: {e}")
        return False
    
    # Step 2: Test catch creation exactly like your mobile app
    print("\n2. Testing catch creation (like mobile app)...")
    catch_data = {
        "species": "Mobile Test Fish",
        "weight": 3.0,
        "photo_url": "http://172.20.10.7:8000/uploads/test-image.jpg",
        "location": {
            "lat": 43.054013148362685,
            "lng": -89.45045256464
        },
        "shared_with_followers": True
    }
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    print(f"   Request URL: {BASE_URL}/catches")
    print(f"   Headers: {headers}")
    print(f"   Data: {json.dumps(catch_data, indent=2)}")
    
    try:
        response = requests.post(f"{BASE_URL}/catches", json=catch_data, headers=headers)
        print(f"   Response Status: {response.status_code}")
        print(f"   Response Headers: {dict(response.headers)}")
        
        if response.status_code == 201:
            catch_response = response.json()
            print("✅ Catch created successfully!")
            print(f"   Created catch: {catch_response['species']}")
            return True
        else:
            print(f"❌ Catch creation failed: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error details: {json.dumps(error_data, indent=2)}")
            except Exception:
                print(f"   Error text: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Catch creation error: {e}")
        return False

def test_token_validation():
    print("\n3. Testing different token formats...")
    
    # Get a valid token first
    login_data = {"email": "test@Rod Royale.com", "password": "testpassword123"}
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    access_token = response.json()['token']['access_token']
    
    test_cases = [
        {"name": "Valid Bearer token", "header": f"Bearer {access_token}", "should_work": True},
        {"name": "Token without Bearer", "header": access_token, "should_work": False},
        {"name": "Malformed Bearer", "header": f"bearer {access_token}", "should_work": False},
        {"name": "Empty token", "header": "", "should_work": False},
    ]
    
    for test_case in test_cases:
        headers = {"Authorization": test_case["header"]} if test_case["header"] else {}
        
        try:
            response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
            success = response.status_code == 200
            expected = test_case["should_work"]
            
            status = "✅" if success == expected else "❌"
            print(f"   {status} {test_case['name']}: {response.status_code}")
            
            if not success and response.status_code != 401:
                print(f"      Unexpected error: {response.text}")
                
        except Exception as e:
            print(f"   ❌ {test_case['name']}: Exception - {e}")

if __name__ == "__main__":
    print("🚀 Starting mobile authentication debugging...")
    success = test_mobile_auth_flow()
    test_token_validation()
    
    if success:
        print("\n✅ Mobile authentication flow works correctly!")
        print("💡 If your mobile app is still failing, check:")
        print("   1. Token is sent as 'Bearer <token>' in Authorization header")
        print("   2. Content-Type is 'application/json'")
        print("   3. Token hasn't expired (30 minutes)")
        print("   4. Network connectivity to the API server")
    else:
        print("\n❌ Mobile authentication flow failed!")
    
    print("\n📚 Check server logs for more details")
