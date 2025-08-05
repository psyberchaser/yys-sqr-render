// YYS-SQR Mobile Result Screen
import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  Image,
  Alert,
  Linking,
  Share,
} from 'react-native';

export default function ResultScreen({ route, navigation }) {
  const { result, imageUri } = route.params;
  const [showDetails, setShowDetails] = useState(false);

  const handleShare = async () => {
    try {
      const message = `YYS-SQR Scan Result:\n\nWatermark ID: ${result.watermark_id}\nMessage: ${result.secret_message || 'N/A'}\nConfidence: ${result.confidence}\nMethod: ${result.method}`;
      
      await Share.share({
        message: message,
        title: 'YYS-SQR Scan Result',
      });
    } catch (error) {
      console.error('Error sharing:', error);
    }
  };

  const openEtherscan = () => {
    if (result.transaction_hash) {
      const url = `https://sepolia.etherscan.io/tx/${result.transaction_hash}`;
      Linking.openURL(url);
    }
  };

  const openIPFS = () => {
    if (result.ipfs_cid) {
      const url = `https://ipfs.filebase.io/ipfs/${result.ipfs_cid}`;
      Linking.openURL(url);
    }
  };

  const scanAnother = () => {
    navigation.navigate('Scan');
  };

  const goHome = () => {
    navigation.navigate('Home');
  };

  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>
          {result.success ? '✅ Watermark Found!' : '❌ No Watermark'}
        </Text>
      </View>

      {imageUri && (
        <View style={styles.imageContainer}>
          <Image source={{ uri: imageUri }} style={styles.image} />
        </View>
      )}

      {result.success ? (
        <View style={styles.resultContainer}>
          {/* Main Result */}
          <View style={styles.card}>
            <Text style={styles.cardTitle}>
              {result.card ? '🎴 Trading Card Found!' : '📝 Decoded Message'}
            </Text>
            {result.card ? (
              <View>
                <Text style={styles.cardNameText}>{result.card.card_name}</Text>
                {result.card.description && (
                  <Text style={styles.descriptionText}>{result.card.description}</Text>
                )}
                <View style={styles.cardMetaContainer}>
                  {result.card.series && (
                    <Text style={styles.metaText}>📚 Series: {result.card.series}</Text>
                  )}
                  <Text style={styles.metaText}>💎 Rarity: {result.card.rarity || 'Common'}</Text>
                  <Text style={styles.metaText}>🔢 ID: {result.watermark_id}</Text>
                </View>
              </View>
            ) : (
              <Text style={styles.messageText}>
                "{result.secret_message || result.watermark_id}"
              </Text>
            )}
          </View>

          {/* Watermark Details */}
          <View style={styles.card}>
            <Text style={styles.cardTitle}>🔍 Detection Details</Text>
            <View style={styles.detailRow}>
              <Text style={styles.detailLabel}>Watermark ID:</Text>
              <Text style={styles.detailValue}>{result.watermark_id}</Text>
            </View>
            {result.confidence && (
              <View style={styles.detailRow}>
                <Text style={styles.detailLabel}>Confidence:</Text>
                <Text style={styles.detailValue}>
                  {(result.confidence * 100).toFixed(1)}%
                </Text>
              </View>
            )}
            <View style={styles.detailRow}>
              <Text style={styles.detailLabel}>Method:</Text>
              <Text style={styles.detailValue}>{result.method}</Text>
            </View>
            {result.card && (
              <View style={styles.detailRow}>
                <Text style={styles.detailLabel}>Scans:</Text>
                <Text style={styles.detailValue}>{result.card.scan_count} times</Text>
              </View>
            )}
            {result.card && result.card.is_minted && (
              <View style={styles.nftContainer}>
                <Text style={styles.nftText}>
                  🎯 This card is already minted as an NFT!
                </Text>
                <Text style={styles.nftOwnerText}>
                  Owner: {result.card.owner_address?.substring(0, 10)}...
                </Text>
              </View>
            )}
            {result.card && !result.card.is_minted && result.is_first_scan && (
              <View style={styles.claimContainer}>
                <Text style={styles.claimText}>
                  🎉 You're the first to scan this card! You can claim the NFT!
                </Text>
              </View>
            )}
            {result.was_destroyed && (
              <View style={styles.warningContainer}>
                <Text style={styles.warningText}>
                  ⚠️ This was a single-use watermark and has been deleted
                </Text>
              </View>
            )}
          </View>

          {/* Blockchain & IPFS Links */}
          {(result.transaction_hash || result.ipfs_cid) && (
            <View style={styles.card}>
              <Text style={styles.cardTitle}>🔗 Blockchain & Storage</Text>
              
              {result.transaction_hash && (
                <TouchableOpacity 
                  style={styles.linkButton}
                  onPress={openEtherscan}
                >
                  <Text style={styles.linkButtonText}>
                    📊 View on Etherscan
                  </Text>
                </TouchableOpacity>
              )}
              
              {result.ipfs_cid && (
                <TouchableOpacity 
                  style={styles.linkButton}
                  onPress={openIPFS}
                >
                  <Text style={styles.linkButtonText}>
                    🌐 View on IPFS
                  </Text>
                </TouchableOpacity>
              )}
            </View>
          )}

          {/* Advanced Details */}
          <TouchableOpacity 
            style={styles.card}
            onPress={() => setShowDetails(!showDetails)}
          >
            <Text style={styles.cardTitle}>
              🔧 Advanced Details {showDetails ? '▼' : '▶'}
            </Text>
            
            {showDetails && (
              <View style={styles.advancedDetails}>
                <Text style={styles.detailText}>
                  Timestamp: {new Date(result.timestamp).toLocaleString()}
                </Text>
                <Text style={styles.detailText}>
                  API Version: {result.api_version}
                </Text>
                {result.corners && (
                  <Text style={styles.detailText}>
                    Corners Detected: {result.corners.length} points
                  </Text>
                )}
              </View>
            )}
          </TouchableOpacity>
        </View>
      ) : (
        <View style={styles.errorContainer}>
          <Text style={styles.errorTitle}>No Watermark Detected</Text>
          <Text style={styles.errorMessage}>
            {result.error || 'Could not find a watermark in this image.'}
          </Text>
          
          <View style={styles.tipsContainer}>
            <Text style={styles.tipsTitle}>💡 Tips for better scanning:</Text>
            <Text style={styles.tipText}>• Ensure good lighting</Text>
            <Text style={styles.tipText}>• Hold camera steady</Text>
            <Text style={styles.tipText}>• Make sure entire image is visible</Text>
            <Text style={styles.tipText}>• Try different angles</Text>
          </View>
        </View>
      )}

      {/* Action Buttons */}
      <View style={styles.actionButtons}>
        <TouchableOpacity style={styles.primaryButton} onPress={scanAnother}>
          <Text style={styles.primaryButtonText}>📷 Scan Another</Text>
        </TouchableOpacity>
        
        {result.success && (
          <TouchableOpacity style={styles.secondaryButton} onPress={handleShare}>
            <Text style={styles.secondaryButtonText}>📤 Share Result</Text>
          </TouchableOpacity>
        )}
        
        <TouchableOpacity style={styles.secondaryButton} onPress={goHome}>
          <Text style={styles.secondaryButtonText}>🏠 Home</Text>
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
  imageContainer: {
    alignItems: 'center',
    padding: 20,
  },
  image: {
    width: 200,
    height: 200,
    borderRadius: 10,
    resizeMode: 'cover',
  },
  resultContainer: {
    padding: 20,
  },
  card: {
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
  cardTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 10,
  },
  messageText: {
    fontSize: 20,
    color: '#2196F3',
    fontWeight: '600',
    textAlign: 'center',
    padding: 15,
    backgroundColor: '#e3f2fd',
    borderRadius: 8,
  },
  cardNameText: {
    fontSize: 24,
    color: '#2196F3',
    fontWeight: 'bold',
    textAlign: 'center',
    marginBottom: 10,
  },
  descriptionText: {
    fontSize: 16,
    color: '#666',
    textAlign: 'center',
    marginBottom: 15,
    fontStyle: 'italic',
  },
  cardMetaContainer: {
    backgroundColor: '#f8f9fa',
    padding: 12,
    borderRadius: 8,
  },
  metaText: {
    fontSize: 14,
    color: '#333',
    marginBottom: 4,
  },
  nftContainer: {
    backgroundColor: '#e8f5e8',
    padding: 12,
    borderRadius: 8,
    marginTop: 10,
  },
  nftText: {
    color: '#2e7d32',
    fontSize: 14,
    fontWeight: '600',
    textAlign: 'center',
  },
  nftOwnerText: {
    color: '#2e7d32',
    fontSize: 12,
    textAlign: 'center',
    marginTop: 4,
  },
  claimContainer: {
    backgroundColor: '#fff3e0',
    padding: 12,
    borderRadius: 8,
    marginTop: 10,
  },
  claimText: {
    color: '#f57c00',
    fontSize: 14,
    fontWeight: '600',
    textAlign: 'center',
  },
  detailRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 8,
  },
  detailLabel: {
    fontSize: 16,
    color: '#666',
    fontWeight: '500',
  },
  detailValue: {
    fontSize: 16,
    color: '#333',
    fontWeight: '600',
  },
  warningContainer: {
    backgroundColor: '#fff3cd',
    padding: 10,
    borderRadius: 5,
    marginTop: 10,
  },
  warningText: {
    color: '#856404',
    fontSize: 14,
    textAlign: 'center',
  },
  linkButton: {
    backgroundColor: '#2196F3',
    padding: 12,
    borderRadius: 8,
    marginBottom: 8,
  },
  linkButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
    textAlign: 'center',
  },
  advancedDetails: {
    marginTop: 10,
    paddingTop: 10,
    borderTopWidth: 1,
    borderTopColor: '#eee',
  },
  detailText: {
    fontSize: 14,
    color: '#666',
    marginBottom: 5,
  },
  errorContainer: {
    padding: 20,
    alignItems: 'center',
  },
  errorTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#f44336',
    marginBottom: 10,
  },
  errorMessage: {
    fontSize: 16,
    color: '#666',
    textAlign: 'center',
    marginBottom: 20,
  },
  tipsContainer: {
    backgroundColor: '#fff',
    padding: 20,
    borderRadius: 10,
    width: '100%',
  },
  tipsTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 10,
  },
  tipText: {
    fontSize: 14,
    color: '#666',
    marginBottom: 5,
  },
  actionButtons: {
    padding: 20,
    gap: 10,
  },
  primaryButton: {
    backgroundColor: '#4CAF50',
    padding: 15,
    borderRadius: 10,
    alignItems: 'center',
  },
  primaryButtonText: {
    color: '#fff',
    fontSize: 18,
    fontWeight: 'bold',
  },
  secondaryButton: {
    backgroundColor: '#2196F3',
    padding: 15,
    borderRadius: 10,
    alignItems: 'center',
  },
  secondaryButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
});