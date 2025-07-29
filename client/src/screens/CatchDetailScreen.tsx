import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  SafeAreaView,
  ScrollView,
  Image,
  TouchableOpacity,
  Alert,
  ActivityIndicator,
} from 'react-native';
import { useNavigation, useRoute } from '@react-navigation/native';
import { NativeStackNavigationProp, NativeStackScreenProps } from '@react-navigation/native-stack';
import { RootStackParamList } from '../navigation/AppNavigator';
import { useAuth } from '../contexts/AuthContext';
import ApiService from '../services/api';
import { formatLocationDisplay } from '../utils/geocoding';

type CatchDetailScreenProps = NativeStackScreenProps<RootStackParamList, 'CatchDetail'>;

const CatchDetailScreen: React.FC = () => {
  const navigation = useNavigation<NativeStackNavigationProp<RootStackParamList>>();
  const route = useRoute<CatchDetailScreenProps['route']>();
  const { catch: catchData } = route.params;
  const { user } = useAuth();
  const [deleting, setDeleting] = useState(false);
  
  const isOwnCatch = user && catchData.user_id === user._id;

  const handleEdit = () => {
    navigation.navigate('EditCatch', { catch: catchData });
  };

  const handleDelete = async () => {
    console.log('🚨 [DELETE BUTTON] Delete button pressed!');
    console.log('🚨 [DELETE BUTTON] Catch ID:', catchData?._id);
    console.log('🚨 [DELETE BUTTON] Is own catch:', isOwnCatch);
    console.log('🚨 [DELETE BUTTON] User context:', user);
    
    if (!catchData) {
      console.error('❌ [DELETE BUTTON] No catch data available');
      Alert.alert('Error', 'No catch data available');
      return;
    }

    try {
      console.log('🔥 [DELETE BUTTON] Starting delete confirmation...');
      
      // For debugging: Skip confirmation and delete directly
      if (true) { // Temporarily enable for debugging
        console.log('⚡ [DELETE BUTTON] BYPASSING CONFIRMATION FOR DEBUGGING');
        console.log('✅ [DELETE BUTTON] Proceeding with deletion directly...');
        setDeleting(true);
        
        try {
          console.log('🗑️ [DELETE BUTTON] Calling API delete method...');
          await ApiService.deleteMyCatch(catchData._id);
          console.log('✅ [DELETE BUTTON] API delete successful, navigating back...');
          
          // Immediate UI feedback
          console.log('🎉 [DELETE BUTTON] Showing success message and navigating...');
          
          // Navigate back immediately with success feedback
          navigation.goBack();
          
          // Show success message after navigation
          setTimeout(() => {
            Alert.alert('Success', 'Battle deleted successfully! 🎣', [
              { text: 'OK' }
            ]);
          }, 100);
          
        } catch (error: any) {
          console.error('❌ [DELETE BUTTON] Delete failed:', error);
          setDeleting(false);
          Alert.alert(
            'Error',
            `Failed to delete battle: ${error.message}`,
            [{ text: 'OK' }]
          );
        }
        return;
      }
    } catch (error: any) {
      console.error('❌ [DELETE BUTTON] Unexpected error in handleDelete:', error);
      Alert.alert('Error', `Unexpected error: ${error.message}`);
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity
          style={styles.backButton}
          onPress={() => navigation.goBack()}
        >
          <Text style={styles.backButtonText}>← Back</Text>
        </TouchableOpacity>
        <Text style={styles.title}>Catch Details</Text>
      </View>

      <ScrollView style={styles.scrollView} showsVerticalScrollIndicator={false}>
        <View style={styles.content}>
          {catchData.photo_url && (
            <Image source={{ uri: catchData.photo_url }} style={styles.image} />
          )}

          <View style={styles.infoCard}>
            <Text style={styles.species}>{catchData.species}</Text>
            <Text style={styles.weight}>{catchData.weight} lbs</Text>
          </View>

          <View style={styles.detailsCard}>
            <View style={styles.detailRow}>
              <Text style={styles.detailLabel}>📍 Location:</Text>
              <Text style={styles.detailValue}>
                {formatLocationDisplay(catchData.location)}
              </Text>
            </View>

            <View style={styles.detailRow}>
              <Text style={styles.detailLabel}>📅 Date:</Text>
              <Text style={styles.detailValue}>
                {new Date(catchData.created_at).toLocaleDateString('en-US', {
                  weekday: 'long',
                  year: 'numeric',
                  month: 'long',
                  day: 'numeric',
                })}
              </Text>
            </View>

            <View style={styles.detailRow}>
              <Text style={styles.detailLabel}>🕐 Time:</Text>
              <Text style={styles.detailValue}>
                {new Date(catchData.created_at).toLocaleTimeString('en-US', {
                  hour: '2-digit',
                  minute: '2-digit',
                })}
              </Text>
            </View>

            <View style={styles.detailRow}>
              <Text style={styles.detailLabel}>👥 Sharing:</Text>
              <Text style={styles.detailValue}>
                {catchData.shared_with_followers ? 'Shared with followers' : 'Private catch'}
              </Text>
            </View>
          </View>

          <View style={styles.statsCard}>
            <Text style={styles.statsTitle}>🎣 Catch Stats</Text>
            <View style={styles.statsGrid}>
              <View style={styles.statItem}>
                <Text style={styles.statLabel}>Species</Text>
                <Text style={styles.statValue}>{catchData.species}</Text>
              </View>
              <View style={styles.statItem}>
                <Text style={styles.statLabel}>Weight</Text>
                <Text style={styles.statValue}>{catchData.weight} lbs</Text>
              </View>
              <View style={styles.statItem}>
                <Text style={styles.statLabel}>Location</Text>
                <Text style={styles.statValue}>
                  {formatLocationDisplay(catchData.location)}
                </Text>
              </View>
            </View>
          </View>
        </View>

        {/* Edit/Delete Buttons for own catches */}
        {isOwnCatch && (
          <View style={styles.actionSection}>
            <Text style={styles.actionTitle}></Text>
            <View style={styles.actionButtons}>
              <TouchableOpacity 
                style={styles.editButton} 
                onPress={handleEdit}
                disabled={deleting}
              >
                <Text style={styles.editButtonText}>✏️ EDIT</Text>
              </TouchableOpacity>
              
              <TouchableOpacity 
                style={[styles.deleteButton, deleting && styles.disabledButton]} 
                onPress={handleDelete}
                disabled={deleting}
              >
                {deleting ? (
                  <ActivityIndicator color="white" size="small" />
                ) : (
                  <Text style={styles.deleteButtonText}>🗑️ DELETE</Text>
                )}
              </TouchableOpacity>
            </View>
          </View>
        )}
      </ScrollView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f0f8ff',
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 20,
    paddingBottom: 10,
    backgroundColor: 'white',
    borderBottomWidth: 1,
    borderBottomColor: '#eee',
  },
  backButton: {
    marginRight: 15,
  },
  backButtonText: {
    fontSize: 18,
    color: '#2196F3',
    fontWeight: '600',
  },
  title: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#333',
  },
  scrollView: {
    flex: 1,
  },
  content: {
    padding: 20,
  },
  image: {
    width: '100%',
    height: 250,
    borderRadius: 12,
    marginBottom: 20,
    backgroundColor: '#f0f0f0',
  },
  infoCard: {
    backgroundColor: 'white',
    padding: 20,
    borderRadius: 12,
    marginBottom: 20,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  species: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 8,
    textAlign: 'center',
  },
  weight: {
    fontSize: 24,
    fontWeight: '600',
    color: '#2196F3',
  },
  detailsCard: {
    backgroundColor: 'white',
    padding: 20,
    borderRadius: 12,
    marginBottom: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  detailRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0',
  },
  detailLabel: {
    fontSize: 16,
    color: '#666',
    flex: 1,
  },
  detailValue: {
    fontSize: 16,
    color: '#333',
    fontWeight: '500',
    flex: 2,
    textAlign: 'right',
  },
  statsCard: {
    backgroundColor: 'white',
    padding: 20,
    borderRadius: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  statsTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 15,
    textAlign: 'center',
  },
  statsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  statItem: {
    width: '48%',
    backgroundColor: '#f8f9fa',
    padding: 15,
    borderRadius: 8,
    marginBottom: 10,
    alignItems: 'center',
  },
  statLabel: {
    fontSize: 14,
    color: '#666',
    marginBottom: 5,
  },
  statValue: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#2196F3',
    textAlign: 'center',
  },
  actionSection: {
    backgroundColor: 'white',
    margin: 20,
    padding: 20,
    borderRadius: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  actionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    textAlign: 'center',
    marginBottom: 15,
    textTransform: 'uppercase',
  },
  actionButtons: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    gap: 10,
  },
  editButton: {
    flex: 1,
    backgroundColor: '#2196F3',
    paddingVertical: 12,
    paddingHorizontal: 20,
    borderRadius: 8,
    alignItems: 'center',
  },
  editButtonText: {
    color: 'white',
    fontSize: 14,
    fontWeight: 'bold',
    textTransform: 'uppercase',
  },
  deleteButton: {
    flex: 1,
    backgroundColor: '#f44336',
    paddingVertical: 12,
    paddingHorizontal: 20,
    borderRadius: 8,
    alignItems: 'center',
  },
  deleteButtonText: {
    color: 'white',
    fontSize: 14,
    fontWeight: 'bold',
    textTransform: 'uppercase',
  },
  disabledButton: {
    opacity: 0.6,
  },
});

export default CatchDetailScreen;
