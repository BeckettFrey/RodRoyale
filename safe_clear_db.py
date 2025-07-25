#!/usr/bin/env python3
"""
Safe Database Clearing Script for Rod Royale Backend
Clears all collections with multiple safety confirmations
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

# Database configuration
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "rod_royale_db")

def get_user_confirmation():
    """Get user confirmation with multiple safety prompts"""
    print("🚨" + "=" * 60 + "🚨")
    print("⚠️  WARNING: DATABASE DESTRUCTION IMMINENT ⚠️")
    print("🚨" + "=" * 60 + "🚨")
    print()
    print("This script will PERMANENTLY DELETE ALL DATA from:")
    print(f"📍 Database: {DATABASE_NAME}")
    print(f"🔗 MongoDB URL: {MONGODB_URL}")
    print()
    print("The following collections will be COMPLETELY ERASED:")
    print("🗂️  • users (all user accounts)")
    print("🎣 • catches (all fish catches)")
    print("📍 • pins (all map pins)")
    print("📊 • Any other collections in the database")
    print()
    print("💀 THIS ACTION CANNOT BE UNDONE! 💀")
    print()
    
    # First confirmation
    print("Step 1/3: Are you absolutely sure you want to continue?")
    response1 = input("Type 'YES' (all caps) to continue: ").strip()
    if response1 != "YES":
        print("❌ Operation cancelled. Database remains unchanged.")
        return False
    
    print()
    # Second confirmation with database name
    print("Step 2/3: Confirm database name")
    print(f"You are about to delete database: {DATABASE_NAME}")
    response2 = input(f"Type the database name '{DATABASE_NAME}' exactly: ").strip()
    if response2 != DATABASE_NAME:
        print("❌ Database name doesn't match. Operation cancelled.")
        return False
    
    print()
    # Final confirmation
    print("Step 3/3: Final confirmation")
    print("⚠️  LAST CHANCE TO CANCEL ⚠️")
    print("This is your final warning before all data is destroyed.")
    response3 = input("Type 'DELETE EVERYTHING' to proceed: ").strip()
    if response3 != "DELETE EVERYTHING":
        print("❌ Final confirmation failed. Operation cancelled.")
        return False
    
    print()
    print("🔥 Confirmations received. Proceeding with database destruction...")
    return True

async def get_database_stats(db):
    """Get database statistics before clearing"""
    stats = {}
    collections = await db.list_collection_names()
    
    for collection_name in collections:
        collection = db[collection_name]
        count = await collection.count_documents({})
        stats[collection_name] = count
    
    return stats

async def clear_database():
    """Clear all collections in the database"""
    print("🔥 Starting database destruction process...")
    print("=" * 50)
    
    try:
        # Connect to MongoDB
        client = AsyncIOMotorClient(MONGODB_URL)
        db = client[DATABASE_NAME]
        
        # Test connection
        await client.admin.command('ping')
        print("✅ Connected to MongoDB")
        
        # Get database statistics
        print("\n📊 Getting database statistics...")
        stats = await get_database_stats(db)
        
        if not stats:
            print("📭 Database is already empty - nothing to clear")
            client.close()
            return True
        
        print("\n📋 Current database contents:")
        total_documents = 0
        for collection_name, count in stats.items():
            print(f"   📁 {collection_name}: {count:,} documents")
            total_documents += count
        
        print(f"\n🔢 Total documents to be deleted: {total_documents:,}")
        
        if total_documents == 0:
            print("📭 No documents found - database is effectively empty")
            client.close()
            return True
        
        # Add a small delay for dramatic effect
        print("\n⏳ Starting destruction in 3 seconds...")
        await asyncio.sleep(1)
        print("⏳ 2...")
        await asyncio.sleep(1)
        print("⏳ 1...")
        await asyncio.sleep(1)
        print("💥 DESTROYING DATABASE NOW!")
        print()
        
        # Clear each collection
        deleted_total = 0
        for collection_name in stats.keys():
            collection = db[collection_name]
            result = await collection.delete_many({})
            deleted_count = result.deleted_count
            deleted_total += deleted_count
            print(f"🗑️  {collection_name}: {deleted_count:,} documents deleted")
        
        print("\n" + "=" * 50)
        print("🎉 DATABASE DESTRUCTION COMPLETE!")
        print(f"💀 Total documents obliterated: {deleted_total:,}")
        print("🆕 Database is now completely empty and ready for fresh data")
        print("=" * 50)
        
        # Close the connection
        client.close()
        return True
        
    except Exception as e:
        print(f"❌ Error during database destruction: {e}")
        return False

def create_backup_reminder():
    """Remind user about backups (just a message)"""
    print("\n💡 PRO TIP FOR NEXT TIME:")
    print("Consider creating a backup before clearing:")
    print("   mongodump --uri=\"{MONGODB_URL}\" --db={DATABASE_NAME}")
    print("   (This is just a reminder - no backup was created)")

async def main():
    """Main function with safety confirmations"""
    print("🎣 Rod Royale Backend - SAFE Database Destroyer")
    print(f"⏰ Script started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Get user confirmation
    if not get_user_confirmation():
        print("\n✅ Operation safely cancelled. Your data is safe!")
        return False
    
    # Clear the database
    print(f"\n⏰ Destruction started at: {datetime.now().strftime('%H:%M:%S')}")
    success = await clear_database()
    
    if success:
        print(f"⏰ Destruction completed at: {datetime.now().strftime('%H:%M:%S')}")
        create_backup_reminder()
        
        # Ask about running tests
        print("\n" + "=" * 50)
        run_tests = input("🤔 Run API tests with fresh database? (y/N): ").lower().strip()
        
        if run_tests in ['y', 'yes']:
            print("\n🚀 You can now run: python test_api.py")
        
        print("\n🎉 All done! Database is fresh and ready for testing.")
    else:
        print(f"⏰ Operation failed at: {datetime.now().strftime('%H:%M:%S')}")
        print("❌ Database clearing failed. Check the error messages above.")
    
    return success

if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n\n⏹️  Operation cancelled by user (Ctrl+C)")
        print("✅ Database remains unchanged")
        exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        print("🛡️  Database may still be intact")
        exit(1)
