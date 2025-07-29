import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  SafeAreaView,
  ScrollView,
  TouchableOpacity,
  Alert,
  TextInput,
  Modal,
  Dimensions,
} from 'react-native';
import { Image } from 'react-native';
import { useAuth } from '../contexts/AuthContext';
import ApiService from '../services/api';
import { Catch, UpdateUserRequest } from '../types/api';
import RodRoyaleTheme from '../theme/RodRoyaleTheme';

const { width } = Dimensions.get('window');

const ProfileScreen: React.FC = () => {
  const [catches, setCatches] = useState<Catch[]>([]);
  const [loading, setLoading] = useState(true);
  const [showEditModal, setShowEditModal] = useState(false);
  const [editUsername, setEditUsername] = useState('');
  const [editBio, setEditBio] = useState('');
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPasswordSection, setShowPasswordSection] = useState(false);
  const [deletingAccount, setDeletingAccount] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [deleteConfirmText, setDeleteConfirmText] = useState('');
  const { user, logout, updateUser } = useAuth();

  // Helper functions to safely get followers/following counts
  const getFollowersCount = () => {
    return Array.isArray(user?.followers) ? user.followers.length : 0;
  };

  const getFollowingCount = () => {
    return Array.isArray(user?.following) ? user.following.length : 0;
  };

  const loadUserCatches = async () => {
    if (!user) return;

    try {
      const userCatches = await ApiService.getMyCatches();
      setCatches(userCatches);
      console.log('Catches loaded successfully:', catches.length);
    } catch (error: any) {
      console.error('Error loading catches:', error);
      // Don't show network errors for catches loading since profile can still function
      // without catches data
      if (error.code !== 'ERR_NETWORK' && error.message !== 'Network Error') {
        console.error('Non-network error loading catches:', error);
      }
    } finally {
      setLoading(false);
    }
  };

  // Remove automatic refresh on focus to prevent infinite loop
  // The social stats will update when user data changes from other actions (follow/unfollow)
  // useFocusEffect is not needed here since the user state is managed globally

  useEffect(() => {
    loadUserCatches();
    if (user) {
      setEditUsername(user.username);
      setEditBio(user.bio || '');
    }
    // Reset password fields when modal is closed
    if (!showEditModal) {
      setCurrentPassword('');
      setNewPassword('');
      setConfirmPassword('');
      setShowPasswordSection(false);
    }
  }, [user, showEditModal]);

  // Log user data changes for debugging (reduced logging)
  useEffect(() => {
    if (user) {
      console.log('ProfileScreen: User data updated:', {
        username: user.username,
        followersCount: getFollowersCount(),
        followingCount: getFollowingCount(),
        userObjectId: user._id
      });
    }
  }, [user]); // Removed lastRefresh as dependency to prevent infinite loop

  const handleLogout = async () => {
    console.log('Logout button pressed - proceeding directly');
    try {
      await logout();
      console.log('Logout successful - user should be redirected to login');
    } catch (error) {
      console.error('Logout error:', error);
      Alert.alert('Logout Error', 'Failed to logout. Please try again.');
    }
  };

  const handleSaveProfile = async () => {
    if (!user) return;

    // Basic validation
    if (!editUsername.trim()) {
      Alert.alert('Validation Error', 'Username cannot be empty.');
      return;
    }

    // Password validation if user wants to change password
    if (showPasswordSection) {
      if (!currentPassword) {
        Alert.alert('Validation Error', 'Current password is required to change password.');
        return;
      }
      if (!newPassword) {
        Alert.alert('Validation Error', 'New password is required.');
        return;
      }
      if (newPassword.length < 6) {
        Alert.alert('Validation Error', 'New password must be at least 6 characters long.');
        return;
      }
      if (newPassword !== confirmPassword) {
        Alert.alert('Validation Error', 'New password and confirmation do not match.');
        return;
      }
      if (currentPassword === newPassword) {
        Alert.alert('Validation Error', 'New password must be different from current password.');
        return;
      }
    }

    try {
      console.log('🔄 Saving profile changes:', {
        userId: user._id,
        username: editUsername,
        bio: editBio,
        changingPassword: showPasswordSection
      });

      // Update profile information
      const updateData: UpdateUserRequest = {
        username: editUsername.trim(),
        bio: editBio.trim()
      };

      const updatedUser = await ApiService.updateUser(user._id, updateData);
      
      console.log('✅ Profile updated successfully:', updatedUser);
      
      await updateUser(updatedUser);

      // Change password if requested
      if (showPasswordSection) {
        try {
          await ApiService.changePassword(currentPassword, newPassword);
          console.log('✅ Password changed successfully');
          
          // Clear password fields
          setCurrentPassword('');
          setNewPassword('');
          setConfirmPassword('');
          setShowPasswordSection(false);
          
          setShowEditModal(false);
          
          // Log out user immediately after password change
          await logout();
          
          Alert.alert(
            'Success', 
            'Profile and password updated successfully! You have been logged out. Please log in again with your new password.'
          );
          return;
        } catch (passwordError: any) {
          console.error('❌ Error changing password:', passwordError);
          let passwordErrorMessage = 'Unable to change password. Please try again.';
          
          // Handle network errors specifically for password change
          if (passwordError.code === 'ERR_NETWORK' || passwordError.message === 'Network Error') {
            passwordErrorMessage = 'Network connection failed. Please check your internet connection and ensure the server is running.';
          } else if (passwordError.response?.status === 400) {
            passwordErrorMessage = passwordError.response.data?.detail || 'Current password is incorrect.';
          } else if (passwordError.response?.status >= 500) {
            passwordErrorMessage = 'Server error occurred. Please try again later.';
          } else if (passwordError.message) {
            passwordErrorMessage = passwordError.message;
          }
          
          Alert.alert('Password Change Failed', passwordErrorMessage);
          return;
        }
      }

      setShowEditModal(false);
      Alert.alert('Success', 'Profile updated successfully!');
    } catch (error: any) {
      console.error('❌ Error updating profile:', error);
      
      let errorMessage = 'Unable to update profile. Please try again.';
      
      // Handle network errors specifically
      if (error.code === 'ERR_NETWORK' || error.message === 'Network Error') {
        errorMessage = 'Network connection failed. Please check your internet connection and ensure the server is running.';
      } else if (error.response?.status === 403) {
        errorMessage = 'Permission denied. Please log in again.';
      } else if (error.response?.status === 422) {
        errorMessage = 'Invalid data provided. Please check your input.';
      } else if (error.response?.status >= 500) {
        errorMessage = 'Server error occurred. Please try again later.';
      } else if (error.message) {
        errorMessage = error.message;
      }
      
      Alert.alert('Update Failed', errorMessage);
    }
  };

  const handleDeleteAccount = async () => {
    if (!user) return;
    setShowDeleteModal(true);
  };

  const confirmDeleteAccount = async () => {
    if (!user) return;

    // Check if user typed their username correctly
    if (deleteConfirmText.trim() !== user.username) {
      Alert.alert(
        'Confirmation Failed',
        `Please type "${user.username}" exactly to confirm account deletion.`
      );
      return;
    }

    setDeletingAccount(true);
    try {
      console.log('🗑️ Starting account deletion for user:', user.username);
      
      await ApiService.deleteMyAccount();
      
      console.log('✅ Account deleted successfully');
      
      // Close the modal first
      setShowDeleteModal(false);
      setDeleteConfirmText('');
      
      // The API service will clear the token, but we should also clear local state
      await logout();
      
      Alert.alert(
        '✅ Account Deleted',
        'Your account has been permanently deleted. Thank you for using our app.',
        [{ text: 'OK' }]
      );
      
    } catch (error: any) {
      console.error('❌ Error deleting account:', error);
      
      let errorMessage = 'Unable to delete account. Please try again.';
      
      // Handle network errors specifically
      if (error.code === 'ERR_NETWORK' || error.message === 'Network Error') {
        errorMessage = 'Network connection failed. Please check your internet connection and ensure the server is running.';
      } else if (error.response?.status === 403) {
        errorMessage = 'Permission denied. Please log in again.';
      } else if (error.response?.status === 404) {
        errorMessage = 'Account not found. It may have already been deleted.';
      } else if (error.response?.status >= 500) {
        errorMessage = 'Server error occurred. Please try again later.';
      } else if (error.message) {
        errorMessage = error.message;
      }
      
      Alert.alert('Deletion Failed', errorMessage);
    } finally {
      setDeletingAccount(false);
    }
  };

  if (loading) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.centered}>
          <View style={styles.loadingSpinner} />
          <Text style={styles.loadingText}>Loading profile...</Text>
        </View>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView style={styles.scrollView} showsVerticalScrollIndicator={false}>
        {/* Header */}
      <View style={styles.header}>
                <Image 
                  source={require('../../assets/images/rod_royale_title_logo.png')} 
                  style={styles.logo}
                  resizeMode="contain"
                />
                <Text style={styles.subtitle}>ACCOUNT INFO</Text>
                <Text style={styles.description}>Manage your profile here.</Text>
              </View>

        {/* Profile Section */}
        <View style={styles.profileSection}>
          <View style={styles.avatarContainer}>
            <View style={styles.avatar}>
              <Text style={styles.avatarText}>
                {user?.username?.charAt(0).toUpperCase() || 'U'}
              </Text>
            </View>
          </View>
          
          <Text style={styles.username}>{user?.username}</Text>
          <Text style={styles.email}>{user?.email}</Text>
          {user?.bio && (
            <View style={styles.bioContainer}>
              <Text style={styles.bio}>{user.bio}</Text>
            </View>
          )}
        </View>

        {/* Social Stats Section */}
        <View style={styles.socialStatsSection}>
          <View style={styles.socialStatsHeaderContainer}>
            <Text style={styles.socialStatsHeader}>
              🌐 Social Network
            </Text>
          </View>
          <View style={styles.socialStatsContainer}>
            <TouchableOpacity 
              style={styles.socialStatItem}
              activeOpacity={0.7}
              onPress={() => {
                Alert.alert('Followers', `You have ${getFollowersCount()} followers`);
              }}
            >
              <Text style={styles.socialStatNumber}>
                {getFollowersCount()}
              </Text>
              <Text style={styles.socialStatLabel}>Followers</Text>
            </TouchableOpacity>
            
            <View style={styles.socialStatDivider} />
            
            <TouchableOpacity 
              style={styles.socialStatItem}
              activeOpacity={0.7}
              onPress={() => {
                Alert.alert('Following', `You are following ${getFollowingCount()} users`);
              }}
            >
              <Text style={styles.socialStatNumber}>
                {getFollowingCount()}
              </Text>
              <Text style={styles.socialStatLabel}>Following</Text>
            </TouchableOpacity>
          </View>
        </View>
        {/* Edit Profile Button */}
        <TouchableOpacity
          style={styles.editButton}
          onPress={() => setShowEditModal(true)}
        >
          <Text style={styles.editButtonText}>✏️ Edit Profile</Text>
        </TouchableOpacity>

        {/* Logout Button */}
        <TouchableOpacity style={styles.logoutButton} onPress={handleLogout}>
          <Text style={styles.logoutButtonText}>Sign Out</Text>
        </TouchableOpacity>

        {/* Delete Account Button */}
        <TouchableOpacity 
          style={[styles.deleteButton, deletingAccount && styles.deleteButtonDisabled]} 
          onPress={handleDeleteAccount}
          disabled={deletingAccount}
        >
          <Text style={styles.deleteButtonText}>
            {deletingAccount ? '🗑️ Deleting Account...' : '🗑️ Delete Account'}
          </Text>
        </TouchableOpacity>
      </ScrollView>

      {/* Edit Modal */}
      <Modal
        visible={showEditModal}
        animationType="slide"
        presentationStyle="pageSheet"
      >
        <SafeAreaView style={styles.modalContainer}>
          <View style={styles.modalHeader}>
            <TouchableOpacity 
              style={styles.modalButton}
              onPress={() => setShowEditModal(false)}
            >
              <Text style={styles.modalCancel}>Cancel</Text>
            </TouchableOpacity>
            <Text style={styles.modalTitle}>Edit Profile</Text>
            <TouchableOpacity 
              style={styles.modalButton}
              onPress={handleSaveProfile}
            >
              <Text style={styles.modalSave}>Save</Text>
            </TouchableOpacity>
          </View>

          <ScrollView style={styles.modalContent}>
            <View style={styles.inputGroup}>
              <Text style={styles.inputLabel}>Username</Text>
              <View style={styles.inputContainer}>
                <TextInput
                  style={styles.input}
                  value={editUsername}
                  onChangeText={setEditUsername}
                  placeholder="Enter username"
                  placeholderTextColor="#9CA3AF"
                />
              </View>
            </View>

            <View style={styles.inputGroup}>
              <Text style={styles.inputLabel}>Bio</Text>
              <View style={[styles.inputContainer, styles.bioInputContainer]}>
                <TextInput
                  style={[styles.input, styles.bioInput]}
                  value={editBio}
                  onChangeText={setEditBio}
                  placeholder="Tell us about your fishing passion..."
                  placeholderTextColor="#9CA3AF"
                  multiline
                  numberOfLines={4}
                  textAlignVertical="top"
                />
              </View>
            </View>

            {/* Password Change Section */}
            <View style={styles.passwordSection}>
              <TouchableOpacity
                style={styles.passwordToggle}
                onPress={() => setShowPasswordSection(!showPasswordSection)}
              >
                <Text style={styles.passwordToggleText}>
                  🔐 Change Password {showPasswordSection ? '▼' : '▶'}
                </Text>
              </TouchableOpacity>

              {showPasswordSection && (
                <View style={styles.passwordFields}>
                  <View style={styles.inputGroup}>
                    <Text style={styles.inputLabel}>Current Password</Text>
                    <View style={styles.inputContainer}>
                      <TextInput
                        style={styles.input}
                        value={currentPassword}
                        onChangeText={setCurrentPassword}
                        placeholder="Enter current password"
                        placeholderTextColor="#9CA3AF"
                        secureTextEntry
                        autoCapitalize="none"
                        autoCorrect={false}
                      />
                    </View>
                  </View>

                  <View style={styles.inputGroup}>
                    <Text style={styles.inputLabel}>New Password</Text>
                    <View style={styles.inputContainer}>
                      <TextInput
                        style={styles.input}
                        value={newPassword}
                        onChangeText={setNewPassword}
                        placeholder="Enter new password (min 6 characters)"
                        placeholderTextColor="#9CA3AF"
                        secureTextEntry
                        autoCapitalize="none"
                        autoCorrect={false}
                      />
                    </View>
                  </View>

                  <View style={styles.inputGroup}>
                    <Text style={styles.inputLabel}>Confirm New Password</Text>
                    <View style={styles.inputContainer}>
                      <TextInput
                        style={styles.input}
                        value={confirmPassword}
                        onChangeText={setConfirmPassword}
                        placeholder="Confirm new password"
                        placeholderTextColor="#9CA3AF"
                        secureTextEntry
                        autoCapitalize="none"
                        autoCorrect={false}
                      />
                    </View>
                  </View>

                  <Text style={styles.passwordNote}>
                    💡 Changing your password will log you out and require you to log in again with the new password.
                  </Text>
                </View>
              )}
            </View>
          </ScrollView>
        </SafeAreaView>
      </Modal>

      {/* Delete Account Confirmation Modal */}
      <Modal
        visible={showDeleteModal}
        animationType="slide"
        presentationStyle="pageSheet"
      >
        <SafeAreaView style={styles.modalContainer}>
          <View style={styles.modalHeader}>
            <TouchableOpacity 
              style={styles.modalButton}
              onPress={() => {
                setShowDeleteModal(false);
                setDeleteConfirmText('');
              }}
            >
              <Text style={styles.modalCancel}>Cancel</Text>
            </TouchableOpacity>
            <Text style={styles.deleteModalTitle}>Delete Account</Text>
            <TouchableOpacity 
              style={[styles.modalButton, deletingAccount && { opacity: 0.5 }]}
              onPress={confirmDeleteAccount}
              disabled={deletingAccount}
            >
              <Text style={styles.deleteModalConfirm}>
                {deletingAccount ? 'Deleting...' : 'Delete'}
              </Text>
            </TouchableOpacity>
          </View>

          <ScrollView style={styles.modalContent}>
            <View style={styles.deleteWarningContainer}>
              <Text style={styles.deleteWarningEmoji}>⚠️</Text>
              
              <Text style={styles.deleteWarningTitle}>
                This action cannot be undone
              </Text>
              
              <Text style={styles.deleteWarningText}>
                Deleting your account will permanently remove:
              </Text>
              
              <View style={styles.deleteWarningList}>
                <Text style={styles.deleteWarningItem}>• All your catches and posts</Text>
                <Text style={styles.deleteWarningItem}>• Your followers and following lists</Text>
                <Text style={styles.deleteWarningItem}>• All your profile data and settings</Text>
                <Text style={styles.deleteWarningItem}>• Your account history and statistics</Text>
              </View>
              
              <Text style={styles.deleteConfirmationPrompt}>
                Type "<Text style={styles.usernameHighlight}>{user?.username}</Text>" below to confirm:
              </Text>
              
              <View style={styles.inputContainer}>
                <TextInput
                  style={[styles.input, styles.deleteConfirmInput]}
                  value={deleteConfirmText}
                  onChangeText={setDeleteConfirmText}
                  placeholder={`Type ${user?.username} here`}
                  placeholderTextColor="#9CA3AF"
                  autoCapitalize="none"
                  autoCorrect={false}
                />
              </View>
            </View>
          </ScrollView>
        </SafeAreaView>
      </Modal>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
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
      fontSize: 14,
      color: RodRoyaleTheme.colors.textSecondary,
      textAlign: 'center',
      marginBottom: RodRoyaleTheme.spacing.sm,
    },
  container: {
    flex: 1,
    backgroundColor: RodRoyaleTheme.colors.background, // Sky blue
  },
  scrollView: {
    flex: 1,
  },
  centered: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingSpinner: {
    width: 40,
    height: 40,
    borderRadius: 20,
    borderWidth: 3,
    borderColor: '#E5E7EB',
    borderTopColor: '#3B82F6',
    marginBottom: 16,
  },
  loadingText: {
    fontSize: 16,
    color: '#6B7280',
    fontWeight: '500',
  },
  header: {
    padding: RodRoyaleTheme.spacing.lg,
    backgroundColor: RodRoyaleTheme.colors.surface,
    borderBottomWidth: 3,
    borderBottomColor: RodRoyaleTheme.colors.primary,
    alignItems: 'center',
    ...RodRoyaleTheme.shadows.medium,
  },
  headerContent: {
    alignItems: 'center',
  },
  editButton: {
    backgroundColor: RodRoyaleTheme.colors.secondary,
    paddingHorizontal: RodRoyaleTheme.spacing.lg,
    paddingVertical: RodRoyaleTheme.spacing.md,
    borderRadius: 20,
    marginHorizontal: RodRoyaleTheme.spacing.lg,
    marginBottom: 16,
    alignItems: 'center',
    shadowColor: RodRoyaleTheme.colors.secondary,
    shadowOffset: {
      width: 0,
      height: 3,
    },
    shadowOpacity: 0.25,
    shadowRadius: 6,
    elevation: 4,
  },
  editButtonText: {
    color: '#FFFFFF',
    fontSize: 14,
    fontWeight: '600',
  },
  profileSection: {
    alignItems: 'center',
    paddingTop: 40,
    paddingBottom: 32,
    paddingHorizontal: 24,
  },
  avatarContainer: {
    marginBottom: 20,
  },
  avatar: {
    width: 80,
    height: 80,
    borderRadius: 40,
    backgroundColor: '#3B82F6',
    justifyContent: 'center',
    alignItems: 'center',
    shadowColor: '#3B82F6',
    shadowOffset: {
      width: 0,
      height: 4,
    },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 4,
  },
  avatarText: {
    fontSize: 32,
    fontWeight: '700',
    color: '#FFFFFF',
  },
  username: {
    fontSize: 28,
    fontWeight: '700',
    color: '#111827',
    marginBottom: 4,
    letterSpacing: -0.5,
  },
  email: {
    fontSize: 16,
    color: '#6B7280',
    fontWeight: '500',
    marginBottom: 16,
  },
  bioContainer: {
    backgroundColor: '#F9FAFB',
    paddingHorizontal: 20,
    paddingVertical: 16,
    borderRadius: 20,
    maxWidth: width - 48,
  },
  bio: {
    fontSize: 16,
    color: '#374151',
    lineHeight: 24,
    textAlign: 'center',
  },
  testButton: {
    backgroundColor: '#FF9800',
    marginHorizontal: 24,
    marginBottom: 16,
    paddingVertical: 16,
    borderRadius: 20,
    alignItems: 'center',
    shadowColor: '#FF9800',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.2,
    shadowRadius: 4,
    elevation: 2,
  },
  testButtonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '600',
  },
  logoutButton: {
    backgroundColor: '#EF4444',
    marginHorizontal: 24,
    marginBottom: 16,
    paddingVertical: 16,
    borderRadius: 20,
    alignItems: 'center',
    shadowColor: '#EF4444',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.2,
    shadowRadius: 4,
    elevation: 2,
  },
  logoutButtonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '600',
  },
  modalContainer: {
    flex: 1,
    backgroundColor: '#FAFAFA',
  },
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 20,
    paddingHorizontal: 24,
    backgroundColor: '#FFFFFF',
    borderBottomWidth: 1,
    borderBottomColor: '#E5E7EB',
  },
  modalButton: {
    minWidth: 60,
  },
  modalCancel: {
    fontSize: 16,
    color: '#6B7280',
    fontWeight: '500',
  },
  modalTitle: {
    fontSize: 18,
    fontWeight: '700',
    color: '#111827',
  },
  modalSave: {
    fontSize: 16,
    color: '#3B82F6',
    fontWeight: '600',
    textAlign: 'right',
  },
  modalContent: {
    flex: 1,
    paddingHorizontal: 24,
    paddingTop: 32,
  },
  inputGroup: {
    marginBottom: 28,
  },
  inputLabel: {
    fontSize: 16,
    fontWeight: '600',
    color: '#374151',
    marginBottom: 12,
    letterSpacing: -0.2,
  },
  inputContainer: {
    backgroundColor: '#FFFFFF',
    borderRadius: 20,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 1,
    },
    shadowOpacity: 0.05,
    shadowRadius: 2,
    elevation: 1,
  },
  input: {
    paddingHorizontal: 20,
    paddingVertical: 16,
    fontSize: 16,
    color: '#111827',
    borderRadius: 16,
  },
  bioInputContainer: {
    minHeight: 120,
  },
  bioInput: {
    minHeight: 120,
    textAlignVertical: 'top',
    paddingTop: 16,
  },
  deleteButton: {
    backgroundColor: '#DC2626',
    marginHorizontal: 24,
    marginBottom: 32,
    paddingVertical: 16,
    borderRadius: 20,
    alignItems: 'center',
    shadowColor: '#DC2626',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.2,
    shadowRadius: 4,
    elevation: 2,
    borderWidth: 1,
    borderColor: '#B91C1C',
  },
  deleteButtonDisabled: {
    opacity: 0.6,
    backgroundColor: '#9CA3AF',
    shadowColor: '#9CA3AF',
    borderColor: '#6B7280',
  },
  deleteButtonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '600',
  },
  
  // Delete Modal Styles
  deleteModalTitle: {
    fontSize: 18,
    fontWeight: '700',
    color: '#DC2626',  // Red color for delete
  },
  deleteModalConfirm: {
    fontSize: 16,
    color: '#DC2626',  // Red color for delete action
    fontWeight: '600',
    textAlign: 'right',
  },
  deleteWarningContainer: {
    paddingVertical: 20,
    alignItems: 'center',
  },
  deleteWarningEmoji: {
    fontSize: 48,
    marginBottom: 16,
  },
  deleteWarningTitle: {
    fontSize: 20,
    fontWeight: '700',
    color: '#DC2626',
    marginBottom: 16,
    textAlign: 'center',
  },
  deleteWarningText: {
    fontSize: 16,
    color: '#374151',
    marginBottom: 16,
    textAlign: 'center',
    lineHeight: 24,
  },
  deleteWarningList: {
    alignSelf: 'stretch',
    marginBottom: 24,
    paddingHorizontal: 20,
  },
  deleteWarningItem: {
    fontSize: 15,
    color: '#EF4444',
    marginBottom: 8,
    lineHeight: 22,
    alignSelf: 'center'
  },
  deleteConfirmationPrompt: {
    fontSize: 16,
    color: '#374151',
    marginBottom: 16,
    textAlign: 'center',
    fontWeight: '600',
  },
  usernameHighlight: {
    fontWeight: '700',
    color: '#DC2626',
    backgroundColor: '#FEE2E2',
    paddingHorizontal: 4,
    paddingVertical: 2,
    borderRadius: 4,
  },
  deleteConfirmInput: {
    borderWidth: 2,
    borderColor: '#DC2626',
    backgroundColor: '#FEF2F2',
  },
  
  // Password Change Styles
  passwordSection: {
    marginTop: 8,
  },
  passwordToggle: {
    backgroundColor: '#F3F4F6',
    paddingVertical: 12,
    paddingHorizontal: 16,
    borderRadius: 12,
    marginBottom: 16,
  },
  passwordToggleText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#374151',
  },
  passwordFields: {
    paddingLeft: 8,
  },
  passwordNote: {
    fontSize: 12,
    color: '#6B7280',
    fontStyle: 'italic',
    textAlign: 'center',
    marginTop: 12,
    paddingHorizontal: 16,
    lineHeight: 18,
  },
  
  // Social Stats Styles
  socialStatsSection: {
    paddingHorizontal: 24,
    paddingVertical: 20,
    backgroundColor: RodRoyaleTheme.colors.surface,
    marginHorizontal: 24,
    borderRadius: 20,
    marginBottom: 20,
    borderWidth: 1,
    borderColor: RodRoyaleTheme.colors.border,
    ...RodRoyaleTheme.shadows.medium,
  },
  socialStatsHeaderContainer: {
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 16,
  },
  socialStatsHeader: {
    fontSize: 16,
    fontWeight: '600',
    color: RodRoyaleTheme.colors.primary,
    textAlign: 'center',
    letterSpacing: 0.5,
  },
  socialStatsContainer: {
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
  },
  socialStatItem: {
    flex: 1,
    alignItems: 'center',
    paddingVertical: 12,
    paddingHorizontal: 16,
    borderRadius: 12,
    backgroundColor: 'transparent',
  },
  socialStatItemRefreshing: {
    opacity: 0.7,
  },
  socialStatNumber: {
    fontSize: 28,
    fontWeight: '700',
    color: RodRoyaleTheme.colors.primary,
    marginBottom: 4,
    textShadowColor: 'rgba(0,0,0,0.1)',
    textShadowOffset: { width: 0, height: 1 },
    textShadowRadius: 2,
  },
  socialStatLabel: {
    fontSize: 14,
    fontWeight: '600',
    color: RodRoyaleTheme.colors.textSecondary,
    textTransform: 'uppercase',
    letterSpacing: 0.5,
  },
  socialStatDivider: {
    width: 1,
    height: 40,
    backgroundColor: RodRoyaleTheme.colors.border,
    marginHorizontal: 20,
  },
});

export default ProfileScreen;