import React, { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  Alert,
  SafeAreaView,
  KeyboardAvoidingView,
  Platform,
  Image,
  Dimensions,
  ScrollView,
  ActivityIndicator,
} from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { RootStackParamList } from '../navigation/AppNavigator';
import { useAuth } from '../contexts/AuthContext';
import RodRoyaleTheme, { ComponentThemes } from '../theme/RodRoyaleTheme';

const { width } = Dimensions.get('window');

type RegisterScreenNavigationProp = NativeStackNavigationProp<RootStackParamList, 'Register'>;

const RegisterScreen: React.FC = () => {
  const [email, setEmail] = useState('');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [bio, setBio] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const navigation = useNavigation<RegisterScreenNavigationProp>();
  const { register } = useAuth();

  const handleRegister = async () => {
    if (!email.trim() || !username.trim() || !password.trim()) {
      Alert.alert('Error', 'Please enter email, username, and password');
      return;
    }

    if (password.length < 6) {
      Alert.alert('Error', 'Password must be at least 6 characters long');
      return;
    }

    setIsLoading(true);
    try {
      console.log('Attempting to register user:', { username, email, bio });
      await register(username.trim(), email.trim(), password, bio.trim());
      console.log('Registration successful');
    } catch (error: any) {
      console.error('Registration error:', error);
      
      let errorMessage = 'Unable to create account. Please try again.';
      
      if (error.response) {
        // Server responded with error status
        const status = error.response.status;
        const data = error.response.data;
        
        if (status === 400) {
          errorMessage = data.detail || 'Invalid user data. Please check your inputs.';
        } else if (status === 409) {
          errorMessage = 'Username or email already exists. Please choose different ones.';
        } else if (status >= 500) {
          errorMessage = 'Server error. Please try again later.';
        } else {
          errorMessage = `Registration failed: ${data.detail || 'Unknown error'}`;
        }
      } else if (error.request) {
        // Network error
        errorMessage = 'Cannot connect to server. Please check your internet connection and make sure the backend is running.';
      }
      
      Alert.alert('Registration Failed', errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <KeyboardAvoidingView
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        style={styles.keyboardAvoidingView}
      >
        <ScrollView 
          contentContainerStyle={styles.scrollContent}
          showsVerticalScrollIndicator={false}
          keyboardShouldPersistTaps="handled"
        >
          <View style={styles.content}>
            {/* Rod Royale Logo */}
            <View style={styles.logoContainer}>
              <Image
                source={require('../../assets/rod_royale_logo.png')}
                style={styles.logo}
                resizeMode="contain"
              />
            </View>
            
            {/* App Title */}
            <Text style={styles.title}>JOIN THE ROYALE</Text>
            <Text style={styles.subtitle}>⚔️ Become a Fishing Champion! ⚔️</Text>

            <View style={styles.form}>
              <View style={styles.inputContainer}>
                <TextInput
                  style={styles.input}
                  placeholder="Champion Username"
                  placeholderTextColor={RodRoyaleTheme.colors.textSecondary}
                  value={username}
                  onChangeText={setUsername}
                  autoCapitalize="none"
                  autoCorrect={false}
                />
              </View>
              
              <View style={styles.inputContainer}>
                <TextInput
                  style={styles.input}
                  placeholder="Email Address"
                  placeholderTextColor={RodRoyaleTheme.colors.textSecondary}
                  value={email}
                  onChangeText={setEmail}
                  keyboardType="email-address"
                  autoCapitalize="none"
                  autoCorrect={false}
                />
              </View>
              
              <View style={styles.inputContainer}>
                <TextInput
                  style={styles.input}
                  placeholder="Battle Password (min 6 characters)"
                  placeholderTextColor={RodRoyaleTheme.colors.textSecondary}
                  value={password}
                  onChangeText={setPassword}
                  secureTextEntry
                  autoCapitalize="none"
                  autoCorrect={false}
                />
              </View>
              
              <View style={[styles.inputContainer, styles.bioContainer]}>
                <TextInput
                  style={[styles.input, styles.bioInput]}
                  placeholder="Your fishing battle story (optional)..."
                  placeholderTextColor={RodRoyaleTheme.colors.textSecondary}
                  value={bio}
                  onChangeText={setBio}
                  multiline
                  numberOfLines={3}
                  textAlignVertical="top"
                />
              </View>

              <TouchableOpacity
                style={[styles.button, isLoading && styles.buttonDisabled]}
                onPress={handleRegister}
                disabled={isLoading}
              >
                {isLoading ? (
                  <View style={styles.buttonLoadingContainer}>
                    <ActivityIndicator size="small" color="white" />
                    <Text style={styles.buttonText}>JOINING BATTLE...</Text>
                  </View>
                ) : (
                  <Text style={styles.buttonText}>⚔️ JOIN THE BATTLE</Text>
                )}
              </TouchableOpacity>

              <TouchableOpacity
                style={styles.linkButton}
                onPress={() => navigation.navigate('Login')}
              >
                <Text style={styles.linkText}>
                  🎣 Already a Champion? Enter Battle!
                </Text>
              </TouchableOpacity>
            </View>
          </View>
        </ScrollView>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: RodRoyaleTheme.colors.background, // Sky blue
  },
  keyboardAvoidingView: {
    flex: 1,
  },
  scrollContent: {
    flexGrow: 1,
    justifyContent: 'center',
    paddingVertical: RodRoyaleTheme.spacing.lg,
  },
  content: {
    paddingHorizontal: RodRoyaleTheme.spacing.xl,
  },
  logoContainer: {
    alignItems: 'center',
    marginBottom: RodRoyaleTheme.spacing.md,
  },
  logo: {
    width: width * 0.35, // Slightly smaller for register screen
    height: width * 0.35 * 0.8, // Maintain aspect ratio
    marginBottom: RodRoyaleTheme.spacing.sm,
  },
  title: {
    ...RodRoyaleTheme.typography.h1,
    fontSize: 32,
    textAlign: 'center',
    marginBottom: RodRoyaleTheme.spacing.sm,
    letterSpacing: 1.5,
  },
  subtitle: {
    ...RodRoyaleTheme.typography.body,
    fontSize: 16,
    textAlign: 'center',
    marginBottom: RodRoyaleTheme.spacing.xl,
    color: RodRoyaleTheme.colors.primaryDark,
    fontWeight: 'bold',
  },
  form: {
    gap: RodRoyaleTheme.spacing.md,
  },
  inputContainer: {
    ...ComponentThemes.card.default,
    borderWidth: 3,
    borderColor: RodRoyaleTheme.colors.primaryDark,
    backgroundColor: RodRoyaleTheme.colors.surface,
    paddingHorizontal: 0,
    paddingVertical: 0,
  },
  bioContainer: {
    minHeight: 90,
  },
  input: {
    height: 56,
    paddingHorizontal: RodRoyaleTheme.spacing.md,
    fontSize: 16,
    color: RodRoyaleTheme.colors.text,
    fontWeight: '500',
  },
  bioInput: {
    height: 80,
    paddingTop: RodRoyaleTheme.spacing.md,
    paddingBottom: RodRoyaleTheme.spacing.md,
    textAlignVertical: 'top',
  },
  button: {
    ...ComponentThemes.button.primary,
    height: 56,
    justifyContent: 'center',
    alignItems: 'center',
    marginTop: RodRoyaleTheme.spacing.md,
  },
  buttonDisabled: {
    opacity: 0.6,
  },
  buttonLoadingContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  buttonText: {
    ...RodRoyaleTheme.typography.competitive,
    fontSize: 18,
    color: RodRoyaleTheme.colors.primaryDark,
    fontWeight: 'bold',
  },
  linkButton: {
    marginTop: RodRoyaleTheme.spacing.lg,
    alignItems: 'center',
    padding: RodRoyaleTheme.spacing.md,
  },
  linkText: {
    ...RodRoyaleTheme.typography.accent,
    fontSize: 16,
    color: RodRoyaleTheme.colors.primaryDark,
    textDecorationLine: 'underline',
  },
});

export default RegisterScreen;
