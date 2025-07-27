# File: tests/conftest.py
"""
Test configuration and fixtures for Rod Royale API tests
"""

import pytest
import asyncio
from httpx import AsyncClient
from fastapi.testclient import TestClient
from bson import ObjectId
from datetime import datetime
import os

# Import the main application
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app
from config import settings
from auth import AuthUtils

# Test database configuration
TEST_DATABASE_NAME = f"{settings.DATABASE_NAME}_test"
TEST_MONGODB_URL = settings.MONGODB_URL

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()

@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """Set up test database configuration for the entire test session."""
    # Override the database name to use test database
    import os
    os.environ["DATABASE_NAME"] = f"{settings.DATABASE_NAME}_test"
    
    # Force reload settings to pick up the new database name
    import importlib
    import config
    importlib.reload(config)
    
    yield
    
    # Reset after tests
    os.environ.pop("DATABASE_NAME", None)

@pytest.fixture(scope="function")
def client():
    """Provide a test client for the FastAPI application."""
    with TestClient(app) as test_client:
        yield test_client

@pytest.fixture(scope="function")
async def test_db():
    """Provide a clean test database for each test."""
    # Get the test database directly
    from database import db
    test_database = db.database
    
    if test_database is None:
        # If database is not connected, skip the test
        pytest.skip("Database not connected")
    
    # Clean the database before each test
    await test_database.users.delete_many({})
    await test_database.catches.delete_many({})
    await test_database.pins.delete_many({})
    
    yield test_database
    
    # Clean up after test
    await test_database.users.delete_many({})
    await test_database.catches.delete_many({})
    await test_database.pins.delete_many({})

@pytest.fixture(scope="function")
async def async_client():
    """Provide an async test client for the FastAPI application."""
    async with AsyncClient(app=app, base_url="http://test") as test_client:
        yield test_client

@pytest.fixture
def sample_user_data():
    """Provide sample user data for testing."""
    return {
        "username": "test_angler",
        "email": "test@example.com",
        "password": "secure_password123",
        "bio": "I love fishing!"
    }

@pytest.fixture
def sample_catch_data():
    """Provide sample catch data for testing."""
    return {
        "species": "Largemouth Bass",
        "weight": 4.2,
        "photo_url": "https://example.com/bass.jpg",
        "location": {
            "lat": 40.7128,
            "lng": -74.0060
        },
        "shared_with_followers": True,
        "add_to_map": True
    }

@pytest.fixture
def sample_pin_data():
    """Provide sample pin data for testing."""
    return {
        "location": {
            "lat": 40.7128,
            "lng": -74.0060
        },
        "visibility": "public"
    }

@pytest.fixture
async def test_user(test_db, sample_user_data):
    """Create a test user in the database."""
    import uuid
    user_data = sample_user_data.copy()
    password = user_data.pop("password")
    user_data["username"] = f"test_angler_{uuid.uuid4().hex[:8]}"
    user_data["email"] = f"test_{uuid.uuid4().hex[:8]}@example.com"
    user_data["password_hash"] = AuthUtils.hash_password(password)
    user_data["_id"] = ObjectId()
    user_data["followers"] = []
    user_data["following"] = []
    
    await test_db.users.insert_one(user_data)
    return user_data

@pytest.fixture
async def test_user_2(test_db):
    """Create a second test user for relationship testing."""
    import uuid
    user_data = {
        "_id": ObjectId(),
        "username": f"test_angler_2_{uuid.uuid4().hex[:8]}",
        "email": f"test2_{uuid.uuid4().hex[:8]}@example.com",
        "password_hash": AuthUtils.hash_password("password123"),
        "bio": "Another fishing enthusiast",
        "followers": [],
        "following": []
    }
    
    await test_db.users.insert_one(user_data)
    return user_data

@pytest.fixture
async def auth_token(test_user):
    """Generate an authentication token for the test user."""
    return AuthUtils.create_access_token(str(test_user["_id"]))

@pytest.fixture
async def auth_headers(auth_token):
    """Provide authorization headers with the test user's token."""
    return {"Authorization": f"Bearer {auth_token}"}

@pytest.fixture
async def test_catch(test_db, test_user, sample_catch_data):
    """Create a test catch in the database."""
    catch_data = sample_catch_data.copy()
    catch_data["_id"] = ObjectId()
    catch_data["user_id"] = test_user["_id"]
    catch_data["created_at"] = datetime.utcnow()
    
    await test_db.catches.insert_one(catch_data)
    return catch_data

