import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { Platform } from 'react-native';
import { User, Catch, Pin, CreateUserRequest, UpdateUserRequest, CreateCatchRequest, CreatePinRequest, UserStats, LeaderboardResponse, LeaderboardMetric } from '../types/api';
import { Config } from '../config';

const TOKEN_STORAGE_KEY = '@Rod Royale_token';

interface LoginRequest {
  email: string;
  password: string;
}

interface RegisterRequest {
  username: string;
  email: string;
  password: string;
  bio?: string;
}

interface AuthResponse {
  user: User;
  token: {
    access_token: string;
    token_type: string;
  };
}

class ApiService {
  private baseURL: string;
  private onUnauthorized?: () => Promise<void>;

  constructor() {
    this.baseURL = Config.API_BASE_URL;
    console.log('🔧 [API SERVICE] Initializing with base URL:', this.baseURL);
    console.log('🔧 [API SERVICE] Platform:', Platform.OS);
    this.setupInterceptors();
    this.setupDefaultTimeout();
  }

  setUnauthorizedHandler(handler: () => Promise<void>) {
    this.onUnauthorized = handler;
  }

  // Setup default timeout for all requests
  private setupDefaultTimeout() {
    axios.defaults.timeout = 15000; // 15 second timeout
    
    // iOS-specific axios configuration
    if (Platform.OS === 'ios') {
      axios.defaults.headers.common['User-Agent'] = 'RodRoyaleApp/1.0 iOS';
      axios.defaults.headers.common['Accept'] = 'application/json';
      // Ensure keep-alive is disabled for iOS simulator
      axios.defaults.headers.common['Connection'] = 'close';
    }
    
    console.log('⏱️ [API SERVICE] Set default timeout to 15 seconds');
  }

