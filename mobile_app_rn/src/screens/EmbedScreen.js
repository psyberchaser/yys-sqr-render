// YYS-SQR Mobile Embed Screen
import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  TextInput,
  Alert,
  ActivityIndicator,
  Image,
  ScrollView,
} from 'react-native';
import * as ImagePicker from 'expo-image-picker';
import * as FileSystem from 'expo-file-system';
import * as MediaLibrary from 'expo-media-library';
import YYSApiService from '../services/YYSApiService';

export default function EmbedScreen({ navigation }) {
  const [selectedImage, setSelectedImage] = useState(null);
  const [message, setMessage] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [result, setResult] = useState(null);

  const pickImage = async () => {
    try {
      const result = await ImagePicker.launchImageLibraryAsync({
        mediaTypes: ImagePicker.MediaTypeOptions.Images,
        allowsEditing: true,
        aspect: [1, 1],
        quality: 0.8,
        base64: true,
      });

      if (!result.canceled) {
        setSelectedImage(result.assets[0]);
        setResult(null); // Clear previous result
      }
    } catch (error) {
      console.error('Error picking image:', error);
      Alert.alert('Error', 'Failed to pick image');
    }
  };

  const takePhoto = async () => {
    try {
      const { status } = await ImagePicker.requestCameraPermissionsAsync();
      if (status !== 'granted') {
        Alert.alert('Permission needed', 'Camera permission is required to take photos');
        return;
      }

      const result = await ImagePicker.launchCameraAsync({
        allowsEditing: true,
        aspect: [1, 1],
        quality: 0.8,
        base64: true,
      });

      if (!result.canceled) {
        setSelectedImage(result.assets[0]);
        setResult(null); // Clear previous result
      }
    } catch (error) {
      console.error('Error taking photo:', error);
      Alert.alert('Error', 'Failed to take photo');
    }
  };

  const embedWatermark = async () => {
    if (!selectedImage) {
      Alert.alert('No Image', 'Please select an image first');
      return;
    }

    if (!message.trim()) {
      Alert.alert('No Message', 'Please enter a message to embed');
      return;
    }

    if (message.length > 5) {
      Alert.alert('Message Too Long', 'Message must be 5 characters or less');
      return;
    }

    setIsProcessing(true);

    try {
      const response = await YYSApiService.embedWatermark(
        selectedImage.base64,
        message.trim()
      );

      if (response.success) {
        setResult(response);
        Alert.alert(
          'Success!', 
          `Watermark embedded successfully!\n\nMessage: "${response.message}"`
        );
      } else {
        Alert.alert('Error', response.error || 'Failed to embed watermark');
      }
    } catch (error) {
      console.error('Error embedding watermark:', error);
      Alert.alert('Error', 'Failed to embed watermark. Check your connection.');
    } finally {
      setIsProcessing(false);
    }
  };

  const saveWatermarkedImage = async () => {
    if (!result || !result.watermarked_image) {
      Alert.alert('Error', 'No watermarked image to save');
      return;
    }

    try {
      // Request media library permissions
      const { status } = await ImagePicker.requestMediaLibraryPermissionsAsync();
      if (status !== 'granted') {
        Alert.alert('Permission needed', 'Media library permission is required to save images');
        return;
      }

      // Create file path
      const filename = `yys_sqr_watermarked_${Date.now()}.png`;
      const fileUri = FileSystem.documentDirectory + filename;

      // Write base64 to file
      await FileSystem.writeAsStringAsync(fileUri, result.watermarked_image, {
        encoding: FileSystem.EncodingType.Base64,
      });

      // Save to media library
      const asset = await MediaLibrary.createAssetAsync(fileUri);
      
      Alert.alert(
        'Saved!', 
        `Watermarked image saved to your photo library.\n\nFilename: ${filename}`
      );
    } catch (error) {
      console.error('Error saving image:', error);
      Alert.alert('Error', 'Failed to save image to photo library');
    }
  };

  const reset = () => {
    setSelectedImage(null);
    setMessage('');
    setResult(null);
  };

  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>Embed Watermark</Text>
        <Text style={styles.subtitle}>Hide secret messages in images</Text>
      </View>

      {/* Step 1: Select Image */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>📷 Step 1: Select Image</Text>
        
        <View style={styles.imagePickerContainer}>
          <TouchableOpacity style={styles.imagePickerButton} onPress={pickImage}>
            <Text style={styles.buttonText}>📁 Choose from Library</Text>
          </TouchableOpacity>
          
          <TouchableOpacity style={styles.imagePickerButton} onPress={takePhoto}>
            <Text style={styles.buttonText}>📸 Take Photo</Text>
          </TouchableOpacity>
        </View>

        {selectedImage && (
          <View style={styles.selectedImageContainer}>
            <Image source={{ uri: selectedImage.uri }} style={styles.selectedImage} />
            <Text style={styles.imageInfo}>
              Selected: {selectedImage.width}x{selectedImage.height}
            </Text>
          </View>
        )}
      </View>

      {/* Step 2: Enter Message */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>✏️ Step 2: Enter Message (Max 5 chars)</Text>
        
        <TextInput
          style={styles.messageInput}
          value={message}
          onChangeText={setMessage}
          placeholder="Enter secret message..."
          maxLength={5}
          autoCapitalize="characters"
        />
        
        <Text style={styles.characterCount}>
          {message.length}/5 characters
        </Text>
      </View>

      {/* Step 3: Embed */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>🔒 Step 3: Embed Watermark</Text>
        
        <TouchableOpacity
          style={[
            styles.embedButton,
            (!selectedImage || !message.trim() || isProcessing) && styles.disabledButton
          ]}
          onPress={embedWatermark}
          disabled={!selectedImage || !message.trim() || isProcessing}
        >
          {isProcessing ? (
            <ActivityIndicator color="#fff" />
          ) : (
            <Text style={styles.embedButtonText}>🔒 Embed Watermark</Text>
          )}
        </TouchableOpacity>
      </View>

      {/* Results */}
      {result && (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>✅ Success!</Text>
          
          <View style={styles.resultContainer}>
            <Text style={styles.resultText}>
              Message "{result.message}" embedded successfully!
            </Text>
            
            <Text style={styles.resultDetails}>
              Timestamp: {new Date(result.timestamp).toLocaleString()}
            </Text>

            {result.watermarked_image && (
              <View style={styles.watermarkedImageContainer}>
                <Image 
                  source={{ uri: `data:image/png;base64,${result.watermarked_image}` }} 
                  style={styles.watermarkedImage} 
                />
                
                <TouchableOpacity
                  style={styles.saveButton}
                  onPress={saveWatermarkedImage}
                >
                  <Text style={styles.saveButtonText}>💾 Save to Photos</Text>
                </TouchableOpacity>
              </View>
            )}
          </View>
        </View>
      )}

      {/* Action Buttons */}
      <View style={styles.actionButtons}>
        <TouchableOpacity style={styles.resetButton} onPress={reset}>
          <Text style={styles.resetButtonText}>🔄 Start Over</Text>
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
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
  },
  subtitle: {
    fontSize: 16,
    color: '#666',
    marginTop: 5,
  },
  section: {
    margin: 20,
    backgroundColor: '#fff',
    padding: 20,
    borderRadius: 10,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 3.84,
    elevation: 5,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 15,
  },
  imagePickerContainer: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    marginBottom: 15,
  },
  imagePickerButton: {
    backgroundColor: '#2196F3',
    padding: 15,
    borderRadius: 8,
    flex: 0.45,
  },
  buttonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
    textAlign: 'center',
  },
  selectedImageContainer: {
    alignItems: 'center',
    marginTop: 15,
  },
  selectedImage: {
    width: 200,
    height: 200,
    borderRadius: 10,
    resizeMode: 'cover',
  },
  imageInfo: {
    fontSize: 14,
    color: '#666',
    marginTop: 10,
  },
  messageInput: {
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 8,
    padding: 15,
    fontSize: 18,
    textAlign: 'center',
    backgroundColor: '#f9f9f9',
  },
  characterCount: {
    fontSize: 14,
    color: '#666',
    textAlign: 'right',
    marginTop: 5,
  },
  embedButton: {
    backgroundColor: '#4CAF50',
    padding: 18,
    borderRadius: 10,
    alignItems: 'center',
  },
  disabledButton: {
    backgroundColor: '#ccc',
  },
  embedButtonText: {
    color: '#fff',
    fontSize: 18,
    fontWeight: 'bold',
  },
  resultContainer: {
    alignItems: 'center',
  },
  resultText: {
    fontSize: 18,
    color: '#4CAF50',
    fontWeight: '600',
    textAlign: 'center',
    marginBottom: 10,
  },
  resultDetails: {
    fontSize: 14,
    color: '#666',
    marginBottom: 20,
  },
  watermarkedImageContainer: {
    alignItems: 'center',
  },
  watermarkedImage: {
    width: 200,
    height: 200,
    borderRadius: 10,
    resizeMode: 'cover',
    marginBottom: 15,
  },
  saveButton: {
    backgroundColor: '#FF9800',
    padding: 12,
    borderRadius: 8,
    minWidth: 150,
  },
  saveButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
    textAlign: 'center',
  },
  actionButtons: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    padding: 20,
    gap: 10,
  },
  resetButton: {
    backgroundColor: '#f44336',
    padding: 15,
    borderRadius: 10,
    flex: 0.45,
  },
  resetButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
    textAlign: 'center',
  },
  homeButton: {
    backgroundColor: '#2196F3',
    padding: 15,
    borderRadius: 10,
    flex: 0.45,
  },
  homeButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
    textAlign: 'center',
  },
});