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
import { CameraView, useCameraPermissions } from 'expo-camera';
import * as MediaLibrary from 'expo-media-library';
import * as FileSystem from 'expo-file-system';
import * as ImageManipulator from 'expo-image-manipulator';
import YYSApiService from '../services/YYSApiService';

const { width, height } = Dimensions.get('window');

export default function ScanScreen({ navigation }) {
  const [permission, requestPermission] = useCameraPermissions();
  const [isScanning, setIsScanning] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [autoScanEnabled, setAutoScanEnabled] = useState(true);
  const cameraRef = useRef(null);
  const scanTimeoutRef = useRef(null);

  useEffect(() => {
    if (!permission) {
      requestPermission();
    }
  }, [permission]);

  const takePicture = async () => {
    if (cameraRef.current && !isProcessing) {
      setIsProcessing(true);
      try {
        const photo = await cameraRef.current.takePictureAsync({
          quality: 0.8, // Better quality for watermark detection
          base64: true,
          skipProcessing: false,
          exif: false,
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
      // Debug: Log original image size
      console.log(`Original image size: ${(photo.base64.length * 0.75 / 1024 / 1024).toFixed(2)} MB`);
      console.log(`Original dimensions: ${photo.width}x${photo.height}`);
      
      // Try multiple image sizes for better detection success
      const imageSizes = [
        { width: 1024, compress: 0.8 },
        { width: 800, compress: 0.7 },
        { width: 600, compress: 0.6 }
      ];
      
      for (const { width: targetWidth, compress } of imageSizes) {
        try {
          console.log(`Trying with width: ${targetWidth}px, compression: ${compress}`);
          
          // Resize image for processing
          const resizedImage = await ImageManipulator.manipulateAsync(
            photo.uri,
            [{ resize: { width: targetWidth } }],
            { 
              compress: compress, 
              format: ImageManipulator.SaveFormat.JPEG,
              base64: true 
            }
          );
          
          console.log(`Resized image size: ${(resizedImage.base64.length * 0.75 / 1024 / 1024).toFixed(2)} MB`);
          console.log(`Resized dimensions: ${resizedImage.width}x${resizedImage.height}`);
          
          // Call our Python backend API for automatic corner detection and decoding
          console.log('Sending resized image to API for scanning...');
          console.log('API URL:', YYSApiService.client.defaults.baseURL);
          
          const result = await YYSApiService.scanWatermark(resizedImage.base64);
          console.log('Full API response:', JSON.stringify(result, null, 2));
          
          if (result.success) {
            // Success - navigate to result
            navigation.navigate('Result', { 
              result: result,
              imageUri: photo.uri 
            });
            return; // Exit function on success
          } else {
            console.log(`Failed with size ${targetWidth}:`, result.error);
            // Continue to next size
          }
        } catch (sizeError) {
          console.log(`Error with size ${targetWidth}:`, sizeError.message);
          // Continue to next size
        }
      }
      
      // If we get here, all sizes failed
      console.log('All image sizes failed');
      Alert.alert(
        'No Watermark Found', 
        'Could not detect watermark with automatic scanning. Try:\n• Better lighting\n• Clearer photo\n• Use Manual Scan instead'
      );

    } catch (error) {
      console.error('Error processing image:', error);
      Alert.alert(
        'Processing Error', 
        `Failed to process image: ${error.message}\n\nTry:\n• Check internet connection\n• Use Manual Scan instead\n• Restart the app`
      );
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

  if (!permission) {
    return (
      <View style={styles.container}>
        <Text>Requesting camera permission...</Text>
      </View>
    );
  }

  if (!permission.granted) {
    return (
      <View style={styles.container}>
        <Text style={styles.text}>No access to camera</Text>
        <TouchableOpacity style={styles.button} onPress={requestPermission}>
          <Text style={styles.buttonText}>Grant Permission</Text>
        </TouchableOpacity>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <CameraView 
        style={styles.camera} 
        facing="back"
        ref={cameraRef}
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
            
            <TouchableOpacity
              style={[styles.button, styles.manualButton]}
              onPress={() => navigation.navigate('ManualScan')}
              disabled={isProcessing}
            >
              <Text style={styles.buttonText}>✏️ Manual</Text>
            </TouchableOpacity>
          </View>
        </View>
      </CameraView>
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
    paddingHorizontal: 10,
  },
  button: {
    backgroundColor: 'rgba(0,0,0,0.7)',
    paddingHorizontal: 15,
    paddingVertical: 12,
    borderRadius: 20,
    minWidth: 100,
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
  manualButton: {
    backgroundColor: '#FF9800',
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