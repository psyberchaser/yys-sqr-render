// Manual Corner Selection Screen - Like Desktop App
import React, { useState, useRef } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Alert,
  ActivityIndicator,
  Dimensions,
  Image,
} from 'react-native';
import * as ImagePicker from 'expo-image-picker';
import * as ImageManipulator from 'expo-image-manipulator';
import YYSApiService from '../services/YYSApiService';

const { width, height } = Dimensions.get('window');

export default function ManualScanScreen({ navigation }) {
  const [selectedImage, setSelectedImage] = useState(null);
  const [corners, setCorners] = useState([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [imageSize, setImageSize] = useState({ width: 0, height: 0 });

  const pickImage = async () => {
    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ImagePicker.MediaType.Images,
      allowsEditing: false,
      quality: 0.8,
      base64: true,
    });

    if (!result.canceled) {
      const image = result.assets[0];
      setSelectedImage(image);
      setCorners([]);
      
      // Get image dimensions for coordinate scaling
      Image.getSize(image.uri, (w, h) => {
        setImageSize({ width: w, height: h });
      });
    }
  };

  const handleImagePress = (event) => {
    if (corners.length >= 4) {
      Alert.alert('Info', 'All 4 corners selected. Tap "Scan Watermark" to process.');
      return;
    }

    const { locationX, locationY } = event.nativeEvent;
    const newCorner = { x: locationX, y: locationY };
    setCorners([...corners, newCorner]);
  };

  const resetCorners = () => {
    setCorners([]);
  };

  const scanWatermark = async () => {
    if (corners.length !== 4) {
      Alert.alert('Error', 'Please select exactly 4 corners first.');
      return;
    }

    if (!selectedImage) {
      Alert.alert('Error', 'Please select an image first.');
      return;
    }

    setIsProcessing(true);

    try {
      // Resize image for processing
      const resizedImage = await ImageManipulator.manipulateAsync(
        selectedImage.uri,
        [{ resize: { width: 800 } }],
        { 
          compress: 0.5, 
          format: ImageManipulator.SaveFormat.JPEG,
          base64: true 
        }
      );

      // Scale corners to match resized image
      const scaleX = resizedImage.width / imageSize.width;
      const scaleY = resizedImage.height / imageSize.height;
      
      const scaledCorners = corners.map(corner => [
        corner.x * scaleX,
        corner.y * scaleY
      ]);

      console.log('Sending manual corners:', scaledCorners);
      console.log('Image size:', resizedImage.width, 'x', resizedImage.height);

      // Send to API with manual corners
      const result = await YYSApiService.scanWatermarkManual(resizedImage.base64, scaledCorners);
      
      if (result.success) {
        navigation.navigate('Result', { 
          result: result,
          imageUri: selectedImage.uri 
        });
      } else {
        Alert.alert(
          'No Watermark Found', 
          result.error || 'Could not decode watermark. Check corner selection.'
        );
      }
    } catch (error) {
      console.error('Error processing image:', error);
      Alert.alert('Error', 'Failed to process image. Check your connection.');
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Manual Corner Selection</Text>
      <Text style={styles.subtitle}>
        1. Select an image{'\n'}
        2. Tap the 4 corners of the watermarked area{'\n'}
        3. Tap "Scan Watermark"
      </Text>

      {!selectedImage ? (
        <View style={styles.placeholderContainer}>
          <TouchableOpacity style={styles.button} onPress={pickImage}>
            <Text style={styles.buttonText}>Select Image</Text>
          </TouchableOpacity>
        </View>
      ) : (
        <View style={styles.imageContainer}>
          <TouchableOpacity onPress={handleImagePress} activeOpacity={1}>
            <Image 
              source={{ uri: selectedImage.uri }} 
              style={styles.image}
              resizeMode="contain"
            />
            
            {/* Render corner markers */}
            {corners.map((corner, index) => (
              <View
                key={index}
                style={[
                  styles.cornerMarker,
                  {
                    left: corner.x - 10,
                    top: corner.y - 10,
                  }
                ]}
              >
                <Text style={styles.cornerNumber}>{index + 1}</Text>
              </View>
            ))}
          </TouchableOpacity>

          <View style={styles.controlsContainer}>
            <Text style={styles.cornerCount}>
              Corners selected: {corners.length}/4
            </Text>
            
            <View style={styles.buttonRow}>
              <TouchableOpacity 
                style={[styles.button, styles.secondaryButton]} 
                onPress={resetCorners}
              >
                <Text style={styles.buttonText}>Reset Corners</Text>
              </TouchableOpacity>
              
              <TouchableOpacity 
                style={[styles.button, styles.secondaryButton]} 
                onPress={pickImage}
              >
                <Text style={styles.buttonText}>New Image</Text>
              </TouchableOpacity>
            </View>

            <TouchableOpacity
              style={[
                styles.button,
                styles.scanButton,
                (corners.length !== 4 || isProcessing) && styles.disabledButton
              ]}
              onPress={scanWatermark}
              disabled={corners.length !== 4 || isProcessing}
            >
              {isProcessing ? (
                <ActivityIndicator color="#fff" />
              ) : (
                <Text style={styles.buttonText}>
                  Scan Watermark ({corners.length}/4)
                </Text>
              )}
            </TouchableOpacity>
          </View>
        </View>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
    padding: 20,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    textAlign: 'center',
    marginBottom: 10,
    color: '#333',
  },
  subtitle: {
    fontSize: 16,
    textAlign: 'center',
    marginBottom: 20,
    color: '#666',
    lineHeight: 22,
  },
  placeholderContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  imageContainer: {
    flex: 1,
  },
  image: {
    width: width - 40,
    height: height * 0.5,
    backgroundColor: '#eee',
  },
  cornerMarker: {
    position: 'absolute',
    width: 20,
    height: 20,
    borderRadius: 10,
    backgroundColor: '#2196F3',
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 2,
    borderColor: '#fff',
  },
  cornerNumber: {
    color: '#fff',
    fontSize: 12,
    fontWeight: 'bold',
  },
  controlsContainer: {
    marginTop: 20,
  },
  cornerCount: {
    fontSize: 18,
    textAlign: 'center',
    marginBottom: 15,
    color: '#333',
    fontWeight: '500',
  },
  buttonRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 15,
  },
  button: {
    backgroundColor: '#2196F3',
    padding: 15,
    borderRadius: 8,
    alignItems: 'center',
    minWidth: 120,
  },
  secondaryButton: {
    backgroundColor: '#757575',
    flex: 0.45,
  },
  scanButton: {
    backgroundColor: '#4CAF50',
    marginTop: 10,
  },
  disabledButton: {
    backgroundColor: '#ccc',
  },
  buttonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
});