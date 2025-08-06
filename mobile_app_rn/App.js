// YYS-SQR Mobile App - React Native + Expo
import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import { StatusBar } from 'expo-status-bar';

// Import screens
import HomeScreen from './src/screens/HomeScreen';
import ScanScreen from './src/screens/ScanScreen';
import ManualScanScreen from './src/screens/ManualScanScreen';
import EmbedScreen from './src/screens/EmbedScreen';
import ResultScreen from './src/screens/ResultScreen';
import WalletScreen from './src/screens/WalletScreen';

const Stack = createStackNavigator();

export default function App() {
  return (
    <NavigationContainer>
      <StatusBar style="auto" />
      <Stack.Navigator 
        initialRouteName="Home"
        screenOptions={{
          headerStyle: {
            backgroundColor: '#2196F3',
          },
          headerTintColor: '#fff',
          headerTitleStyle: {
            fontWeight: 'bold',
          },
        }}
      >
        <Stack.Screen 
          name="Home" 
          component={HomeScreen} 
          options={{ title: 'YYS-SQR Scanner' }}
        />
        <Stack.Screen 
          name="Scan" 
          component={ScanScreen} 
          options={{ title: 'Auto Scan' }}
        />
        <Stack.Screen 
          name="ManualScan" 
          component={ManualScanScreen} 
          options={{ title: 'Manual Scan' }}
        />
        <Stack.Screen 
          name="Embed" 
          component={EmbedScreen} 
          options={{ title: 'Embed Watermark' }}
        />
        <Stack.Screen 
          name="Result" 
          component={ResultScreen} 
          options={{ title: 'Scan Result' }}
        />
        <Stack.Screen 
          name="Wallet" 
          component={WalletScreen} 
          options={{ title: 'Your Wallet' }}
        />
      </Stack.Navigator>
    </NavigationContainer>
  );
}