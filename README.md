# RodRoyale Backend 🎣
[![CI](https://github.com/BeckettFrey/RodRoyale-backend/actions/workflows/test.yml/badge.svg)](https://github.com/BeckettFrey/RodRoyale-backend/actions/workflows/test.yml)

[![codecov](https://codecov.io/gh/BeckettFrey/RodRoyale-backend/branch/main/graph/badge.svg)](https://codecov.io/gh/BeckettFrey/RodRoyale-backend)

**RodRoyale Backend** is a robust FastAPI backend powering the ultimate social fishing app. Built with async MongoDB integration, it enables anglers to share catches, compete on leaderboards, and connect with the fishing community through an intuitive API.

> ✅ **Stage-Ready**: This API is stable and ready for the staging phase of the product lifecycle. I will work on increasing test coverage intermittently.

## 📂 Project Structure

```text
└── RodRoyale-Backend/
  ├── docs/
  │   ├── LICENSE
  │   └── SECURITY_OUTLINE.md
  ├── models/
  │   ├── __init__.py
  │   └── schemas.py
  ├── routers/
  │   ├── __init__.py
  │   ├── auth.py
  │   ├── catches.py
  │   ├── leaderboard.py
  │   ├── leaderboard_monthly.py
  │   ├── pins.py
  │   ├── uploads.py
  │   └── users.py
  ├── scripts/
  │   └── set-heroku-env.sh
  ├── services/
  │   ├── __init__.py
  │   └── cloudinary_service.py
  ├── tests/
  │   ├── conftest.py
  │   ├── README.md
  │   ├── run_tests.py
  │   ├── test_auth.py
  │   ├── test_catches.py
  │   ├── test_integration.py
  │   ├── test_leaderboards.py
  │   ├── test_pins.py
  │   ├── test_pins_fixed.py
  │   └── test_users.py
  ├── auth.py
  ├── config.py
  ├── database.py
  ├── db_manager.py
  ├── docker-compose.yml
  ├── Dockerfile
  ├── main.py
  ├── Procfile
  ├── pytest.ini
  ├── README.md
  ├── requirements-dev.txt
  └── requirements.txt
```

---

## ✨ Features

- 👤 **User Management** - Complete registration, profiles, and social following system
- 🎣 **Catch Sharing** - Upload fishing catches with images, species, and location data
- 🗺️ **Interactive Map** - Pin catches to map locations with customizable privacy controls
- ☁️ **Cloud Storage** - Seamless Cloudinary integration for optimized image uploads
- 🔒 **Privacy Controls** - Flexible visibility: private, mutuals-only, or public sharing
- ⚡ **Async Performance** - Motor-powered MongoDB operations for lightning-fast responses
- 🏆 **Leaderboards** - Monthly and global catch statistics and rankings

---

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/BeckettFrey/RodRoyale-backend.git
cd RodRoyale-backend

# Install dependencies
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt requirements-dev.txt
```

### Setup

1. **Configure your environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your credentials:
   # - MONGODB_URI
   # - CLOUDINARY_CLOUD_NAME
   # - CLOUDINARY_API_KEY
   # - CLOUDINARY_API_SECRET
   Etc.
   ```
   
2. **Initialize and test connection:**
   ```bash
   python db_manager.py init
   ```

3. **Start the server:**
   ```bash
   python main.py
   ```

### Local Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up --build

# Access API at http://localhost:8000
```

---

### View API Documentation
- **Swagger UI**: http://localhost:8000/docs

---

### API Endpoints Overview
- **Authentication** - `/auth/` - Register, login, token management
- **Users** - `/users/` - Profile management and social features
- **Catches** - `/catches/` - Create, view, and manage fishing catches
- **Leaderboards** - `/leaderboards/` - Rankings and statistics
- **Maps** - `/maps/` - Location-based catch discovery

---

## 🏗️ Architecture

RodRoyale Backend is built with cutting-edge Python technologies:

- **🚀 FastAPI** - High-performance async API framework
- **🍃 Motor** - Async MongoDB driver for seamless database operations
- **📊 Pydantic** - Type-safe data validation and serialization
- **☁️ Cloudinary** - Professional image upload and optimization
- **🔐 JWT** - Secure authentication and authorization
- **🧪 Pytest** - Comprehensive testing framework
- **🧪 Heroku** - Cloud platform for deployment

---

## 🗺️ Roadmap

Exciting features planned for future releases:

- 📊 **Advanced Analytics** - Detailed fishing statistics and insights
- 🖼️ **AI Image Recognition** - Automatic species identification
- 🌊 **Weather Integration** - Real-time fishing conditions
- 🎮 **Gamification** - Achievements, badges, and challenges
- 🔗 **Social Integrations** - Share catches to social media platforms

---

## 🤝 Contributing

During staging I would appreciate any feedback or suggestions; see CONTRIBUTING.md!

### Development Setup
```bash
# Clone and install
git clone https://github.com/BeckettFrey/RodRoyale-backend.git
cd RodRoyale-backend
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Run tests
pytest

# Code formatting
black .
flake8 .
```

### Current Status
- ✅ Core API functionality complete
- ✅ User authentication and profiles
- ✅ Catch management with images
- ✅ Leaderboard system operational
- 🚧 Advanced analytics in development
- 🚧 Mobile optimizations expanding

---

*Rod Royale Backend - Where anglers connect, compete, and share their greatest catches.*
