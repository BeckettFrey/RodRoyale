#!/usr/bin/env python3
"""
Database Management Utility for Rod Royale Backend
Provides tools for database initialization, seeding, and cleanup
Enhanced with Faker library for realistic test data
"""

import asyncio
import sys
import random
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorClient
from faker import Faker
from config import settings

print(f"Connecting to: {settings.MONGODB_URL}, Database: {settings.DATABASE_NAME}")

# Initialize Faker with US locale
fake = Faker('en_US')

# US fishing locations with popular fishing spots
US_FISHING_LOCATIONS = [
    # Florida
    {"lat": 25.7617, "lng": -80.1918, "state": "FL", "name": "Miami"},
    {"lat": 28.5383, "lng": -81.3792, "state": "FL", "name": "Orlando"},
    {"lat": 30.4383, "lng": -84.2807, "state": "FL", "name": "Tallahassee"},
    {"lat": 27.9506, "lng": -82.4572, "state": "FL", "name": "Tampa"},
    
    # Texas
    {"lat": 29.7604, "lng": -95.3698, "state": "TX", "name": "Houston"},
    {"lat": 30.2672, "lng": -97.7431, "state": "TX", "name": "Austin"},
    {"lat": 32.7767, "lng": -96.7970, "state": "TX", "name": "Dallas"},
    {"lat": 29.4241, "lng": -98.4936, "state": "TX", "name": "San Antonio"},
    
    # California
    {"lat": 34.0522, "lng": -118.2437, "state": "CA", "name": "Los Angeles"},
    {"lat": 37.7749, "lng": -122.4194, "state": "CA", "name": "San Francisco"},
    {"lat": 32.7157, "lng": -117.1611, "state": "CA", "name": "San Diego"},
    {"lat": 38.5816, "lng": -121.4944, "state": "CA", "name": "Sacramento"},
    
    # Colorado
    {"lat": 39.7392, "lng": -104.9903, "state": "CO", "name": "Denver"},
    {"lat": 38.8339, "lng": -104.8214, "state": "CO", "name": "Colorado Springs"},
    
    # New York
    {"lat": 40.7128, "lng": -74.0060, "state": "NY", "name": "New York City"},
    {"lat": 42.3601, "lng": -71.0589, "state": "MA", "name": "Boston"},
    
    # Washington
    {"lat": 47.6062, "lng": -122.3321, "state": "WA", "name": "Seattle"},
    {"lat": 45.5152, "lng": -122.6784, "state": "OR", "name": "Portland"},
    
    # Great Lakes region
    {"lat": 41.8781, "lng": -87.6298, "state": "IL", "name": "Chicago"},
    {"lat": 42.3314, "lng": -83.0458, "state": "MI", "name": "Detroit"},
    {"lat": 44.9778, "lng": -93.2650, "state": "MN", "name": "Minneapolis"},
    
    # Southeast
    {"lat": 33.7490, "lng": -84.3880, "state": "GA", "name": "Atlanta"},
    {"lat": 35.2271, "lng": -80.8431, "state": "NC", "name": "Charlotte"},
    {"lat": 36.1627, "lng": -86.7816, "state": "TN", "name": "Nashville"},
    
    # Louisiana
    {"lat": 29.9511, "lng": -90.0715, "state": "LA", "name": "New Orleans"},
    {"lat": 30.4515, "lng": -91.1871, "state": "LA", "name": "Baton Rouge"},
]

