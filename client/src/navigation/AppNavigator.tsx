import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { MaterialIcons } from '@expo/vector-icons';

// Screens
import LoginScreen from '../screens/LoginScreen';
import RegisterScreen from '../screens/RegisterScreen';
import HomeScreen from '../screens/HomeScreen';
import MapScreen from '../screens/MapScreen';
import ProfileScreen from '../screens/ProfileScreen';
import AddCatchScreen from '../screens/AddCatchScreen';
import EditCatchScreen from '../screens/EditCatchScreen';
import CatchDetailScreen from '../screens/CatchDetailScreen';
import DiscoverScreen from '../screens/DiscoverScreen';
import LeadersScreen from '../screens/LeaderboardScreen';

import { useAuth } from '../contexts/AuthContext';
import { Catch } from '../types/api';
import RodRoyaleTheme, { ComponentThemes } from '../theme/RodRoyaleTheme';

export type RootStackParamList = {
  Auth: undefined;
  Main: undefined;
  Login: undefined;
  Register: undefined;
  CatchDetail: { catch: Catch };
  EditCatch: { catch: Catch };
  AddCatch: undefined;
  Discover: undefined;
  Map: undefined;
};

export type MainTabParamList = {
  Home: undefined;
  Leaders: undefined;
  Profile: undefined;
};

const Stack = createNativeStackNavigator<RootStackParamList>();
const Tab = createBottomTabNavigator<MainTabParamList>();

const AuthStack = () => (
  <Stack.Navigator screenOptions={{ headerShown: false }}>
    <Stack.Screen name="Login" component={LoginScreen} />
    <Stack.Screen name="Register" component={RegisterScreen} />
  </Stack.Navigator>
);

const MainTabs = () => (
  <Tab.Navigator
    initialRouteName="Home" 
    screenOptions={({ route }) => ({
      tabBarIcon: ({ color, size }) => {
        let iconName: string;

        switch (route.name) {
          case 'Home':
            iconName = 'home';
            break;
          case 'Leaders':
            iconName = 'leaderboard';
            break;
          case 'Profile':
            iconName = 'person';
            break;
          default:
            iconName = 'circle';
        }

        return <MaterialIcons name={iconName as any} size={size} color={color} />;
      },
      tabBarActiveTintColor: RodRoyaleTheme.colors.secondary, // Mustard yellow
      tabBarInactiveTintColor: RodRoyaleTheme.colors.textSecondary,
      tabBarStyle: {
        ...ComponentThemes.tabBar,
        height: 65,
        paddingBottom: 8,
        paddingTop: 8,
      },
      tabBarLabelStyle: {
        fontSize: 12,
        fontWeight: 'bold',
        textTransform: 'uppercase',
      },
      headerShown: false,
    })}
  >
    <Tab.Screen name="Leaders" component={LeadersScreen} />
    <Tab.Screen name="Home" component={HomeScreen} />
    <Tab.Screen name="Profile" component={ProfileScreen} />
  </Tab.Navigator>
);

const AppNavigator: React.FC = () => {
  const { user, isLoading } = useAuth();

  if (isLoading) {
    return null; // or a loading component
  }

  return (
    <NavigationContainer>
      <Stack.Navigator screenOptions={{ headerShown: false }}>
        {user ? (
          <>
            <Stack.Screen name="Main" component={MainTabs} />
            <Stack.Screen name="CatchDetail" component={CatchDetailScreen} />
            <Stack.Screen name="EditCatch" component={EditCatchScreen} />
            <Stack.Screen 
              name="Discover" 
              component={DiscoverScreen}
              options={{
                headerShown: true,
                title: '🔍 Discover Anglers',
                headerStyle: {
                  backgroundColor: RodRoyaleTheme.colors.surface,
                },
                headerTitleStyle: {
                  color: RodRoyaleTheme.colors.primary,
                  fontSize: 18,
                  fontWeight: 'bold',
                },
                headerBackTitleVisible: false,
                headerTintColor: RodRoyaleTheme.colors.primary,
              }}
            />
            <Stack.Screen 
              name="Map" 
              component={MapScreen}
              options={{
                headerShown: true,
                title: '🗺️ Fishing Map',
                headerStyle: {
                  backgroundColor: RodRoyaleTheme.colors.surface,
                },
                headerTitleStyle: {
                  color: RodRoyaleTheme.colors.primary,
                  fontSize: 18,
                  fontWeight: 'bold',
                },
                headerBackTitleVisible: false,
                headerTintColor: RodRoyaleTheme.colors.primary,
              }}
            />
            <Stack.Screen 
              name="AddCatch" 
              component={AddCatchScreen}
              options={{
                headerShown: true,
                title: '🎣 Add Catch',
                headerStyle: {
                  backgroundColor: RodRoyaleTheme.colors.surface,
                },
                headerTitleStyle: {
                  color: RodRoyaleTheme.colors.text,
                  fontSize: 18,
                  fontWeight: 'bold',
                },
                headerBackTitleVisible: false,
                headerTintColor: RodRoyaleTheme.colors.primary,
              }}
            />
          </>
        ) : (
          <Stack.Screen name="Auth" component={AuthStack} />
        )}
      </Stack.Navigator>
    </NavigationContainer>
  );
};

export default AppNavigator;
