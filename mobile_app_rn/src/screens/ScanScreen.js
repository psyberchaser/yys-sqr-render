// YYS-SQR Mobile Scanner Screen with Auto Corner Detection
import React, { useState, useEffect, useRef } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Alert,
  ActivityIndicator,
  Dimensions,
} from 'react-native';
import { Camera } from 'expo-camera';
import * as MediaLibrary from 'expo-media-library';
import * as FileSystem from 'expo-file-system';
import { YYSApiService } from '../services/YYSApiService';

const { width, height } = Dimensions.get('window');

export default function ScanScreen({ navigation }) {
  const [hasPermission, setHasPermission] = useState(null);
  const [isScanning, setIsScanning] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [autoScanEnabled, setAutoScanEnabled] = useState(true);
  const cameraRef = useRef(null);
  const scanTimeoutRef = useRef(null);

  useEffect(() => {
    (async () => {
      const { status } = await Camera.requestCameraPermissionsAsync();
      setHasPermission(status === 'granted');
    })();
  }, []);

  const takePicture = async () => {
    if (cameraRef.current && !isProcessing) {
      setIsProcessing(true);
      try {
        const photo = await cameraRef.current.takePictureAsync({
          quality: 0.8,
          base64: true,
        });
        
        await processImage(photo);
      } catch (error) {
        console.error('Error taking picture:', error);
        Alert.alert('Error', 'Failed to take picture');
        setIsProcessing(false);
      }
    }
  };

  const processImage = async (photo) => {
    try {
      // Convert to base64 if needed
      const base64Image = photo.base64;
      
      // Call our Python backend API for automatic corner detection and decoding
      const result = await YYSApiService.scanWatermark(base64Image);
      
      if (result.success) {
        // Navigate to result screen with the decoded data
        navigation.navigate('Result', { 
          result: result,
          imageUri: photo.uri 
        });
      } else {
        Alert.alert(
          'No Watermark Found', 
          result.error || 'Could not detect watermark in image. Try:\n• Better lighting\n• Clearer photo\n• Ensure entire watermarked image is visible'
        );
      }
    } catch (error) {
      console.error('Error processing image:', error);
      Alert.alert('Error', 'Failed to process image. Check your connection.');
    } finally {
      setIsProcessing(false);
    }
  };

  const startAutoScan = () => {
    if (autoScanEnabled && !isProcessing) {
      setIsScanning(true);
      // Auto-scan every 2 seconds
      scanTimeoutRef.current = setTimeout(() => {
        takePicture();
        setIsScanning(false);
      }, 2000);
    }
  };

  const stopAutoScan = () => {
    setIsScanning(false);
    if (scanTimeoutRef.current) {
      clearTimeout(scanTimeoutRef.current);
    }
  };

  const toggleAutoScan = () => {
    if (autoScanEnabled) {
      stopAutoScan();
    } else {
      startAutoScan();
    }
    setAutoScanEnabled(!autoScanEnabled);
  };

  if (hasPermission === null) {
    return (
      <View style={styles.container}>
        <Text>Requesting camera permission...</Text>
      </View>
    );
  }

  if (hasPermission === false) {
    return (
      <View style={styles.container}>
        <Text style={styles.text}>No access to camera</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <Camera 
        style={styles.camera} 
        type={Camera.Constants.Type.back}
        ref={cameraRef}
        autoFocus={Camera.Constants.AutoFocus.on}
      >
        <View style={styles.overlay}>
          {/* Scanning frame overlay */}
          <View style={styles.scanFrame}>
            <View style={[styles.corner, styles.topLeft]} />
            <View style={[styles.corner, styles.topRight]} />
            <View style={[styles.corner, styles.bottomLeft]} />
            <View style={[styles.corner, styles.bottomRight]} />
          </View>
          
          {/* Instructions */}
          <View style={styles.instructionsContainer}>
            <Text style={styles.instructions}>
              {isProcessing 
                ? '🔍 Processing image...' 
                : isScanning 
                ? '📸 Auto-scanning...' 
                : 'Point camera at watermarked image'
              }
            </Text>
          </View>

          {/* Controls */}
          <View style={styles.controls}>
            <TouchableOpacity
              style={[styles.button, styles.autoScanButton, autoScanEnabled && styles.activeButton]}
              onPress={toggleAutoScan}
              disabled={isProcessing}
            >
              <Text style={styles.buttonText}>
                {autoScanEnabled ? '🔄 Auto Scan ON' : '⏸️ Auto Scan OFF'}
              </Text>
            </TouchableOpacity>

            <TouchableOpacity
              style={[styles.button, styles.captureButton]}
              onPress={takePicture}
              disabled={isProcessing}
            >
              {isProcessing ? (
                <ActivityIndicator color="#fff" />
              ) : (
                <Text style={styles.buttonText}>📷 Scan Now</Text>
              )}
            </TouchableOpacity>
          </View>
        </View>
      </Camera>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#000',
  },
  camera: {
    flex: 1,
  },
  overlay: {
    flex: 1,
    backgroundColor: 'transparent',
    justifyContent: 'space-between',
  },
  scanFrame: {
    position: 'absolute',
    top: height * 0.2,
    left: width * 0.1,
    width: width * 0.8,
    height: width * 0.8,
    borderWidth: 2,
    borderColor: '#00ff00',
    borderRadius: 10,
  },
  corner: {
    position: 'absolute',
    width: 20,
    height: 20,
    borderColor: '#00ff00',
    borderWidth: 3,
  },
  topLeft: {
    top: -3,
    left: -3,
    borderRightWidth: 0,
    borderBottomWidth: 0,
  },
  topRight: {
    top: -3,
    right: -3,
    borderLeftWidth: 0,
    borderBottomWidth: 0,
  },
  bottomLeft: {
    bottom: -3,
    left: -3,
    borderRightWidth: 0,
    borderTopWidth: 0,
  },
  bottomRight: {
    bottom: -3,
    right: -3,
    borderLeftWidth: 0,
    borderTopWidth: 0,
  },
  instructionsContainer: {
    position: 'absolute',
    top: height * 0.1,
    left: 0,
    right: 0,
    alignItems: 'center',
  },
  instructions: {
    color: '#fff',
    fontSize: 16,
    textAlign: 'center',
    backgroundColor: 'rgba(0,0,0,0.7)',
    padding: 10,
    borderRadius: 5,
  },
  controls: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    alignItems: 'center',
    paddingBottom: 50,
    paddingHorizontal: 20,
  },
  button: {
    backgroundColor: 'rgba(0,0,0,0.7)',
    paddingHorizontal: 20,
    paddingVertical: 15,
    borderRadius: 25,
    minWidth: 120,
    alignItems: 'center',
  },
  activeButton: {
    backgroundColor: '#2196F3',
  },
  captureButton: {
    backgroundColor: '#ff4444',
  },
  autoScanButton: {
    backgroundColor: '#4CAF50',
  },
  buttonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  text: {
    fontSize: 18,
    color: '#fff',
    textAlign: 'center',
  },
});