# Common fish species by region
FISH_SPECIES_BY_REGION = {
    "FL": ["Largemouth Bass", "Snook", "Redfish", "Tarpon", "Mahi-Mahi", "Grouper", "Snapper"],
    "TX": ["Largemouth Bass", "Striped Bass", "Catfish", "Redfish", "Speckled Trout", "Flounder"],
    "CA": ["Salmon", "Steelhead", "Striped Bass", "Halibut", "Rockfish", "Tuna", "Yellowtail"],
    "CO": ["Rainbow Trout", "Brown Trout", "Cutthroat Trout", "Pike", "Kokanee Salmon"],
    "NY": ["Striped Bass", "Bluefish", "Fluke", "Black Sea Bass", "Smallmouth Bass"],
    "WA": ["Salmon", "Steelhead", "Halibut", "Lingcod", "Rockfish"],
    "OR": ["Salmon", "Steelhead", "Trout", "Halibut", "Rockfish"],
    "IL": ["Walleye", "Northern Pike", "Muskie", "Smallmouth Bass", "Lake Trout"],
    "MI": ["Walleye", "Steelhead", "Salmon", "Pike", "Perch", "Lake Trout"],
    "MN": ["Walleye", "Northern Pike", "Muskie", "Bass", "Crappie"],
    "GA": ["Largemouth Bass", "Striped Bass", "Catfish", "Crappie", "Bream"],
    "NC": ["Largemouth Bass", "Striped Bass", "Catfish", "Redfish", "Speckled Trout"],
    "TN": ["Largemouth Bass", "Smallmouth Bass", "Catfish", "Crappie", "Walleye"],
    "LA": ["Redfish", "Speckled Trout", "Largemouth Bass", "Catfish", "Flounder"],
    "MA": ["Striped Bass", "Bluefish", "Cod", "Haddock", "Flounder"]
}

# Weight ranges by species (in pounds)
SPECIES_WEIGHT_RANGES = {
    "Largemouth Bass": (1.0, 12.0),
    "Smallmouth Bass": (0.5, 8.0),
    "Striped Bass": (2.0, 50.0),
    "Rainbow Trout": (0.5, 15.0),
    "Brown Trout": (1.0, 20.0),
    "Salmon": (3.0, 40.0),
    "Steelhead": (2.0, 25.0),
    "Redfish": (2.0, 40.0),
    "Snook": (1.0, 25.0),
    "Tarpon": (20.0, 200.0),
    "Catfish": (1.0, 80.0),
    "Walleye": (1.0, 12.0),
    "Northern Pike": (2.0, 30.0),
    "Muskie": (5.0, 50.0),
    "Halibut": (5.0, 400.0),
    "Tuna": (10.0, 600.0),
    "Grouper": (2.0, 100.0),
    "Snapper": (1.0, 50.0)
}

def generate_fishing_bio():
    """Generate realistic fishing-related bio"""
    bio_templates = [
        "🎣 {experience} angler from {state}. Love fishing for {species}!",
        "Fishing enthusiast since {year}. {water_type} fishing is my passion.",
        "{experience} fisherman | {species} specialist | Catch and release advocate",
        "Weekend warrior on the water 🌊 | {state} native | {species} hunter",
        "Fishing guide and outdoor enthusiast | {experience} on the water",
        "Chasing {species} across {state} | Always looking for the next big catch",
        "Father of {kids} | Teaching the next generation to fish | {species} expert"
    ]
    
    template = random.choice(bio_templates)
    return template.format(
        experience=random.choice(["Passionate", "Experienced", "Weekend", "Professional", "Lifelong"]),
        state=random.choice(["FL", "TX", "CA", "CO", "WA"]),
        species=random.choice(["bass", "trout", "salmon", "redfish", "tarpon"]),
        water_type=random.choice(["Freshwater", "Saltwater", "Deep sea", "Lake", "River"]),
        year=random.randint(1980, 2015),
        kids=random.randint(1, 4)
    )

def get_weight_for_species(species):
    """Get realistic weight for a fish species"""
    if species in SPECIES_WEIGHT_RANGES:
        min_weight, max_weight = SPECIES_WEIGHT_RANGES[species]
        # Use a weighted random that favors smaller fish (more common)
        weight = random.triangular(min_weight, max_weight, min_weight + (max_weight - min_weight) * 0.3)
        return round(weight, 1)
    else:
        # Default range for unknown species
        return round(random.uniform(1.0, 10.0), 1)

