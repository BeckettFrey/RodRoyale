#!/usr/bin/env python3
"""
Account Deletion API Test
Tests the DELETE /users/me endpoint
"""

import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000/api/v1"
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2ODgzMTY4YWJiOTE5MmY1ODE5YTIwNWQiLCJleHAiOjE3NTM0NzQxMTEsInR5cGUiOiJhY2Nlc3MifQ.YG7YCfJBCtmOuSgjoei0Hl0EwBdG1i4-jlruyvdWRko"

def test_account_deletion():
    """Test account deletion endpoint"""
    print("🗑️  Testing Account Deletion Endpoint")
    print("=" * 50)
    
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }
    
    # First, check current user info
    print("\n1️⃣  Getting current user info before deletion...")
    response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
    if response.status_code == 200:
        user_data = response.json()
        print(f"✅ Current user: {user_data.get('username', 'Unknown')}")
        user_id = user_data.get('id')
    else:
        print(f"❌ Failed to get user info: {response.status_code}")
        return
    
    # Show warning
    print(f"\n⚠️  WARNING: About to delete account!")
    print(f"   User ID: {user_id}")
    print(f"   This action cannot be undone!")
    
    # Ask for confirmation
    confirm = input("\nType 'DELETE' to proceed with account deletion: ")
    if confirm != "DELETE":
        print("❌ Account deletion cancelled")
        return
    
    # Perform deletion
    print(f"\n2️⃣  Deleting account...")
    delete_response = requests.delete(f"{BASE_URL}/users/me", headers=headers)
    
    print(f"📊 Delete Status: {delete_response.status_code}")
    
    if delete_response.status_code == 204:
        print("✅ Account deleted successfully!")
        
        # Try to access the account (should fail)
        print(f"\n3️⃣  Verifying deletion...")
        verify_response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
        
        if verify_response.status_code == 401 or verify_response.status_code == 404:
            print("✅ Verification successful - account no longer exists")
        else:
            print(f"⚠️  Unexpected verification result: {verify_response.status_code}")
            
    elif delete_response.status_code == 401:
        print("❌ Authentication failed - token may be expired")
    else:
        print(f"❌ Deletion failed: {delete_response.status_code}")
        try:
            error_data = delete_response.json()
            print(f"📄 Error details: {json.dumps(error_data, indent=2)}")
        except:
            print(f"📄 Error response: {delete_response.text}")

def show_endpoint_details():
    """Show endpoint details and usage"""
    print("\n📋 ACCOUNT DELETION ENDPOINT DETAILS:")
    print("=" * 60)
    
    print("\n🔗 Endpoint: DELETE /api/v1/users/me")
    print("🔐 Authentication: Required (JWT token)")
    print("📄 Response: 204 No Content (success)")
    print("⚠️  Irreversible: Yes - no way to undo!")
    
    print("\n🗑️  What gets deleted:")
    print("   • Your user account")
    print("   • All your catches (fishing posts)")
    print("   • All your pins on the map")
    print("   • All your uploaded photos")
    
    print("\n🔄 Relationship cleanup:")
    print("   • Removes you from all followers' following lists")
    print("   • Removes you from all followed users' followers lists")
    print("   • Updates follower/following counts for affected users")
    
    print(f"\n🌐 Curl Example:")
    print(f"curl -X DELETE \"{BASE_URL}/users/me\" \\")
    print(f"  -H \"Authorization: Bearer YOUR_TOKEN\" \\")
    print(f"  -H \"Content-Type: application/json\"")

def main():
    """Main test function"""
    print("🗑️  Catchy API - Account Deletion Test")
    print("=" * 60)
    print(f"⏰ Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("⚠️  Make sure your API server is running on localhost:8000")
    
    # Show endpoint details
    show_endpoint_details()
    
    # Ask if user wants to test (dangerous!)
    print(f"\n🚨 DANGER ZONE:")
    print(f"The following test will PERMANENTLY DELETE the authenticated user account!")
    
    proceed = input("\nDo you want to proceed with the deletion test? (y/N): ").lower().strip()
    
    if proceed in ['y', 'yes']:
        test_account_deletion()
    else:
        print("✅ Test skipped - account is safe!")
    
    print(f"\n✅ Test completed at: {datetime.now().strftime('%H:%M:%S')}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️  Test cancelled by user")
    except Exception as e:
        print(f"\n💥 Error: {e}")
