// Wallet Screen for YYS-SQR Mobile App
// Server-side wallet generation - no crypto dependencies
import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  TextInput,
  Alert,
  ActivityIndicator,
  ScrollView,
} from 'react-native';
import YYSApiService from '../services/YYSApiService';

export default function WalletScreen({ navigation }) {
  const [isLoading, setIsLoading] = useState(false);
  const [walletInfo, setWalletInfo] = useState(null);
  const [email, setEmail] = useState('');
  const [balance, setBalance] = useState('0.0000');

  useEffect(() => {
    checkExistingWallet();
  }, []);

  const checkExistingWallet = async () => {
    // Check if user already has a wallet (stored locally)
    // In a real app, you'd use AsyncStorage or SecureStore
    console.log('Checking for existing wallet...');
  };

  const createWallet = async () => {
    if (!email.trim()) {
      Alert.alert('Error', 'Please enter your email address');
      return;
    }

    try {
      setIsLoading(true);
      
      // Call server to create wallet
      const response = await YYSApiService.createWallet(email.trim());
      
      if (response.success) {
        setWalletInfo({
          email: email.trim(),
          walletAddress: response.walletAddress,
          isConnected: true,
        });
        
        Alert.alert('Success', 'Wallet created successfully!');
      } else {
        Alert.alert('Error', response.error || 'Failed to create wallet');
      }
    } catch (error) {
      console.error('Wallet creation error:', error);
      Alert.alert('Error', 'Failed to create wallet. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const getBalance = async () => {
    if (!walletInfo?.walletAddress) return;
    
    try {
      const response = await YYSApiService.getWalletBalance(walletInfo.walletAddress);
      if (response.success) {
        setBalance(response.balance);
      }
    } catch (error) {
      console.error('Balance fetch error:', error);
    }
  };

  const clearWallet = () => {
    setWalletInfo(null);
    setBalance('0.0000');
    setEmail('');
  };

  const copyAddress = () => {
    if (walletInfo?.walletAddress) {
      // In a real app, you'd copy to clipboard
      Alert.alert('Wallet Address', walletInfo.walletAddress);
    }
  };

  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>🔐 Your Wallet</Text>
        <Text style={styles.subtitle}>
          Create a wallet to claim NFTs from scanned cards
        </Text>
      </View>

      {walletInfo && walletInfo.isConnected ? (
        // Connected State
        <View style={styles.connectedContainer}>
          <View style={styles.userCard}>
            <Text style={styles.connectedTitle}>✅ Wallet Ready</Text>
            
            <View style={styles.userInfo}>
              <Text style={styles.userLabel}>Email:</Text>
              <Text style={styles.userValue}>{walletInfo.email}</Text>
            </View>
            
            <TouchableOpacity style={styles.addressButton} onPress={copyAddress}>
              <Text style={styles.addressButtonText}>
                📋 {walletInfo.walletAddress?.substring(0, 10)}...
              </Text>
            </TouchableOpacity>
          </View>

          <View style={styles.balanceCard}>
            <Text style={styles.balanceTitle}>💰 Balance</Text>
            <Text style={styles.balanceAmount}>{balance} ETH</Text>
            <Text style={styles.balanceNetwork}>Sepolia Testnet</Text>
            
            <TouchableOpacity 
              style={styles.refreshButton} 
              onPress={getBalance}
            >
              <Text style={styles.refreshButtonText}>🔄 Refresh</Text>
            </TouchableOpacity>
          </View>

          <TouchableOpacity 
            style={styles.clearButton} 
            onPress={clearWallet}
          >
            <Text style={styles.clearButtonText}>🗑️ Clear Wallet</Text>
          </TouchableOpacity>
        </View>
      ) : (
        // Not Connected State
        <View style={styles.createContainer}>
          <View style={styles.createCard}>
            <Text style={styles.createTitle}>Create Your Wallet</Text>
            <Text style={styles.createDescription}>
              Enter your email to create a secure Ethereum wallet
            </Text>

            <TextInput
              style={styles.emailInput}
              placeholder="Enter your email address"
              value={email}
              onChangeText={setEmail}
              keyboardType="email-address"
              autoCapitalize="none"
              editable={!isLoading}
            />
            
            <TouchableOpacity 
              style={styles.createButton} 
              onPress={createWallet}
              disabled={isLoading || !email.trim()}
            >
              {isLoading ? (
                <ActivityIndicator color="#fff" />
              ) : (
                <Text style={styles.createButtonText}>🚀 Create Wallet</Text>
              )}
            </TouchableOpacity>

            <View style={styles.infoBox}>
              <Text style={styles.infoTitle}>🔒 How it works:</Text>
              <Text style={styles.infoText}>
                • Server creates a real Ethereum wallet for you{'\n'}
                • Your wallet can receive NFTs from scanned cards{'\n'}
                • No seed phrases or complex setup needed{'\n'}
                • Gas fees are covered automatically
              </Text>
            </View>
          </View>
        </View>
      )}

      <View style={styles.actionButtons}>
        <TouchableOpacity 
          style={styles.scanButton} 
          onPress={() => navigation.navigate('Scan')}
        >
          <Text style={styles.scanButtonText}>📷 Scan Cards</Text>
        </TouchableOpacity>
        
        <TouchableOpacity 
          style={styles.homeButton} 
          onPress={() => navigation.navigate('Home')}
        >
          <Text style={styles.homeButtonText}>🏠 Home</Text>
        </TouchableOpacity>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  header: {
    alignItems: 'center',
    padding: 20,
    backgroundColor: '#fff',
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#333',
  },
  subtitle: {
    fontSize: 16,
    color: '#666',
    marginTop: 5,
    textAlign: 'center',
  },
  connectedContainer: {
    padding: 20,
  },
  userCard: {
    backgroundColor: '#fff',
    padding: 20,
    borderRadius: 10,
    marginBottom: 15,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 3.84,
    elevation: 5,
  },
  connectedTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#4CAF50',
    marginBottom: 15,
    textAlign: 'center',
  },
  userInfo: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 15,
  },
  userLabel: {
    fontSize: 16,
    color: '#666',
    fontWeight: '500',
  },
  userValue: {
    fontSize: 16,
    color: '#333',
    fontWeight: '600',
  },
  addressButton: {
    backgroundColor: '#2196F3',
    padding: 12,
    borderRadius: 8,
  },
  addressButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
    textAlign: 'center',
  },
  balanceCard: {
    backgroundColor: '#fff',
    padding: 20,
    borderRadius: 10,
    marginBottom: 15,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 3.84,
    elevation: 5,
  },
  balanceTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 10,
  },
  balanceAmount: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#4CAF50',
    marginBottom: 5,
  },
  balanceNetwork: {
    fontSize: 14,
    color: '#666',
    marginBottom: 15,
  },
  refreshButton: {
    backgroundColor: '#FF9800',
    paddingHorizontal: 20,
    paddingVertical: 8,
    borderRadius: 6,
  },
  refreshButtonText: {
    color: '#fff',
    fontSize: 14,
    fontWeight: '600',
  },
  clearButton: {
    backgroundColor: '#f44336',
    padding: 15,
    borderRadius: 10,
    alignItems: 'center',
  },
  clearButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  createContainer: {
    padding: 20,
  },
  createCard: {
    backgroundColor: '#fff',
    padding: 25,
    borderRadius: 10,
    marginBottom: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 3.84,
    elevation: 5,
  },
  createTitle: {
    fontSize: 22,
    fontWeight: 'bold',
    color: '#333',
    textAlign: 'center',
    marginBottom: 10,
  },
  createDescription: {
    fontSize: 16,
    color: '#666',
    textAlign: 'center',
    marginBottom: 25,
  },
  emailInput: {
    borderWidth: 1,
    borderColor: '#ddd',
    padding: 15,
    borderRadius: 10,
    fontSize: 16,
    backgroundColor: '#f9f9f9',
    marginBottom: 20,
  },
  createButton: {
    backgroundColor: '#4CAF50',
    padding: 15,
    borderRadius: 10,
    alignItems: 'center',
    marginBottom: 20,
  },
  createButtonText: {
    color: '#fff',
    fontSize: 18,
    fontWeight: 'bold',
  },
  infoBox: {
    backgroundColor: '#f0f8ff',
    padding: 15,
    borderRadius: 10,
  },
  infoTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#1e40af',
    marginBottom: 8,
  },
  infoText: {
    fontSize: 14,
    color: '#1e40af',
    lineHeight: 20,
  },
  actionButtons: {
    padding: 20,
    gap: 10,
  },
  scanButton: {
    backgroundColor: '#4CAF50',
    padding: 15,
    borderRadius: 10,
    alignItems: 'center',
  },
  scanButtonText: {
    color: '#fff',
    fontSize: 18,
    fontWeight: 'bold',
  },
  homeButton: {
    backgroundColor: '#2196F3',
    padding: 15,
    borderRadius: 10,
    alignItems: 'center',
  },
  homeButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
});