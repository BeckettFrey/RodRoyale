import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  SafeAreaView,
  ScrollView,
  Alert,
  Switch,
  Image,
  Animated,
  ActivityIndicator,
} from 'react-native';
import * as ImagePicker from 'expo-image-picker';
import * as Location from 'expo-location';
import { useNavigation } from '@react-navigation/native';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { RootStackParamList } from '../navigation/AppNavigator';
import ApiService from '../services/api';
import { Location as LocationType } from '../types/api';
import { reverseGeocode, formatLocationDisplay } from '../utils/geocoding';
import RodRoyaleTheme from '../theme/RodRoyaleTheme';

type AddCatchScreenNavigationProp = NativeStackNavigationProp<RootStackParamList, 'AddCatch'>;

const AddCatchScreen: React.FC = () => {
  const [species, setSpecies] = useState('');
  const [weight, setWeight] = useState('');
  const [photoUrl, setPhotoUrl] = useState('');
  const [location, setLocation] = useState<LocationType | null>(null);
  const [sharedWithFollowers, setSharedWithFollowers] = useState(true);
  const [addToMap, setAddToMap] = useState(true);
  const [mapVisibility, setMapVisibility] = useState<'private' | 'mutuals' | 'public'>('public');
  const [isLoading, setIsLoading] = useState(false);
  const [uploadingImage, setUploadingImage] = useState(false);
  const [gettingLocation, setGettingLocation] = useState(false);
  const [showSuccess, setShowSuccess] = useState(false);
  const [fadeAnim] = useState(new Animated.Value(0));
  const [slideAnim] = useState(new Animated.Value(50));

  const navigation = useNavigation<AddCatchScreenNavigationProp>();

  useEffect(() => {
    getCurrentLocation();
    // Animate form appearance
    Animated.parallel([
      Animated.timing(fadeAnim, {
        toValue: 1,
        duration: 800,
        useNativeDriver: true,
      }),
      Animated.timing(slideAnim, {
        toValue: 0,
        duration: 800,
        useNativeDriver: true,
      }),
    ]).start();
  }, []);

  const clearForm = () => {
    setSpecies('');
    setWeight('');
    setPhotoUrl('');
    setLocation(null);
    setSharedWithFollowers(true);
    setAddToMap(true);
    setMapVisibility('public');
    setShowSuccess(false);
  };

  const getCurrentLocation = async () => {
    setGettingLocation(true);
    
    try {
      let { status } = await Location.requestForegroundPermissionsAsync();
      
      if (status !== 'granted') {
        Alert.alert('Permission denied', 'Please allow location access to tag your catch location.');
        setGettingLocation(false);
        return;
      }

      let position = await Location.getCurrentPositionAsync({
        accuracy: Location.Accuracy.High,
      });
      
      const locationWithCity = await reverseGeocode(
        position.coords.latitude,
        position.coords.longitude
      );
      
      setLocation(locationWithCity);
      setGettingLocation(false);
    } catch (error) {
      console.error('Error getting location:', error);
      Alert.alert('Location Error', 'Unable to get your current location.');
      setGettingLocation(false);
    }
  };

  const handleImagePicker = async () => {
    try {
      const permissionResult = await ImagePicker.requestMediaLibraryPermissionsAsync();
      
      if (permissionResult.granted === false) {
        Alert.alert('Permission required', 'Please allow access to your photo library to add catch photos.');
        return;
      }

      const result = await ImagePicker.launchImageLibraryAsync({
        mediaTypes: ImagePicker.MediaTypeOptions.Images,
        allowsEditing: true,
        aspect: [4, 3],
        quality: 0.8,
      });

      if (!result.canceled && result.assets[0]) {
        setUploadingImage(true);
        
        try {
          const uploadedUrl = await ApiService.uploadImage(result.assets[0].uri);
          setPhotoUrl(uploadedUrl);
        } catch (error) {
          console.error('Image upload failed:', error);
          Alert.alert('Upload Failed', 'Unable to upload image. Please try again.');
        } finally {
          setUploadingImage(false);
        }
      }
    } catch (error) {
      console.error('Image picker error:', error);
      Alert.alert('Error', 'Unable to pick image. Please try again.');
      setUploadingImage(false);
    }
  };

  const handleSubmit = async () => {
    if (!species.trim() || !weight.trim()) {
      Alert.alert('Missing Information', 'Please fill in species and weight.');
      return;
    }

    if (!location) {
      Alert.alert('Location Required', 'Please get your location first.');
      return;
    }

    if (!photoUrl.trim()) {
      Alert.alert('Photo Required', 'Please add a photo of your catch.');
      return;
    }

    setIsLoading(true);

    try {
      const catchData = {
        species: species.trim(),
        weight: parseFloat(weight),
        photo_url: photoUrl,
        location: location,
        shared_with_followers: sharedWithFollowers,
      };

      const newCatch = await ApiService.createCatch(catchData);

      // Create map pin if requested
      if (addToMap) {
        try {
          const pinData = {
            catch_id: newCatch._id,
            location: location,
            visibility: mapVisibility,
          };
          
          await ApiService.createPin(pinData);
        } catch (pinError) {
          console.warn('Failed to create map pin:', pinError);
        }
      }

      // Clear form and show success message
      clearForm();
      setShowSuccess(true);
      
      // Navigate to home screen after showing success message briefly
      setTimeout(() => {
        navigation.navigate('Main');
      }, 2000); // Show success message for 2 seconds

    } catch (error) {
      console.error('Submit failed:', error);
      Alert.alert('Error', 'Unable to save catch. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView 
        style={styles.scrollView} 
        showsVerticalScrollIndicator={false}
        contentContainerStyle={styles.scrollContent}
      >
        {/* Modern Header */}
        <View style={styles.header}>
          
          {showSuccess && (
            <Animated.View style={[styles.successBanner, { opacity: fadeAnim }]}>
              <Text style={styles.successText}>🎉 Catch saved successfully!</Text>
              <Text style={styles.successSubtext}>Redirecting to feed...</Text>
            </Animated.View>
          )}
        </View>

        {/* Modern Form */}
        <Animated.View 
          style={[
            styles.form, 
            { 
              opacity: fadeAnim,
              transform: [{ translateY: slideAnim }]
            }
          ]}
        >
          {/* Photo Section - Featured at top */}
          <View style={styles.photoSection}>
            <Text style={styles.sectionTitle}>📸 Photo Evidence</Text>
            <TouchableOpacity
              style={[styles.photoUploadArea, photoUrl && styles.photoUploadAreaWithImage]}
              onPress={handleImagePicker}
              disabled={uploadingImage}
              activeOpacity={0.8}
            >
              {photoUrl ? (
                <View style={styles.imageContainer}>
                  <Image source={{ uri: photoUrl }} style={styles.uploadedImage} />
                  <View style={styles.imageOverlay}>
                    <Text style={styles.changePhotoText}>Tap to change</Text>
                  </View>
                </View>
              ) : (
                <View style={styles.uploadPlaceholder}>
                  <Text style={styles.uploadIcon}>📷</Text>
                  {uploadingImage ? (
                    <View style={styles.uploadingContainer}>
                      <ActivityIndicator size="small" color="#2196F3" />
                      <Text style={styles.uploadText}>Uploading...</Text>
                    </View>
                  ) : (
                    <>
                      <Text style={styles.uploadText}>Add Photo</Text>
                      <Text style={styles.uploadHint}>Required</Text>
                    </>
                  )}
                </View>
              )}
            </TouchableOpacity>
          </View>

          {/* Catch Details Section */}
          <View style={styles.detailsSection}>
            <Text style={styles.sectionTitle}>🐟 Catch Details</Text>
            
            <View style={styles.inputGroup}>
              <Text style={styles.label}>Species</Text>
              <View style={styles.inputContainer}>
                <TextInput
                  style={styles.input}
                  placeholder="e.g., Largemouth Bass, Rainbow Trout"
                  placeholderTextColor={RodRoyaleTheme.colors.textSecondary}
                  value={species}
                  onChangeText={setSpecies}
                />
              </View>
            </View>

            <View style={styles.inputGroup}>
              <Text style={styles.label}>Weight (lbs)</Text>
              <View style={styles.inputContainer}>
                <TextInput
                  style={styles.input}
                  placeholder="e.g., 3.5"
                  placeholderTextColor={RodRoyaleTheme.colors.textSecondary}
                  value={weight}
                  onChangeText={setWeight}
                  keyboardType="decimal-pad"
                />
              </View>
            </View>
          </View>

          {/* Location Section */}
          <View style={styles.locationSection}>
            <Text style={styles.sectionTitle}>📍 Location</Text>
            <View style={styles.locationCard}>
              <View style={styles.locationInfo}>
                <Text style={styles.locationText}>
                  {gettingLocation
                    ? '🌍 Getting location...'
                    : location
                    ? formatLocationDisplay(location)
                    : 'Location not available'}
                </Text>
              </View>
              <TouchableOpacity
                style={styles.locationButton}
                onPress={getCurrentLocation}
                disabled={gettingLocation}
                activeOpacity={0.7}
              >
                <Text style={styles.locationButtonText}>
                  {gettingLocation ? '⏳' : '🔄'}
                </Text>
              </TouchableOpacity>
            </View>
          </View>

          {/* Privacy Settings Section */}
          <View style={styles.privacySection}>
            <Text style={styles.sectionTitle}>🔒 Privacy Settings</Text>
            
            <View style={styles.settingCard}>
              <View style={styles.settingRow}>
                <View style={styles.settingInfo}>
                  <Text style={styles.settingLabel}>Share with followers</Text>
                  <Text style={styles.settingDescription}>Post to your feed</Text>
                </View>
                <Switch
                  value={sharedWithFollowers}
                  onValueChange={setSharedWithFollowers}
                  trackColor={{ false: '#e0e0e0', true: RodRoyaleTheme.colors.success }}
                  thumbColor={sharedWithFollowers ? '#fff' : '#f4f3f4'}
                />
              </View>
            </View>

            <View style={styles.settingCard}>
              <View style={styles.settingRow}>
                <View style={styles.settingInfo}>
                  <Text style={styles.settingLabel}>Add to map</Text>
                  <Text style={styles.settingDescription}>Show location on map</Text>
                </View>
                <Switch
                  value={addToMap}
                  onValueChange={setAddToMap}
                  trackColor={{ false: '#e0e0e0', true: RodRoyaleTheme.colors.success }}
                  thumbColor={addToMap ? '#fff' : '#f4f3f4'}
                />
              </View>

              {addToMap && (
                <View style={styles.visibilityOptions}>
                  <Text style={styles.visibilityLabel}>Map visibility</Text>
                  <View style={styles.visibilityButtons}>
                    {['private', 'mutuals', 'public'].map((visibility) => (
                      <TouchableOpacity
                        key={visibility}
                        style={[
                          styles.visibilityButton,
                          mapVisibility === visibility && styles.visibilityButtonActive
                        ]}
                        onPress={() => setMapVisibility(visibility as any)}
                        activeOpacity={0.7}
                      >
                        <Text style={[
                          styles.visibilityButtonText,
                          mapVisibility === visibility && styles.visibilityButtonTextActive
                        ]}>
                          {visibility.charAt(0).toUpperCase() + visibility.slice(1)}
                        </Text>
                      </TouchableOpacity>
                    ))}
                  </View>
                </View>
              )}
            </View>
          </View>

          {/* Submit Button */}
          <TouchableOpacity
            style={[styles.submitButton, isLoading && styles.submitButtonDisabled]}
            onPress={handleSubmit}
            disabled={isLoading}
            activeOpacity={0.8}
          >
            {isLoading ? (
              <View style={styles.submitLoadingContainer}>
                <ActivityIndicator size="small" color="white" />
                <Text style={styles.submitButtonText}>Saving Catch...</Text>
              </View>
            ) : (
              <Text style={styles.submitButtonText}>🎣 Save Catch</Text>
            )}
          </TouchableOpacity>
        </Animated.View>
      </ScrollView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8fafc',
  },
  scrollView: {
    flex: 1,
  },
  scrollContent: {
    paddingBottom: 40,
  },
  header: {
    backgroundColor: 'transparent',
    paddingHorizontal: 24,
    borderBottomLeftRadius: 24,
    borderBottomRightRadius: 24,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.1,
    shadowRadius: 12,
    elevation: 8,
  },
  headerContent: {
    alignItems: 'center',
  },
  title: {
    fontSize: 28,
    fontWeight: '700',
    color: RodRoyaleTheme.colors.primary,
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 16,
    color: RodRoyaleTheme.colors.textSecondary,
    fontWeight: '500',
  },
  successBanner: {
    backgroundColor: RodRoyaleTheme.colors.success,
    padding: 16,
    borderRadius: 16,
    marginTop: 20,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.2,
    shadowRadius: 8,
    elevation: 6,
  },
  successText: {
    color: 'white',
    fontWeight: '700',
    fontSize: 16,
    textAlign: 'center',
  },
  successSubtext: {
    color: 'white',
    fontSize: 12,
    textAlign: 'center',
    marginTop: 4,
    opacity: 0.9,
  },
  form: {
    padding: 24,
  },
  
  // Section Styles
  photoSection: {
    marginBottom: 32,
  },
  detailsSection: {
    marginBottom: 32,
  },
  locationSection: {
    marginBottom: 32,
  },
  privacySection: {
    marginBottom: 32,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: '700',
    color: RodRoyaleTheme.colors.primary,
    marginBottom: 16,
  },
  
  // Photo Upload Styles
  photoUploadArea: {
    borderRadius: 20,
    borderWidth: 3,
    borderStyle: 'dashed',
    borderColor: RodRoyaleTheme.colors.primary,
    backgroundColor: 'white',
    minHeight: 200,
    justifyContent: 'center',
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.05,
    shadowRadius: 8,
    elevation: 3,
  },
  photoUploadAreaWithImage: {
    borderStyle: 'solid',
    borderColor: RodRoyaleTheme.colors.success,
    backgroundColor: '#f0f9ff',
  },
  imageContainer: {
    width: '100%',
    height: 200,
    position: 'relative',
    borderRadius: 16,
    overflow: 'hidden',
  },
  uploadedImage: {
    width: '100%',
    height: '100%',
    borderRadius: 16,
  },
  imageOverlay: {
    position: 'absolute',
    bottom: 0,
    left: 0,
    right: 0,
    backgroundColor: 'rgba(0,0,0,0.7)',
    padding: 12,
    alignItems: 'center',
  },
  changePhotoText: {
    color: 'white',
    fontWeight: '600',
    fontSize: 14,
  },
  uploadPlaceholder: {
    alignItems: 'center',
    padding: 32,
  },
  uploadIcon: {
    fontSize: 48,
    marginBottom: 12,
  },
  uploadText: {
    fontSize: 18,
    fontWeight: '600',
    color: RodRoyaleTheme.colors.primary,
    marginBottom: 4,
  },
  uploadingContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  uploadHint: {
    fontSize: 12,
    color: RodRoyaleTheme.colors.textSecondary,
    fontWeight: '500',
  },
  
  // Input Styles
  inputGroup: {
    marginBottom: 20,
  },
  label: {
    fontSize: 16,
    fontWeight: '600',
    color: RodRoyaleTheme.colors.text,
    marginBottom: 8,
  },
  inputContainer: {
    backgroundColor: 'white',
    borderRadius: 16,
    borderWidth: 2,
    borderColor: '#e2e8f0',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.05,
    shadowRadius: 4,
    elevation: 2,
  },
  input: {
    paddingHorizontal: 20,
    paddingVertical: 16,
    fontSize: 16,
    color: RodRoyaleTheme.colors.text,
    borderRadius: 16,
  },
  
  // Location Styles
  locationCard: {
    backgroundColor: 'white',
    borderRadius: 16,
    padding: 20,
    flexDirection: 'row',
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.05,
    shadowRadius: 8,
    elevation: 3,
    borderWidth: 2,
    borderColor: '#e2e8f0',
  },
  locationInfo: {
    flex: 1,
    marginRight: 16,
  },
  locationText: {
    fontSize: 15,
    color: RodRoyaleTheme.colors.text,
    fontWeight: '500',
  },
  locationButton: {
    backgroundColor: RodRoyaleTheme.colors.primary,
    borderRadius: 12,
    width: 44,
    height: 44,
    justifyContent: 'center',
    alignItems: 'center',
    shadowColor: RodRoyaleTheme.colors.primary,
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 4,
  },
  locationButtonText: {
    fontSize: 18,
    color: 'white',
  },
  
  // Settings Styles
  settingCard: {
    backgroundColor: 'white',
    borderRadius: 16,
    padding: 20,
    marginBottom: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.05,
    shadowRadius: 8,
    elevation: 3,
    borderWidth: 2,
    borderColor: '#e2e8f0',
  },
  settingRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  settingInfo: {
    flex: 1,
    marginRight: 16,
  },
  settingLabel: {
    fontSize: 16,
    fontWeight: '600',
    color: RodRoyaleTheme.colors.text,
    marginBottom: 4,
  },
  settingDescription: {
    fontSize: 14,
    color: RodRoyaleTheme.colors.textSecondary,
  },
  
  // Visibility Options
  visibilityOptions: {
    marginTop: 20,
    paddingTop: 20,
    borderTopWidth: 1,
    borderTopColor: '#e2e8f0',
  },
  visibilityLabel: {
    fontSize: 14,
    fontWeight: '600',
    color: RodRoyaleTheme.colors.text,
    marginBottom: 12,
  },
  visibilityButtons: {
    flexDirection: 'row',
    gap: 8,
  },
  visibilityButton: {
    flex: 1,
    paddingVertical: 12,
    paddingHorizontal: 16,
    borderRadius: 12,
    borderWidth: 2,
    borderColor: '#e2e8f0',
    backgroundColor: 'white',
    alignItems: 'center',
  },
  visibilityButtonActive: {
    backgroundColor: RodRoyaleTheme.colors.primary,
    borderColor: RodRoyaleTheme.colors.primary,
  },
  visibilityButtonText: {
    fontSize: 13,
    fontWeight: '600',
    color: RodRoyaleTheme.colors.text,
  },
  visibilityButtonTextActive: {
    color: 'white',
  },
  
  // Submit Button
  submitButton: {
    backgroundColor: RodRoyaleTheme.colors.primary,
    borderRadius: 20,
    padding: 20,
    alignItems: 'center',
    marginTop: 16,
    shadowColor: RodRoyaleTheme.colors.primary,
    shadowOffset: { width: 0, height: 6 },
    shadowOpacity: 0.3,
    shadowRadius: 12,
    elevation: 8,
  },
  submitButtonDisabled: {
    opacity: 0.6,
    backgroundColor: RodRoyaleTheme.colors.textSecondary,
  },
  submitLoadingContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  submitButtonText: {
    fontSize: 18,
    fontWeight: '700',
    color: 'white',
    textTransform: 'uppercase',
    letterSpacing: 1,
  },
});

export default AddCatchScreen;