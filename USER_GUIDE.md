# YYS-SQR User Guide

## Complete Feature Documentation

### Overview

YYS-SQR (Yet Another System - Secure QR) is an advanced watermarking system that combines computer vision, blockchain technology, and decentralized storage to create a comprehensive solution for image authentication and verification.

## Main Interface

### Window Layout

```
┌─────────────────────────────────────────────────────────────┐
│ YYS - SQR                                            [_][□][×]│
├─────────────────────────────────────────────────────────────┤
│ [Embed SQR] [Decode SQR]                                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Tab Content Area                                           │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Embed SQR Tab - Hiding Messages in Images

### Step 1: Image Selection

**Purpose**: Choose the image you want to hide a message in

**How to use**:
1. Click "Select Image" button
2. Browse and select your image file
3. Supported formats: PNG, JPG, JPEG
4. The filename will appear below the button

**Best practices**:
- Use high-quality images (at least 512x512 pixels)
- Avoid heavily compressed images
- Photos work better than graphics with solid colors

### Step 2: Message Input

**Purpose**: Enter the secret message to hide

**How to use**:
1. Click in the text box
2. Type your message (maximum 5 characters)
3. Can include letters, numbers, symbols

**Message ideas**:
- `HELLO` - Simple greeting
- `AUTH` - Authentication code
- `2024` - Year or date
- `OK` - Confirmation
- `$100` - Price or value

### Step 3: Configuration Options

#### Single-Use SQR Checkbox
- **Checked**: Message deletes after first successful scan
- **Unchecked**: Message can be scanned multiple times
- **Use cases**: 
  - Checked: High-security applications, one-time codes
  - Unchecked: Permanent authentication, repeated verification

#### Web3 Features Checkbox
- **Checked**: Uploads image to IPFS and enables blockchain features
- **Unchecked**: Local-only operation
- **Requirements**: Internet connection needed when checked

### Step 4: Embedding Process

1. Click "Embed SQR" button
2. Status updates will appear:
   - "Starting up..." - Initializing the system
   - "Uploading to IPFS..." - If Web3 enabled
   - "Success!" - Process complete
3. Choose save location for watermarked image
4. Results summary shows:
   - Save location
   - Unique ID assigned
   - IPFS CID (if uploaded)
   - Single-use status

## Decode SQR Tab - Revealing Hidden Messages

### Step 1: Photo Selection

**Purpose**: Load a photograph of the watermarked image

**How to use**:
1. Take a photo of the printed/displayed watermarked image
2. Click "Select Photo" button
3. Choose your photo file
4. The image will appear in the viewer

**Photo tips**:
- Ensure entire watermarked image is visible
- Use good lighting
- Hold camera steady
- Avoid shadows or glare
- Take photo straight-on (not at an angle)

### Step 2: Corner Selection

**Purpose**: Mark the four corners of the watermarked image for perspective correction

**How to use**:
1. Click on the four corners in this exact order:
   - **1st click**: Top-left corner
   - **2nd click**: Top-right corner  
   - **3rd click**: Bottom-right corner
   - **4th click**: Bottom-left corner
2. Green dots will appear where you click
3. You can drag dots to adjust positioning
4. The "Step 3" button enables after 4 corners are marked

**Corner selection tips**:
- Click precisely on the corners
- If you make a mistake, click "Select Photo" again to restart
- Zoom in if needed for precision
- The order matters - follow the sequence exactly

### Step 3: Processing and Verification

#### Private Key Input (Optional)
- **Purpose**: Enable blockchain proof-of-scan recording
- **Format**: Ethereum private key (64 hex characters)
- **Security**: Only used for this session, not stored
- **Leave blank**: Skip blockchain features

#### Decode Process
1. Click "Step 3: Computer Vision Processing and Verification"
2. System performs:
   - Perspective correction using OpenCV
   - Watermark extraction
   - Database lookup
   - Blockchain transaction (if key provided)

#### Results Display
Shows:
- **Success/Failure status**
- **Decoded message**
- **Unique ID**
- **IPFS CID** (if available)
- **Single-use notification** (if applicable)
- **Blockchain transaction hash** (if recorded)

#### Etherscan Link
- Appears after successful blockchain transaction
- Click to view transaction details on Etherscan
- Shows proof-of-scan record on Sepolia testnet

## Advanced Features

### Single-Use SQRs

**How it works**:
1. Message embedded with single-use flag
2. First successful scan retrieves message
3. Database entry automatically deleted
4. Subsequent scans show "not found"

**Use cases**:
- One-time authentication codes
- Ticket validation
- Secure document verification
- Anti-counterfeiting

### Blockchain Integration

**What it does**:
- Records proof-of-scan on Ethereum blockchain
- Creates immutable timestamp
- Links scan to wallet address
- Stores IPFS reference

**Requirements**:
- Ethereum wallet with Sepolia testnet ETH
- Private key for transaction signing
- Internet connection

**Transaction details**:
- Network: Sepolia testnet
- Gas limit: 200,000
- Gas price: 10 gwei
- Contract: ProofOfScanV2

### IPFS Storage

**Purpose**:
- Decentralized storage of watermarked images
- Global accessibility
- Censorship resistance

**How it works**:
1. Image uploaded to Filebase (IPFS gateway)
2. Content ID (CID) generated
3. CID stored in local database
4. CID recorded on blockchain

## File Management

### Database Location
- **macOS**: `~/Library/Application Support/YYS-SQR/database.json`
- **Windows**: `%APPDATA%/YYS-SQR/database.json`
- **Linux**: `~/.local/share/YYS-SQR/database.json`

### Database Structure
```json
{
  "abc12": {
    "secret_message": "HELLO",
    "ipfs_cid": "QmXxx...",
    "destroy_on_scan": false
  }
}
```

### Backup and Restore
- **Backup**: Copy database.json file
- **Restore**: Replace database.json file
- **Reset**: Delete database.json file

## Security Considerations

### Message Security
- Messages are cryptographically embedded
- BCH Super error correction provides robustness
- Invisible to casual inspection

### Private Key Safety
- Never share your private key
- Use testnet wallets only
- Keys are not stored by the application

### Network Security
- Blockchain transactions are public
- IPFS content is publicly accessible
- Local database contains sensitive data

## Performance Tips

### For Best Embedding Results
- Use uncompressed or lightly compressed images
- Avoid images with lots of noise or grain
- Larger images generally work better
- Save as PNG for best quality

### For Best Scanning Results
- Print at high resolution (300+ DPI)
- Use matte paper to reduce glare
- Ensure even lighting when photographing
- Keep camera parallel to image surface

### System Performance
- Close other applications for faster processing
- Ensure stable internet for Web3 features
- Use SSD storage for better file I/O
- 8GB+ RAM recommended for large images

## Integration with Other Tools

### Command Line Scripts
Located in `scripts/` directory:
- `embed.py` - Embed watermarks via command line
- `decode.py` - Decode watermarks via command line
- `manual_decode.py` - Manual perspective correction
- `check_capacity.py` - Check watermark capacity

### API Integration
The core functionality can be integrated into other applications:
```python
import trustmark
tm = trustmark.TrustMark(verbose=False, encoding_type=trustmark.TrustMark.Encoding.BCH_SUPER)
watermarked = tm.encode(image, message)
```

### Smart Contract Integration
Contract address: `0xd8b934580fcE35a11B58C6D73aDeE468a2833fa8`
Network: Sepolia testnet
Functions: `recordScan()`, `getScanDetails()`