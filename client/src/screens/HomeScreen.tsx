import React, { useState, useEffect, useMemo, useCallback } from 'react';
import {
  View,
  Text,
  FlatList,
  StyleSheet,
  RefreshControl,
  SafeAreaView,
  TouchableOpacity,
  Image,
  Alert,
} from 'react-native';
import LoadingSpinner from '../components/LoadingSpinner';
import { useNavigation, useFocusEffect } from '@react-navigation/native';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { RootStackParamList } from '../navigation/AppNavigator';
import { useAuth } from '../contexts/AuthContext';
import ApiService from '../services/api';
import { Catch, User } from '../types/api';
import RodRoyaleTheme, { ComponentThemes } from '../theme/RodRoyaleTheme';
import { formatLocationDisplay, reverseGeocode } from '../utils/geocoding';

type HomeScreenNavigationProp = NativeStackNavigationProp<RootStackParamList>;

interface EnrichedCatch extends Catch {
  user?: User;
}

interface CatchItemProps {
  item: EnrichedCatch;
  onPress: (catchItem: Catch) => void;
  currentUserId?: string;
}

const CatchItem: React.FC<CatchItemProps> = ({ item, onPress, currentUserId }) => {
  const isOwnCatch = item.user_id === currentUserId;
  const displayName = item.user?.username || 'Unknown User';
  
  return (
    <TouchableOpacity style={styles.catchItem} onPress={() => onPress(item)}>
      <View style={styles.catchHeader}>
        <View style={styles.userInfo}>
          <Text style={[styles.username, isOwnCatch && styles.ownUsername]}>
            {isOwnCatch ? '🎣 You' : `🎣 ${displayName}`}
          </Text>
          <Text style={styles.date}>
            {new Date(item.created_at).toLocaleDateString()}
          </Text>
        </View>
        <View style={styles.fishInfo}>
          <Text style={styles.species}>{item.species}</Text>
          <Text style={styles.weight}>{item.weight} lbs</Text>
        </View>
      </View>
      
      {item.photo_url && (
        <Image source={{ uri: item.photo_url }} style={styles.catchImage} />
      )}
      
      <View style={styles.catchFooter}>
        <Text style={styles.location}>
          📍 {formatLocationDisplay(item.location)}
        </Text>
        <Text style={styles.shareText}>
          {item.shared_with_followers ? '👥 Shared' : '🔒 Private'}
        </Text>
      </View>
    </TouchableOpacity>
  );
};

