# 🎣 Rod Royale
[![CI](https://github.com/BeckettFrey/RodRoyale/actions/workflows/api.yml/badge.svg)](https://github.com/BeckettFrey/RodRoyale/actions/workflows/api.yml)

[![codecov](https://codecov.io/gh/BeckettFrey/RodRoyale/branch/main/graph/badge.svg)](https://codecov.io/gh/BeckettFrey/RodRoyale)

**Rod Royale** is the ultimate social fishing application that connects anglers worldwide. Share your greatest catches, discover fishing hotspots on interactive maps, compete on leaderboards, and build a community with fellow fishing enthusiasts.

This repository contains both the **FastAPI backend** and **React Native mobile app** in a unified codebase.

## 🎬 **[WATCH THE DEMO VIDEO](https://youtu.be/6ZqDfPWTeqM)** 🎬

[![Watch Demo](https://img.shields.io/badge/📺_DEMO_VIDEO-FF0000?style=for-the-badge&logo=youtube&logoColor=white&labelColor=000000)](https://youtu.be/6ZqDfPWTeqM)

> ✅ **Stage-Ready**: Both API and mobile app are stable and ready for staging.

---

## 📂 Project Structure

```text
└── RodRoyale/
    ├── backend/                    # FastAPI Backend
    │   ├── docs/
    │   ├── models/                 # Pydantic schemas
    │   ├── routers/                # API endpoints
    │   ├── services/               # Business logic
    │   ├── tests/                  # Backend tests
    │   ├── main.py                 # FastAPI app entry
    │   └── requirements.txt
    ├── client/                     # React Native App
    │   ├── android/                # Android build files
    │   ├── ios/                    # iOS build files
    │   ├── src/
    │   │   ├── components/         # Reusable UI components
    │   │   ├── screens/            # App screens
    │   │   ├── navigation/        # Navigation setup
    │   │   ├── services/           # API integration
    │   │   └── types/              # TypeScript definitions
    │   ├── App.tsx                 # React Native entry
    │   └── package.json
    └── README.md
```

---

## ✨ Features

### 🎣 Core Fishing Features
- **Catch Sharing** - Upload catches with photos, species, weight, and location data
- **Interactive Maps** - Pin catches to discover fishing hotspots
- **Privacy Controls** - Share catches publicly, with mutuals, or keep private

### 👥 Social Features
- **User Profiles** - Customizable angler profiles
- **Follow System** - Connect with other anglers and see their catches
- **Leaderboards** - Monthly and global rankings by catch size, frequency, and average weight

### 🔧 Technical Features
- **Cloud Storage** - Cloudinary integration for optimized image uploads
- **Real-time Data** - Async MongoDB operations for fast performance
- **Cross-platform** - Native iOS and Android apps from single codebase
- **Secure Authentication** - JWT-based user authentication and authorization

---

## 🚀 Quick Start

### Prerequisites
- **Node.js** (v20 or higher)
- **Python** (3.11 or higher)
- **MongoDB** (local or cloud instance)
- **React Native CLI**
- **Android Studio** (for Android development)
- **Xcode** (for iOS development, macOS only)

### Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Run interactive quick setup:**
   ```bash
   ./scripts/quick-start.sh
   ```
   
The API will be available at `http://localhost:8000` with documentation at `http://localhost:8000/docs`

### Frontend Setup

1. **Navigate to client directory:**
   ```bash
   cd client
   ```

2. **Run quick setup:**
   ```bash
   ./scripts/quick-start.sh
   ```

   OR
   
   **Run with device/emulator in mind:**
   ```bash
   npm install

   # Android
   npm run android
   
   # iOS
   npm run ios

   # web
   npm run web
   ```

---

## 🏗️ Architecture

### Backend Stack
- **🚀 FastAPI** - High-performance async API framework
- **🍃 Motor** - Async MongoDB driver
- **📊 Pydantic** - Type-safe data validation
- **☁️ Cloudinary** - Image upload and optimization
- **🔐 JWT** - Secure authentication
- **🧪 Pytest** - Comprehensive testing
- **Docker** - Containerized environment for dev/deployment

### Frontend Stack
- **⚛️ React Native** - Cross-platform mobile development
- **🔷 TypeScript** - Type-safe JavaScript
- **🧭 React Navigation** - Navigation and routing
- **🗺️ React Native Maps** - Interactive map functionality
- **📦 AsyncStorage** - Local data persistence
- **🌐 Axios** - HTTP client for API communication

---

## 🧪 Testing

### Backend Tests
```bash
docker exec -it CONTAINER_NAME pytest
```

### Frontend Tests
```bash
# TODO
```

---

## 🗺️ Roadmap

### Upcoming Features
- 📊 **Advanced Analytics** - Detailed fishing statistics and insights
- 🖼️ **AI Fish Recognition** - Automatic species identification from photos
- 🌊 **Weather Integration** - Real-time fishing conditions and forecasts
- 🎮 **Gamification** - Achievements, badges, and fishing challenges
- 🔗 **Social Sharing** - Share catches to Instagram, Facebook, Twitter
- 📡 **Offline Mode** - Cache catches when network is unavailable
- 🎯 **Smart Recommendations** - AI-powered fishing spot suggestions

### Technical Improvements
- 🔧 **GraphQL API** - More efficient data fetching
- 📱 **Push Notifications** - Real-time updates and engagement
- 🌍 **Internationalization** - Multi-language support
- 🔒 **Enhanced Security** - OAuth integration, 2FA
- 📈 **Performance Monitoring** - Analytics and crash reporting

---

## 🤝 Contributing

Welcoming contribution; see CONTRIBUTING.md

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](docs/LICENSE) file for details.

---

## 🎯 Current Status

### ✅ Completed
- Core API functionality with full CRUD operations
- User authentication and social features
- Catch management with image uploads
- Interactive map with location pinning
- Global and monthly leaderboards
- Cross-platform mobile app (iOS and web)
- Docker containerization
- Boilerplate CI/CD pipeline setup

### 🚧 In Progress
- Advanced analytics dashboard
- AI-powered fish species recognition
- Enhanced mobile app performance optimization
- Weather API integration

### 📋 Planned
- Push notification system
- Offline mode capabilities
- Social media integrations
- Advanced privacy controls

---

*Rod Royale - Where anglers connect, compete, and share their greatest catches.* 🎣
