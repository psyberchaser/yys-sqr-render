# YYS-SQR IPFS & NFT Collection Improvements

## Overview
This document details the comprehensive improvements made to fix IPFS integration, NFT collection display, and UI state management in the YYS-SQR system.

## Issues Identified

### 1. NFT Collection Not Displaying
- **Problem**: Mobile app wasn't showing claimed NFTs in wallet
- **Root Cause**: Missing API endpoint and UI implementation

### 2. Broken IPFS Links
- **Problem**: Smart contract showed non-working IPFS links
- **Root Cause**: Web app wasn't uploading images to IPFS, using placeholder URLs

### 3. UI State Issues
- **Problem**: Claim button remained visible after successful NFT claim
- **Root Cause**: Missing state management for claim success

### 4. Missing Image Display
- **Problem**: NFTs had no visual representation in mobile app
- **Root Cause**: No image URLs or IPFS integration

## Solutions Implemented

### 1. IPFS Upload Integration

#### Files Modified:
- `yys-sqr/webapp_server.py`
- `yys-sqr/requirements-webapp.txt`

#### Changes Made:

**Added IPFS Upload Function** (Lines 89-125):
```python
def upload_to_ipfs(file_path, object_name=None):
    """Upload a file to Filebase and return the IPFS CID"""
    # S3 client configuration for Filebase
    s3_client = boto3.client(
        's3',
        endpoint_url='https://s3.filebase.com',
        aws_access_key_id=FILEBASE_ACCESS_KEY,
        aws_secret_access_key=FILEBASE_SECRET_KEY,
        region_name='us-east-1'
    )
    # Upload and retrieve IPFS CID from metadata
```

**Added Configuration Variables** (Lines 82-86):
```python
FILEBASE_ACCESS_KEY = os.environ.get('FILEBASE_ACCESS_KEY', 'A8F8E8F8E8F8E8F8E8F8')
FILEBASE_SECRET_KEY = os.environ.get('FILEBASE_SECRET_KEY', 'secret-key-here')
FILEBASE_BUCKET_NAME = os.environ.get('FILEBASE_BUCKET_NAME', 'yys-sqr-images')
```

**Enhanced Card Creation** (Lines 250-295):
- Upload original image to IPFS
- Upload watermarked image to IPFS
- Store both IPFS CIDs in database
- Set proper metadata_uri for smart contract

### 2. Database Schema Enhancement

#### Files Modified:
- `yys-sqr/database.py`

#### Changes Made:

**Added IPFS Fields** (Lines 22-23):
```python
ipfs_cid = db.Column(db.String(100), nullable=True)  # Original image IPFS CID
watermarked_ipfs_cid = db.Column(db.String(100), nullable=True)  # Watermarked image IPFS CID
```

**Updated to_dict() Method** (Lines 40-41):
```python
'ipfs_cid': self.ipfs_cid,
'watermarked_ipfs_cid': self.watermarked_ipfs_cid,
```

### 3. NFT Collection API

#### Files Modified:
- `yys-sqr/webapp_server.py`

#### Changes Made:

**New API Endpoint** (Lines 700-735):
```python
@app.route('/api/wallet/<wallet_address>/nfts')
def get_user_nfts(wallet_address):
    """Get NFTs owned by a specific wallet"""
    # Query database for owned cards
    # Return NFT data with IPFS links
```

**Enhanced NFT Data Response**:
- Added `ipfs_cid` and `watermarked_ipfs_cid`
- Added `imageUrl` and `watermarkedImageUrl` with Pinata gateway
- Included all necessary metadata for mobile display

### 4. Mobile App Enhancements

#### Files Modified:
- `yys-sqr/mobile_app_rn/src/screens/WalletScreen.js`
- `yys-sqr/mobile_app_rn/src/screens/ResultScreen.js`
- `yys-sqr/mobile_app_rn/src/services/YYSApiService.js`

#### WalletScreen Changes:

**Added State Management** (Lines 22-23):
```javascript
const [userNFTs, setUserNFTs] = useState([]);
const [loadingNFTs, setLoadingNFTs] = useState(false);
```

**Added NFT Fetching Function** (Lines 95-107):
```javascript
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
```

**Enhanced NFT Display UI** (Lines 170-200):
- Added image thumbnails for each NFT
- Improved layout with flexbox design
- Added "View Image" and "Etherscan" buttons
- Better visual hierarchy and spacing

#### ResultScreen Changes:

**Fixed Claim State Management** (Lines 21-22):
```javascript
const [nftClaimed, setNftClaimed] = useState(false);
const [claimResult, setClaimResult] = useState(null);
```