def generate_catch_time(recent_percentage=0.5):
    """
    Generate a catch time with a specified percentage being recent (last 30 days)
    
    Args:
        recent_percentage: Float between 0 and 1, percentage of catches that should be recent
    
    Returns:
        datetime: Generated catch time
    """
    now = datetime.now()
    thirty_days_ago = now - timedelta(days=30)
    
    if random.random() < recent_percentage:
        # Generate a recent catch (within last 30 days)
        return fake.date_time_between(start_date=thirty_days_ago, end_date=now)
    else:
        # Generate an older catch (within last 2 years but more than 30 days ago)
        two_years_ago = now - timedelta(days=730)
        return fake.date_time_between(start_date=two_years_ago, end_date=thirty_days_ago)

if not settings.DATABASE_NAME:
    print("❌ DATABASE_NAME environment variable is not set. Please set it in your .env file.")
    sys.exit(1)

if not settings.MONGODB_URL:
    print("❌ MONGODB_URL environment variable is not set. Please set it in your .env file.")
    sys.exit(1)

async def init_database():
    """Initialize database with indexes"""
    print("🔧 Initializing Rod Royale database...")

    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.DATABASE_NAME]
    
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
        await db.catches.create_index("species")
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

async def seed_database(num_users=50, recent_percentage=0.5):
    """
    Seed database with realistic fake data - each user gets exactly one catch
    
    Args:
        num_users: Number of users to create
        recent_percentage: Percentage of catches that should be within last 30 days (0.0 to 1.0)
    """
    print(f"🌱 Seeding database with {num_users} users (each with one catch)...")
    print(f"📅 {int(recent_percentage * 100)}% of catches will be from the last 30 days")

    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.DATABASE_NAME]

    try:
        # Generate fake users with one catch each
        print("👥 Creating fake users and their catches...")
        user_ids = []
        total_catches = 0
        total_pins = 0
        recent_catches = 0
        
        for i in range(num_users):
            # Generate unique username and email
            base_username = fake.user_name()
            username = f"{base_username}_{random.randint(100, 999)}"
            email = f"{base_username.lower()}{random.randint(100, 999)}@rodroyale.com"
            
            user_data = {
                "username": username,
                "hashed_password": "temppassword123",  
                "email": email,
                "bio": generate_fishing_bio(),
                "followers": [],
                "following": [],
                "is_active": True,  
                "created_at": fake.date_time_between(start_date='-2y', end_date='now')
            }
            
            try:
                result = await db.users.insert_one(user_data)
                user_id = result.inserted_id
                user_ids.append(user_id)
                
                # Generate one catch for this user
                location = random.choice(US_FISHING_LOCATIONS)
                
                # Add some randomness to the exact coordinates (within ~10 miles)
                lat_offset = random.uniform(-0.1, 0.1)
                lng_offset = random.uniform(-0.1, 0.1)
                
                catch_location = {
                    "lat": round(location["lat"] + lat_offset, 6),
                    "lng": round(location["lng"] + lng_offset, 6)
                }
                
                state = location["state"]
                species = random.choice(FISH_SPECIES_BY_REGION.get(state, ["Largemouth Bass"]))
                weight = get_weight_for_species(species)
                catch_time = generate_catch_time(recent_percentage)
                
                # Track if this is a recent catch
                thirty_days_ago = datetime.now() - timedelta(days=30)
                if catch_time >= thirty_days_ago:
                    recent_catches += 1
                
                catch_data = {
                    "user_id": user_id,
                    "species": species,
                    "weight": weight,
                    "photo_url": f"https://example.com/catches/{fake.uuid4()}.jpg",
                    "location": catch_location,
                    "shared_with_followers": random.choice([True, False]),
                    "created_at": catch_time,
                    "notes": fake.sentence(),
                    "weather": random.choice(["Sunny", "Cloudy", "Rainy", "Overcast"]),
                    "water_temp": random.randint(45, 85)
                }
                
                catch_result = await db.catches.insert_one(catch_data)
                total_catches += 1
                
                # Create a pin for this catch (60% chance)
                if random.random() < 0.6:
                    pin_data = {
                        "user_id": user_id,
                        "catch_id": catch_result.inserted_id,
                        "location": catch_location,
                        "visibility": random.choice(["public", "followers", "private"]),
                        "created_at": catch_time
                    }
                    
                    await db.pins.insert_one(pin_data)
                    total_pins += 1
                
                if (i + 1) % 10 == 0:
                    print(f"   ✅ Created {i + 1}/{num_users} users with catches")
                    
            except Exception as e:
                print(f"   ⚠️  Skipped user due to error: {username} - {e}")
                continue
        
        print(f"✅ Created {len(user_ids)} users successfully")
        print(f"✅ Created {total_catches} catches ({recent_catches} recent, {total_catches - recent_catches} older)")
        print(f"✅ Created {total_pins} pins")
        
        # Create some follow relationships
        print("👥 Creating follow relationships...")
        follow_count = 0
        for _ in range(min(100, len(user_ids) * 2)):  # Create some follow relationships
            follower_id = random.choice(user_ids)
            following_id = random.choice(user_ids)
            
            if follower_id != following_id:
                # Add to follower's following list
                await db.users.update_one(
                    {"_id": follower_id},
                    {"$addToSet": {"following": following_id}}
                )
                # Add to followed user's followers list
                await db.users.update_one(
                    {"_id": following_id},
                    {"$addToSet": {"followers": follower_id}}
                )
                follow_count += 1
        
        print(f"✅ Created {follow_count} follow relationships")
        print("🎉 Database seeding complete!")
        
    except Exception as e:
        print(f"❌ Database seeding failed: {e}")
        return False
    finally:
        client.close()
    
    return True

