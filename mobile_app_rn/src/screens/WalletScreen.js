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
  Linking,
  Image,
} from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import YYSApiService from '../services/YYSApiService';

export default function WalletScreen({ navigation }) {
  const [isLoading, setIsLoading] = useState(false);
  const [walletInfo, setWalletInfo] = useState(null);
  const [email, setEmail] = useState('');
  const [balance, setBalance] = useState('0.0000');
  const [userNFTs, setUserNFTs] = useState([]);
  const [loadingNFTs, setLoadingNFTs] = useState(false);

  useEffect(() => {
    checkExistingWallet();
  }, []);

  const checkExistingWallet = async () => {
    try {
      // Check if user already has a wallet stored locally
      const storedWallet = await AsyncStorage.getItem('user_wallet');
      if (storedWallet) {
        const walletData = JSON.parse(storedWallet);
        setWalletInfo(walletData);
        console.log('✅ Found existing wallet:', walletData.walletAddress);
        await updateBalance(walletData.walletAddress);
        await fetchUserNFTs(walletData.walletAddress);
      }
    } catch (error) {
      console.error('Error checking existing wallet:', error);
    }
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
        const walletData = {
          email: email.trim(),
          walletAddress: response.walletAddress,
          isConnected: true,
        };
        
        // Store wallet info locally
        await AsyncStorage.setItem('user_wallet', JSON.stringify(walletData));
        
        setWalletInfo(walletData);
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

  const updateBalance = async (address) => {
    const walletAddress = address || walletInfo?.walletAddress;
    if (!walletAddress) return;
    
    try {
      const response = await YYSApiService.getWalletBalance(walletAddress);
      if (response.success) {
        setBalance(response.balance);
      }
    } catch (error) {
      console.error('Balance fetch error:', error);
    }
  };

  const fetchUserNFTs = async (walletAddress) => {
    try {
      setLoadingNFTs(true);
      const response = await YYSApiService.getUserNFTs(walletAddress);
      if (response.success) {
        setUserNFTs(response.nfts);
      }
    } catch (error) {
      console.error('Error fetching NFTs:', error);
    } finally {
      setLoadingNFTs(false);
    }
  };

  const getBalance = async () => {
    await updateBalance();
  };

  const clearWallet = async () => {
    try {
      await AsyncStorage.removeItem('user_wallet');
      setWalletInfo(null);
      setBalance('0.0000');
      setEmail('');
      Alert.alert('Success', 'Wallet cleared');
    } catch (error) {
      console.error('Error clearing wallet:', error);
    }
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

          {/* NFT Collection */}
          <View style={styles.nftCard}>
            <Text style={styles.nftTitle}>🎨 Your NFT Collection</Text>
            {loadingNFTs ? (
              <ActivityIndicator size="small" color="#2196F3" />
            ) : userNFTs.length > 0 ? (
              <ScrollView style={styles.nftList}>
                {userNFTs.map((nft, index) => (
                  <View key={index} style={styles.nftItem}>
                    {nft.imageUrl && (
                      <Image 
                        source={{ uri: nft.imageUrl }} 
                        style={styles.nftImage}
                        resizeMode="cover"
                      />
                    )}
                    <View style={styles.nftDetails}>
                      <Text style={styles.nftName}>{nft.cardName}</Text>
                      <Text style={styles.nftTokenId}>Token ID: #{nft.tokenId || nft.nft_token_id}</Text>
                      <Text style={styles.nftWatermark}>Card: {nft.watermarkId}</Text>
                      {nft.ipfs_cid && (
                        <Text style={styles.nftIpfs}>IPFS: {nft.ipfs_cid.substring(0, 12)}...</Text>
                      )}
                      <View style={styles.nftButtons}>
                        {nft.etherscanUrl && (
                          <TouchableOpacity 
                            style={styles.nftViewButton}
                            onPress={() => Linking.openURL(nft.etherscanUrl)}
                          >
                            <Text style={styles.nftViewButtonText}>📊 Etherscan</Text>
                          </TouchableOpacity>
                        )}
                        {nft.imageUrl && (
                          <TouchableOpacity 
                            style={styles.nftImageButton}
                            onPress={() => Linking.openURL(nft.imageUrl)}
                          >
                            <Text style={styles.nftImageButtonText}>🖼️ View Image</Text>
                          </TouchableOpacity>
                        )}
                        {nft.ipfs_cid && (
                          <TouchableOpacity 
                            style={styles.nftIpfsButton}
                            onPress={() => Linking.openURL(`https://gateway.pinata.cloud/ipfs/${nft.ipfs_cid}`)}
                          >
                            <Text style={styles.nftIpfsButtonText}>🌐 IPFS</Text>
                          </TouchableOpacity>
                        )}
                      </View>
                    </View>
                  </View>
                ))}
              </ScrollView>
            ) : (
              <Text style={styles.noNftsText}>
                No NFTs yet. Scan cards to claim your first NFT!
              </Text>
            )}
            
            <TouchableOpacity 
              style={styles.refreshButton} 
              onPress={() => fetchUserNFTs(walletInfo.walletAddress)}
            >
              <Text style={styles.refreshButtonText}>🔄 Refresh NFTs</Text>
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
  nftCard: {
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
  nftTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 15,
  },
  nftList: {
    maxHeight: 200,
    marginBottom: 15,
  },
  nftItem: {
    backgroundColor: '#f8f9fa',
    padding: 12,
    borderRadius: 8,
    marginBottom: 10,
    flexDirection: 'row',
  },
  nftImage: {
    width: 60,
    height: 60,
    borderRadius: 8,
    marginRight: 12,
  },
  nftDetails: {
    flex: 1,
  },
  nftName: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 4,
  },
  nftTokenId: {
    fontSize: 14,
    color: '#2196F3',
    marginBottom: 2,
  },
  nftWatermark: {
    fontSize: 12,
    color: '#666',
    marginBottom: 2,
  },
  nftIpfs: {
    fontSize: 11,
    color: '#9C27B0',
    marginBottom: 8,
    fontFamily: 'monospace',
  },
  nftButtons: {
    flexDirection: 'row',
    gap: 6,
    flexWrap: 'wrap',
  },
  nftViewButton: {
    backgroundColor: '#2196F3',
    padding: 6,
    borderRadius: 4,
  },
  nftViewButtonText: {
    color: '#fff',
    fontSize: 12,
    fontWeight: '600',
  },
  nftImageButton: {
    backgroundColor: '#4CAF50',
    padding: 6,
    borderRadius: 4,
  },
  nftImageButtonText: {
    color: '#fff',
    fontSize: 12,
    fontWeight: '600',
  },
  nftIpfsButton: {
    backgroundColor: '#9C27B0',
    padding: 6,
    borderRadius: 4,
  },
  nftIpfsButtonText: {
    color: '#fff',
    fontSize: 12,
    fontWeight: '600',
  },
  noNftsText: {
    fontSize: 14,
    color: '#666',
    textAlign: 'center',
    fontStyle: 'italic',
    marginBottom: 15,
  },
});