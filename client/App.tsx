/**
 * Rod Royale - Social Fishing App
 * React Native Frontend for Rod Royale API
 */

import React from 'react';
import { StatusBar } from 'react-native';
import 'react-native-gesture-handler';
import { AuthProvider } from './src/contexts/AuthContext';
import AppNavigator from './src/navigation/AppNavigator';

const App: React.FC = () => {
  return (
    <>
      <StatusBar barStyle="dark-content" backgroundColor="#f0f8ff" />
      <AuthProvider>
        <AppNavigator />
      </AuthProvider>
    </>
  );
};

export default App;
