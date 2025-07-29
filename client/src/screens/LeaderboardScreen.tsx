import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  ScrollView,
  StyleSheet,
  SafeAreaView,
  TouchableOpacity,
  RefreshControl,
  Alert,
  Image,
} from 'react-native';
import LoadingSpinner from '../components/LoadingSpinner';
import { useAuth } from '../contexts/AuthContext';
import ApiService from '../services/api';
import { UserStats, LeaderboardResponse, LeaderboardMetric, LeaderboardUser } from '../types/api';
import RodRoyaleTheme, { ComponentThemes } from '../theme/RodRoyaleTheme';
import { useNavigation } from '@react-navigation/native';
import { BottomTabNavigationProp } from '@react-navigation/bottom-tabs';
import { MainTabParamList } from '../navigation/AppNavigator';

type LeaderboardScreenNavigationProp = BottomTabNavigationProp<MainTabParamList, 'Leaders'>;

const LeaderboardScreen: React.FC = () => {
  const navigation = useNavigation<LeaderboardScreenNavigationProp>();
  const [myStats, setMyStats] = useState<UserStats | null>(null);
  const [followingLeaderboard, setFollowingLeaderboard] = useState<LeaderboardResponse | null>(null);
  const [globalLeaderboard, setGlobalLeaderboard] = useState<LeaderboardResponse | null>(null);
  const [selectedMetric, setSelectedMetric] = useState<LeaderboardMetric>('biggest_catch_month');
  const [selectedView, setSelectedView] = useState<'following' | 'global'>('following');
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const { user } = useAuth();

  const metricLabels = {
    biggest_catch_month: '� BIGGEST CATCH',
    catches_this_month: '🎣 MOST CATCHES',
    best_average_month: '⚡ BEST AVERAGE'
  };

  const metricUnits = {
    biggest_catch_month: 'lbs',
    catches_this_month: 'catches',
    best_average_month: 'lbs avg'
  };

  const loadData = async () => {
    if (!user) return;

    try {
      // Load personal stats
      const stats = await ApiService.getMyStats();
      setMyStats(stats);

      // Load leaderboards based on selected view and metric
      const [following, global] = await Promise.all([
        ApiService.getFollowingLeaderboard(selectedMetric),
        ApiService.getGlobalLeaderboard(selectedMetric)
      ]);

      setFollowingLeaderboard(following);
      setGlobalLeaderboard(global);
    } catch (error) {
      console.error('Error loading leaderboard data:', error);
      Alert.alert('Error', 'Failed to load leaderboard data. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadData();
    setRefreshing(false);
  };

  const handleMetricChange = (metric: LeaderboardMetric) => {
    setSelectedMetric(metric);
    setLoading(true);
  };

  const handleViewChange = (view: 'following' | 'global') => {
    setSelectedView(view);
  };

  useEffect(() => {
    loadData();
  }, [user, selectedMetric]);

  const renderStatsCard = () => {
    if (!myStats) return null;

    return (
      <View style={styles.statsCard}>
        <Text style={styles.statsTitle}>⚔️ YOUR BATTLE STATS</Text>
        <View style={styles.statsGrid}>
          <View style={styles.statItem}>
            <Text style={styles.statValue}>{myStats.total_catches}</Text>
            <Text style={styles.statLabel}>TOTAL VICTORIES</Text>
          </View>
          <View style={styles.statItem}>
            <Text style={styles.statValue}>{myStats.catches_this_month}</Text>
            <Text style={styles.statLabel}>THIS MONTH</Text>
          </View>
          <View style={styles.statItem}>
            <Text style={styles.statValue}>{myStats.biggest_catch_month.toFixed(1)} lbs</Text>
            <Text style={styles.statLabel}>BIGGEST TROPHY</Text>
          </View>
          <View style={styles.statItem}>
            <Text style={styles.statValue}>{myStats.best_average_month.toFixed(1)} lbs</Text>
            <Text style={styles.statLabel}>POWER AVERAGE</Text>
          </View>
        </View>
        {myStats.biggest_catch_species && (
          <Text style={styles.biggestCatchSpecies}>
            � CHAMPION CATCH: {myStats.biggest_catch_species.toUpperCase()}
          </Text>
        )}
      </View>
    );
  };

  const renderMetricSelector = () => (
    <View style={styles.metricSelector}>
      {Object.entries(metricLabels).map(([metric, label]) => (
        <TouchableOpacity
          key={metric}
          style={[
            styles.metricButton,
            selectedMetric === metric && styles.selectedMetricButton
          ]}
          onPress={() => handleMetricChange(metric as LeaderboardMetric)}
        >
          <Text style={[
            styles.metricButtonText,
            selectedMetric === metric && styles.selectedMetricButtonText
          ]}>
            {label}
          </Text>
        </TouchableOpacity>
      ))}
    </View>
  );

  const renderViewSelector = () => (
    <View style={styles.viewSelector}>
      <TouchableOpacity
        style={[
          styles.viewButton,
          selectedView === 'following' && styles.selectedViewButton
        ]}
        onPress={() => handleViewChange('following')}
      >
        <Text style={[
          styles.viewButtonText,
          selectedView === 'following' && styles.selectedViewButtonText
        ]}>
          👥 SQUAD BATTLE
        </Text>
      </TouchableOpacity>
      <TouchableOpacity
        style={[
          styles.viewButton,
          selectedView === 'global' && styles.selectedViewButton
        ]}
        onPress={() => handleViewChange('global')}
      >
        <Text style={[
          styles.viewButtonText,
          selectedView === 'global' && styles.selectedViewButtonText
        ]}>
        🌍 WORLD ARENA
        </Text>
      </TouchableOpacity>
    </View>
  );

  const renderLeaderboardItem = (item: LeaderboardUser, index: number) => {
    const value = item[selectedMetric];
    const unit = metricUnits[selectedMetric];
    
    const getRankEmoji = (rank: number) => {
      switch (rank) {
        case 1: return '🥇';
        case 2: return '🥈';
        case 3: return '🥉';
        default: return `#${rank}`;
      }
    };

    return (
      <View key={item._id} style={[
        styles.leaderboardItem,
        item.is_current_user && styles.currentUserItem
      ]}>
        <View style={styles.rankContainer}>
          <Text style={[
            styles.rankText,
            item.is_current_user && styles.currentUserText
          ]}>
            {getRankEmoji(item.rank)}
          </Text>
        </View>
        <View style={styles.userContainer}>
          <Text style={[
            styles.usernameText,
            item.is_current_user && styles.currentUserText
          ]}>
            {item.is_current_user ? '👑 You' : `🎣 ${item.username}`}
          </Text>
        </View>
        <View style={styles.valueContainer}>
          <Text style={[
            styles.valueText,
            item.is_current_user && styles.currentUserText
          ]}>
            {typeof value === 'number' ? value.toFixed(1) : value} {unit}
          </Text>
        </View>
      </View>
    );
  };

  const renderLeaderboard = () => {
    const currentLeaderboard = selectedView === 'following' ? followingLeaderboard : globalLeaderboard;
    
    if (!currentLeaderboard) return null;

    return (
      <View style={styles.leaderboardContainer}>
        <View style={styles.leaderboardHeader}>
          <Text style={styles.leaderboardTitle}>
            {selectedView === 'following' ? '👥 Following Rankings' : '🌍 Global Rankings'}
          </Text>
          <Text style={styles.leaderboardSubtitle}>
            {metricLabels[selectedMetric]} • {currentLeaderboard.total_users} anglers
          </Text>
          {currentLeaderboard.current_user_rank && (
            <Text style={styles.yourRank}>
              Your rank: #{currentLeaderboard.current_user_rank}
            </Text>
          )}
        </View>
        
        <ScrollView style={styles.leaderboardList}>
          {currentLeaderboard.leaderboard.map((item, index) => 
            renderLeaderboardItem(item, index)
          )}
        </ScrollView>
      </View>
    );
  };

  if (loading && !refreshing) {
    return (
      <SafeAreaView style={styles.container}>
        <LoadingSpinner message="Loading leaderboard..." />
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView
        style={styles.scrollView}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
      >
        <View style={styles.header}>
          <Image 
            source={require('../../assets/images/rod_royale_title_logo.png')} 
            style={styles.logo}
            resizeMode="contain"
          />
          <Text style={styles.subtitle}>MONTHLY BATTLE ARENA</Text>
          <Text style={styles.description}>Compete with elite anglers worldwide</Text>
        </View>

        {renderStatsCard()}
        {renderMetricSelector()}
        {renderViewSelector()}
        {renderLeaderboard()}
      </ScrollView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: RodRoyaleTheme.colors.background, // Sky blue
  },
  scrollView: {
    flex: 1,
  },
  header: {
    padding: RodRoyaleTheme.spacing.lg,
    alignItems: 'center',
    backgroundColor: RodRoyaleTheme.colors.surface,
    borderBottomWidth: 3,
    borderBottomColor: RodRoyaleTheme.colors.primary,
    ...RodRoyaleTheme.shadows.medium,
  },
  logo: {
    width: 200,
    height: 80,
    marginBottom: RodRoyaleTheme.spacing.sm,
  },
  title: {
    ...RodRoyaleTheme.typography.h1,
    marginBottom: RodRoyaleTheme.spacing.sm,
  },
  subtitle: {
    ...RodRoyaleTheme.typography.competitive,
    color: RodRoyaleTheme.colors.primary,
    marginBottom: RodRoyaleTheme.spacing.xs,
  },
  description: {
    ...RodRoyaleTheme.typography.bodySecondary,
    textAlign: 'center',
    fontStyle: 'italic',
  },
  centered: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingText: {
    ...RodRoyaleTheme.typography.body,
    fontSize: 18,
  } as any,
  statsCard: {
    margin: RodRoyaleTheme.spacing.md,
    padding: RodRoyaleTheme.spacing.lg,
    ...ComponentThemes.card.competitive,
    backgroundColor: RodRoyaleTheme.colors.surface,
  },
  statsTitle: {
    ...RodRoyaleTheme.typography.competitive,
    color: RodRoyaleTheme.colors.secondary,
    fontSize: 20,
    marginBottom: RodRoyaleTheme.spacing.md,
    textAlign: 'center',
    textShadowColor: RodRoyaleTheme.colors.primaryDark,
    textShadowOffset: { width: 1, height: 1 },
    textShadowRadius: 2,
  },
  statsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  statItem: {
    width: '48%',
    alignItems: 'center',
    marginBottom: RodRoyaleTheme.spacing.md,
    padding: RodRoyaleTheme.spacing.sm,
    backgroundColor: RodRoyaleTheme.colors.backgroundLight,
    borderRadius: RodRoyaleTheme.borderRadius.md,
    borderWidth: 2,
    borderColor: RodRoyaleTheme.colors.primary,
  },
  statValue: {
    fontSize: 28,
    fontWeight: 'bold',
    color: RodRoyaleTheme.colors.secondary,
    textShadowColor: RodRoyaleTheme.colors.primaryDark,
    textShadowOffset: { width: 1, height: 1 },
    textShadowRadius: 2,
  },
  statLabel: {
    ...RodRoyaleTheme.typography.competitive,
    fontSize: 10,
    color: RodRoyaleTheme.colors.text,
    marginTop: RodRoyaleTheme.spacing.xs,
    textAlign: 'center',
  },
  biggestCatchSpecies: {
    textAlign: 'center',
    ...RodRoyaleTheme.typography.competitive,
    fontSize: 14,
    color: RodRoyaleTheme.colors.success,
    marginTop: RodRoyaleTheme.spacing.sm,
  },
  metricSelector: {
    flexDirection: 'row',
    margin: RodRoyaleTheme.spacing.md,
    backgroundColor: RodRoyaleTheme.colors.surface,
    borderRadius: RodRoyaleTheme.borderRadius.md,
    padding: RodRoyaleTheme.spacing.xs,
    borderWidth: 2,
    borderColor: RodRoyaleTheme.colors.primary,
    ...RodRoyaleTheme.shadows.medium,
  },
  metricButton: {
    flex: 1,
    padding: RodRoyaleTheme.spacing.sm,
    alignItems: 'center',
    borderRadius: RodRoyaleTheme.borderRadius.sm,
    marginHorizontal: 2,
  },
  selectedMetricButton: {
    backgroundColor: RodRoyaleTheme.colors.secondary,
    borderWidth: 2,
    borderColor: RodRoyaleTheme.colors.primaryDark,
  },
  metricButtonText: {
    fontSize: 12,
    color: RodRoyaleTheme.colors.text,
    fontWeight: 'bold',
    textAlign: 'center',
  },
  selectedMetricButtonText: {
    color: RodRoyaleTheme.colors.primaryDark,
    fontWeight: 'bold',
    textShadowColor: RodRoyaleTheme.colors.surface,
    textShadowOffset: { width: 1, height: 1 },
    textShadowRadius: 1,
  },
  viewSelector: {
    flexDirection: 'row',
    marginHorizontal: RodRoyaleTheme.spacing.md,
    marginBottom: RodRoyaleTheme.spacing.md,
    backgroundColor: RodRoyaleTheme.colors.surface,
    borderRadius: RodRoyaleTheme.borderRadius.md,
    padding: RodRoyaleTheme.spacing.xs,
    borderWidth: 2,
    borderColor: RodRoyaleTheme.colors.primary,
    ...RodRoyaleTheme.shadows.medium,
  },
  viewButton: {
    flex: 1,
    padding: RodRoyaleTheme.spacing.sm,
    alignItems: 'center',
    borderRadius: RodRoyaleTheme.borderRadius.sm,
    marginHorizontal: 2,
  },
  selectedViewButton: {
    backgroundColor: RodRoyaleTheme.colors.success,
    borderWidth: 2,
    borderColor: RodRoyaleTheme.colors.primaryDark,
  },
  viewButtonText: {
    fontSize: 14,
    color: RodRoyaleTheme.colors.text,
    fontWeight: 'bold',
  },
  selectedViewButtonText: {
    color: RodRoyaleTheme.colors.surface,
    fontWeight: 'bold',
    textShadowColor: RodRoyaleTheme.colors.primaryDark,
    textShadowOffset: { width: 1, height: 1 },
    textShadowRadius: 1,
  },
  leaderboardContainer: {
    margin: RodRoyaleTheme.spacing.md,
    ...ComponentThemes.card.competitive,
  },
  leaderboardHeader: {
    padding: RodRoyaleTheme.spacing.lg,
    borderBottomWidth: 2,
    borderBottomColor: RodRoyaleTheme.colors.primary,
    backgroundColor: RodRoyaleTheme.colors.backgroundLight,
    borderTopLeftRadius: 12,
    borderTopRightRadius: 12,
  },
  leaderboardTitle: {
    ...RodRoyaleTheme.typography.competitive,
    fontSize: 18,
    color: RodRoyaleTheme.colors.primary,
    marginBottom: RodRoyaleTheme.spacing.xs,
  },
  leaderboardSubtitle: {
    ...RodRoyaleTheme.typography.bodySecondary,
    fontSize: 12,
    marginBottom: RodRoyaleTheme.spacing.xs,
  },
  yourRank: {
    fontSize: 16,
    color: RodRoyaleTheme.colors.secondary,
    fontWeight: 'bold',
    textShadowColor: RodRoyaleTheme.colors.primaryDark,
    textShadowOffset: { width: 1, height: 1 },
    textShadowRadius: 1,
  },
  leaderboardList: {
    maxHeight: 400,
    borderBottomLeftRadius: 12,
    borderBottomRightRadius: 12,
    overflow: 'hidden',
  },
  leaderboardItem: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: RodRoyaleTheme.spacing.md,
    borderBottomWidth: 1,
    borderBottomColor: RodRoyaleTheme.colors.border,
    backgroundColor: RodRoyaleTheme.colors.surface,
  },
  currentUserItem: {
    backgroundColor: RodRoyaleTheme.colors.successLight,
    borderLeftWidth: 4,
    borderLeftColor: RodRoyaleTheme.colors.secondary,
  },
  rankContainer: {
    width: 50,
    alignItems: 'center',
  },
  rankText: {
    fontSize: 16,
    fontWeight: 'bold',
    color: RodRoyaleTheme.colors.primary,
  },
  userContainer: {
    flex: 1,
    marginLeft: RodRoyaleTheme.spacing.sm,
  },
  usernameText: {
    fontSize: 16,
    color: RodRoyaleTheme.colors.text,
    fontWeight: '600',
  },
  currentUserText: {
    color: RodRoyaleTheme.colors.secondary,
    fontWeight: 'bold',
    textShadowColor: RodRoyaleTheme.colors.primaryDark,
    textShadowOffset: { width: 1, height: 1 },
    textShadowRadius: 1,
  },
  valueContainer: {
    alignItems: 'flex-end',
  },
  valueText: {
    fontSize: 16,
    fontWeight: 'bold',
    color: RodRoyaleTheme.colors.success,
  },
});

export default LeaderboardScreen;
