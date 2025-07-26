#!/usr/bin/env python3
"""
Create a test user for debugging
"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def create_test_user():
    print("👤 Creating test user...")
    
    user_data = {
        "username": "testuser",
        "email": "test@RodRoyale.com",
        "password": "testpassword123",
        "bio": "Test user for debugging iOS issues"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/register", json=user_data)
        if response.status_code == 201:
            result = response.json()
            print("✅ Test user created successfully!")
            print(f"   Username: {result['user']['username']}")
            print(f"   Email: {result['user']['email']}")
            print(f"   User ID: {result['user']['_id']}")
            return True
        else:
            print(f"❌ Failed to create user: {response.status_code}")
            try:
                error = response.json()
                print(f"   Error: {json.dumps(error, indent=2)}")
            except:
                print(f"   Error text: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error creating user: {e}")
        return False

if __name__ == "__main__":
    create_test_user()
