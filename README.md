# 🎣 Catchy Backend API

A RESTful API built with FastAPI and MongoDB for Catchy - a social fishing application where anglers can share their catches, follow other fishers, and discover fishing spots on an interactive map.

## 🚀 Features

- **User Management**: User registration, profiles, following/followers system
- **Catch Sharing**: Upload and share fishing catches with photos and details
- **Interactive Map**: Pin catches to map locations with privacy controls
- **Access Control**: Granular privacy settings (private, mutuals, public)
- **Real-time Data**: Async MongoDB operations for optimal performance

## 💾 Tech Stack

- **FastAPI**: Modern, fast web framework for building APIs
- **MongoDB**: Document database with Motor async driver
- **Pydantic**: Data validation and serialization
- **Uvicorn**: ASGI server for development and production

## 📦 Core Models

### User
```json
{
  "id": "ObjectId",
  "username": "string",
  "email": "string", 
  "bio": "optional string",
  "followers": ["user_id"],
  "following": ["user_id"]
}
```

### Catch
```json
{
  "id": "ObjectId",
  "user_id": "ObjectId",
  "species": "string",
  "weight": "float",
  "photo_url": "string",
  "location": {
    "lat": "float",
    "lng": "float"
  },
  "shared_with_followers": "bool",
  "created_at": "datetime"
}
```

### Pin
```json
{
  "id": "ObjectId",
  "user_id": "ObjectId", 
  "catch_id": "ObjectId",
  "location": {
    "lat": "float",
    "lng": "float"
  },
  "visibility": "private" | "mutuals" | "public"
}
```

## 🔧 Installation & Setup

### Prerequisites
- Python 3.8+
- MongoDB (local installation or MongoDB Atlas)
- Docker (optional, for containerized deployment)

### Quick Start

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Catchy-Backend
   ```

2. **Run the startup script**
   ```bash
   ./start.sh
   ```

### Docker Deployment

For a complete setup with MongoDB included:

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

The API will be available at `http://localhost:8000`

### Manual Setup

1. **Create virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set environment variables**
   ```bash
   # Copy example environment file
   cp .env.example .env
   
   # Edit .env with your MongoDB settings
   export MONGODB_URL="mongodb://localhost:27017"  # or your MongoDB Atlas URL
   export DATABASE_NAME="catchy_db"
   ```

4. **Initialize database**
   ```bash
   python3 db_manager.py init
   python3 db_manager.py seed  # Optional: add sample data
   ```

5. **Start the server**
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

## 📡 API Endpoints

### Users
- `POST /api/v1/users` - Create a new user
- `GET /api/v1/users/{user_id}` - Get user profile
- `PUT /api/v1/users/{user_id}` - Update user profile
- `POST /api/v1/users/{user_id}/follow/{target_user_id}` - Follow user
- `DELETE /api/v1/users/{user_id}/follow/{target_user_id}` - Unfollow user

### Catches
- `POST /api/v1/catches` - Upload new catch
- `GET /api/v1/catches/{catch_id}` - Get single catch
- `GET /api/v1/catches/users/{user_id}/catches` - List user's catches
- `PUT /api/v1/catches/{catch_id}` - Update catch
- `DELETE /api/v1/catches/{catch_id}` - Delete catch

### Pins
- `POST /api/v1/pins` - Add catch to map
- `GET /api/v1/pins` - Get accessible map pins
- `PUT /api/v1/pins/{pin_id}` - Update pin
- `DELETE /api/v1/pins/{pin_id}` - Delete pin

## 🛡️ Access Control Logic

The API implements sophisticated access control:

- **Public**: Visible to everyone
- **Mutuals**: Visible only if both users follow each other
- **Private**: Visible only to the owner
- **Followers Only**: Catches shared only with followers

## 🧪 Testing the API

Once the server is running, you can:

1. **View API Documentation**: Visit `http://localhost:8000/docs` for interactive Swagger UI
2. **Alternative Docs**: Visit `http://localhost:8000/redoc` for ReDoc documentation
3. **Health Check**: Visit `http://localhost:8000/health` to verify the API is running
4. **Run Test Script**: Execute `python3 test_api.py` to test all endpoints

### Database Management

Use the included database manager for common tasks:

```bash
# Initialize database with proper indexes
python3 db_manager.py init

# Add sample data for testing
python3 db_manager.py seed

# View database statistics
python3 db_manager.py stats

# Clear all data (destructive!)
python3 db_manager.py clear
```

### Example API Calls

**Create a User:**
```bash
curl -X POST "http://localhost:8000/api/v1/users" \
     -H "Content-Type: application/json" \
     -d '{
       "username": "angler_mike",
       "email": "mike@example.com",
       "bio": "Passionate bass fisherman from Texas"
     }'
```

**Upload a Catch:**
```bash
curl -X POST "http://localhost:8000/api/v1/catches?user_id=USER_ID" \
     -H "Content-Type: application/json" \
     -d '{
       "species": "Largemouth Bass",
       "weight": 3.5,
       "photo_url": "https://example.com/photo.jpg",
       "location": {"lat": 30.2672, "lng": -97.7431},
       "shared_with_followers": false
     }'
```

## 🗃️ Database Indexes

The application automatically creates optimized indexes:

- **Users**: `email` (unique), `username` (unique)
- **Catches**: `user_id`, `created_at`, geospatial index on `location`
- **Pins**: `user_id`, `catch_id`, geospatial index on `location`

## 🌍 Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `MONGODB_URL` | `mongodb://localhost:27017` | MongoDB connection string |
| `DATABASE_NAME` | `catchy_db` | Database name |

## 🚦 Development Status

This is a complete, production-ready API implementation with:

- ✅ Full CRUD operations for all models
- ✅ Async MongoDB operations
- ✅ Data validation with Pydantic
- ✅ Comprehensive error handling
- ✅ Access control and privacy features
- ✅ Database indexing for performance
- ✅ API documentation
- ✅ Health check endpoints

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For questions or issues:
1. Check the [API documentation](http://localhost:8000/docs) when running locally
2. Review the error messages - they're designed to be helpful
3. Ensure MongoDB is running and accessible
4. Verify all required environment variables are set

---

**Happy Fishing! 🎣**