#!/usr/bin/env python3
"""
Quick Follow/Unfollow API Test Script
Tests the actual API endpoints for following users
"""

import requests
import json

# Configuration
BASE_URL = "http://localhost:8000/api/v1"
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2ODgzMTY4YWJiOTE5MmY1ODE5YTIwNWQiLCJleHAiOjE3NTM0NzQxMTEsInR5cGUiOiJhY2Nlc3MifQ.YG7YCfJBCtmOuSgjoei0Hl0EwBdG1i4-jlruyvdWRko"

# Test user IDs from the demo (replace with your actual user IDs)
USER1_ID = "6883e334708410222d580c60"  # Mike (follower)
USER2_ID = "6883e334708410222d580c61"  # Sarah (target)

def make_request(method, endpoint, expected_status=200):
    """Make an API request and return the response"""
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
            response = requests.post(url, headers=headers)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers)
        
        print(f"📊 Status: {response.status_code}")
        
        if response.status_code == expected_status:
            print("✅ Success!")
        else:
            print(f"⚠️  Expected {expected_status}, got {response.status_code}")
        
        # Try to parse JSON response
        try:
            data = response.json()
            print(f"📄 Response: {json.dumps(data, indent=2)}")
            return data
        except:
            print(f"📄 Response: {response.text}")
            return response.text
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return None

def test_follow_workflow():
    """Test the complete follow workflow"""
    print("🎣 Testing Follow/Unfollow Workflow")
    print("=" * 50)
    
    # 1. Get initial user states
    print("\n1️⃣  Getting initial user states...")
    mike_before = make_request("GET", f"/users/{USER1_ID}")
    sarah_before = make_request("GET", f"/users/{USER2_ID}")
    
    if mike_before and sarah_before:
        print(f"\n📊 Mike's following count before: {len(mike_before.get('following', []))}")
        print(f"📊 Sarah's followers count before: {len(sarah_before.get('followers', []))}")
    
    # 2. Follow user
    print("\n2️⃣  Mike follows Sarah...")
    follow_result = make_request("POST", f"/users/{USER1_ID}/follow/{USER2_ID}")
    
    # 3. Verify the follow worked
    print("\n3️⃣  Verifying follow relationship...")
    mike_after = make_request("GET", f"/users/{USER1_ID}")
    sarah_after = make_request("GET", f"/users/{USER2_ID}")
    
    if mike_after and sarah_after:
        mike_following = len(mike_after.get('following', []))
        sarah_followers = len(sarah_after.get('followers', []))
        
        print(f"\n📊 Mike's following count after: {mike_following}")
        print(f"📊 Sarah's followers count after: {sarah_followers}")
        
        # Check if Sarah's ID is in Mike's following list
        sarah_in_following = USER2_ID in [str(f) for f in mike_after.get('following', [])]
        # Check if Mike's ID is in Sarah's followers list  
        mike_in_followers = USER1_ID in [str(f) for f in sarah_after.get('followers', [])]
        
        print(f"\n✅ Sarah in Mike's following: {sarah_in_following}")
        print(f"✅ Mike in Sarah's followers: {mike_in_followers}")
        
        if sarah_in_following and mike_in_followers:
            print("🎉 Follow relationship established successfully!")
        else:
            print("❌ Follow relationship not properly established!")
    
    # 4. Test getting followers/following lists
    print("\n4️⃣  Testing followers/following endpoints...")
    make_request("GET", f"/users/{USER2_ID}/followers")  # Sarah's followers
    make_request("GET", f"/users/{USER1_ID}/following")  # Mike's following
    
    # 5. Test unfollow
    print("\n5️⃣  Testing unfollow...")
    unfollow_result = make_request("DELETE", f"/users/{USER1_ID}/follow/{USER2_ID}")
    
    # 6. Verify unfollow worked
    print("\n6️⃣  Verifying unfollow...")
    mike_final = make_request("GET", f"/users/{USER1_ID}")
    sarah_final = make_request("GET", f"/users/{USER2_ID}")
    
    if mike_final and sarah_final:
        mike_following_final = len(mike_final.get('following', []))
        sarah_followers_final = len(sarah_final.get('followers', []))
        
        print(f"\n📊 Mike's following count final: {mike_following_final}")
        print(f"📊 Sarah's followers count final: {sarah_followers_final}")
        
        if mike_following_final == 0 and sarah_followers_final == 0:
            print("🎉 Unfollow worked successfully!")
        else:
            print("❌ Unfollow may not have worked properly!")

if __name__ == "__main__":
    print("🚀 Starting Follow/Unfollow API Test")
    print(f"🎯 Using User IDs: {USER1_ID} -> {USER2_ID}")
    print("⚠️  Make sure your API server is running on localhost:8000")
    
    input("\nPress Enter to continue...")
    
    try:
        test_follow_workflow()
        print("\n✅ Test completed!")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
