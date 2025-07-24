#!/usr/bin/env python3
"""
Database Management Utility for Catchy Backend
Provides tools for database initialization, seeding, and cleanup
"""

import asyncio
import sys
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
import os

# Default MongoDB settings
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "catchy_db")

async def init_database():
    """Initialize database with indexes"""
    print("🔧 Initializing Catchy database...")
    
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client[DATABASE_NAME]
    
    try:
        # Test connection
        await client.admin.command('ping')
        print("✅ Connected to MongoDB")
        
        # Create indexes
        print("📊 Creating database indexes...")
        
        # User collection indexes
        await db.users.create_index("email", unique=True)
        await db.users.create_index("username", unique=True)
        print("   ✅ User indexes created")
        
        # Catch collection indexes
        await db.catches.create_index("user_id")
        await db.catches.create_index("created_at")
        await db.catches.create_index([("location.lat", 1), ("location.lng", 1)])
        print("   ✅ Catch indexes created")
        
        # Pin collection indexes
        await db.pins.create_index("user_id")
        await db.pins.create_index("catch_id")
        await db.pins.create_index([("location.lat", 1), ("location.lng", 1)])
        print("   ✅ Pin indexes created")
        
        print("🎉 Database initialization complete!")
        
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return False
    finally:
        client.close()
    
    return True

async def seed_database():
    """Seed database with sample data"""
    print("🌱 Seeding database with sample data...")
    
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client[DATABASE_NAME]
    
    try:
        # Sample users
        sample_users = [
            {
                "username": "demo_angler",
                "email": "demo@catchy.com",
                "bio": "Demo angler account for testing",
                "followers": [],
                "following": []
            },
            {
                "username": "bass_master",
                "email": "bass@catchy.com", 
                "bio": "Bass fishing expert from Florida",
                "followers": [],
                "following": []
            }
        ]
        
        # Insert users
        user_results = []
        for user_data in sample_users:
            # Check if user already exists
            existing = await db.users.find_one({"email": user_data["email"]})
            if not existing:
                result = await db.users.insert_one(user_data)
                user_results.append(result.inserted_id)
                print(f"   ✅ Created user: {user_data['username']}")
            else:
                user_results.append(existing["_id"])
                print(f"   ⚠️  User {user_data['username']} already exists")
        
        if len(user_results) >= 1:
            user1_id = user_results[0]
            
            # Sample catches
            sample_catches = [
                {
                    "user_id": user1_id,
                    "species": "Largemouth Bass",
                    "weight": 4.2,
                    "photo_url": "https://example.com/demo-bass.jpg",
                    "location": {"lat": 28.5383, "lng": -81.3792},  # Orlando, FL
                    "shared_with_followers": False,
                    "created_at": datetime.utcnow()
                },
                {
                    "user_id": user1_id,
                    "species": "Rainbow Trout",
                    "weight": 2.1,
                    "photo_url": "https://example.com/demo-trout.jpg",
                    "location": {"lat": 39.7392, "lng": -104.9903},  # Denver, CO
                    "shared_with_followers": True,
                    "created_at": datetime.utcnow()
                }
            ]
            
            # Insert catches
            catch_results = []
            for catch_data in sample_catches:
                result = await db.catches.insert_one(catch_data)
                catch_results.append(result.inserted_id)
                print(f"   ✅ Created catch: {catch_data['species']}")
            
            # Sample pins
            if catch_results:
                sample_pins = [
                    {
                        "user_id": user1_id,
                        "catch_id": catch_results[0],
                        "location": {"lat": 28.5383, "lng": -81.3792},
                        "visibility": "public"
                    }
                ]
                
                for pin_data in sample_pins:
                    await db.pins.insert_one(pin_data)
                    print("   ✅ Created pin for catch")
        
        print("🎉 Database seeding complete!")
        
    except Exception as e:
        print(f"❌ Database seeding failed: {e}")
        return False
    finally:
        client.close()
    
    return True

async def clear_database():
    """Clear all data from database"""
    print("🗑️  Clearing database...")
    
    response = input("⚠️  This will delete ALL data. Are you sure? (type 'yes' to confirm): ")
    if response.lower() != 'yes':
        print("Operation cancelled.")
        return False
    
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client[DATABASE_NAME]
    
    try:
        # Drop all collections
        await db.users.drop()
        await db.catches.drop() 
        await db.pins.drop()
        print("✅ All collections cleared")
        
        # Recreate indexes
        await init_database()
        
    except Exception as e:
        print(f"❌ Database clearing failed: {e}")
        return False
    finally:
        client.close()
    
    return True

async def show_stats():
    """Show database statistics"""
    print("📊 Database Statistics")
    print("=" * 30)
    
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client[DATABASE_NAME]
    
    try:
        # Get collection counts
        user_count = await db.users.count_documents({})
        catch_count = await db.catches.count_documents({})
        pin_count = await db.pins.count_documents({})
        
        print(f"Users: {user_count}")
        print(f"Catches: {catch_count}")
        print(f"Pins: {pin_count}")
        
        # Show recent catches
        if catch_count > 0:
            print("\nRecent Catches:")
            async for catch in db.catches.find().sort("created_at", -1).limit(5):
                user = await db.users.find_one({"_id": catch["user_id"]})
                username = user["username"] if user else "Unknown"
                print(f"  - {catch['species']} ({catch['weight']}lbs) by {username}")
        
    except Exception as e:
        print(f"❌ Error retrieving stats: {e}")
        return False
    finally:
        client.close()
    
    return True

def print_usage():
    """Print usage information"""
    print("Catchy Database Management Utility")
    print("=" * 40)
    print("Usage: python db_manager.py <command>")
    print()
    print("Commands:")
    print("  init    - Initialize database with indexes")
    print("  seed    - Seed database with sample data") 
    print("  clear   - Clear all data from database")
    print("  stats   - Show database statistics")
    print("  help    - Show this help message")

async def main():
    if len(sys.argv) != 2:
        print_usage()
        return
    
    command = sys.argv[1].lower()
    
    if command == "init":
        await init_database()
    elif command == "seed":
        await seed_database()
    elif command == "clear":
        await clear_database()
    elif command == "stats":
        await show_stats()
    elif command == "help":
        print_usage()
    else:
        print(f"❌ Unknown command: {command}")
        print_usage()

if __name__ == "__main__":
    asyncio.run(main())
