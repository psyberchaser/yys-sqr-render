# YYS-SQR Mobile App (React Native + Expo)

A mobile watermark scanner with automatic corner detection and blockchain integration.

## 🚀 Quick Setup

### Prerequisites
- Node.js 16+ 
- Expo CLI: `npm install -g @expo/cli`
- YYS-SQR Python backend running (see ../api_server.py)

### Installation

1. **Install dependencies**:
   ```bash
   cd yys-sqr/mobile_app_rn
   npm install
   ```

2. **Start the backend server**:
   ```bash
   # In another terminal, from yys-sqr directory
   python api_server.py
   ```

3. **Update API URL**:
   Edit `src/services/YYSApiService.js` and change:
   ```javascript
   const API_BASE_URL = 'http://YOUR_COMPUTER_IP:5000/api';
   ```

4. **Start the app**:
   ```bash
   expo start
   ```

5. **Run on device**:
   - Install Expo Go app on your phone
   - Scan the QR code from the terminal
   - Or press `i` for iOS simulator, `a` for Android emulator

## 📱 Features

### 🔍 **Automatic Scanning**
- **Real-time camera preview** with scanning frame overlay
- **Auto-scan mode** - automatically takes photos every 2 seconds
- **Manual scan** - tap to capture when ready
- **Automatic corner detection** - no manual corner clicking needed!

### 🎯 **Smart Detection**
- **4 detection methods** tried automatically:
  - Document corners (best for printed images)
  - Contour-based detection
  - Harris corner detection
  - Edge-based detection
- **High confidence filtering** - only shows reliable results
- **Visual feedback** - clear success/failure indicators

### 📊 **Rich Results**
- **Decoded message** display
- **Detection confidence** and method used
- **Blockchain integration** - links to Etherscan
- **IPFS links** - view stored images
- **Share functionality** - share results with others

### 🔗 **Backend Integration**
- **RESTful API** communication with Python backend
- **Base64 image transfer** - efficient and reliable
- **Error handling** - graceful degradation when offline
- **Health monitoring** - server status checking

## 🏗️ Architecture

```
📱 React Native App
    ↓ HTTP/JSON
🐍 Python Backend (api_server.py)
    ↓ OpenCV
🔍 Auto Corner Detection
    ↓ TrustMark
💧 Watermark Decoding
    ↓ Web3
⛓️ Blockchain Recording
```

## 📂 Project Structure

```
mobile_app_rn/
├── App.js                 # Main navigation
├── package.json          # Dependencies
├── src/
│   ├── screens/
│   │   ├── HomeScreen.js     # Main menu
│   │   ├── ScanScreen.js     # Camera scanning
│   │   ├── ResultScreen.js   # Results display
│   │   └── EmbedScreen.js    # Watermark embedding
│   └── services/
│       └── YYSApiService.js  # Backend API client
└── README.md
```

## 🔧 Configuration

### API Endpoint
Update the backend URL in `src/services/YYSApiService.js`:

```javascript
// For local development
const API_BASE_URL = 'http://localhost:5000/api';

// For device testing (replace with your computer's IP)
const API_BASE_URL = 'http://192.168.1.100:5000/api';

// For production
const API_BASE_URL = 'https://your-server.com/api';
```

### Camera Permissions
The app automatically requests camera permissions. Make sure to:
- Allow camera access when prompted
- Check device settings if camera doesn't work

## 📱 Usage

### Scanning Watermarks

1. **Open the app** and tap "Scan Watermark"
2. **Point camera** at a watermarked image
3. **Choose scanning mode**:
   - **Auto Scan ON**: Automatically scans every 2 seconds
   - **Auto Scan OFF**: Tap "Scan Now" button manually
4. **Wait for processing** - the app will:
   - Detect corners automatically
   - Apply perspective correction
   - Decode the watermark
   - Look up the message
5. **View results** with decoded message and details

### Tips for Best Results

- **Good lighting** - avoid shadows and glare
- **Steady hands** - hold phone stable
- **Full image visible** - ensure entire watermarked image is in frame
- **Reasonable distance** - not too close or far
- **Clean lens** - wipe camera lens if blurry

## 🚀 Deployment

### Building for Production

1. **Configure app.json**:
   ```json
   {
     "expo": {
       "name": "YYS-SQR Scanner",
       "slug": "yys-sqr-scanner",
       "version": "1.0.0",
       "platforms": ["ios", "android"],
       "icon": "./assets/icon.png",
       "splash": {
         "image": "./assets/splash.png"
       }
     }
   }
   ```

2. **Build for iOS**:
   ```bash
   expo build:ios
   ```

3. **Build for Android**:
   ```bash
   expo build:android
   ```

### App Store Deployment

1. **iOS App Store**:
   - Use Expo's build service or Xcode
   - Follow Apple's submission guidelines
   - Include camera usage description

2. **Google Play Store**:
   - Generate signed APK with Expo
   - Follow Google Play policies
   - Include camera permission description

## 🔍 Troubleshooting

### Common Issues

**Camera not working:**
- Check permissions in device settings
- Restart the app
- Try on a different device

**"Server Offline" error:**
- Make sure Python backend is running
- Check API_BASE_URL in YYSApiService.js
- Verify network connectivity
- Try `curl http://YOUR_IP:5000/api/health`

**No watermark detected:**
- Ensure image has a watermark embedded
- Try better lighting
- Hold camera steadier
- Make sure entire image is visible

**App crashes:**
- Check Expo CLI version: `expo --version`
- Clear cache: `expo r -c`
- Reinstall dependencies: `rm -rf node_modules && npm install`

### Development Tips

**Testing on device:**
- Use your computer's IP address, not localhost
- Make sure phone and computer are on same WiFi
- Disable firewall temporarily if needed

**Debugging:**
- Use `console.log()` statements
- Check Expo DevTools in browser
- Use React Native Debugger

## 🔮 Future Enhancements

### Planned Features
- **Offline mode** - local processing without backend
- **Batch scanning** - scan multiple images at once
- **History** - save scan results locally
- **Settings** - configure detection parameters
- **Dark mode** - better UI themes

### Technical Improvements
- **Native OpenCV** - port corner detection to React Native
- **WebAssembly** - run TrustMark in browser
- **Push notifications** - blockchain transaction updates
- **Biometric auth** - secure private key storage

## 📄 License

Same as parent YYS-SQR project - MIT License