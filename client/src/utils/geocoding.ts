import * as Location from 'expo-location';
import { Location as LocationType } from '../types/api';

export const reverseGeocode = async (latitude: number, longitude: number): Promise<LocationType> => {
  try {
    console.log('🌍 [GEOCODING] Starting reverse geocode for:', latitude, longitude);
    const result = await Location.reverseGeocodeAsync({
      latitude,
      longitude,
    });

    console.log('🌍 [GEOCODING] Raw result:', JSON.stringify(result, null, 2));

    if (result && result.length > 0) {
      const location = result[0];
      console.log('🌍 [GEOCODING] First location result:', JSON.stringify(location, null, 2));
      
      // Try multiple fields for city name in order of preference
      const city = location.city || 
                   location.subregion || 
                   location.district || 
                   location.name ||
                   undefined;
      
      const state = location.region || 
                    location.isoCountryCode || 
                    undefined;
      
      const country = location.country || undefined;
      
      console.log('🌍 [GEOCODING] Extracted data:', { city, state, country });
      
      const geocodedLocation = {
        lat: latitude,
        lng: longitude,
        city,
        state,
        country,
      };
      
      console.log('🌍 [GEOCODING] Final location object:', geocodedLocation);
      return geocodedLocation;
    } else {
      console.warn('🌍 [GEOCODING] No results returned from reverse geocoding');
    }
  } catch (error) {
    console.warn('🌍 [GEOCODING] Reverse geocoding failed:', error);
  }

  // Fallback to coordinates only if geocoding fails
  console.log('🌍 [GEOCODING] Using coordinate fallback');
  return {
    lat: latitude,
    lng: longitude,
  };
};

export const formatLocationDisplay = (location: LocationType): string => {
  if (location.city) {
    const parts = [location.city];
    if (location.state) {
      parts.push(location.state);
    }
    if (location.country) {
      parts.push(location.country);
    }
    return parts.join(', ');
  }
  
  // Fallback to coordinates if no city data
  return `${location.lat.toFixed(4)}, ${location.lng.toFixed(4)}`;
};
