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
  ActivityIndicator,
} from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { RootStackParamList } from '../navigation/AppNavigator';
import { useAuth } from '../contexts/AuthContext';
import RodRoyaleTheme, { ComponentThemes } from '../theme/RodRoyaleTheme';

const { width } = Dimensions.get('window');

type LoginScreenNavigationProp = NativeStackNavigationProp<RootStackParamList, 'Login'>;

const LoginScreen: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const navigation = useNavigation<LoginScreenNavigationProp>();
  const { login } = useAuth();

  const handleLogin = async () => {
    if (!email.trim() || !password.trim()) {
      Alert.alert('Error', 'Please enter both email and password');
      return;
    }

    setIsLoading(true);
    try {
      console.log('Attempting to login user:', { email });
      await login(email.trim(), password);
      console.log('Login successful');
    } catch (error: any) {
      console.error('Login error:', error);
      
      let errorMessage = 'Unable to login. Please check your credentials.';
      
      if (error.response) {
        const status = error.response.status;
        const data = error.response.data;
        
        if (status === 401) {
          errorMessage = 'Invalid email or password.';
        } else if (status === 400) {
          errorMessage = data.detail || 'Invalid login data.';
        } else if (status >= 500) {
          errorMessage = 'Server error. Please try again later.';
        }
      } else if (error.request) {
        errorMessage = 'Cannot connect to server. Please check your connection.';
      }
      
      Alert.alert('Login Failed', errorMessage);
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
        <View style={styles.content}>
          {/* Rod Royale Logo */}
          <View style={styles.logoContainer}>
            <Image
              source={require('../../assets/rod_royale_logo.png')}
              style={styles.logo}
              resizeMode="contain"
            />
          </View>
          
          {/* App Descriptive */}
            <Text style={styles.subtitle}>⚔️ Cast ‘til the Ultimate Catch! ⚔️</Text>

          <View style={styles.form}>
            <View style={styles.inputContainer}>
              <TextInput
                style={styles.input}
                placeholder="Email"
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
                placeholder="Password"
                placeholderTextColor={RodRoyaleTheme.colors.textSecondary}
                value={password}
                onChangeText={setPassword}
                secureTextEntry
                autoCapitalize="none"
                autoCorrect={false}
              />
            </View>

            <TouchableOpacity
              style={[styles.button, isLoading && styles.buttonDisabled]}
              onPress={handleLogin}
              disabled={isLoading}
            >
              {isLoading ? (
                <View style={styles.buttonLoadingContainer}>
                  <ActivityIndicator size="small" color="white" />
                  <Text style={styles.buttonText}>ENTERING BATTLE...</Text>
                </View>
              ) : (
                <Text style={styles.buttonText}>⚔️ ENTER BATTLE</Text>
              )}
            </TouchableOpacity>

            <TouchableOpacity
              style={styles.linkButton}
              onPress={() => navigation.navigate('Register')}
            >
              <Text style={styles.linkText}>
                New? Join Today!
              </Text>
            </TouchableOpacity>
          </View>
        </View>
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
  content: {
    flex: 1,
    justifyContent: 'center',
    paddingHorizontal: RodRoyaleTheme.spacing.xl,
  },
  logoContainer: {
    alignItems: 'center',
    marginBottom: RodRoyaleTheme.spacing.md,
  },
  logo: {
    width: width * 0.4, // 40% of screen width
    height: width * 0.4 * 0.8, // Maintain aspect ratio
    marginBottom: RodRoyaleTheme.spacing.sm,
  },
  title: {
    ...RodRoyaleTheme.typography.h1,
    fontSize: 36,
    textAlign: 'center',
    marginBottom: RodRoyaleTheme.spacing.sm,
    letterSpacing: 2,
  },
  subtitle: {
    ...RodRoyaleTheme.typography.body,
    fontSize: 16,
    textAlign: 'center',
    marginBottom: RodRoyaleTheme.spacing.xxl,
    color: RodRoyaleTheme.colors.primaryDark,
    fontWeight: 'bold',
  },
  form: {
    gap: RodRoyaleTheme.spacing.lg,
  },
  inputContainer: {
    ...ComponentThemes.card.default,
    borderWidth: 3,
    borderColor: RodRoyaleTheme.colors.primaryDark,
    backgroundColor: RodRoyaleTheme.colors.surface,
    paddingHorizontal: 0,
    paddingVertical: 0,
  },
  input: {
    height: 56,
    paddingHorizontal: RodRoyaleTheme.spacing.md,
    fontSize: 16,
    color: RodRoyaleTheme.colors.text,
    fontWeight: '500',
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

export default LoginScreen;