@pytest.fixture
async def test_pin(test_db, test_user, test_catch, sample_pin_data):
    """Create a test pin in the database."""
    pin_data = sample_pin_data.copy()
    pin_data["_id"] = ObjectId()
    pin_data["user_id"] = test_user["_id"]
    pin_data["catch_id"] = test_catch["_id"]
    
    await test_db.pins.insert_one(pin_data)
    return pin_data

@pytest.fixture
def multiple_users_data():
    """Provide data for creating multiple test users."""
    return [
        {
            "username": f"angler_{i}",
            "email": f"angler{i}@example.com",
            "password": f"password{i}",
            "bio": f"Fishing enthusiast #{i}"
        }
        for i in range(1, 6)
    ]

@pytest.fixture
async def multiple_test_users(test_db, multiple_users_data):
    """Create multiple test users in the database."""
    import uuid
    users = []
    for i, user_data in enumerate(multiple_users_data):
        data = user_data.copy()
        password = data.pop("password")
        data["username"] = f"angler_{i}_{uuid.uuid4().hex[:8]}"
        data["email"] = f"angler{i}_{uuid.uuid4().hex[:8]}@example.com"
        data["password_hash"] = AuthUtils.hash_password(password)
        data["_id"] = ObjectId()
        data["followers"] = []
        data["following"] = []
        users.append(data)
    
    await test_db.users.insert_many(users)
    return users

@pytest.fixture
def api_endpoints():
    """Provide a comprehensive list of API endpoints for testing."""
    return {
        "auth": [
            "POST /api/v1/auth/register",
            "POST /api/v1/auth/login", 
            "POST /api/v1/auth/refresh",
            "GET /api/v1/auth/me",
            "POST /api/v1/auth/logout"
        ],
        "users": [
            "POST /api/v1/users/",
            "GET /api/v1/users/search",
            "GET /api/v1/users/{user_id}",
            "GET /api/v1/users/me",
            "PUT /api/v1/users/{user_id}",
            "POST /api/v1/users/{user_id}/follow/{target_user_id}",
            "DELETE /api/v1/users/{user_id}/follow/{target_user_id}",
            "GET /api/v1/users/{user_id}/followers",
            "GET /api/v1/users/{user_id}/following",
            "DELETE /api/v1/users/me"
        ],
        "catches": [
            "POST /api/v1/catches/",
            "POST /api/v1/catches/upload-with-image",
            "GET /api/v1/catches/feed",
            "GET /api/v1/catches/me",
            "GET /api/v1/catches/{catch_id}",
            "GET /api/v1/catches/users/{user_id}/catches",
            "PUT /api/v1/catches/{catch_id}",
            "DELETE /api/v1/catches/{catch_id}"
        ],
        "pins": [
            "POST /api/v1/pins/",
            "GET /api/v1/pins/",
            "PUT /api/v1/pins/{pin_id}",
            "DELETE /api/v1/pins/{pin_id}"
        ],
        "uploads": [
            "POST /api/v1/uploads/image",
            "DELETE /api/v1/uploads/image/{public_id}",
            "GET /api/v1/uploads/image/{public_id}/thumbnail",
            "GET /api/v1/uploads/image/{public_id}/optimized"
        ],
        "leaderboard": [
            "GET /api/v1/leaderboard/my-stats",
            "GET /api/v1/leaderboard/following-comparison", 
            "GET /api/v1/leaderboard/global",
            "GET /api/v1/leaderboard/species/{species}"
        ]
    }

# Utility functions for tests
class TestHelpers:
    @staticmethod
    def assert_valid_object_id(obj_id: str):
        """Assert that a string is a valid MongoDB ObjectId."""
        assert ObjectId.is_valid(obj_id), f"Invalid ObjectId: {obj_id}"
    
    @staticmethod
    def assert_valid_user_response(user_data: dict, include_email: bool = False):
        """Assert that user response data has required fields."""
        required_fields = ["id", "username", "bio", "followers", "following"]
        if include_email:
            required_fields.append("email")
        
        for field in required_fields:
            assert field in user_data, f"Missing field: {field}"
    
    @staticmethod
    def assert_valid_catch_response(catch_data: dict):
        """Assert that catch response data has required fields."""
        required_fields = [
            "id", "species", "weight", "photo_url", "location", 
            "user_id", "created_at", "shared_with_followers", "add_to_map"
        ]
        
        for field in required_fields:
            assert field in catch_data, f"Missing field: {field}"
    
    @staticmethod
    def assert_valid_pin_response(pin_data: dict):
        """Assert that pin response data has required fields."""
        required_fields = ["id", "catch_id", "location", "visibility", "user_id"]
        
        for field in required_fields:
            assert field in pin_data, f"Missing field: {field}"

@pytest.fixture
def helpers():
    """Provide test helper functions."""
    return TestHelpers