const HomeScreen: React.FC = () => {
  const [catches, setCatches] = useState<EnrichedCatch[]>([]);
  const [refreshing, setRefreshing] = useState(false);
  const [loading, setLoading] = useState(true);
  const [showMyPostsOnly, setShowMyPostsOnly] = useState(false);
  const navigation = useNavigation<HomeScreenNavigationProp>();
  const { user } = useAuth();

  const loadAllPosts = async () => {
    if (!user) return;

    try {
      console.log('📱 [HOME] Loading all posts (social feed)...');
      const enrichedFeed = await ApiService.getEnrichedFeed();
      
      // Geocode locations that don't have city information
      const catchesWithCities = await Promise.all(
        enrichedFeed.map(async (catch_item) => {
          // If the location already has city information, use it as-is
          if (catch_item.location.city) {
            return catch_item;
          }
          
          // Otherwise, geocode the coordinates to get city information
          try {
            console.log('🌍 [HOME] Geocoding coordinates for catch:', catch_item._id);
            const geocodedLocation = await reverseGeocode(
              catch_item.location.lat, 
              catch_item.location.lng
            );
            
            return {
              ...catch_item,
              location: geocodedLocation
            };
          } catch (error) {
            console.warn('🌍 [HOME] Geocoding failed for catch:', catch_item._id, error);
            return catch_item; // Return original if geocoding fails
          }
        })
      );
      
      setCatches(catchesWithCities);
      console.log('✅ [HOME] Loaded', catchesWithCities.length, 'posts from social feed');
    } catch (error) {
      console.error('❌ [HOME] Error loading social feed:', error);
      Alert.alert('Error', 'Unable to load social feed. Please try again.');
    }
  };

  const loadMyPosts = async () => {
    if (!user) return;

    try {
      console.log('👤 [HOME] Loading my posts only...');
      const userCatches = await ApiService.getMyCatches();
      
      // Geocode user catches that don't have city information
      const userCatchesWithCities = await Promise.all(
        userCatches.map(async (catch_item) => {
          if (catch_item.location.city) {
            return catch_item;
          }
          
          try {
            console.log('🌍 [HOME] Geocoding coordinates for user catch:', catch_item._id);
            const geocodedLocation = await reverseGeocode(
              catch_item.location.lat, 
              catch_item.location.lng
            );
            
            return {
              ...catch_item,
              location: geocodedLocation
            };
          } catch (error) {
            console.warn('🌍 [HOME] Geocoding failed for user catch:', catch_item._id, error);
            return catch_item;
          }
        })
      );
      
      setCatches(userCatchesWithCities);
      console.log('✅ [HOME] Loaded', userCatchesWithCities.length, 'of my posts');
    } catch (error) {
      console.error('❌ [HOME] Error loading my posts:', error);
      Alert.alert('Error', 'Unable to load your posts. Please try again.');
    }
  };

  const loadCatches = async () => {
    if (!user) return;

    setLoading(true);
    try {
      if (showMyPostsOnly) {
        await loadMyPosts();
      } else {
        await loadAllPosts();
      }
    } finally {
      setLoading(false);
    }
  };  const onRefresh = async () => {
    setRefreshing(true);
    await loadCatches();
    setRefreshing(false);
  };

  const handleCatchPress = (catch_item: Catch) => {
    navigation.navigate('CatchDetail', { catch: catch_item });
  };

  useEffect(() => {
    loadCatches();
  }, [user, showMyPostsOnly]);

  // Refresh feed when screen comes back into focus (e.g., after deleting a catch)
  useFocusEffect(
    useCallback(() => {
      console.log('🏠 [HOME] Screen focused, refreshing feed...');
      loadCatches();
    }, [])
  );

  const sortedCatches = useMemo(() => {
    return [...catches].sort((a, b) => 
      new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
    );
  }, [catches]);

  if (loading) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.header}>
          <View style={styles.headerButtons}>
            <TouchableOpacity 
              style={styles.headerButton}
              onPress={() => navigation.navigate('Discover')}
            >
              <Text style={styles.headerButtonIcon}>👥</Text>
              <Text style={styles.headerButtonText}>Discover</Text>
            </TouchableOpacity>
            
            <TouchableOpacity 
              style={styles.fishButton}
              onPress={() => navigation.navigate('AddCatch')}
            >
              <Text style={styles.fishButtonText}>🐟</Text>
            </TouchableOpacity>
            
            <TouchableOpacity 
              style={styles.headerButton}
              onPress={() => navigation.navigate('Map')}
            >
              <Text style={styles.headerButtonIcon}>🗺️</Text>
              <Text style={styles.headerButtonText}>Map</Text>
            </TouchableOpacity>
          </View>
        </View>
        
        {/* Filter Toggle */}
        <View style={styles.filterContainer}>
          <View style={styles.filterToggle}>
            <TouchableOpacity
              style={[styles.filterButton, !showMyPostsOnly && styles.filterButtonActive]}
              onPress={() => setShowMyPostsOnly(false)}
              activeOpacity={0.7}
            >
              <Text style={[styles.filterButtonText, !showMyPostsOnly && styles.filterButtonTextActive]}>
                🌍 All Posts
              </Text>
            </TouchableOpacity>
            <TouchableOpacity
              style={[styles.filterButton, showMyPostsOnly && styles.filterButtonActive]}
              onPress={() => setShowMyPostsOnly(true)}
              activeOpacity={0.7}
            >
              <Text style={[styles.filterButtonText, showMyPostsOnly && styles.filterButtonTextActive]}>
                👤 My Posts
              </Text>
            </TouchableOpacity>
          </View>
        </View>
        
        <LoadingSpinner message={showMyPostsOnly ? 'Loading your posts...' : 'Loading feed...'} />
      </SafeAreaView>
    );
  }

  if (catches.length === 0) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.header}>
          <View style={styles.headerButtons}>
            <TouchableOpacity 
              style={styles.headerButton}
              onPress={() => navigation.navigate('Discover')}
            >
              <Text style={styles.headerButtonIcon}>👥</Text>
              <Text style={styles.headerButtonText}>Discover</Text>
            </TouchableOpacity>
            
            <TouchableOpacity 
              style={styles.fishButton}
              onPress={() => navigation.navigate('AddCatch')}
            >
              <Text style={styles.fishButtonText}>🐟</Text>
            </TouchableOpacity>
            
            <TouchableOpacity 
              style={styles.headerButton}
              onPress={() => navigation.navigate('Map')}
            >
              <Text style={styles.headerButtonIcon}>🗺️</Text>
              <Text style={styles.headerButtonText}>Map</Text>
            </TouchableOpacity>
          </View>
        </View>
        
        {/* Filter Toggle */}
        <View style={styles.filterContainer}>
          <View style={styles.filterToggle}>
            <TouchableOpacity
              style={[styles.filterButton, !showMyPostsOnly && styles.filterButtonActive]}
              onPress={() => setShowMyPostsOnly(false)}
              activeOpacity={0.7}
            >
              <Text style={[styles.filterButtonText, !showMyPostsOnly && styles.filterButtonTextActive]}>
                🌍 All Posts
              </Text>
            </TouchableOpacity>
            <TouchableOpacity
              style={[styles.filterButton, showMyPostsOnly && styles.filterButtonActive]}
              onPress={() => setShowMyPostsOnly(true)}
              activeOpacity={0.7}
            >
              <Text style={[styles.filterButtonText, showMyPostsOnly && styles.filterButtonTextActive]}>
                👤 My Posts
              </Text>
            </TouchableOpacity>
          </View>
        </View>
        
        <View style={styles.centered}>
          <Text style={styles.emptyText}>🎯 NO BATTLES YET!</Text>
          <Text style={styles.emptyText}>
            {showMyPostsOnly 
              ? 'Start sharing your fishing adventures by adding your first catch.'
              : 'Start your fishing conquest or follow elite anglers to see their victories'
            }
          </Text>
        </View>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <View style={styles.headerButtons}>
          <TouchableOpacity 
            style={styles.headerButton}
            onPress={() => navigation.navigate('Discover')}
          >
            <Text style={styles.headerButtonIcon}>👥</Text>
            <Text style={styles.headerButtonText}>Discover</Text>
          </TouchableOpacity>
          
          <TouchableOpacity 
            style={styles.fishButton}
            onPress={() => navigation.navigate('AddCatch')}
          >
            <Text style={styles.fishButtonText}>🐟</Text>
          </TouchableOpacity>
          
          <TouchableOpacity 
            style={styles.headerButton}
            onPress={() => navigation.navigate('Map')}
          >
            <Text style={styles.headerButtonIcon}>🗺️</Text>
            <Text style={styles.headerButtonText}>Map</Text>
          </TouchableOpacity>
        </View>
      </View>

      {/* Filter Toggle */}
      <View style={styles.filterContainer}>
        <View style={styles.filterToggle}>
          <TouchableOpacity
            style={[styles.filterButton, !showMyPostsOnly && styles.filterButtonActive]}
            onPress={() => setShowMyPostsOnly(false)}
            activeOpacity={0.7}
          >
            <Text style={[styles.filterButtonText, !showMyPostsOnly && styles.filterButtonTextActive]}>
              🌍 All Posts
            </Text>
          </TouchableOpacity>
          <TouchableOpacity
            style={[styles.filterButton, showMyPostsOnly && styles.filterButtonActive]}
            onPress={() => setShowMyPostsOnly(true)}
            activeOpacity={0.7}
          >
            <Text style={[styles.filterButtonText, showMyPostsOnly && styles.filterButtonTextActive]}>
              👤 My Posts
            </Text>
          </TouchableOpacity>
        </View>
      </View>

      <FlatList
        data={sortedCatches}
        keyExtractor={(item) => item._id}
        renderItem={({ item }) => (
          <CatchItem 
            item={item} 
            onPress={handleCatchPress} 
            currentUserId={user?._id}
          />
        )}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
        contentContainerStyle={styles.listContainer}
        ListEmptyComponent={
          <View style={styles.emptyContainer}>
            <Text style={styles.emptyTitle}>No catches yet!</Text>
            <Text style={styles.emptyText}>
              Start sharing your fishing adventures by adding your first catch.
            </Text>
            <TouchableOpacity
              style={styles.addButton}
              onPress={() => navigation.navigate('AddCatch')}
            >
              <Text style={styles.addButtonText}>Add First Catch</Text>
            </TouchableOpacity>
          </View>
        }
      />
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: RodRoyaleTheme.colors.background, // Sky blue
  },
  centered: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingText: {
    ...RodRoyaleTheme.typography.body,
    fontSize: 18,
    color: RodRoyaleTheme.colors.textSecondary,
  },
  header: {
    padding: RodRoyaleTheme.spacing.lg,
    paddingBottom: RodRoyaleTheme.spacing.sm,
    backgroundColor: RodRoyaleTheme.colors.surface,
    borderBottomWidth: 3,
    borderBottomColor: RodRoyaleTheme.colors.primary,
    alignItems: 'center',
    ...RodRoyaleTheme.shadows.medium,
  },
  headerButtons: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    width: '100%',
    paddingHorizontal: RodRoyaleTheme.spacing.md,
  },
  headerButton: {
    alignItems: 'center',
    justifyContent: 'center',
    padding: RodRoyaleTheme.spacing.sm,
    borderRadius: 12,
    backgroundColor: RodRoyaleTheme.colors.backgroundLight,
    borderWidth: 2,
    borderColor: RodRoyaleTheme.colors.primary,
    minWidth: 70,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 3,
    elevation: 3,
  },
  headerButtonIcon: {
    fontSize: 24,
    marginBottom: 4,
  },
  headerButtonText: {
    fontSize: 12,
    fontWeight: 'bold',
    color: RodRoyaleTheme.colors.text,
    textAlign: 'center',
  },
  fishButton: {
    width: 60,
    height: 60,
    borderRadius: 30,
    backgroundColor: RodRoyaleTheme.colors.secondary,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: RodRoyaleTheme.spacing.sm,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 3 },
    shadowOpacity: 0.3,
    shadowRadius: 5,
    elevation: 8,
    borderWidth: 3,
    borderColor: RodRoyaleTheme.colors.primaryDark,
  },
  fishButtonText: {
    fontSize: 32,
  },
  logo: {
    width: 180,
    height: 70,
    marginBottom: RodRoyaleTheme.spacing.xs,
  },
  title: {
    ...RodRoyaleTheme.typography.h1,
    marginBottom: RodRoyaleTheme.spacing.xs,
  },
  subtitle: {
    ...RodRoyaleTheme.typography.competitive,
    fontSize: 16,
    color: RodRoyaleTheme.colors.primary,
  },
  listContainer: {
    paddingHorizontal: RodRoyaleTheme.spacing.lg,
    paddingTop: RodRoyaleTheme.spacing.lg,
    paddingBottom: RodRoyaleTheme.spacing.lg,
  },
  catchItem: {
    ...ComponentThemes.card.default,
    padding: RodRoyaleTheme.spacing.md,
    marginBottom: RodRoyaleTheme.spacing.md,
    marginHorizontal: RodRoyaleTheme.spacing.md,
  },
  catchHeader: {
    marginBottom: RodRoyaleTheme.spacing.sm,
  },
  userInfo: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: RodRoyaleTheme.spacing.xs,
  },
  username: {
    ...RodRoyaleTheme.typography.accent,
    fontSize: 16,
  },
  ownUsername: {
    color: RodRoyaleTheme.colors.secondary,
    textShadowColor: RodRoyaleTheme.colors.primaryDark,
    textShadowOffset: { width: 1, height: 1 },
    textShadowRadius: 1,
  },
  fishInfo: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  species: {
    ...RodRoyaleTheme.typography.h3,
    fontSize: 20,
    flex: 1,
  },
  weight: {
    fontSize: 18,
    fontWeight: 'bold' as const,
    color: RodRoyaleTheme.colors.success,
    textShadowColor: RodRoyaleTheme.colors.surface,
    textShadowOffset: { width: 1, height: 1 },
    textShadowRadius: 1,
  },
  catchImage: {
    width: '100%',
    height: 200,
    borderRadius: RodRoyaleTheme.borderRadius.md,
    marginBottom: RodRoyaleTheme.spacing.sm,
    backgroundColor: RodRoyaleTheme.colors.backgroundLight,
    borderWidth: 2,
    borderColor: RodRoyaleTheme.colors.border,
  },
  catchFooter: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: RodRoyaleTheme.spacing.xs,
  },
  location: {
    ...RodRoyaleTheme.typography.bodySecondary,
    flex: 1,
  },
  date: {
    ...RodRoyaleTheme.typography.bodySecondary,
  },
  shareText: {
    fontSize: 12,
    color: RodRoyaleTheme.colors.textSecondary,
    fontStyle: 'italic',
    fontWeight: 'bold' as const,
  },
  emptyContainer: {
    alignItems: 'center',
    paddingVertical: RodRoyaleTheme.spacing.xxl,
  },
  emptyTitle: {
    ...RodRoyaleTheme.typography.h2,
    marginBottom: RodRoyaleTheme.spacing.sm,
  },
  emptyText: {
    ...RodRoyaleTheme.typography.body,
    textAlign: 'center',
    marginBottom: RodRoyaleTheme.spacing.lg,
    paddingHorizontal: RodRoyaleTheme.spacing.lg,
    fontWeight: 'bold' as const,
    color: RodRoyaleTheme.colors.primary,
  },
  addButton: {
    ...ComponentThemes.button.primary,
    paddingHorizontal: RodRoyaleTheme.spacing.xl,
    paddingVertical: RodRoyaleTheme.spacing.md,
  },
  addButtonText: {
    color: RodRoyaleTheme.colors.primaryDark,
    fontSize: 16,
    fontWeight: 'bold' as const,
    textTransform: 'uppercase' as const,
  },
  
  // Filter Toggle Styles
  filterContainer: {
    paddingHorizontal: RodRoyaleTheme.spacing.lg,
    paddingVertical: RodRoyaleTheme.spacing.sm,
    backgroundColor: RodRoyaleTheme.colors.background,
  },
  filterToggle: {
    flexDirection: 'row',
    backgroundColor: RodRoyaleTheme.colors.backgroundLight,
    borderRadius: 25,
    padding: 4,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  filterButton: {
    flex: 1,
    paddingVertical: 12,
    paddingHorizontal: 20,
    borderRadius: 20,
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: 'transparent',
  },
  filterButtonActive: {
    backgroundColor: RodRoyaleTheme.colors.primary,
    shadowColor: RodRoyaleTheme.colors.primary,
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.3,
    shadowRadius: 4,
    elevation: 4,
  },
  filterButtonText: {
    fontSize: 14,
    fontWeight: '600',
    color: RodRoyaleTheme.colors.textSecondary,
  },
  filterButtonTextActive: {
    color: 'white',
    fontWeight: '700',
  },
});

export default HomeScreen;