**Enhanced Claim Success UI** (Lines 195-215):
- Success container with transaction details
- Token ID display
- Direct Etherscan link button
- Proper state transitions

**Improved IPFS Gateway** (Line 44):
```javascript
const url = `https://gateway.pinata.cloud/ipfs/${result.ipfs_cid}`;
```

#### API Service Enhancement:

**Added NFT Fetching Method** (Lines 172-180):
```javascript
async getUserNFTs(walletAddress) {
  try {
    const response = await this.client.get(`/wallet/${walletAddress}/nfts`);
    return response.data;
  } catch (error) {
    console.error('API Error - getUserNFTs:', error);
    throw new Error(error.response?.data?.error || 'Network error');
  }
}
```

### 5. Smart Contract Integration

#### Files Referenced:
- `yys-sqr/contracts/contracts/YYSSQRCards.sol`

#### How It Works:

**NFT Minting Flow**:
1. Server calls `mintCard(address, watermarkId, metadataURI)`
2. Contract stores `metadataURI` in `tokenURIs[tokenId]`
3. `tokenURI(tokenId)` returns the stored IPFS link
4. Now returns real IPFS links instead of placeholders

**Previous Issue**:
```python
# Old fallback created fake links
metadata_uri = card.metadata_uri or f"https://ipfs.io/ipfs/QmYYSSQR{watermark_id}"
```

**New Solution**:
```python
# Real IPFS upload during card creation
metadata_uri = f"https://gateway.pinata.cloud/ipfs/{original_ipfs_cid}" if original_ipfs_cid else None
```

## Deployment Process

### 1. Server Deployment
```bash
git add .
git commit -m "Add IPFS upload functionality and NFT image display"
git push
# Render auto-deploys from git push
```

### 2. Mobile App Deployment
```bash
# Update app version
# mobile_app_rn/app.json: "version": "1.2.0"

# Push EAS update
eas update --branch production --message "NFT collection with images"
```

## Technical Architecture

### IPFS Flow:
1. **Card Creation** → Upload images to Filebase S3
2. **Filebase** → Automatically pins to IPFS network
3. **Database** → Stores IPFS CIDs
4. **Smart Contract** → Gets real IPFS metadata URI
5. **Mobile App** → Displays images from Pinata gateway

### Data Flow:
```
Web App → IPFS Upload → Database Storage → Smart Contract → Mobile Display
```

## Environment Variables Required

```bash
# Server environment
FILEBASE_ACCESS_KEY=your_access_key
FILEBASE_SECRET_KEY=your_secret_key  
FILEBASE_BUCKET_NAME=yys-sqr-images
```

## Files Modified Summary

| File | Purpose | Key Changes |
|------|---------|-------------|
| `webapp_server.py` | Server logic | Added IPFS upload, NFT API endpoint |
| `database.py` | Data model | Added IPFS CID fields |
| `requirements-webapp.txt` | Dependencies | Added boto3 for S3/IPFS |
| `WalletScreen.js` | Mobile UI | NFT collection display with images |
| `ResultScreen.js` | Mobile UI | Fixed claim states, better IPFS links |
| `YYSApiService.js` | API client | Added NFT fetching method |
| `app.json` | App config | Version bump for EAS update |

## Testing Verification

### New Card Creation:
1. Create card via web app
2. Images uploaded to IPFS ✅
3. Database stores IPFS CIDs ✅
4. Smart contract gets real metadata URI ✅

### NFT Claiming:
1. Scan card and claim NFT
2. Transaction succeeds ✅
3. Mobile app shows success state ✅
4. Wallet displays NFT with image ✅

### IPFS Links:
1. Smart contract tokenURI returns real IPFS link ✅
2. Mobile app can display images ✅
3. "View Image" button opens working IPFS link ✅

## Future Considerations

1. **Database Migration**: Existing cards without IPFS CIDs will use fallback URLs
2. **Error Handling**: IPFS upload failures gracefully handled with warnings
3. **Performance**: Images cached by Pinata gateway for fast loading
4. **Scalability**: Filebase provides unlimited IPFS storage

## Commit History

- `49c88814`: Add IPFS upload functionality and NFT image display
- `bf9338dd`: Bump app version to 1.2.0 for major UI improvements
- `6b642146`: Major UI improvements and NFT wallet features
- `381ca846`: Fix transaction hash format - ensure 0x prefix for Etherscan links

This comprehensive update transforms the YYS-SQR system from a mock NFT platform into a fully functional blockchain application with proper IPFS integration and professional mobile UI.