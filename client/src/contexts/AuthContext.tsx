import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { User } from '../types/api';
import ApiService from '../services/api';

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (username: string, email: string, password: string, bio?: string) => Promise<void>;
  logout: () => Promise<void>;
  updateUser: (user: User) => Promise<void>;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

const USER_STORAGE_KEY = '@Rod Royale_user';

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadStoredUser();
    // inject logout into ApiService when provider mounts
    ApiService.setUnauthorizedHandler(async () => {
      await logout();
      console.log('AuthContext (onUnauthorized): User logged out due to unauthorized access');
    });
  }, []);

  const loadStoredUser = async () => {
    try {
      const storedUser = await AsyncStorage.getItem(USER_STORAGE_KEY);
      if (storedUser) {
        setUser(JSON.parse(storedUser));
      }
    } catch (error) {
      console.error('Error loading stored user:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const login = async (email: string, password: string) => {
    try {
      console.log('AuthContext: Attempting login...');
      const authResponse = await ApiService.login({ email, password });
      console.log('AuthContext: Login successful, storing user...');
      await AsyncStorage.setItem(USER_STORAGE_KEY, JSON.stringify(authResponse.user));
      setUser(authResponse.user);
      console.log('AuthContext: User stored successfully');
    } catch (error) {
      console.error('AuthContext: Login error:', error);
      throw error;
    }
  };

  const register = async (username: string, email: string, password: string, bio?: string) => {
    try {
      console.log('AuthContext: Attempting registration...');
      const authResponse = await ApiService.register({ username, email, password, bio });
      console.log('AuthContext: Registration successful, storing user...');
      await AsyncStorage.setItem(USER_STORAGE_KEY, JSON.stringify(authResponse.user));
      setUser(authResponse.user);
      console.log('AuthContext: User stored successfully');
    } catch (error) {
      console.error('AuthContext: Registration error:', error);
      throw error;
    }
  };

  const logout = async () => {
    try {
      console.log('AuthContext: Logging out...');
      await ApiService.logout(); // Clear JWT token
      console.log('AuthContext: Removing user from AsyncStorage...');
      await AsyncStorage.removeItem(USER_STORAGE_KEY);
      console.log('AuthContext: Setting user to null...');
      setUser(null);
      console.log('AuthContext: Logout completed successfully');
    } catch (error) {
      console.error('AuthContext: Error during logout:', error);
      throw error;
    }
  };

  const updateUser = async (userData: User) => {
    try {
      await AsyncStorage.setItem(USER_STORAGE_KEY, JSON.stringify(userData));
      setUser(userData);
    } catch (error) {
      console.error('Error updating user:', error);
      throw error;
    }
  };

  const refreshUser = async () => {
    if (!user) return;
    
    try {
      console.log('AuthContext: Refreshing user data...');
      console.log('AuthContext: Current user before refresh:', {
        username: user.username,
        userId: user._id,
        followers: user.followers,
        following: user.following,
        followersCount: user.followers?.length || 0,
        followingCount: user.following?.length || 0
      });
      
      // Try using the specific user ID endpoint instead of /users/me
      const currentUser = await ApiService.getUser(user._id);
      console.log('AuthContext: User data received from API:', {
        username: currentUser.username,
        followers: currentUser.followers,
        following: currentUser.following,
        followersLength: currentUser.followers?.length,
        followingLength: currentUser.following?.length,
        followersType: typeof currentUser.followers,
        followingType: typeof currentUser.following
      });
      
      // Force a new object reference to trigger re-renders
      const newUserData = { ...currentUser };
      
      await AsyncStorage.setItem(USER_STORAGE_KEY, JSON.stringify(newUserData));
      setUser(newUserData);
      
      console.log('AuthContext: User state updated with fresh data');
      console.log('AuthContext: New user state:', {
        username: newUserData.username,
        followersCount: newUserData.followers?.length || 0,
        followingCount: newUserData.following?.length || 0
      });
    } catch (error: any) {
      console.error('AuthContext: Error refreshing user data:', error);
      
      // Only force logout for 401 (unauthorized) - don't force logout for 400 errors
      if (error.response?.status === 401) {
        console.warn('AuthContext: Unauthorized (401), token expired or invalid, forcing logout');
        await logout();
        return;
      }
      
      // For all other errors (including 400), don't force logout - let user continue with cached data
      console.log('AuthContext: Non-critical error during refresh, continuing with cached data');
    }
  };

  const value: AuthContextType = {
    user,
    isLoading,
    login,
    register,
    logout,
    updateUser,
    refreshUser,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

