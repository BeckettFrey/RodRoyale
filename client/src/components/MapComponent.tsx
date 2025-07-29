import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, Platform, TouchableOpacity } from 'react-native';
import { Pin } from '../types/api';

interface MapComponentProps {
  currentLocation: {
    latitude: number;
    longitude: number;
    latitudeDelta: number;
    longitudeDelta: number;
  };
  pins: Pin[];
  onMarkerPress: (pin: Pin) => void;
  getMarkerColor: (visibility: string) => string;
}

const MapComponent: React.FC<MapComponentProps> = ({
  currentLocation,
  pins,
  onMarkerPress,
  getMarkerColor,
}) => {
  const [MapModule, setMapModule] = useState<any>(null);

  console.log('🗺️ [MAP COMPONENT] Rendering with:', {
    pins: pins.length,
    currentLocation: currentLocation,
    hasMarkerPress: !!onMarkerPress,
    hasMarkerColor: !!getMarkerColor
  });

  useEffect(() => {
    console.log('🗺️ [MAP COMPONENT] Current location updated:', currentLocation);
  }, [currentLocation]);

  useEffect(() => {
    if (Platform.OS !== 'web') {
      // Dynamic import only on native platforms
      import('react-native-maps').then((module) => {
        setMapModule(module);
      }).catch((error) => {
        console.error('Failed to load map module:', error);
      });
    }
  }, []);

  if (Platform.OS === 'web') {
    console.log('🗺️ [MAP COMPONENT] Rendering web version with pins:', pins.length);
    return (
      <View style={styles.webMapPlaceholder}>
        <Text style={styles.webMapText}>🗺️ Interactive Map</Text>
        <Text style={styles.webMapSubtext}>Maps are available on mobile devices</Text>
        <Text style={styles.webMapSubtext}>Use the Expo Go app on your phone to view the map</Text>
        {pins.length > 0 ? (
          <View style={styles.webPinsList}>
            <Text style={styles.webPinsTitle}>📍 Fishing Locations ({pins.length})</Text>
            {pins.slice(0, 5).map((pin) => (
              <TouchableOpacity 
                key={pin.id} 
                style={styles.webPinItem}
                onPress={() => onMarkerPress(pin)}
              >
                <Text style={styles.webPinText}>
                  • {pin.catch_info?.species || 'Fish'} - {pin.catch_info?.weight || 'Unknown'} lbs ({pin.visibility})
                </Text>
              </TouchableOpacity>
            ))}
            {pins.length > 5 && (
              <Text style={styles.webPinText}>... and {pins.length - 5} more</Text>
            )}
          </View>
        ) : (
          <View style={styles.webPinsList}>
            <Text style={styles.webNoPinsText}>
              No fishing pins available. Create catches with "Add to Map" enabled to see them here!
            </Text>
          </View>
        )}
      </View>
    );
  }

  // Show loading while map module loads
  if (!MapModule) {
    return (
      <View style={[styles.map]}>
        <Text>Loading map...</Text>
      </View>
    );
  }

  const { default: MapView, Marker, PROVIDER_GOOGLE } = MapModule;

  console.log('🗺️ [MAP COMPONENT] Rendering native map with region:', currentLocation);

  // Native map view
  return (
    <MapView
      provider={PROVIDER_GOOGLE}
      style={styles.map}
      region={currentLocation}
      onRegionChange={(region: any) => {
        console.log('🗺️ [MAP COMPONENT] Region changed:', region);
      }}
      showsUserLocation={true}
      showsMyLocationButton={false}
      mapType="standard"
    >
      {pins.map((pin) => {
        console.log('🗺️ [MAP COMPONENT] Rendering pin:', pin.id, pin.location);
        return (
          <Marker
            key={pin.id}
            coordinate={{
              latitude: pin.location.lat,
              longitude: pin.location.lng,
            }}
            title={`🐟 ${pin.catch_info?.species || 'Fish Catch'}`}
            description={`⚖️ ${pin.catch_info?.weight || 'Unknown'} lbs | 👁️ ${pin.visibility} | 🎣 ${pin.owner_info?.username || 'Unknown'}`}
            pinColor={getMarkerColor(pin.visibility)}
            onPress={() => onMarkerPress(pin)}
          />
        );
      })}
    </MapView>
  );
};

const styles = StyleSheet.create({
  map: {
    flex: 1,
    margin: 20,
    marginTop: 10,
    borderRadius: 12,
  },
  webMapPlaceholder: {
    flex: 1,
    margin: 20,
    marginTop: 10,
    borderRadius: 12,
    backgroundColor: '#f8f9fa',
    borderWidth: 2,
    borderColor: '#e9ecef',
    borderStyle: 'dashed',
    justifyContent: 'center',
    alignItems: 'center',
    padding: 40,
  },
  webMapText: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#2196F3',
    marginBottom: 10,
  },
  webMapSubtext: {
    fontSize: 16,
    color: '#666',
    textAlign: 'center',
    marginBottom: 5,
  },
  webPinsList: {
    marginTop: 20,
    padding: 20,
    backgroundColor: 'white',
    borderRadius: 10,
    width: '100%',
    maxWidth: 400,
  },
  webPinsTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 10,
  },
  webPinItem: {
    backgroundColor: '#f8f9fa',
    padding: 10,
    marginBottom: 5,
    borderRadius: 5,
    borderLeftWidth: 3,
    borderLeftColor: '#007AFF',
  },
  webPinText: {
    fontSize: 14,
    color: '#333',
  },
  webNoPinsText: {
    fontSize: 16,
    color: '#999',
    textAlign: 'center',
    fontStyle: 'italic',
    padding: 20,
  },
});

export default MapComponent;
