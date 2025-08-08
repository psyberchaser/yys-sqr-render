// YYS-SQR Mobile Home Screen
import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Alert,
  ActivityIndicator,
  ScrollView,
  RefreshControl,
} from 'react-native';
import YYSApiService from '../services/YYSApiService';

export default function HomeScreen({ navigation }) {
  const [serverStatus, setServerStatus] = useState('checking');
  const [capacityInfo, setCapacityInfo] = useState(null);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    checkServerStatus();
    getCapacityInfo();
  }, []);

  const checkServerStatus = async () => {
    try {
      console.log('🔍 Checking server health at:', YYSApiService.client.defaults.baseURL);
      console.log('🔍 Full health URL:', YYSApiService.client.defaults.baseURL + '/health');
      
      const result = await YYSApiService.healthCheck();
      console.log('✅ Health check result:', result);
      
      // If we get any response, server is working
      if (result) {
        setServerStatus('online');
        console.log('✅ Server marked as online - response received:', result);
      } else {
        setServerStatus('offline');
        console.log('❌ Server response empty');
      }
    } catch (error) {
      setServerStatus('offline');
      console.error('❌ Server health check failed:', error);
      console.error('❌ Error details:', error.message);
      console.error('❌ Error response:', error.response?.data);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await checkServerStatus();
    await getCapacityInfo();
    setRefreshing(false);
  };

  const getCapacityInfo = async () => {
    try {
      const capacity = await YYSApiService.getCapacity();
      setCapacityInfo(capacity);
    } catch (error) {
      console.error('Failed to get capacity info:', error);
    }
  };

  const navigateToScan = () => {
    navigation.navigate('Scan');
  };



  const getStatusColor = () => {
    switch (serverStatus) {
      case 'online': return '#4CAF50';
      case 'offline': return '#f44336';
      default: return '#FF9800';
    }
  };

  const getStatusText = () => {
    switch (serverStatus) {
      case 'online': return '✅ Server Online';
      case 'offline': return '❌ Server Offline';
      default: return '🔄 Checking...';
    }
  };

  return (
    <ScrollView 
      style={styles.container}
      contentContainerStyle={styles.scrollContent}
      refreshControl={
        <RefreshControl
          refreshing={refreshing}
          onRefresh={onRefresh}
          colors={['#2196F3']}
          tintColor="#2196F3"
        />
      }
    >
      <View style={styles.header}>
        <Text style={styles.title}>YYS-SQR</Text>
        <Text style={styles.subtitle}>Watermark Scanner & NFT Platform</Text>
        
        <View style={styles.statusCard}>
          <View style={styles.statusContainer}>
            <Text style={[styles.statusText, { color: getStatusColor() }]}>
              {getStatusText()}
            </Text>
            {serverStatus === 'checking' && (
              <ActivityIndicator size="small" color="#FF9800" style={styles.spinner} />
            )}
          </View>
          
          <TouchableOpacity onPress={checkServerStatus} style={styles.refreshButton}>
            <Text style={styles.refreshText}>🔄 Refresh Status</Text>
          </TouchableOpacity>

          {capacityInfo && (
            <View style={styles.infoContainer}>
              <Text style={styles.infoText}>
                📊 Capacity: {capacityInfo.capacity_characters} characters
              </Text>
              <Text style={styles.infoText}>
                🔒 Encoding: {capacityInfo.encoding}
              </Text>
            </View>
          )}
        </View>
      </View>

      <View style={styles.actionsSection}>
        <Text style={styles.sectionTitle}>🚀 Quick Actions</Text>
        
        <View style={styles.buttonGrid}>
          <TouchableOpacity
            style={[styles.actionButton, styles.scanButton]}
            onPress={navigateToScan}
          >
            <View style={styles.buttonContent}>
              <Text style={styles.buttonIcon}>📷</Text>
              <Text style={styles.buttonText}>Auto Scan</Text>
              <Text style={styles.buttonSubtext}>
                AI-powered detection
              </Text>
            </View>
          </TouchableOpacity>

          <TouchableOpacity
            style={[styles.actionButton, styles.manualButton]}
            onPress={() => navigation.navigate('ManualScan')}
          >
            <View style={styles.buttonContent}>
              <Text style={styles.buttonIcon}>👆</Text>
              <Text style={styles.buttonText}>Manual Scan</Text>
              <Text style={styles.buttonSubtext}>
                Select corners
              </Text>
            </View>
          </TouchableOpacity>
        </View>

        <View style={styles.buttonGrid}>
          <TouchableOpacity
            style={[styles.actionButton, styles.walletButton]}
            onPress={() => navigation.navigate('Wallet')}
          >
            <View style={styles.buttonContent}>
              <Text style={styles.buttonIcon}>💰</Text>
              <Text style={styles.buttonText}>Wallet</Text>
              <Text style={styles.buttonSubtext}>
                Claim NFTs
              </Text>
            </View>
          </TouchableOpacity>
        </View>
      </View>

      <View style={styles.featuresSection}>
        <Text style={styles.sectionTitle}>✨ Features</Text>
        
        <View style={styles.featureCard}>
          <Text style={styles.featureIcon}>🤖</Text>
          <View style={styles.featureContent}>
            <Text style={styles.featureTitle}>AI Corner Detection</Text>
            <Text style={styles.featureDescription}>
              Advanced computer vision automatically finds watermark boundaries
            </Text>
          </View>
        </View>

        <View style={styles.featureCard}>
          <Text style={styles.featureIcon}>🎨</Text>
          <View style={styles.featureContent}>
            <Text style={styles.featureTitle}>NFT Integration</Text>
            <Text style={styles.featureDescription}>
              Scan trading cards to claim unique NFTs on Ethereum blockchain
            </Text>
          </View>
        </View>

        <View style={styles.featureCard}>
          <Text style={styles.featureIcon}>🔐</Text>
          <View style={styles.featureContent}>
            <Text style={styles.featureTitle}>Secure Watermarking</Text>
            <Text style={styles.featureDescription}>
              Hide secret messages in images using advanced steganography
            </Text>
          </View>
        </View>
      </View>

      <View style={styles.footer}>
        <Text style={styles.footerText}>
          Powered by advanced computer vision & blockchain technology
        </Text>
        <Text style={styles.versionText}>v1.0.0</Text>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8f9fa',
  },
  scrollContent: {
    paddingHorizontal: 20,
    paddingBottom: 30,
  },
  header: {
    alignItems: 'center',
    marginTop: 50,
    marginBottom: 30,
  },
  title: {
    fontSize: 36,
    fontWeight: 'bold',
    color: '#2196F3',
    marginBottom: 8,
    textAlign: 'center',
  },
  subtitle: {
    fontSize: 16,
    color: '#666',
    marginBottom: 25,
    textAlign: 'center',
  },
  statusCard: {
    backgroundColor: '#fff',
    padding: 20,
    borderRadius: 15,
    width: '100%',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 5,
  },
  statusContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 15,
  },
  statusText: {
    fontSize: 18,
    fontWeight: '600',
  },
  spinner: {
    marginLeft: 10,
  },
  refreshButton: {
    alignSelf: 'center',
    paddingHorizontal: 20,
    paddingVertical: 8,
    backgroundColor: '#e3f2fd',
    borderRadius: 20,
    marginBottom: 15,
  },
  refreshText: {
    fontSize: 14,
    color: '#2196F3',
    fontWeight: '600',
  },
  infoContainer: {
    backgroundColor: '#f0f8ff',
    padding: 15,
    borderRadius: 10,
    alignItems: 'center',
  },
  infoText: {
    fontSize: 14,
    color: '#1976d2',
    marginBottom: 4,
    textAlign: 'center',
  },
  actionsSection: {
    marginVertical: 25,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 15,
    textAlign: 'center',
  },
  buttonGrid: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 15,
  },
  actionButton: {
    backgroundColor: '#fff',
    flex: 0.48,
    borderRadius: 15,
    padding: 20,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 5,
  },
  buttonContent: {
    alignItems: 'center',
  },
  scanButton: {
    borderTopWidth: 4,
    borderTopColor: '#4CAF50',
  },
  manualButton: {
    borderTopWidth: 4,
    borderTopColor: '#FF9800',
  },

  walletButton: {
    borderTopWidth: 4,
    borderTopColor: '#9C27B0',
  },
  buttonIcon: {
    fontSize: 32,
    marginBottom: 8,
  },
  buttonText: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 4,
    textAlign: 'center',
  },
  buttonSubtext: {
    fontSize: 12,
    color: '#666',
    textAlign: 'center',
    lineHeight: 16,
  },
  featuresSection: {
    marginVertical: 20,
  },
  featureCard: {
    backgroundColor: '#fff',
    flexDirection: 'row',
    padding: 20,
    borderRadius: 12,
    marginBottom: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 4,
    elevation: 2,
  },
  featureIcon: {
    fontSize: 24,
    marginRight: 15,
    alignSelf: 'flex-start',
    marginTop: 2,
  },
  featureContent: {
    flex: 1,
  },
  featureTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginBottom: 4,
  },
  featureDescription: {
    fontSize: 14,
    color: '#666',
    lineHeight: 20,
  },
  footer: {
    alignItems: 'center',
    marginTop: 30,
    paddingTop: 20,
    borderTopWidth: 1,
    borderTopColor: '#e0e0e0',
  },
  footerText: {
    fontSize: 12,
    color: '#999',
    textAlign: 'center',
    marginBottom: 5,
  },
  versionText: {
    fontSize: 10,
    color: '#ccc',
    textAlign: 'center',
  },
});