#!/usr/bin/env python3
"""
Database Clearing Script for Catchy Backend
Clears all collections to start with a fresh database
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database configuration
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "catchy_db")

async def clear_database():
    """Clear all collections in the database"""
    print("🗑️  Clearing Catchy Database")
    print("=" * 40)
    
    try:
        # Connect to MongoDB
        client = AsyncIOMotorClient(MONGODB_URL)
        db = client[DATABASE_NAME]
        
        # Get all collection names
        collections = await db.list_collection_names()
        
        if not collections:
            print("📭 Database is already empty")
            return True
        
        print(f"📋 Found collections: {', '.join(collections)}")
        
        # Clear each collection
        for collection_name in collections:
            collection = db[collection_name]
            result = await collection.delete_many({})
            print(f"✅ Cleared {collection_name}: {result.deleted_count} documents deleted")
        
        print("\n" + "=" * 40)
        print("🎉 Database cleared successfully!")
        print("Ready for fresh API testing")
        
        # Close the connection
        client.close()
        return True
        
    except Exception as e:
        print(f"❌ Error clearing database: {e}")
        return False

def run_api_tests():
    """Run the API test script after clearing database"""
    import subprocess
    import sys
    
    print("\n🚀 Starting API tests...")
    try:
        # Run the test script
        result = subprocess.run([sys.executable, "test_api.py"], 
                              capture_output=False, 
                              text=True)
        return result.returncode == 0
    except FileNotFoundError:
        print("❌ test_api.py not found. Make sure it's in the same directory.")
        return False
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return False

async def main():
    """Main function to clear database and optionally run tests"""
    print("🎣 Catchy Backend - Database Reset & Test")
    print("=" * 50)
    
    # Clear the database
    success = await clear_database()
    
    if not success:
        print("❌ Database clearing failed. Exiting.")
        return False
    
    # Ask if user wants to run tests
    print("\n" + "=" * 50)
    run_tests = input("🤔 Would you like to run API tests now? (y/N): ").lower().strip()
    
    if run_tests in ['y', 'yes']:
        success = run_api_tests()
        if success:
            print("\n🎉 All tests completed successfully!")
        else:
            print("\n⚠️  Some tests may have failed. Check output above.")
    else:
        print("\n✅ Database cleared. You can now run your tests manually.")
    
    return success

if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n\n⏹️  Operation cancelled by user")
        exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        exit(1)