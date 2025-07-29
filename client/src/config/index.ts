import { Platform } from 'react-native';

const getApiBaseUrl = () => {
  if (process.env.ENVIRONMENT === 'production') {
    return 'https://rod-royale-6e0e562ef71b.herokuapp.com/api/v1';
  }

  // Development environment
  if (Platform.OS === 'web') {
    // Web can use localhost
    return 'http://localhost:8000/api/v1';
  }
  
  if (Platform.OS === 'android') {
    // Android emulator uses special IP
    return 'http://10.0.2.2:8000/api/v1';
  }
  
  if (Platform.OS === 'ios') {
    // iOS simulator works best with localhost
    return 'http://localhost:8000/api/v1';
  }
  
  // Fallback for physical devices - use local IP
  return 'http://192.168.86.29:8000/api/v1';
};

export const Config = {
  API_BASE_URL: getApiBaseUrl(),
};
