// YYS-SQR Mobile Home Screen
import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Alert,
  ActivityIndicator,
} from 'react-native';
import YYSApiService from '../services/YYSApiService';

export default function HomeScreen({ navigation }) {
  const [serverStatus, setServerStatus] = useState('checking');
  const [capacityInfo, setCapacityInfo] = useState(null);

  useEffect(() => {
    checkServerStatus();
    getCapacityInfo();
  }, []);

  const checkServerStatus = async () => {
    try {
      await YYSApiService.healthCheck();
      setServerStatus('online');
    } catch (error) {
      setServerStatus('offline');
      console.error('Server health check failed:', error);
    }
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
    if (serverStatus !== 'online') {
      Alert.alert(
        'Server Offline',
        'The YYS-SQR backend server is not available. Please check your connection and try again.',
        [
          { text: 'Retry', onPress: checkServerStatus },
          { text: 'Cancel', style: 'cancel' },
        ]
      );
      return;
    }
    navigation.navigate('Scan');
  };

  const navigateToEmbed = () => {
    if (serverStatus !== 'online') {
      Alert.alert(
        'Server Offline',
        'The YYS-SQR backend server is not available. Please check your connection and try again.',
        [
          { text: 'Retry', onPress: checkServerStatus },
          { text: 'Cancel', style: 'cancel' },
        ]
      );
      return;
    }
    navigation.navigate('Embed');
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
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>YYS-SQR</Text>
        <Text style={styles.subtitle}>Watermark Scanner</Text>
        
        <View style={styles.statusContainer}>
          <Text style={[styles.statusText, { color: getStatusColor() }]}>
            {getStatusText()}
          </Text>
          {serverStatus === 'checking' && (
            <ActivityIndicator size="small" color="#FF9800" style={styles.spinner} />
          )}
        </View>

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

      <View style={styles.buttonsContainer}>
        <TouchableOpacity
          style={[styles.button, styles.scanButton]}
          onPress={navigateToScan}
          disabled={serverStatus !== 'online'}
        >
          <Text style={styles.buttonIcon}>📷</Text>
          <Text style={styles.buttonText}>Scan Watermark</Text>
          <Text style={styles.buttonSubtext}>
            Automatically detect and decode hidden messages
          </Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={[styles.button, styles.embedButton]}
          onPress={navigateToEmbed}
          disabled={serverStatus !== 'online'}
        >
          <Text style={styles.buttonIcon}>🔒</Text>
          <Text style={styles.buttonText}>Embed Watermark</Text>
          <Text style={styles.buttonSubtext}>
            Hide secret messages in images
          </Text>
        </TouchableOpacity>
      </View>

      <View style={styles.footer}>
        <TouchableOpacity onPress={checkServerStatus} style={styles.refreshButton}>
          <Text style={styles.refreshText}>🔄 Refresh Status</Text>
        </TouchableOpacity>
        
        <Text style={styles.footerText}>
          Advanced computer vision with automatic corner detection
        </Text>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
    padding: 20,
  },
  header: {
    alignItems: 'center',
    marginTop: 40,
    marginBottom: 40,
  },
  title: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#2196F3',
    marginBottom: 5,
  },
  subtitle: {
    fontSize: 18,
    color: '#666',
    marginBottom: 20,
  },
  statusContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 20,
  },
  statusText: {
    fontSize: 16,
    fontWeight: '600',
  },
  spinner: {
    marginLeft: 10,
  },
  infoContainer: {
    backgroundColor: '#e3f2fd',
    padding: 15,
    borderRadius: 10,
    alignItems: 'center',
  },
  infoText: {
    fontSize: 14,
    color: '#1976d2',
    marginBottom: 2,
  },
  buttonsContainer: {
    flex: 1,
    justifyContent: 'center',
    gap: 20,
  },
  button: {
    backgroundColor: '#fff',
    padding: 25,
    borderRadius: 15,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 3.84,
    elevation: 5,
  },
  scanButton: {
    borderLeftWidth: 5,
    borderLeftColor: '#4CAF50',
  },
  embedButton: {
    borderLeftWidth: 5,
    borderLeftColor: '#2196F3',
  },
  buttonIcon: {
    fontSize: 40,
    marginBottom: 10,
  },
  buttonText: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 5,
  },
  buttonSubtext: {
    fontSize: 14,
    color: '#666',
    textAlign: 'center',
  },
  footer: {
    alignItems: 'center',
    marginTop: 20,
  },
  refreshButton: {
    padding: 10,
    marginBottom: 10,
  },
  refreshText: {
    fontSize: 16,
    color: '#2196F3',
  },
  footerText: {
    fontSize: 12,
    color: '#999',
    textAlign: 'center',
  },
});