  // Setup axios interceptors for token management
  private setupInterceptors() {
    // Request interceptor to add auth token
    axios.interceptors.request.use(
      async (config) => {
        const token = await AsyncStorage.getItem(TOKEN_STORAGE_KEY);
        
        // Check if this is a request to our API - be more permissive
        const isApiRequest = config.url && (
          config.url.includes('/api/v1') || 
          config.url.includes(':8000')
        );
        
        if (token && isApiRequest) {
          config.headers.Authorization = `Bearer ${token}`;
          console.log(`✅ Adding auth token to request: ${config.url}`);
        } else if (isApiRequest) {
          console.log(`❌ No token found for API request: ${config.url}`);
        }

        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // Response interceptor to handle token expiration
    axios.interceptors.response.use(
      (response) => response,
      async (error) => {
        if (error.response?.status === 401 || error.response?.status === 500 || error.response?.status === 403) {
          // Token expired or invalid
          await this.clearToken();
          if (this.onUnauthorized) {
            await this.onUnauthorized(); 
          }
        }
        return Promise.reject(error);
      }
    );
  }

  // Token management
  async setToken(token: string): Promise<void> {
    await AsyncStorage.setItem(TOKEN_STORAGE_KEY, token);
  }

  async getToken(): Promise<string | null> {
    return await AsyncStorage.getItem(TOKEN_STORAGE_KEY);
  }

  async clearToken(): Promise<void> {
    await AsyncStorage.removeItem(TOKEN_STORAGE_KEY);
  }

  // Check if user is authenticated
  async isAuthenticated(): Promise<boolean> {
    const token = await this.getToken();
    return !!token;
  }

  // Test token validity
  async testAuth(): Promise<boolean> {
    try {
      await this.getCurrentUser();
      return true;
    } catch (error) {
      console.log('Auth test failed:', error);
      return false;
    }
  }

  // Authentication
  async login(credentials: LoginRequest): Promise<AuthResponse> {
    const response = await axios.post(`${this.baseURL}/auth/login`, credentials);
    const authData = response.data;
    console.log('Login response:', { 
      token_preview: authData.token?.access_token?.substring(0, 20) + '...', 
      user: authData.user 
    });
    await this.setToken(authData.token.access_token);
    console.log('Token stored successfully');
    return authData;
  }

  async register(userData: RegisterRequest): Promise<AuthResponse> {
    const response = await axios.post(`${this.baseURL}/auth/register`, userData);
    const authData = response.data;
    await this.setToken(authData.token.access_token);
    console.log('Token stored successfully');
    return authData;
  }

  async logout(): Promise<void> {
    await this.clearToken();
  }

  // Update base URL for production
  setBaseURL(url: string) {
    this.baseURL = url;
  }

  // User Management
  async getCurrentUser(): Promise<User> {
    console.log('👤 [GET CURRENT USER] Fetching current user data...');
    
    // Debug token information
    const token = await this.getToken();
    console.log('🔑 [GET CURRENT USER] Token info:', {
      hasToken: !!token,
      tokenLength: token?.length || 0,
      tokenPreview: token ? `${token.substring(0, 20)}...${token.substring(token.length - 10)}` : 'No token',
      url: `${this.baseURL}/users/me`
    });
    
    try {
      const response = await axios.get(`${this.baseURL}/users/me`);
      console.log('✅ [GET CURRENT USER] Success:', {
        username: response.data.username,
        followersCount: response.data.followers?.length || 0,
        followingCount: response.data.following?.length || 0,
        followers: response.data.followers,
        following: response.data.following
      });
      return response.data;
    } catch (error: any) {
      console.error('❌ [GET CURRENT USER] Failed:', {
        message: error.message,
        status: error.response?.status,
        statusText: error.response?.statusText,
        data: error.response?.data,
        url: error.config?.url,
        headers: error.config?.headers ? {
          Authorization: error.config.headers.Authorization ? 'Present' : 'Missing',
          'Content-Type': error.config.headers['Content-Type']
        } : 'No headers'
      });
      
      // If it's a 401, the token is definitely invalid - clear it
      if (error.response?.status === 401) {
        console.warn('🚨 [GET CURRENT USER] Unauthorized (401), clearing token');
        await this.clearToken();
      }
      
      throw error;
    }
  }

  async deleteMyAccount(): Promise<void> {
    console.log('🗑️ [DELETE ACCOUNT] Starting account deletion...');
    
    // Ensure we're authenticated
    const hasToken = await this.isAuthenticated();
    if (!hasToken) {
      throw new Error('No authentication token found. Please log in again.');
    }
    
    try {
      const response = await axios.delete(`${this.baseURL}/users/me`);
      console.log('✅ [DELETE ACCOUNT] Account deleted successfully:', response.status);
      
      // Clear token after successful deletion
      await this.clearToken();
      
    } catch (error: any) {
      console.error('❌ [DELETE ACCOUNT] Failed to delete account:', {
        message: error.message,
        status: error.response?.status,
        data: error.response?.data,
        url: error.config?.url
      });
      
      if (error.response?.status === 403) {
        throw new Error('Permission denied. Please log in again.');
      } else if (error.response?.status === 404) {
        throw new Error('Account not found. It may have already been deleted.');
      } else {
        throw new Error(`Failed to delete account: ${error.response?.data?.detail || error.message}`);
      }
    }
  }

  async getUser(userId: string): Promise<User> {
    const response = await axios.get(`${this.baseURL}/users/${userId}`);
    return response.data;
  }

  async updateUser(userId: string, userData: UpdateUserRequest): Promise<User> {
    console.log('🔄 [UPDATE USER] Updating user profile:', { userId, userData });
    
    // Ensure we're authenticated
    const hasToken = await this.isAuthenticated();
    if (!hasToken) {
      throw new Error('No authentication token found. Please log in again.');
    }
    
    const response = await axios.put(`${this.baseURL}/users/${userId}`, userData);
    console.log('✅ [UPDATE USER] Profile updated successfully:', response.data);
    return response.data;
  }

  async getAllUsers(): Promise<User[]> {
    // Note: This endpoint might not exist in the current API
    // For now, we'll try to use it and handle errors gracefully
    try {
      const response = await axios.get(`${this.baseURL}/users`);
      return response.data;
    } catch (error: any) {
      console.warn('getAllUsers endpoint not available:', error.message);
      // Return empty array for now - in production, you might want to implement 
      // a search-based approach or request the backend team to add this endpoint
      return [];
    }
  }

  async searchUsers(query: string, limit: number = 10): Promise<User[]> {
    const response = await axios.get(`${this.baseURL}/users/search`, {
      params: { q: query, limit }
    });
    return response.data;
  }

  // Deprecated - use register() instead
  async createUser(userData: CreateUserRequest): Promise<User> {
    console.warn('createUser is deprecated, use register() instead');
    const registerData = { ...userData, password: 'temp123' }; // This shouldn't be used
    const authResponse = await this.register(registerData);
    return authResponse.user;
  }

  async followUser(userId: string, targetUserId: string): Promise<void> {
    console.log('👥 [FOLLOW USER] Starting follow action:', { userId, targetUserId });
    
    // Ensure we're authenticated
    const hasToken = await this.isAuthenticated();
    if (!hasToken) {
      throw new Error('No authentication token found. Please log in again.');
    }
    
    try {
      const response = await axios.post(`${this.baseURL}/users/${userId}/follow/${targetUserId}`);
      console.log('✅ [FOLLOW USER] Successfully followed user:', response.status);
      console.log('✅ [FOLLOW USER] Response data:', response.data);
    } catch (error: any) {
      console.error('❌ [FOLLOW USER] Failed to follow user:', {
        message: error.message,
        status: error.response?.status,
        data: error.response?.data,
        url: error.config?.url
      });
      
      if (error.response?.status === 403) {
        throw new Error('Permission denied. You may not have permission to perform this action.');
      } else if (error.response?.status === 404) {
        throw new Error('User not found. Please check the user ID.');
      } else if (error.response?.status === 409) {
        throw new Error('You are already following this user.');
      } else {
        throw new Error(`Failed to follow user: ${error.response?.data?.detail || error.message}`);
      }
    }
  }

  async unfollowUser(userId: string, targetUserId: string): Promise<void> {
    console.log('👥 [UNFOLLOW USER] Starting unfollow action:', { userId, targetUserId });
    
    // Ensure we're authenticated
    const hasToken = await this.isAuthenticated();
    if (!hasToken) {
      throw new Error('No authentication token found. Please log in again.');
    }
    
    try {
      const response = await axios.delete(`${this.baseURL}/users/${userId}/follow/${targetUserId}`);
      console.log('✅ [UNFOLLOW USER] Successfully unfollowed user:', response.status);
      console.log('✅ [UNFOLLOW USER] Response data:', response.data);
    } catch (error: any) {
      console.error('❌ [UNFOLLOW USER] Failed to unfollow user:', {
        message: error.message,
        status: error.response?.status,
        data: error.response?.data,
        url: error.config?.url
      });
      
      if (error.response?.status === 403) {
        throw new Error('Permission denied. You may not have permission to perform this action.');
      } else if (error.response?.status === 404) {
        throw new Error('User not found or you are not following this user.');
      } else {
        throw new Error(`Failed to unfollow user: ${error.response?.data?.detail || error.message}`);
      }
    }
  }

  // Get user's followers
  async getUserFollowers(userId: string): Promise<User[]> {
    console.log('👥 [GET FOLLOWERS] Fetching followers for user:', userId);
    
    try {
      const response = await axios.get(`${this.baseURL}/users/${userId}/followers`);
      console.log('✅ [GET FOLLOWERS] Success:', response.data.length, 'followers');
      return response.data;
    } catch (error: any) {
      console.error('❌ [GET FOLLOWERS] Failed:', {
        message: error.message,
        status: error.response?.status,
        data: error.response?.data
      });
      throw new Error(`Failed to get followers: ${error.response?.data?.detail || error.message}`);
    }
  }

  // Get user's following list
  async getUserFollowing(userId: string): Promise<User[]> {
    console.log('👥 [GET FOLLOWING] Fetching following list for user:', userId);
    
    try {
      const response = await axios.get(`${this.baseURL}/users/${userId}/following`);
      console.log('✅ [GET FOLLOWING] Success:', response.data.length, 'following');
      return response.data;
    } catch (error: any) {
      console.error('❌ [GET FOLLOWING] Failed:', {
        message: error.message,
        status: error.response?.status,
        data: error.response?.data
      });
      throw new Error(`Failed to get following list: ${error.response?.data?.detail || error.message}`);
    }
  }

  // Check if user is following another user
  async isFollowing(userId: string, targetUserId: string): Promise<boolean> {
    try {
      const following = await this.getUserFollowing(userId);
      return following.some(user => user._id === targetUserId);
    } catch (error) {
      console.error('Failed to check following status:', error);
      return false;
    }
  }

  // Catch Management
  async createCatch(catchData: CreateCatchRequest): Promise<Catch> {
    console.log('🎣 [CREATE CATCH] Starting with JWT auth');
    console.log('🎣 [CREATE CATCH] Base URL:', this.baseURL);
    console.log('🎣 [CREATE CATCH] Platform:', Platform.OS);
    console.log('🎣 [CREATE CATCH] Catch data:', catchData);
    
    // Test if we're properly authenticated
    const hasToken = await this.isAuthenticated();
    console.log('🔑 [CREATE CATCH] Has token:', hasToken);
    
    if (!hasToken) {
      const error = 'No authentication token found. Please log in again.';
      console.error('❌ [CREATE CATCH] Auth failed:', error);
      throw new Error(error);
    }
    
    // For iOS, try multiple URLs if needed
    const urlsToTry = Platform.OS === 'ios' ? [
      'http://localhost:8000/api/v1',
      'http://127.0.0.1:8000/api/v1',
      'http://192.168.86.29:8000/api/v1',
      this.baseURL
    ] : [this.baseURL];
    
    // Retry logic for iOS simulator
    const maxRetries = Platform.OS === 'ios' ? 2 : 1;
    let lastError: any;
    
    for (const baseUrl of urlsToTry) {
      console.log(`🌐 [CREATE CATCH] Trying URL: ${baseUrl}`);
      
      for (let attempt = 1; attempt <= maxRetries; attempt++) {
        console.log(`🔄 [CREATE CATCH] Attempt ${attempt}/${maxRetries} for ${baseUrl}`);
        
        try {
          // iOS simulator-specific configuration
          const requestConfig: any = {
            timeout: Platform.OS === 'ios' ? 45000 : 30000,
            headers: {
              'Content-Type': 'application/json',
              'Accept': 'application/json',
            },
          };
          
          // Add additional iOS-specific headers if needed
          if (Platform.OS === 'ios') {
            requestConfig.headers['User-Agent'] = 'RodRoyaleApp/1.0 iOS';
            requestConfig.headers['Connection'] = 'close';
            requestConfig.httpAgent = false;
            requestConfig.httpsAgent = false;
          }
          
          console.log('🌐 [CREATE CATCH] Making request to:', `${baseUrl}/catches`);
          console.log('🔍 [CREATE CATCH] Full request details:', {
            url: `${baseUrl}/catches`,
            method: 'POST',
            headers: requestConfig.headers,
            dataPreview: JSON.stringify(catchData).substring(0, 200) + '...'
          });
          
          console.log('📋 [CREATE CATCH] Request config:', JSON.stringify(requestConfig, null, 2));
          
          const response = await axios.post(`${baseUrl}/catches`, catchData, requestConfig);
          console.log('✅ [CREATE CATCH] Success response:', response.data);
          return response.data;
          
        } catch (error: any) {
          console.error(`❌ [CREATE CATCH] Attempt ${attempt} failed for ${baseUrl}:`, error.message);
          lastError = error;
          
          if (error.code === 'ECONNABORTED' && attempt < maxRetries) {
            console.log(`⏱️ [CREATE CATCH] Timeout on attempt ${attempt}, retrying in 1 second...`);
            await new Promise(resolve => setTimeout(resolve, 1000));
            continue;
          }
          
          // If not a timeout or last attempt for this URL, break inner loop
          if (error.code !== 'ECONNABORTED' || attempt === maxRetries) {
            break;
          }
        }
      }
      
      // If we got here and it wasn't a network error, don't try other URLs
      if (lastError && lastError.response) {
        console.log('🛑 [CREATE CATCH] Got server response, not trying other URLs');
        break;
      }
    }
    
    // Handle the final error
    const error = lastError;
    if (error.code === 'ECONNABORTED') {
      console.error('⏱️ [CREATE CATCH] All retry attempts timed out');
      throw new Error('Request timed out after multiple attempts. Please check your network connection.');
    }
    
    if (error.response) {
      console.error('📡 [CREATE CATCH] Response error:', {
        status: error.response.status,
        statusText: error.response.statusText,
        data: error.response.data,
        headers: error.response.headers
      });
      throw new Error(`Server responded with ${error.response.status}: ${error.response.statusText}`);
    } else if (error.request) {
      console.error('📡 [CREATE CATCH] Network error - no response:', error.request);
      console.error('🔗 [CREATE CATCH] Attempted URLs:', urlsToTry);
      throw new Error('Network error: Unable to reach the server. Please check your connection.');
    } else {
      console.error('❌ [CREATE CATCH] Setup error:', error.message);
      throw new Error(`Request setup error: ${error.message}`);
    }
  }

  // Alternative method for iOS - combined catch creation with image upload
  async createCatchWithImage(
    catchData: Omit<CreateCatchRequest, 'photo_url'>,
    imageUri?: string
  ): Promise<Catch> {
    console.log('🎣 [CREATE CATCH WITH IMAGE] Starting combined upload...');
    console.log('🎣 [CREATE CATCH WITH IMAGE] Platform:', Platform.OS);
    
    // Test if we're properly authenticated
    const hasToken = await this.isAuthenticated();
    if (!hasToken) {
      throw new Error('No authentication token found. Please log in again.');
    }

    try {
      // Create FormData for combined upload
      const formData = new FormData();
      
      // Add catch data as JSON
      formData.append('catch_data', JSON.stringify(catchData));
      
      // Add image if provided
      if (imageUri) {
        const filename = `catch_${Date.now()}.jpg`;
        
        if (imageUri.startsWith('data:')) {
          // Convert base64 to blob
          const response = await fetch(imageUri);
          const blob = await response.blob();
          // @ts-ignore
          formData.append('image', blob, filename);
        } else {
          // @ts-ignore - React Native FormData typing
          formData.append('image', {
            uri: imageUri,
            type: 'image/jpeg',
            name: filename,
          });
        }
      }

      console.log('🌐 [CREATE CATCH WITH IMAGE] Making combined upload request...');
      
      const requestConfig: any = {
        timeout: Platform.OS === 'ios' ? 90000 : 60000, // Extra long timeout for combined upload
        headers: {
          'Content-Type': 'multipart/form-data',
          'Accept': 'application/json',
        },
      };

      if (Platform.OS === 'ios') {
        requestConfig.headers['User-Agent'] = 'RodRoyaleApp/1.0 iOS';
        requestConfig.httpAgent = false;
        requestConfig.httpsAgent = false;
      }

      const response = await axios.post(`${this.baseURL}/catches/upload-with-image`, formData, requestConfig);
      console.log('✅ [CREATE CATCH WITH IMAGE] Success:', response.data);
      return response.data;
      
    } catch (error: any) {
      console.error('❌ [CREATE CATCH WITH IMAGE] Failed:', error);
      
      if (error.code === 'ECONNABORTED') {
        throw new Error('Combined upload timed out. Please try the regular method.');
      }
      
      if (error.response) {
        console.error('📡 [CREATE CATCH WITH IMAGE] Server error:', {
          status: error.response.status,
          data: error.response.data
        });
        throw new Error(`Server error: ${error.response.status}`);
      }
      
      throw new Error(`Combined upload failed: ${error.message}`);
    }
  }

  async getCatch(catchId: string): Promise<Catch> {
    const response = await axios.get(`${this.baseURL}/catches/${catchId}`);
    return response.data;
  }

  async getMyCatches(): Promise<Catch[]> {
    const response = await axios.get(`${this.baseURL}/catches/me`);
    return response.data;
  }

  async getFeed(limit?: number, skip?: number): Promise<Catch[]> {
    // Get social feed from the dedicated backend endpoint
    // This endpoint returns user's catches + followers' catches, properly ordered
    const params: any = {};
    if (limit) params.limit = limit;
    if (skip) params.skip = skip;

    const response = await axios.get(`${this.baseURL}/catches/feed`, { params });
    return response.data;
  }

  async getEnrichedFeed(limit?: number, skip?: number): Promise<(Catch & { user?: User })[]> {
    // Get feed and enrich with user information
    const feedCatches = await this.getFeed(limit, skip);
    const userCache = new Map<string, User>();
    
    // Enrich each catch with user information
    const enrichedCatches = await Promise.all(
      feedCatches.map(async (catch_item) => {
        try {
          // Check cache first
          let user = userCache.get(catch_item.user_id);
          
          if (!user) {
            // Fetch user info if not in cache
            user = await this.getUser(catch_item.user_id);
            userCache.set(catch_item.user_id, user);
          }
          
          return { ...catch_item, user };
        } catch (error) {
          console.warn(`Failed to load user info for catch ${catch_item._id}:`, error);
          return catch_item;
        }
      })
    );
    
    return enrichedCatches;
  }

  async getUserCatches(userId: string): Promise<Catch[]> {
    const response = await axios.get(`${this.baseURL}/catches/users/${userId}/catches`);
    return response.data;
  }

  async updateCatch(catchId: string, catchData: Partial<CreateCatchRequest>): Promise<Catch> {
    console.log('Updating catch:', catchId, catchData);
    
    // Ensure we're authenticated
    const hasToken = await this.isAuthenticated();
    if (!hasToken) {
      throw new Error('No authentication token found. Please log in again.');
    }
    
    const response = await axios.put(`${this.baseURL}/catches/${catchId}`, catchData);
    console.log('Update catch response:', response.data);
    return response.data;
  }

  async deleteCatch(catchId: string, deleteImages: boolean = true): Promise<void> {
    console.log('🔥 [DELETE] Starting catch deletion:', { catchId, deleteImages });
    
    // Ensure we're authenticated
    const hasToken = await this.isAuthenticated();
    console.log('🔑 [DELETE] Authentication check:', { hasToken });
    
    if (!hasToken) {
      const error = 'No authentication token found. Please log in again.';
      console.error('❌ [DELETE] Auth failed:', error);
      throw new Error(error);
    }

    try {
      // Optionally get catch details first to clean up images
      if (deleteImages) {
        console.log('🖼️ [DELETE] Starting image cleanup...');
        try {
          const catchData = await this.getCatch(catchId);
          console.log('✅ [DELETE] Retrieved catch for cleanup:', { 
            id: catchData._id, 
            hasPhoto: !!catchData.photo_url,
            photoUrl: catchData.photo_url?.substring(0, 50) + '...' 
          });
          
          // If catch has images, attempt to delete them from Cloudinary
          if (catchData.photo_url) {
            // Extract public_id from Cloudinary URL
            const publicId = this.extractPublicIdFromUrl(catchData.photo_url);
            console.log('🔍 [DELETE] Extracted public_id:', publicId);
            
            if (publicId) {
              console.log('🗑️ [DELETE] Attempting to delete image from Cloudinary...');
              try {
                await this.deleteImage(publicId);
                console.log('✅ [DELETE] Successfully deleted image from Cloudinary');
              } catch (imageError) {
                console.warn('⚠️ [DELETE] Failed to delete image from Cloudinary:', imageError);
                // Continue with catch deletion even if image deletion fails
              }
            }
          }
        } catch (fetchError) {
          console.warn('⚠️ [DELETE] Could not fetch catch details for image cleanup:', fetchError);
          // Continue with deletion anyway
        }
      }

      // Delete the catch from the database
      console.log('🗂️ [DELETE] Deleting catch from database...');
      console.log('🌐 [DELETE] DELETE URL:', `${this.baseURL}/catches/${catchId}`);
      
      const response = await axios.delete(`${this.baseURL}/catches/${catchId}`);
      
      console.log('✅ [DELETE] Successfully deleted catch from database:', {
        status: response.status,
        data: response.data
      });
      
    } catch (error: any) {
      console.error('❌ [DELETE] Failed to delete catch:', {
        message: error.message,
        status: error.response?.status,
        statusText: error.response?.statusText,
        data: error.response?.data,
        url: error.config?.url,
        method: error.config?.method
      });
      
      throw new Error(`Failed to delete catch: ${error.response?.data?.detail || error.message}`);
    }
  }

  // Helper method to extract Cloudinary public_id from URL
  private extractPublicIdFromUrl(imageUrl: string): string | null {
    try {
      // Cloudinary URLs typically look like:
      // https://res.cloudinary.com/[cloud]/image/upload/[version]/[public_id].[format]
      // or https://res.cloudinary.com/[cloud]/image/upload/[public_id].[format]
      
      if (!imageUrl.includes('cloudinary.com')) {
        console.log('Not a Cloudinary URL, skipping extraction');
        return null;
      }

      // Extract the path after '/upload/'
      const uploadIndex = imageUrl.indexOf('/upload/');
      if (uploadIndex === -1) {
        console.log('Could not find /upload/ in URL');
        return null;
      }

      let pathAfterUpload = imageUrl.substring(uploadIndex + 8); // +8 for '/upload/'
      
      // Remove version if present (starts with 'v' followed by numbers)
      if (pathAfterUpload.match(/^v\d+\//)) {
        pathAfterUpload = pathAfterUpload.replace(/^v\d+\//, '');
      }

      // Remove file extension
      const publicId = pathAfterUpload.replace(/\.[^.]+$/, '');
      
      console.log('Extracted public_id:', publicId);
      return publicId;
      
    } catch (error) {
      console.error('Error extracting public_id from URL:', error);
      return null;
    }
  }

  // Batch operations for better UX
  async deleteMyCatch(catchId: string): Promise<void> {
    console.log('🎯 [DELETE MY CATCH] Starting deleteMyCatch for ID:', catchId);
    
    // Verify ownership before deletion
    try {
      console.log('🔍 [DELETE MY CATCH] Fetching user catches to verify ownership...');
      const myCatches = await this.getMyCatches();
      console.log('📋 [DELETE MY CATCH] User has', myCatches.length, 'total catches');
      
      const catchToDelete = myCatches.find(c => c._id === catchId);
      console.log('🎣 [DELETE MY CATCH] Found target catch:', !!catchToDelete);
      
      if (!catchToDelete) {
        const error = 'Catch not found or you do not have permission to delete it';
        console.error('❌ [DELETE MY CATCH] Ownership verification failed:', error);
        throw new Error(error);
      }
      
      console.log('✅ [DELETE MY CATCH] Ownership verified, proceeding with deletion...');
      await this.deleteCatch(catchId, true);
      console.log('🎉 [DELETE MY CATCH] Successfully deleted your catch');
      
    } catch (error: any) {
      console.error('❌ [DELETE MY CATCH] Failed to delete your catch:', error);
      throw new Error(`Failed to delete catch: ${error.message}`);
    }
  }

  async updateMyCatch(catchId: string, catchData: Partial<CreateCatchRequest>): Promise<Catch> {
    // Verify ownership before update
    try {
      const myCatches = await this.getMyCatches();
      const catchToUpdate = myCatches.find(c => c._id === catchId);
      
      if (!catchToUpdate) {
        throw new Error('Catch not found or you do not have permission to edit it');
      }
      
      const updatedCatch = await this.updateCatch(catchId, catchData);
      console.log('Successfully updated your catch');
      return updatedCatch;
      
    } catch (error: any) {
      console.error('Failed to update your catch:', error);
      throw new Error(`Failed to update catch: ${error.message}`);
    }
  }

  // Utility method to check if user can edit/delete a catch
  async canEditCatch(catchId: string): Promise<boolean> {
    try {
      const myCatches = await this.getMyCatches();
      return myCatches.some(c => c._id === catchId);
    } catch (error) {
      console.error('Failed to check catch permissions:', error);
      return false;
    }
  }

  // Update catch with new image (handles old image cleanup)
  async updateCatchWithNewImage(
    catchId: string, 
    newImageUri: string, 
    otherData: Partial<Omit<CreateCatchRequest, 'photo_url'>>
  ): Promise<Catch> {
    try {
      // Get current catch data
      const currentCatch = await this.getCatch(catchId);
      const oldImageUrl = currentCatch.photo_url;
      
      // Upload new image
      console.log('Uploading new image for catch update...');
      const newImageUrl = await this.uploadImage(newImageUri, 'Rod Royale/catches');
      
      // Update catch with new image URL
      const updateData: Partial<CreateCatchRequest> = {
        ...otherData,
        photo_url: newImageUrl
      };
      
      const updatedCatch = await this.updateMyCatch(catchId, updateData);
      
      // Clean up old image after successful update
      if (oldImageUrl && oldImageUrl !== newImageUrl) {
        const oldPublicId = this.extractPublicIdFromUrl(oldImageUrl);
        if (oldPublicId) {
          try {
            await this.deleteImage(oldPublicId);
            console.log('Successfully cleaned up old image');
          } catch (cleanupError) {
            console.warn('Failed to cleanup old image (catch updated successfully):', cleanupError);
          }
        }
      }
      
      return updatedCatch;
      
    } catch (error: any) {
      console.error('Failed to update catch with new image:', error);
      throw new Error(`Failed to update catch: ${error.message}`);
    }
  }

  // Pin Management
  async createPin(pinData: CreatePinRequest): Promise<Pin> {
    console.log('🔧 [API] createPin called with data:', pinData);
    console.log('🔧 [API] createPin URL:', `${this.baseURL}/pins`);
    
    const response = await axios.post(`${this.baseURL}/pins`, pinData);
    console.log('🔧 [API] createPin response status:', response.status);
    console.log('🔧 [API] createPin response data:', response.data);
    
    return response.data;
  }

  async getPins(lat?: number, lng?: number, radius?: number): Promise<Pin[]> {
    const params: any = {};
    
    if (lat !== undefined) params.lat = lat;
    if (lng !== undefined) params.lng = lng;
    if (radius !== undefined) params.radius = radius;
    
    console.log('🔧 [API] getPins called with params:', params);
    console.log('🔧 [API] getPins URL:', `${this.baseURL}/pins`);
    
    const response = await axios.get(`${this.baseURL}/pins`, { params });
    console.log('🔧 [API] getPins response status:', response.status);
    console.log('🔧 [API] getPins response data length:', response.data?.length || 0);
    console.log('🔧 [API] getPins response data preview:', response.data?.slice(0, 2) || []);
    
    return response.data;
  }

  async updatePin(pinId: string, pinData: Partial<CreatePinRequest>): Promise<Pin> {
    const response = await axios.put(`${this.baseURL}/pins/${pinId}`, pinData);
    return response.data;
  }

  async deletePin(pinId: string, userId: string): Promise<void> {
    await axios.delete(`${this.baseURL}/pins/${pinId}`, {
      params: { user_id: userId }
    });
  }

  // Image Upload and Management
  async uploadImage(imageUri: string, folder: string = 'Rod Royale/catches'): Promise<string> {
    try {
      // Create FormData for image upload - React Native specific format
      const formData = new FormData();
      
      // Get file info from the URI
      const filename = `image_${Date.now()}.jpg`;
      
      // Check if the imageUri is base64 data
      if (imageUri.startsWith('data:')) {
        // Convert base64 to blob for upload
        console.log('Converting base64 to blob...');
        const response = await fetch(imageUri);
        const blob = await response.blob();
        
        // @ts-ignore - React Native FormData typing issue
        formData.append('file', blob, filename);
      } else {
        // Regular file URI
        // @ts-ignore - React Native FormData typing issue
        formData.append('file', {
          uri: imageUri,
          type: 'image/jpeg',
          name: filename,
        });
      }

      console.log('Uploading image to Cloudinary via backend:', { uri: imageUri.substring(0, 50) + '...', filename, folder });
      console.log('Request URL:', `${this.baseURL}/upload/image`);

      const response = await axios.post(`${this.baseURL}/upload/image`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        params: { folder },
        timeout: 30000, // 30 second timeout for uploads
      });

      console.log('Upload response:', response.data);
      
      // Backend returns Cloudinary response with multiple URLs and public_id
      if (response.data.url || response.data.secure_url) {
        const imageUrl = response.data.secure_url || response.data.url;
        console.log('Cloudinary image URL:', imageUrl);
        console.log('Cloudinary public_id:', response.data.public_id);
        return imageUrl;
      } else {
        console.error('Unexpected response format:', response.data);
        throw new Error('Invalid response format from upload endpoint');
      }
    } catch (error: any) {
      console.error('Image upload failed:', error);
      
      // Log more details about the error
      if (error.response) {
        console.error('Upload error response:', {
          status: error.response.status,
          data: error.response.data,
          headers: error.response.headers,
        });
      } else if (error.request) {
        console.error('Upload error request:', error.request);
      } else {
        console.error('Upload error message:', error.message);
      }
      
      // Return a more user-friendly error message
      throw new Error(`Failed to upload image: ${error.message}`);
    }
  }

  // Delete image from Cloudinary
  async deleteImage(publicId: string): Promise<boolean> {
    try {
      console.log('Deleting image from Cloudinary:', publicId);
      const response = await axios.delete(`${this.baseURL}/upload/image/${publicId}`);
      console.log('Delete response:', response.data);
      return true;
    } catch (error: any) {
      console.error('Image deletion failed:', error);
      throw new Error(`Failed to delete image: ${error.message}`);
    }
  }

  // Get thumbnail URL for an image
  async getThumbnailUrl(publicId: string, width: number = 300, height: number = 300): Promise<string> {
    try {
      console.log('Getting thumbnail URL for:', publicId, { width, height });
      const response = await axios.get(`${this.baseURL}/upload/image/${publicId}/thumbnail`, {
        params: { width, height }
      });
      console.log('Thumbnail response:', response.data);
      return response.data.thumbnail_url;
    } catch (error: any) {
      console.error('Failed to get thumbnail URL:', error);
      throw new Error(`Failed to get thumbnail: ${error.message}`);
    }
  }

  // Get optimized URL for an image
  async getOptimizedUrl(publicId: string, width?: number, height?: number): Promise<string> {
    try {
      console.log('Getting optimized URL for:', publicId, { width, height });
      const params: any = {};
      if (width) params.width = width;
      if (height) params.height = height;
      
      const response = await axios.get(`${this.baseURL}/upload/image/${publicId}/optimized`, {
        params
      });
      console.log('Optimized URL response:', response.data);
      return response.data.optimized_url;
    } catch (error: any) {
      console.error('Failed to get optimized URL:', error);
      throw new Error(`Failed to get optimized image: ${error.message}`);
    }
  }

  // Health Check
  async healthCheck(): Promise<{ status: string }> {
    const response = await axios.get(`${this.baseURL.replace('/api/v1', '')}/health`);
    return response.data;
  }

  // Leaderboard Management
  async getMyStats(): Promise<UserStats> {
    const response = await axios.get(`${this.baseURL}/leaderboard/my-stats`);
    console.log('📊 [LEADERBOARD] My stats response:', response.data);
    return response.data;
  }

  async getFollowingLeaderboard(metric: LeaderboardMetric): Promise<LeaderboardResponse> {
    const response = await axios.get(`${this.baseURL}/leaderboard/following-comparison`, {
      params: { metric }
    });
    return response.data;
  }

  async getGlobalLeaderboard(metric: LeaderboardMetric, limit: number = 50): Promise<LeaderboardResponse> {
    console.log('🌍 [LEADERBOARD] Fetching global leaderboard:', { metric, limit });
    const response = await axios.get(`${this.baseURL}/leaderboard/global`, {
      params: { metric, limit }
    });
    console.log('🌍 [LEADERBOARD] Global leaderboard response:', response.data);
    return response.data;
  }

  async getSpeciesLeaderboard(species: string, metric: LeaderboardMetric, limit: number = 50): Promise<LeaderboardResponse> {
    const response = await axios.get(`${this.baseURL}/leaderboard/species/${species.toLowerCase()}`, {
      params: { metric, limit }
    });
    return response.data;
  }

  // Password Management
  async changePassword(currentPassword: string, newPassword: string): Promise<{ message: string; detail: string }> {
    const response = await axios.post(`${this.baseURL}/auth/change-password`, {
      current_password: currentPassword,
      new_password: newPassword
    });
    return response.data;
  }
}

export default new ApiService();
