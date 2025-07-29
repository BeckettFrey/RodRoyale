import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  SafeAreaView,
  ScrollView,
  TextInput,
  TouchableOpacity,
  Image,
  Alert,
  ActivityIndicator,
  Switch,
} from 'react-native';
import { useNavigation, useRoute } from '@react-navigation/native';
import { NativeStackNavigationProp, NativeStackScreenProps } from '@react-navigation/native-stack';
import * as ImagePicker from 'expo-image-picker';
import { RootStackParamList } from '../navigation/AppNavigator';
import ApiService from '../services/api';
import RodRoyaleTheme from '../theme/RodRoyaleTheme';

type EditCatchScreenProps = NativeStackScreenProps<RootStackParamList, 'EditCatch'>;

const EditCatchScreen: React.FC = () => {
  const navigation = useNavigation<NativeStackNavigationProp<RootStackParamList>>();
  const route = useRoute<EditCatchScreenProps['route']>();
  const { catch: originalCatch } = route.params;

  // Form state
  const [species, setSpecies] = useState(originalCatch.species);
  const [weight, setWeight] = useState(originalCatch.weight.toString());
  const [sharedWithFollowers, setSharedWithFollowers] = useState(originalCatch.shared_with_followers);
  const [imageUri, setImageUri] = useState<string | null>(null);
  const [updating, setUpdating] = useState(false);

  const handleImagePicker = async () => {
    try {
      // Request permission
      const permissionResult = await ImagePicker.requestMediaLibraryPermissionsAsync();
      
      if (!permissionResult.granted) {
        Alert.alert('Permission Required', 'Please allow access to your photo library to select images.');
        return;
      }

      // Launch image picker
      const result = await ImagePicker.launchImageLibraryAsync({
        mediaTypes: ImagePicker.MediaTypeOptions.Images,
        allowsEditing: true,
        aspect: [4, 3],
        quality: 0.8,
      });

      if (!result.canceled && result.assets[0]) {
        setImageUri(result.assets[0].uri);
      }
    } catch (error) {
      console.error('Error picking image:', error);
      Alert.alert('Error', 'Failed to select image. Please try again.');
    }
  };

  const handleCamera = async () => {
    try {
      // Request permission
      const permissionResult = await ImagePicker.requestCameraPermissionsAsync();
      
      if (!permissionResult.granted) {
        Alert.alert('Permission Required', 'Please allow camera access to take photos.');
        return;
      }

      // Launch camera
      const result = await ImagePicker.launchCameraAsync({
        allowsEditing: true,
        aspect: [4, 3],
        quality: 0.8,
      });

      if (!result.canceled && result.assets[0]) {
        setImageUri(result.assets[0].uri);
      }
    } catch (error) {
      console.error('Error taking photo:', error);
      Alert.alert('Error', 'Failed to take photo. Please try again.');
    }
  };

  const showImagePicker = () => {
    Alert.alert(
      'Select Photo',
      'Choose how you want to update your catch photo',
      [
        { text: 'Camera', onPress: handleCamera },
        { text: 'Photo Library', onPress: handleImagePicker },
        { text: 'Cancel', style: 'cancel' },
      ]
    );
  };

  const handleUpdate = async () => {
    // Validation
    if (!species.trim()) {
      Alert.alert('Error', 'Please enter the fish species.');
      return;
    }

    const weightNum = parseFloat(weight);
    if (isNaN(weightNum) || weightNum <= 0) {
      Alert.alert('Error', 'Please enter a valid weight.');
      return;
    }

    setUpdating(true);

    try {
      if (imageUri) {
        // Update with new image
        await ApiService.updateCatchWithNewImage(
          originalCatch._id,
          imageUri,
          {
            species: species.trim(),
            weight: weightNum,
            shared_with_followers: sharedWithFollowers,
            location: originalCatch.location, // Keep original location
          }
        );
      } else {
        // Update without changing image
        await ApiService.updateMyCatch(originalCatch._id, {
          species: species.trim(),
          weight: weightNum,
          shared_with_followers: sharedWithFollowers,
        });
      }

      Alert.alert(
        'Success',
        'Catch updated successfully!',
        [
          {
            text: 'OK',
            onPress: () => navigation.goBack(),
          },
        ]
      );
    } catch (error: any) {
      console.error('Update error:', error);
      Alert.alert('Error', error.message || 'Failed to update catch. Please try again.');
    } finally {
      setUpdating(false);
    }
  };

  const currentImageUri = imageUri || originalCatch.photo_url;

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity
          style={styles.backButton}
          onPress={() => navigation.goBack()}
        >
          <Text style={styles.backButtonText}>← CANCEL</Text>
        </TouchableOpacity>
        <Text style={styles.title}>⚔️ EDIT BATTLE</Text>
      </View>

      <ScrollView style={styles.scrollView} showsVerticalScrollIndicator={false}>
        <View style={styles.content}>
          {/* Image Section */}
          <View style={styles.imageSection}>
            <Text style={styles.sectionTitle}>📸 BATTLE PHOTO</Text>
            <TouchableOpacity style={styles.imageContainer} onPress={showImagePicker}>
              {currentImageUri ? (
                <>
                  <Image source={{ uri: currentImageUri }} style={styles.image} />
                  <View style={styles.imageOverlay}>
                    <Text style={styles.changeImageText}>
                      {imageUri ? '✓ NEW PHOTO' : 'TAP TO CHANGE'}
                    </Text>
                  </View>
                </>
              ) : (
                <View style={styles.placeholderImage}>
                  <Text style={styles.placeholderText}>📷</Text>
                  <Text style={styles.placeholderText}>TAP TO ADD PHOTO</Text>
                </View>
              )}
            </TouchableOpacity>
          </View>

          {/* Species Input */}
          <View style={styles.inputSection}>
            <Text style={styles.sectionTitle}>🎯 TARGET SPECIES</Text>
            <TextInput
              style={styles.input}
              value={species}
              onChangeText={setSpecies}
              placeholder="Enter fish species..."
              placeholderTextColor={RodRoyaleTheme.colors.textSecondary}
            />
          </View>

          {/* Weight Input */}
          <View style={styles.inputSection}>
            <Text style={styles.sectionTitle}>⚖️ BATTLE WEIGHT</Text>
            <TextInput
              style={styles.input}
              value={weight}
              onChangeText={setWeight}
              placeholder="Enter weight in lbs..."
              placeholderTextColor={RodRoyaleTheme.colors.textSecondary}
              keyboardType="decimal-pad"
            />
          </View>

          {/* Sharing Toggle */}
          <View style={styles.inputSection}>
            <Text style={styles.sectionTitle}>👥 SHARE VICTORY</Text>
            <View style={styles.switchContainer}>
              <Text style={styles.switchLabel}>
                {sharedWithFollowers ? '🏆 PUBLIC VICTORY' : '🔒 PRIVATE BATTLE'}
              </Text>
              <Switch
                value={sharedWithFollowers}
                onValueChange={setSharedWithFollowers}
                trackColor={{ 
                  false: RodRoyaleTheme.colors.surface, 
                  true: RodRoyaleTheme.colors.secondary 
                }}
                thumbColor={sharedWithFollowers ? RodRoyaleTheme.colors.primary : RodRoyaleTheme.colors.textSecondary}
              />
            </View>
          </View>

          {/* Update Button */}
          <TouchableOpacity 
            style={[styles.updateButton, updating && styles.disabledButton]}
            onPress={handleUpdate}
            disabled={updating}
          >
            {updating ? (
              <ActivityIndicator color="white" />
            ) : (
              <Text style={styles.updateButtonText}>⚔️ UPDATE</Text>
            )}
          </TouchableOpacity>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: RodRoyaleTheme.colors.background,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 20,
    paddingBottom: 10,
    backgroundColor: RodRoyaleTheme.colors.surface,
    borderBottomWidth: 2,
    borderBottomColor: RodRoyaleTheme.colors.primary,
    ...RodRoyaleTheme.shadows.medium,
  },
  backButton: {
    marginRight: 15,
  },
  backButtonText: {
    fontSize: 16,
    color: RodRoyaleTheme.colors.primary,
    fontWeight: 'bold',
  },
  title: {
    fontSize: 20,
    fontWeight: 'bold',
    color: RodRoyaleTheme.colors.text,
    textShadowColor: 'rgba(0,0,0,0.1)',
    textShadowOffset: { width: 1, height: 1 },
    textShadowRadius: 2,
  },
  scrollView: {
    flex: 1,
  },
  content: {
    padding: 20,
  },
  imageSection: {
    marginBottom: 25,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: RodRoyaleTheme.colors.text,
    marginBottom: 12,
    textTransform: 'uppercase',
    textShadowColor: 'rgba(0,0,0,0.1)',
    textShadowOffset: { width: 1, height: 1 },
    textShadowRadius: 1,
  },
  imageContainer: {
    position: 'relative',
    borderRadius: 12,
    overflow: 'hidden',
    ...RodRoyaleTheme.shadows.medium,
  },
  image: {
    width: '100%',
    height: 200,
    backgroundColor: RodRoyaleTheme.colors.surface,
  },
  imageOverlay: {
    position: 'absolute',
    bottom: 0,
    left: 0,
    right: 0,
    backgroundColor: 'rgba(0,0,0,0.7)',
    padding: 10,
    alignItems: 'center',
  },
  changeImageText: {
    color: 'white',
    fontWeight: 'bold',
    fontSize: 14,
  },
  placeholderImage: {
    width: '100%',
    height: 200,
    backgroundColor: RodRoyaleTheme.colors.surface,
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 2,
    borderColor: RodRoyaleTheme.colors.primary,
    borderStyle: 'dashed',
  },
  placeholderText: {
    color: RodRoyaleTheme.colors.textSecondary,
    fontSize: 18,
    fontWeight: 'bold',
    textAlign: 'center',
  },
  inputSection: {
    marginBottom: 25,
  },
  input: {
    backgroundColor: RodRoyaleTheme.colors.surface,
    borderWidth: 2,
    borderColor: RodRoyaleTheme.colors.primary,
    borderRadius: 8,
    padding: 15,
    fontSize: 16,
    color: RodRoyaleTheme.colors.text,
    fontWeight: '600',
    ...RodRoyaleTheme.shadows.medium,
  },
  switchContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    backgroundColor: RodRoyaleTheme.colors.surface,
    padding: 15,
    borderRadius: 8,
    borderWidth: 2,
    borderColor: RodRoyaleTheme.colors.primary,
    ...RodRoyaleTheme.shadows.medium,
  },
  switchLabel: {
    fontSize: 16,
    fontWeight: 'bold',
    color: RodRoyaleTheme.colors.text,
    textTransform: 'uppercase',
  },
  updateButton: {
    backgroundColor: RodRoyaleTheme.colors.secondary,
    paddingVertical: 18,
    paddingHorizontal: 30,
    borderRadius: 12,
    alignItems: 'center',
    marginTop: 20,
    borderWidth: 3,
    borderColor: RodRoyaleTheme.colors.primary,
    ...RodRoyaleTheme.shadows.large,
  },
  disabledButton: {
    opacity: 0.6,
  },
  updateButtonText: {
    color: 'white',
    fontSize: 18,
    fontWeight: 'bold',
    textTransform: 'uppercase',
    textShadowColor: 'rgba(0,0,0,0.3)',
    textShadowOffset: { width: 1, height: 1 },
    textShadowRadius: 2,
  },
});

export default EditCatchScreen;
