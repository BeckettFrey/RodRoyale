import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  Alert,
  SafeAreaView,
} from 'react-native';
import LoadingSpinner from '../components/LoadingSpinner';
import * as Location from 'expo-location';
import { useAuth } from '../contexts/AuthContext';
import { useFocusEffect, useNavigation } from '@react-navigation/native';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { RootStackParamList } from '../navigation/AppNavigator';
import ApiService from '../services/api';
import { Pin } from '../types/api';
import MapComponent from '../components/MapComponent';

type MapScreenNavigationProp = NativeStackNavigationProp<RootStackParamList, 'Map'>;

interface MapScreenProps {}

const MapScreen: React.FC<MapScreenProps> = () => {
  const navigation = useNavigation<MapScreenNavigationProp>();
  const [pins, setPins] = useState<Pin[]>([]);
  const [loading, setLoading] = useState(true);
  const [currentLocation, setCurrentLocation] = useState({
    latitude: 37.78825,
    longitude: -122.4324,
    latitudeDelta: 0.0922,
    longitudeDelta: 0.0421,
  });
  const { user } = useAuth();

  // Calculate deltas based on pins spread
  const calculateMapRegion = (pins: Pin[], userLocation?: { latitude: number; longitude: number }) => {
    if (pins.length === 0) {
      // If no pins, use user location or default with standard zoom
      const centerLat = userLocation?.latitude || 37.78825;
      const centerLng = userLocation?.longitude || -122.4324;
      return {
        latitude: centerLat,
        longitude: centerLng,
        latitudeDelta: 0.05, // Closer zoom when no pins
        longitudeDelta: 0.05,
      };
    }

    // Calculate bounds from all pins
    const latitudes = pins.map(pin => pin.location.lat);
    const longitudes = pins.map(pin => pin.location.lng);

    console.log("PINS",pins)
    
    const minLat = Math.min(...latitudes);
    const maxLat = Math.max(...latitudes);
    const minLng = Math.min(...longitudes);
    const maxLng = Math.max(...longitudes);
    
    // Calculate center
    const centerLat = (minLat + maxLat) / 2;
    const centerLng = (minLng + maxLng) / 2;
    
    // Calculate deltas with padding (20% extra space around pins)
    const latDelta = Math.max((maxLat - minLat) * 1.2, 0.01); // Minimum delta for single pin
    const lngDelta = Math.max((maxLng - minLng) * 1.2, 0.01);
    
    return {
      latitude: centerLat,
      longitude: centerLng,
      latitudeDelta: latDelta,
      longitudeDelta: lngDelta,
    };
  };

  const loadPins = async (centerLat?: number, centerLng?: number, radius?: number) => {
    if (!user) {
      console.log('🗺️ [MAP] No user logged in, skipping pin load');
      setLoading(false);
      return;
    }

    try {
      console.log('🗺️ [MAP] Loading pins for user:', user.username);
      console.log('🗺️ [MAP] Loading with params:', { centerLat, centerLng, radius });
      
      // Use API filtering parameters if provided
      const mapPins = await ApiService.getPins(centerLat, centerLng, radius);
      console.log('🗺️ [MAP] Raw API response:', mapPins);
      console.log('🗺️ [MAP] Loaded pins count:', mapPins.length);
      
      // Enhanced validation with detailed logging
      const validPins = mapPins.filter((pin, index) => {
        console.log(`🗺️ [MAP] Validating pin ${index}:`, pin);
        
        if (!pin.id) {
          console.warn(`🗺️ [MAP] Pin ${index} missing id:`, pin);
          return false;
        }
        
        if (!pin.location) {
          console.warn(`🗺️ [MAP] Pin ${index} missing location:`, pin);
          return false;
        }
        
        if (typeof pin.location.lat !== 'number' || isNaN(pin.location.lat)) {
          console.warn(`🗺️ [MAP] Pin ${index} invalid latitude:`, pin.location.lat);
          return false;
        }
        
        if (typeof pin.location.lng !== 'number' || isNaN(pin.location.lng)) {
          console.warn(`🗺️ [MAP] Pin ${index} invalid longitude:`, pin.location.lng);
          return false;
        }
        
        // Check if coordinates are reasonable (not 0,0 or extreme values)
        if (Math.abs(pin.location.lat) > 90 || Math.abs(pin.location.lng) > 180) {
          console.warn(`🗺️ [MAP] Pin ${index} has extreme coordinates:`, pin.location);
          return false;
        }
        
        console.log(`🗺️ [MAP] Pin ${index} is valid:`, {
          id: pin.id,
          lat: pin.location.lat,
          lng: pin.location.lng,
          visibility: pin.visibility
        });
        return true;
      });
      
      console.log('🗺️ [MAP] Valid pins count:', validPins.length);
      console.log('🗺️ [MAP] Valid pins:', validPins.map(p => ({ 
        id: p.id, 
        lat: p.location.lat, 
        lng: p.location.lng,
        species: p.catch_info?.species || 'Unknown'
      })));
      
      setPins(validPins);
      
      // Update map region based on pins, but only if we have pins
      if (validPins.length > 0) {
        const newRegion = calculateMapRegion(validPins, currentLocation);
        setCurrentLocation(newRegion);
        console.log('🗺️ [MAP] Updated region based on pins:', newRegion);
      } else {
        console.log('🗺️ [MAP] No valid pins, keeping current region');
      }
    } catch (error: any) {
      console.error('🗺️ [MAP] Error loading pins:', error);
      // More detailed error logging
      if (error.response) {
        console.error('🗺️ [MAP] API Error Response:', error.response.data);
        console.error('🗺️ [MAP] API Error Status:', error.response.status);
      }
      Alert.alert('Error', 'Unable to load map pins. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const getCurrentLocation = async () => {
    try {
      let { status } = await Location.requestForegroundPermissionsAsync();
      
      if (status !== 'granted') {
        console.warn('📍 [MAP] Location permission denied');
        return;
      }

      let location = await Location.getCurrentPositionAsync({
        accuracy: Location.Accuracy.High,
      });
      
      const userLocation = {
        latitude: location.coords.latitude,
        longitude: location.coords.longitude,
      };
      
      // Update current location, but keep existing deltas if pins are loaded
      setCurrentLocation(prev => ({
        ...userLocation,
        latitudeDelta: prev.latitudeDelta,
        longitudeDelta: prev.longitudeDelta,
      }));
      
      console.log('📍 [MAP] Got user location:', userLocation);
      
      // Optionally reload pins within a reasonable radius of user location
      // This helps show relevant nearby pins
      if (pins.length === 0) {
        await loadPins(userLocation.latitude, userLocation.longitude, 50); // 50km radius
      }
    } catch (error) {
      console.error('❌ [MAP] Error getting location:', error);
    }
  };

  useEffect(() => {
    console.log('🗺️ [MAP] MapScreen mounted, user:', user?.username);
    getCurrentLocation();
    loadPins(); // Load all pins initially
  }, [user]);

  // Reload pins when screen comes into focus (e.g., after adding a new catch)
  useFocusEffect(
    React.useCallback(() => {
      console.log('🗺️ [MAP] Screen focused, reloading pins...');
      loadPins();
    }, [user])
  );

  // Debug effect to log state changes
  useEffect(() => {
    console.log('🗺️ [MAP] Pins state updated:', pins.length, 'pins');
    console.log('🗺️ [MAP] Current pins:', pins.map(p => ({ 
      id: p.id, 
      lat: p.location.lat, 
      lng: p.location.lng 
    })));
  }, [pins]);

  useEffect(() => {
    console.log('🗺️ [MAP] Current location updated:', currentLocation);
  }, [currentLocation]);

  // Function to refresh pins within current map bounds
  const refreshPinsInView = async () => {
    const radius = Math.max(
      currentLocation.latitudeDelta * 111, // Convert degrees to km (rough)
      currentLocation.longitudeDelta * 111 * Math.cos(currentLocation.latitude * Math.PI / 180)
    );
    
    console.log('🔄 [MAP] Refreshing pins within view, radius:', radius.toFixed(2), 'km');
    await loadPins(currentLocation.latitude, currentLocation.longitude, Math.min(radius, 100)); // Max 100km
  };

  const getMarkerColor = (visibility: string) => {
    switch (visibility) {
      case 'public':
        return '#4CAF50'; // Green
      case 'mutuals':
        return '#FF9800'; // Orange  
      case 'private':
        return '#F44336'; // Red
      default:
        return '#2196F3'; // Blue
    }
  };

  const handleMarkerPress = (pin: Pin) => {
    console.log('🗺️ [MAP] Marker pressed:', pin);
    
    const species = pin.catch_info?.species || 'Fish';
    const username = pin.owner_info?.username || 'Unknown Angler';
    const weight = pin.catch_info?.weight || 'Unknown';
    const date = pin.catch_info?.created_at 
      ? new Date(pin.catch_info.created_at).toLocaleDateString()
      : 'Unknown Date';
    
    // Simple location display with coordinates
    const locationDisplay = `${pin.location.lat.toFixed(4)}, ${pin.location.lng.toFixed(4)}`;
    
    Alert.alert(
      `🐟 ${species}`,
      `🎣 Caught by: ${username}\n⚖️ Weight: ${weight} lbs\n📅 Date: ${date}\n📍 Location: ${locationDisplay}\n👁️ Visibility: ${pin.visibility}`,
      [{ text: 'OK' }]
    );
  };

  if (loading) {
    return (
      <SafeAreaView style={styles.container}>
        <LoadingSpinner message="🎣 Loading fishing spots..." />
      </SafeAreaView>
    );
  }

  console.log('🗺️ [MAP] Rendering MapComponent with:', {
    pinCount: pins.length,
    currentLocation,
    pinsPreview: pins.slice(0, 3) // Log first 3 pins
  });

  return (
    <SafeAreaView style={styles.container}>
      <MapComponent
        currentLocation={currentLocation}
        pins={pins}
        onMarkerPress={handleMarkerPress}
        getMarkerColor={getMarkerColor}
      />

      {pins.length === 0 && (
        <View style={styles.noPinsContainer}>
          <Text style={styles.noPinsText}>
            No pins yet! Add catches with "Add to Map" enabled to see them here.
          </Text>
        </View>
      )}
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
    textAlign: 'center',
  },
  noPinsContainer: {
    position: 'absolute',
    bottom: 20,
    left: 20,
    right: 20,
    backgroundColor: 'white',
    padding: 20,
    borderRadius: 15,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.25,
    shadowRadius: 4,
    elevation: 5,
    alignItems: 'center',
  },
  noPinsText: {
    fontSize: 16,
    color: '#999',
    fontStyle: 'italic',
    textAlign: 'center',
  },
});

export default MapScreen;