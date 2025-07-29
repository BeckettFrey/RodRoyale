# File: database.py
from motor.motor_asyncio import AsyncIOMotorClient
from config import settings
import logging

logger = logging.getLogger(__name__)

class Database:
    client: AsyncIOMotorClient = None
    database = None

db = Database()

async def connect_to_mongo():
    """Create database connection"""
    try:
        db.client = AsyncIOMotorClient(settings.MONGODB_URL)
        db.database = db.client[settings.DATABASE_NAME]
        
        # Test the connection
        await db.client.admin.command('ping')
        logger.info("Connected to MongoDB successfully")
        
        # Create indexes for better performance
        await create_indexes()
        
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        raise

async def close_mongo_connection():
    """Close database connection"""
    if db.client:
        db.client.close()
        logger.info("Disconnected from MongoDB")

async def create_indexes():
    """Create database indexes for better performance"""
    try:
        # User collection indexes
        await db.database.users.create_index("email", unique=True)
        await db.database.users.create_index("username", unique=True)
        
        # Catch collection indexes
        await db.database.catches.create_index("user_id")
        await db.database.catches.create_index("created_at")
        await db.database.catches.create_index([("location.lat", 1), ("location.lng", 1)])
        
        # Pin collection indexes
        await db.database.pins.create_index("user_id")
        await db.database.pins.create_index("catch_id")
        await db.database.pins.create_index([("location.lat", 1), ("location.lng", 1)])
        
        logger.info("Database indexes created successfully")
        
    except Exception as e:
        logger.warning(f"Error creating indexes: {e}")

def get_database():
    return db.database