async def seed_database_multiple_catches(num_users=50, catches_per_user_range=(1, 10), recent_percentage=0.5):
    """
    Seed database with realistic fake data - multiple catches per user (original behavior)
    
    Args:
        num_users: Number of users to create
        catches_per_user_range: Tuple of (min, max) catches per user
        recent_percentage: Percentage of catches that should be within last 30 days (0.0 to 1.0)
    """
    print(f"🌱 Seeding database with {num_users} users and multiple catches each...")
    print(f"📅 {int(recent_percentage * 100)}% of catches will be from the last 30 days")

    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.DATABASE_NAME]

    try:
        # Generate fake users
        print("👥 Creating fake users...")
        user_ids = []
        
        for i in range(num_users):
            # Generate unique username and email
            base_username = fake.user_name()
            username = f"{base_username}_{random.randint(100, 999)}"
            email = f"{base_username.lower()}{random.randint(100, 999)}@rodroyale.com"
            
            user_data = {
                "username": username,
                "email": email,
                "bio": generate_fishing_bio(),
                "followers": [],
                "following": [],
                "created_at": fake.date_time_between(start_date='-2y', end_date='now')
            }
            
            try:
                result = await db.users.insert_one(user_data)
                user_ids.append(result.inserted_id)
                if (i + 1) % 10 == 0:
                    print(f"   ✅ Created {i + 1}/{num_users} users")
            except Exception:
                print(f"   ⚠️  Skipped duplicate user: {username}")
                continue
        
        print(f"✅ Created {len(user_ids)} users successfully")
        
        # Generate catches for each user
        print("🎣 Creating catches...")
        total_catches = 0
        total_pins = 0
        recent_catches = 0
        
        for user_id in user_ids:
            num_catches = random.randint(*catches_per_user_range)
            
            for _ in range(num_catches):
                # Pick a random location
                location = random.choice(US_FISHING_LOCATIONS)
                
                # Add some randomness to the exact coordinates (within ~10 miles)
                lat_offset = random.uniform(-0.1, 0.1)
                lng_offset = random.uniform(-0.1, 0.1)
                
                catch_location = {
                    "lat": round(location["lat"] + lat_offset, 6),
                    "lng": round(location["lng"] + lng_offset, 6)
                }
                
                # Choose species based on region
                state = location["state"]
                if state in FISH_SPECIES_BY_REGION:
                    species = random.choice(FISH_SPECIES_BY_REGION[state])
                else:
                    species = random.choice(["Largemouth Bass", "Rainbow Trout", "Catfish"])
                
                weight = get_weight_for_species(species)
                
                # Generate catch time with specified recent percentage
                catch_time = generate_catch_time(recent_percentage)
                
                # Track if this is a recent catch
                thirty_days_ago = datetime.now() - timedelta(days=30)
                if catch_time >= thirty_days_ago:
                    recent_catches += 1
                
                catch_data = {
                    "user_id": user_id,
                    "species": species,
                    "weight": weight,
                    "photo_url": f"https://example.com/catches/{fake.uuid4()}.jpg",
                    "location": catch_location,
                    "shared_with_followers": random.choice([True, False]),
                    "created_at": catch_time,
                    "notes": fake.sentence() if random.random() < 0.3 else None,
                    "weather": random.choice(["Sunny", "Cloudy", "Rainy", "Overcast"]) if random.random() < 0.5 else None,
                    "water_temp": random.randint(45, 85) if random.random() < 0.4 else None
                }
                
                result = await db.catches.insert_one(catch_data)
                total_catches += 1
                
                # Create a pin for some catches (about 60% chance)
                if random.random() < 0.6:
                    pin_data = {
                        "user_id": user_id,
                        "catch_id": result.inserted_id,
                        "location": catch_location,
                        "visibility": random.choice(["public", "followers", "private"]),
                        "created_at": catch_time
                    }
                    
                    await db.pins.insert_one(pin_data)
                    total_pins += 1
        
        print(f"✅ Created {total_catches} catches ({recent_catches} recent, {total_catches - recent_catches} older)")
        print(f"✅ Created {total_pins} pins")
        
        # Create some follow relationships
        print("👥 Creating follow relationships...")
        follow_count = 0
        for _ in range(min(100, len(user_ids) * 2)):  # Create some follow relationships
            follower_id = random.choice(user_ids)
            following_id = random.choice(user_ids)
            
            if follower_id != following_id:
                # Add to follower's following list
                await db.users.update_one(
                    {"_id": follower_id},
                    {"$addToSet": {"following": following_id}}
                )
                # Add to followed user's followers list
                await db.users.update_one(
                    {"_id": following_id},
                    {"$addToSet": {"followers": follower_id}}
                )
                follow_count += 1
        
        print(f"✅ Created {follow_count} follow relationships")
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

    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.DATABASE_NAME]

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
    print("=" * 50)

    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.DATABASE_NAME]

    try:
        # Get collection counts
        user_count = await db.users.count_documents({})
        catch_count = await db.catches.count_documents({})
        pin_count = await db.pins.count_documents({})
        
        print(f"Users: {user_count}")
        print(f"Catches: {catch_count}")
        print(f"Pins: {pin_count}")
        
        if catch_count > 0:
            # Show recent vs older catches
            thirty_days_ago = datetime.now() - timedelta(days=30)
            recent_catch_count = await db.catches.count_documents({"created_at": {"$gte": thirty_days_ago}})
            older_catch_count = catch_count - recent_catch_count
            
            print("\n📅 Catch Timeline:")
            print(f"  - Recent (last 30 days): {recent_catch_count}")
            print(f"  - Older (30+ days ago): {older_catch_count}")
            
            # Show species distribution
            print("\n🐟 Top Fish Species:")
            species_pipeline = [
                {"$group": {"_id": "$species", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}},
                {"$limit": 10}
            ]
            async for species in db.catches.aggregate(species_pipeline):
                print(f"  - {species['_id']}: {species['count']} catches")
            
            # Show location distribution
            print("\n🗺️  Catches by State:")
            # This is a simplified version - in reality you'd need to reverse geocode
            print("  (Location stats would require reverse geocoding)")
            
            # Show recent catches
            print("\n🎣 Recent Catches:")
            async for catch in db.catches.find().sort("created_at", -1).limit(10):
                user = await db.users.find_one({"_id": catch["user_id"]})
                username = user["username"] if user else "Unknown"
                date_str = catch["created_at"].strftime("%Y-%m-%d")
                print(f"  - {catch['species']} ({catch['weight']}lbs) by {username} on {date_str}")
        
        # Show user with most catches
        if user_count > 0:
            print("\n🏆 Top Anglers:")
            top_anglers_pipeline = [
                {"$group": {"_id": "$user_id", "catch_count": {"$sum": 1}}},
                {"$sort": {"catch_count": -1}},
                {"$limit": 5}
            ]
            async for angler in db.catches.aggregate(top_anglers_pipeline):
                user = await db.users.find_one({"_id": angler["_id"]})
                username = user["username"] if user else "Unknown"
                print(f"  - {username}: {angler['catch_count']} catches")
        
    except Exception as e:
        print(f"❌ Error retrieving stats: {e}")
        return False
    finally:
        client.close()
    
    return True

