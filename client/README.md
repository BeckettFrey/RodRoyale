# 🎣 Rod Royale Frontend - React Native App

A social fishing application built with React Native and TypeScript that connects to the Rod Royale Backend API. Share your fishing catches, discover fishing spots on an interactive map, and connect with other anglers.

## 🛠️ Tech Stack

- **React Native 0.80.2**: Cross-platform mobile development
- **TypeScript**: Type-safe JavaScript
- **React Navigation 6**: Navigation and routing
- **React Native Maps**: Interactive map functionality
- **AsyncStorage**: Local data persistence
- **Axios**: HTTP client for API communication
- **React Native Vector Icons**: Icon library

## 📦 Prerequisites

Before you begin, ensure you have:

- Node.js (v20 or higher)
- React Native CLI
- Android Studio (for Android development)
- Xcode (for iOS development, macOS only)
- Your Rod Royale Backend API running (see backend repository)

## 🔧 Installation

1. **Install dependencies**
   ```bash
   npm install
   ```

## ⚙️ Configuration

To use the default backend configuration for staging, copy the example environment file:

```sh
cp .env.example .env
```

This will create a `.env` file with default values. You can modify this file to match your backend settings if needed.

## 📁 Project Structure

```
src/
├── components/          # Reusable UI components
├── config/             # Configuration files
├── contexts/           # React Context providers
├── navigation/         # Navigation setup
├── screens/           # Screen components
├── services/          # API service layer
└── types/             # TypeScript type definitions
```

## 🔌 API Integration

The app connects to the Rod Royale Backend API with the following endpoints:

- **Users**: `/api/v1/users` - User management and profiles
- **Catches**: `/api/v1/catches` - Catch sharing and management
- **Pins**: `/api/v1/pins` - Map pins and fishing spots

**Happy Fishing! 🎣**

## Step 1: Start Metro

First, you will need to run **Metro**, the JavaScript build tool for React Native.

To start the Metro dev server, run the following command from the root of your React Native project:

```sh
# Using npm
npm start

# OR using Yarn
yarn start
```

## Step 2: Build and run your app

With Metro running, open a new terminal window/pane from the root of your React Native project, and use one of the following commands to build and run your Android or iOS app:

### Android

```sh
# Using npm
npm run android

# OR using Yarn
yarn android
```

### iOS

```sh
# Using npm
npm run ios

# OR using Yarn
yarn ios
```

If everything is set up correctly, you should see your new app running in the Android Emulator, iOS Simulator, or your connected device.

This is one way to run your app — you can also build it directly from Android Studio or Xcode.

# Learn More

To learn more about React Native, take a look at the following resources:

- [React Native Website](https://reactnative.dev) - learn more about React Native.
- [Getting Started](https://reactnative.dev/docs/environment-setup) - an **overview** of React Native and how setup your environment.
- [Learn the Basics](https://reactnative.dev/docs/getting-started) - a **guided tour** of the React Native **basics**.
- [Blog](https://reactnative.dev/blog) - read the latest official React Native **Blog** posts.
- [`@facebook/react-native`](https://github.com/facebook/react-native) - the Open Source; GitHub **repository** for React Native.
