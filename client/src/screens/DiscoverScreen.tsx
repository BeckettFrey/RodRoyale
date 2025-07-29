import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  SafeAreaView,
  ScrollView,
  TouchableOpacity,
  TextInput,
  Alert,
} from 'react-native';
import LoadingSpinner from '../components/LoadingSpinner';
import { useAuth } from '../contexts/AuthContext';
import ApiService from '../services/api';
import { User } from '../types/api';

const DiscoverScreen: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<User[]>([]);
  const [loading, setLoading] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);
  const [followingUsers, setFollowingUsers] = useState<Set<string>>(new Set());
  const { user, refreshUser } = useAuth();

  const searchUsers = async (query: string) => {
    if (!query.trim()) {
      setSearchResults([]);
      setHasSearched(false);
      return;
    }

    try {
      setLoading(true);
      setHasSearched(true);
      const results = await ApiService.searchUsers(query.trim(), 20);
      // Filter out current user from the results
      const otherUsers = results.filter((u: User) => u._id !== user?._id);
      setSearchResults(otherUsers);
    } catch (error) {
      console.error('Error searching users:', error);
      Alert.alert('Error', 'Unable to search for users. Please try again.');
      setSearchResults([]);
    } finally {
      setLoading(false);
    }
  };

  const handleFollowToggle = async (targetUser: User) => {
    if (!user) return;
    
    try {
      const isFollowing = followingUsers.has(targetUser._id);
      
      if (isFollowing) {
        await ApiService.unfollowUser(user._id, targetUser._id);
        setFollowingUsers(prev => {
          const newSet = new Set(prev);
          newSet.delete(targetUser._id);
          return newSet;
        });
        Alert.alert('Success', `You unfollowed ${targetUser.username}`);
      } else {
        await ApiService.followUser(user._id, targetUser._id);
        setFollowingUsers(prev => new Set([...prev, targetUser._id]));
        Alert.alert('Success', `You are now following ${targetUser.username}`);
      }
      
      // Add a small delay to ensure backend has processed the change
      console.log('DiscoverScreen: Waiting for backend to process follow/unfollow...');
      await new Promise(resolve => setTimeout(resolve, 500));
      
      // Refresh user data to update following count in ProfileScreen
      console.log('DiscoverScreen: Refreshing user data after follow/unfollow...');
      console.log('DiscoverScreen: Current user before refresh:', {
        username: user.username,
        followersCount: user.followers?.length || 0,
        followingCount: user.following?.length || 0
      });
      
      await refreshUser();
      
      console.log('DiscoverScreen: User data refresh completed');
      console.log('DiscoverScreen: Updated user after refresh should be available in ProfileScreen');
    } catch (error) {
      console.error('Error toggling follow:', error);
      Alert.alert('Error', 'Unable to update follow status. Please try again.');
    }
  };

  useEffect(() => {
    if (user?.following && Array.isArray(user.following)) {
      console.log('DiscoverScreen: Updating followingUsers with:', user.following);
      setFollowingUsers(new Set(user.following));
    } else {
      console.log('DiscoverScreen: User following is not an array:', user?.following);
      setFollowingUsers(new Set());
    }
  }, [user?.following]);

  const handleSearch = () => {
    searchUsers(searchQuery);
  };

  const handleSearchInputChange = (text: string) => {
    setSearchQuery(text);
    // Clear results when input is cleared, but don't auto-search
    if (text.trim().length === 0) {
      setSearchResults([]);
      setHasSearched(false);
    }
  };

  const renderUserCard = (discoveredUser: User) => {
    const isFollowing = followingUsers.has(discoveredUser._id);
    
    return (
      <View key={discoveredUser._id} style={styles.userCard}>
        <View style={styles.userInfo}>
          <Text style={styles.username}>🎣 {discoveredUser.username}</Text>
          <Text style={styles.email}>{discoveredUser.email}</Text>
          {discoveredUser.bio && (
            <Text style={styles.bio} numberOfLines={2}>
              {discoveredUser.bio}
            </Text>
          )}
          <View style={styles.socialStats}>
            <Text style={styles.socialStat}>
              👥 {discoveredUser.followers.length} followers
            </Text>
            <Text style={styles.socialStat}>
              ➡️ {discoveredUser.following.length} following
            </Text>
          </View>
        </View>
        <TouchableOpacity
          style={[
            styles.followButton,
            isFollowing ? styles.unfollowButton : styles.followButtonActive
          ]}
          onPress={() => handleFollowToggle(discoveredUser)}
        >
          <Text style={[
            styles.followButtonText,
            isFollowing ? styles.unfollowButtonText : styles.followButtonActiveText
          ]}>
            {isFollowing ? 'Unfollow' : 'Follow'}
          </Text>
        </TouchableOpacity>
      </View>
    );
  };

  if (loading) {
    return (
      <SafeAreaView style={styles.container}>
        <LoadingSpinner message="🔍 Searching..." />
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.searchContainer}>
        <TextInput
          style={styles.searchInput}
          placeholder="Enter keywords..."
          value={searchQuery}
          onChangeText={handleSearchInputChange}
          clearButtonMode="while-editing"
          onSubmitEditing={handleSearch}
          returnKeyType="search"
        />
        <TouchableOpacity style={styles.searchButton} onPress={handleSearch}>
          <Text style={styles.searchButtonText}>Search</Text>
        </TouchableOpacity>
      </View>

      <ScrollView style={styles.scrollView}>
        {!hasSearched && !searchQuery ? (
          <View style={styles.emptyState}>
            <Text style={styles.emptyStateText}>
              🌊 Ready to discover new anglers?
            </Text>
            <Text style={styles.emptyStateSubtext}>
              Enter a username or keywords above and press Search to find fellow fishing enthusiasts to follow!
            </Text>
            <Text style={styles.emptyStateNote}>
              💡 Tip: Search works on both usernames and bio descriptions. Try searching for "bass", "Florida", or any fishing-related terms!
            </Text>
          </View>
        ) : searchResults.length > 0 ? (
          <View style={styles.usersList}>
            <Text style={styles.resultsText}>
              Found {searchResults.length} angler{searchResults.length !== 1 ? 's' : ''}
            </Text>
            {searchResults.map(renderUserCard)}
          </View>
        ) : hasSearched ? (
          <View style={styles.emptyState}>
            <Text style={styles.emptyStateText}>
              🎯 No anglers found matching "{searchQuery}"
            </Text>
            <Text style={styles.emptyStateSubtext}>
              Try searching for different keywords, usernames, or fishing-related terms.
            </Text>
          </View>
        ) : null}
      </ScrollView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f0f8ff',
  },
  centered: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingText: {
    fontSize: 18,
    color: '#666',
  },
  searchContainer: {
    paddingHorizontal: 20,
    paddingBottom: 20,
    paddingTop: 20,
    flexDirection: 'row',
    gap: 10,
  },
  searchInput: {
    flex: 1,
    height: 50,
    backgroundColor: 'white',
    borderRadius: 25,
    paddingHorizontal: 20,
    fontSize: 16,
    borderWidth: 1,
    borderColor: '#ddd',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  searchButton: {
    backgroundColor: '#2196F3',
    paddingHorizontal: 20,
    paddingVertical: 15,
    borderRadius: 25,
    justifyContent: 'center',
    alignItems: 'center',
  },
  searchButtonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: 'bold',
  },
  scrollView: {
    flex: 1,
  },
  emptyState: {
    alignItems: 'center',
    paddingVertical: 60,
    paddingHorizontal: 40,
  },
  emptyStateText: {
    fontSize: 18,
    color: '#666',
    textAlign: 'center',
    marginBottom: 10,
  },
  emptyStateSubtext: {
    fontSize: 14,
    color: '#999',
    textAlign: 'center',
  },
  emptyStateNote: {
    fontSize: 12,
    color: '#666',
    textAlign: 'center',
    marginTop: 15,
    fontStyle: 'italic',
  },
  usersList: {
    paddingHorizontal: 20,
  },
  resultsText: {
    fontSize: 16,
    color: '#666',
    marginBottom: 15,
    textAlign: 'center',
  },
  userCard: {
    backgroundColor: 'white',
    borderRadius: 12,
    padding: 20,
    marginBottom: 15,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  userInfo: {
    flex: 1,
    marginRight: 15,
  },
  username: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 5,
  },
  email: {
    fontSize: 14,
    color: '#666',
    marginBottom: 8,
  },
  bio: {
    fontSize: 14,
    color: '#333',
    marginBottom: 10,
    lineHeight: 18,
  },
  socialStats: {
    flexDirection: 'row',
    gap: 15,
  },
  socialStat: {
    fontSize: 12,
    color: '#666',
  },
  followButton: {
    paddingHorizontal: 20,
    paddingVertical: 10,
    borderRadius: 20,
    minWidth: 80,
    alignItems: 'center',
  },
  followButtonActive: {
    backgroundColor: '#4CAF50',
  },
  unfollowButton: {
    backgroundColor: 'white',
    borderWidth: 1,
    borderColor: '#ddd',
  },
  followButtonText: {
    fontSize: 14,
    fontWeight: 'bold',
  },
  followButtonActiveText: {
    color: 'white',
  },
  unfollowButtonText: {
    color: '#666',
  },
});

export default DiscoverScreen;
