#!/usr/bin/env python3
"""
Account Deletion Test & Demo
Shows how users can delete their account and the cascading effects
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

async def create_test_scenario(db):
    """Create a comprehensive test scenario with multiple users and relationships"""
    print("👥 Creating test scenario for account deletion...")
    
    # User to be deleted (has followers, following, catches, pins)
    target_user = {
        "_id": ObjectId(),
        "username": "delete_me_user",
        "email": "deleteme@example.com",
        "password_hash": "$2b$12$dummy_hash_for_delete_user",
        "bio": "I will be deleted soon!",
        "followers": [],
        "following": []
    }
    
    # User 1 - Follows the target user
    follower1 = {
        "_id": ObjectId(),
        "username": "follower_one",
        "email": "follower1@example.com", 
        "password_hash": "$2b$12$dummy_hash_for_follower1",
        "bio": "I follow delete_me_user",
        "followers": [],
        "following": [target_user["_id"]]
    }
    
    # User 2 - Followed by the target user
    followed_user = {
        "_id": ObjectId(),
        "username": "followed_user",
        "email": "followed@example.com",
        "password_hash": "$2b$12$dummy_hash_for_followed",
        "bio": "delete_me_user follows me",
        "followers": [target_user["_id"]],
        "following": []
    }
    
    # Set up relationships
    target_user["followers"] = [follower1["_id"]]
    target_user["following"] = [followed_user["_id"]]
    
    # Insert users
    await db.users.insert_many([target_user, follower1, followed_user])
    
    # Create catches for target user
    catches = [
        {
            "_id": ObjectId(),
            "user_id": target_user["_id"],
            "species": "Bass",
            "weight": 3.2,
            "photo_url": "https://example.com/bass1.jpg",
            "location": {"lat": 40.7128, "lng": -74.0060},
            "shared_with_followers": True,
            "add_to_map": True,
            "created_at": datetime.utcnow()
        },
        {
            "_id": ObjectId(),
            "user_id": target_user["_id"],
            "species": "Trout",
            "weight": 1.8,
            "photo_url": "https://example.com/trout1.jpg",
            "location": {"lat": 41.8781, "lng": -87.6298},
            "shared_with_followers": False,
            "add_to_map": False,
            "created_at": datetime.utcnow()
        }
    ]
    
    await db.catches.insert_many(catches)
    
    # Create pins for target user
    pins = [
        {
            "_id": ObjectId(),
            "user_id": target_user["_id"],
            "catch_id": catches[0]["_id"],
            "location": {"lat": 40.7128, "lng": -74.0060},
            "visibility": "public"
        }
    ]
    
    await db.pins.insert_many(pins)
    
    print(f"✅ Created target user: {target_user['_id']}")
    print(f"✅ Created follower: {follower1['_id']}")
    print(f"✅ Created followed user: {followed_user['_id']}")
    print(f"✅ Created {len(catches)} catches")
    print(f"✅ Created {len(pins)} pins")
    
    return target_user, follower1, followed_user

async def show_before_state(db, target_user_id, follower_id, followed_id):
    """Show the state before deletion"""
    print("\n📊 STATE BEFORE DELETION:")
    print("=" * 50)
    
    # Target user stats
    target = await db.users.find_one({"_id": target_user_id})
    catches_count = await db.catches.count_documents({"user_id": target_user_id})
    pins_count = await db.pins.count_documents({"user_id": target_user_id})
    
    print(f"\n🎯 Target User ({target['username']}):")
    print(f"   👥 Followers: {len(target.get('followers', []))}")
    print(f"   ➡️  Following: {len(target.get('following', []))}")
    print(f"   🎣 Catches: {catches_count}")
    print(f"   📍 Pins: {pins_count}")
    
    # Follower stats
    follower = await db.users.find_one({"_id": follower_id})
    print(f"\n👤 Follower ({follower['username']}):")
    print(f"   ➡️  Following: {len(follower.get('following', []))}")
    print(f"   📋 Following IDs: {[str(f) for f in follower.get('following', [])]}")
    
    # Followed user stats
    followed = await db.users.find_one({"_id": followed_id})
    print(f"\n👥 Followed User ({followed['username']}):")
    print(f"   👥 Followers: {len(followed.get('followers', []))}")
    print(f"   📋 Follower IDs: {[str(f) for f in followed.get('followers', [])]}")

async def simulate_account_deletion(db, target_user_id):
    """Simulate the account deletion process"""
    print("\n🗑️  SIMULATING ACCOUNT DELETION...")
    print("=" * 50)
    
    # Get user data before deletion
    user = await db.users.find_one({"_id": target_user_id})
    if not user:
        print("❌ User not found!")
        return False
    
    print(f"🔍 Found user: {user['username']}")
    
    # Step 1: Remove user from followers' following lists
    followers = user.get("followers", [])
    if followers:
        result1 = await db.users.update_many(
            {"_id": {"$in": followers}},
            {"$pull": {"following": target_user_id}}
        )
        print(f"✅ Updated {result1.modified_count} followers' following lists")
    
    # Step 2: Remove user from following users' followers lists
    following = user.get("following", [])
    if following:
        result2 = await db.users.update_many(
            {"_id": {"$in": following}},
            {"$pull": {"followers": target_user_id}}
        )
        print(f"✅ Updated {result2.modified_count} users' followers lists")
    
    # Step 3: Delete all user's catches
    catches_result = await db.catches.delete_many({"user_id": target_user_id})
    print(f"✅ Deleted {catches_result.deleted_count} catches")
    
    # Step 4: Delete all user's pins
    pins_result = await db.pins.delete_many({"user_id": target_user_id})
    print(f"✅ Deleted {pins_result.deleted_count} pins")
    
    # Step 5: Delete the user account
    user_result = await db.users.delete_one({"_id": target_user_id})
    print(f"✅ Deleted user account: {user_result.deleted_count} user")
    
    print("\n🎉 Account deletion completed successfully!")
    return True

async def show_after_state(db, follower_id, followed_id):
    """Show the state after deletion"""
    print("\n📊 STATE AFTER DELETION:")
    print("=" * 50)
    
    # Follower stats
    follower = await db.users.find_one({"_id": follower_id})
    print(f"\n👤 Follower ({follower['username']}):")
    print(f"   ➡️  Following: {len(follower.get('following', []))}")
    print(f"   📋 Following IDs: {[str(f) for f in follower.get('following', [])]}")
    
    # Followed user stats
    followed = await db.users.find_one({"_id": followed_id})
    print(f"\n👥 Followed User ({followed['username']}):")
    print(f"   👥 Followers: {len(followed.get('followers', []))}")
    print(f"   📋 Follower IDs: {[str(f) for f in followed.get('followers', [])]}")

def show_curl_example():
    """Show curl command for account deletion"""
    print("\n🌐 CURL COMMAND FOR ACCOUNT DELETION:")
    print("=" * 60)
    
    token = "YOUR_JWT_TOKEN_HERE"
    
    print("\n⚠️  DELETE YOUR ACCOUNT:")
    print(f"curl -X DELETE \"{BASE_URL}/users/me\" \\")
    print(f"  -H \"Authorization: Bearer {token}\" \\")
    print("  -H \"Content-Type: application/json\"")
    
    print("\n🚨 WARNING: This action cannot be undone!")
    print("   • Deletes your user account permanently")
    print("   • Deletes all your catches and pins")
    print("   • Removes you from all followers' following lists")
    print("   • Removes you from all followed users' followers lists")

async def main():
    """Main demonstration function"""
    print("🗑️  Rod Royale Backend - Account Deletion Demo")
    print("=" * 60)
    print(f"⏰ Demo started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Connect to database
        client = AsyncIOMotorClient(MONGODB_URL)
        db = client[DATABASE_NAME]
        
        # Test connection
        await client.admin.command('ping')
        print("✅ Connected to MongoDB")
        
        # Create test scenario
        target_user, follower1, followed_user = await create_test_scenario(db)
        target_user_id = target_user["_id"]
        follower_id = follower1["_id"]
        followed_id = followed_user["_id"]
        
        # Show before state
        await show_before_state(db, target_user_id, follower_id, followed_id)
        
        # Simulate account deletion
        success = await simulate_account_deletion(db, target_user_id)
        
        if success:
            # Show after state
            await show_after_state(db, follower_id, followed_id)
            
            print("\n✅ DEMO COMPLETED SUCCESSFULLY!")
            print("Account deletion properly cleaned up all relationships!")
        else:
            print("\n❌ DEMO FAILED!")
            print("Account deletion encountered errors.")
        
        # Show curl example
        show_curl_example()
        
        print("\n📝 Test users created with IDs:")
        print(f"   Target (deleted): {target_user_id}")
        print(f"   Follower: {follower_id}")
        print(f"   Followed: {followed_id}")
        
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