def print_usage():
    """Print usage information"""
    print("Rod Royale Database Management Utility")
    print("=" * 40)
    print("Usage: python db_manager.py <command> [options]")
    print()
    print("Commands:")
    print("  init                    - Initialize database with indexes")
    print("  seed [users] [recent%]  - Seed database with fake data (default: 50 users, 1 catch each, 50% recent)") 
    print("  seed-multi [users] [recent%] - Seed database with multiple catches per user")
    print("  clear                   - Clear all data from database")
    print("  stats                   - Show database statistics")
    print("  help                    - Show this help message")
    print()
    print("Parameters:")
    print("  users     - Number of users to create (1-1000, default: 50)")
    print("  recent%   - Percentage of catches from last 30 days (0-100, default: 50)")
    print()
    print("Examples:")
    print("  python db_manager.py seed 100 75       # 100 users, 75% recent catches")
    print("  python db_manager.py seed-multi 50 25  # 50 users with multiple catches, 25% recent")
    print("  python db_manager.py seed              # 50 users, 50% recent catches (defaults)")
    print()
    print("Note: Requires 'faker' library. Install with: pip install faker")

async def main():
    if len(sys.argv) < 2:
        print_usage()
        return
    
    command = sys.argv[1].lower()
    
    if command == "init":
        await init_database()
    elif command == "seed":
        # Check for optional parameters
        num_users = 50  # default
        recent_percentage = 0.5  # default 50%
        
        if len(sys.argv) > 2:
            try:
                num_users = int(sys.argv[2])
                if num_users < 1 or num_users > 1000:
                    print("❌ Number of users must be between 1 and 1000")
                    return
            except ValueError:
                print("❌ Invalid number of users. Please provide a valid integer.")
                return
        
        if len(sys.argv) > 3:
            try:
                recent_percent = int(sys.argv[3])
                if recent_percent < 0 or recent_percent > 100:
                    print("❌ Recent percentage must be between 0 and 100")
                    return
                recent_percentage = recent_percent / 100.0
            except ValueError:
                print("❌ Invalid recent percentage. Please provide a valid integer (0-100).")
                return
        
        await seed_database(num_users, recent_percentage)
    elif command == "seed-multi":
        # Check for optional parameters
        num_users = 50  # default
        recent_percentage = 0.5  # default 50%
        
        if len(sys.argv) > 2:
            try:
                num_users = int(sys.argv[2])
                if num_users < 1 or num_users > 1000:
                    print("❌ Number of users must be between 1 and 1000")
                    return
            except ValueError:
                print("❌ Invalid number of users. Please provide a valid integer.")
                return
        
        if len(sys.argv) > 3:
            try:
                recent_percent = int(sys.argv[3])
                if recent_percent < 0 or recent_percent > 100:
                    print("❌ Recent percentage must be between 0 and 100")
                    return
                recent_percentage = recent_percent / 100.0
            except ValueError:
                print("❌ Invalid recent percentage. Please provide a valid integer (0-100).")
                return
        
        await seed_database_multiple_catches(num_users, (1, 10), recent_percentage)
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