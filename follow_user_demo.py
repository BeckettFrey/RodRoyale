#!/usr/bin/env python3
"""
Follow User Example & Validation Script
Demonstrates how to follow another user and validates that both users are updated correctly
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
import os
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

# Database configuration
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "rod_royale_db")
BASE_URL = "http://localhost:8000/api/v1"

async def create_test_users(db):
    """Create two test users for the follow demonstration"""
    print("👥 Creating test users...")
    
    # User 1 - The follower
    user1 = {
        "_id": ObjectId(),
        "username": "angler_mike",
        "email": "mike@example.com",
        "password_hash": "$2b$12$dummy_hash_for_mike",
        "bio": "Love bass fishing!",
        "followers": [],
        "following": []
    }
    
    # User 2 - The one being followed
    user2 = {
        "_id": ObjectId(),
        "username": "fishing_sarah",
        "email": "sarah@example.com", 
        "password_hash": "$2b$12$dummy_hash_for_sarah",
        "bio": "Professional angler and fishing guide",
        "followers": [],
        "following": []
    }
    
    # Insert users
    await db.users.insert_many([user1, user2])
    
    print(f"✅ Created user1 (mike): {user1['_id']}")
    print(f"✅ Created user2 (sarah): {user2['_id']}")
    
    return user1, user2

async def get_user_details(db, user_id, username):
    """Get and display user details"""
    user = await db.users.find_one({"_id": user_id})
    if user:
        print(f"\n📊 {username} ({user_id}):")
        print(f"   👤 Username: {user['username']}")
        print(f"   📧 Email: {user['email']}")
        print(f"   👥 Followers: {len(user.get('followers', []))} users")
        print(f"   ➡️  Following: {len(user.get('following', []))} users")
        
        if user.get('followers'):
            print(f"   📋 Follower IDs: {[str(f) for f in user['followers']]}")
        if user.get('following'):
            print(f"   📋 Following IDs: {[str(f) for f in user['following']]}")
    return user

async def simulate_follow_action(db, follower_id, target_id):
    """Simulate the follow action that happens in the API"""
    print("\n🔄 Simulating follow action...")
    print(f"   👤 {follower_id} is following {target_id}")
    
    # This simulates what happens in the API endpoint
    # Add to following list (follower's perspective)
    result1 = await db.users.update_one(
        {"_id": follower_id},
        {"$addToSet": {"following": target_id}}
    )
    
    # Add to followers list (target's perspective)  
    result2 = await db.users.update_one(
        {"_id": target_id},
        {"$addToSet": {"followers": follower_id}}
    )
    
    print(f"✅ Updated follower's following list: {result1.modified_count} document(s)")
    print(f"✅ Updated target's followers list: {result2.modified_count} document(s)")
    
    return result1.modified_count > 0 or result2.modified_count > 0

def create_curl_examples(user1_id, user2_id):
    """Create curl command examples"""
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2ODgzMTY4YWJiOTE5MmY1ODE5YTIwNWQiLCJleHAiOjE3NTM0NzQxMTEsInR5cGUiOiJhY2Nlc3MifQ.YG7YCfJBCtmOuSgjoei0Hl0EwBdG1i4-jlruyvdWRko"
    
    print("\n🌐 CURL COMMAND EXAMPLES:")
    print("=" * 60)
    
    print("\n1️⃣  Follow user (mike follows sarah):")
    print(f"curl -X POST \"{BASE_URL}/users/{user1_id}/follow/{user2_id}\" \\")
    print(f"  -H \"Authorization: Bearer {token}\" \\")
    print("  -H \"Content-Type: application/json\"")
    
    print("\n2️⃣  Get mike's profile (check following):")
    print(f"curl -X GET \"{BASE_URL}/users/{user1_id}\" \\")
    print(f"  -H \"Authorization: Bearer {token}\"")
    
    print("\n3️⃣  Get sarah's profile (check followers):")
    print(f"curl -X GET \"{BASE_URL}/users/{user2_id}\" \\")
    print(f"  -H \"Authorization: Bearer {token}\"")
    
    print("\n4️⃣  Get sarah's followers list:")
    print(f"curl -X GET \"{BASE_URL}/users/{user2_id}/followers\" \\")
    print(f"  -H \"Authorization: Bearer {token}\"")
    
    print("\n5️⃣  Get mike's following list:")
    print(f"curl -X GET \"{BASE_URL}/users/{user1_id}/following\" \\")
    print(f"  -H \"Authorization: Bearer {token}\"")
    
    print("\n6️⃣  Unfollow user (mike unfollows sarah):")
    print(f"curl -X DELETE \"{BASE_URL}/users/{user1_id}/follow/{user2_id}\" \\")
    print(f"  -H \"Authorization: Bearer {token}\"")

async def validate_follow_relationship(db, follower_id, target_id, follower_name, target_name):
    """Validate that the follow relationship exists in both users"""
    print("\n🔍 VALIDATION: Checking follow relationship...")
    
    follower = await db.users.find_one({"_id": follower_id})
    target = await db.users.find_one({"_id": target_id})
    
    # Check if target is in follower's following list
    following_check = target_id in follower.get('following', [])
    
    # Check if follower is in target's followers list  
    followers_check = follower_id in target.get('followers', [])
    
    print(f"✅ {follower_name} has {target_name} in following list: {following_check}")
    print(f"✅ {target_name} has {follower_name} in followers list: {followers_check}")
    
    if following_check and followers_check:
        print("🎉 SUCCESS: Follow relationship is properly established!")
        return True
    else:
        print("❌ FAILURE: Follow relationship is incomplete!")
        return False

async def main():
    """Main demonstration function"""
    print("🎣 Rod Royale Backend - Follow User Demo & Validation")
    print("=" * 60)
    print(f"⏰ Demo started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Connect to database
        client = AsyncIOMotorClient(MONGODB_URL)
        db = client[DATABASE_NAME]
        
        # Test connection
        await client.admin.command('ping')
        print("✅ Connected to MongoDB")
        
        # Create test users
        user1, user2 = await create_test_users(db)
        user1_id = user1["_id"]
        user2_id = user2["_id"]
        
        print("\n" + "=" * 60)
        print("📊 BEFORE FOLLOWING:")
        await get_user_details(db, user1_id, "Mike (Follower)")
        await get_user_details(db, user2_id, "Sarah (Target)")
        
        print("\n" + "=" * 60)
        print("🔄 PERFORMING FOLLOW ACTION:")
        success = await simulate_follow_action(db, user1_id, user2_id)
        
        if success:
            print("\n" + "=" * 60)
            print("📊 AFTER FOLLOWING:")
            await get_user_details(db, user1_id, "Mike (Follower)")
            await get_user_details(db, user2_id, "Sarah (Target)")
            
            print("\n" + "=" * 60)
            # Validate the relationship
            validation_success = await validate_follow_relationship(
                db, user1_id, user2_id, "Mike", "Sarah"
            )
            
            if validation_success:
                print("\n✅ DEMO COMPLETED SUCCESSFULLY!")
                print("Both users have been updated correctly.")
            else:
                print("\n❌ DEMO FAILED!")
                print("Follow relationship was not established properly.")
        
        # Generate curl examples
        create_curl_examples(str(user1_id), str(user2_id))
        
        print("\n📝 Test users created with IDs:")
        print(f"   Mike (Follower): {user1_id}")
        print(f"   Sarah (Target): {user2_id}")
        print("\n💡 You can use these IDs to test the API endpoints!")
        
        # Close connection
        client.close()
        
    except Exception as e:
        print(f"❌ Error during demo: {e}")
        return False
    
    return True

if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n\n⏹️  Demo cancelled by user")
        exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        exit(1)
