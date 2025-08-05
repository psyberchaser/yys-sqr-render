# YYS-SQR Complete Digital Twinning System Documentation

## 🎯 System Overview

This is a complete digital twinning platform for trading cards using invisible watermarks. Users can create cards through a web interface, embed watermarks, and scan physical cards with a mobile app to claim digital NFTs.

## 📱 Mobile App (React Native + Expo)

### **Location**: `yys-sqr/mobile_app_rn/`

### **Key Features**:
- **Automatic Scanning**: Camera-based watermark detection
- **Manual Corner Selection**: 4-point manual corner selection for difficult scans
- **Card Embedding**: Create watermarked images directly in app
- **Enhanced Results**: Rich card metadata from database

### **Core Files**:
- `src/screens/ScanScreen.js` - Automatic camera scanning
- `src/screens/ManualScanScreen.js` - Manual 4-corner selection
- `src/screens/EmbedScreen.js` - Watermark embedding
- `src/screens/ResultScreen.js` - Scan results display
- `src/services/YYSApiService.js` - API communication

### **Deployment**:
```bash
# Deploy to EAS (Expo Application Services)
cd mobile_app_rn
eas build --platform ios --profile preview
eas update --branch preview --message "Update message"
```

### **Key Improvements Made**:
1. **Enhanced Scanning**: Multiple image sizes (1024px, 800px, 600px) for better detection
2. **Manual Fallback**: 4-corner selection with proper coordinate scaling
3. **Rich Results**: Full card metadata instead of just watermark ID
4. **Better Error Handling**: Detailed logging and user feedback
5. **OTA Updates**: Instant updates without app store approval

## 🌐 Web Application (Flask + PostgreSQL)

### **Location**: `yys-sqr/webapp_server.py` + templates + static files

### **Key Features**:
- **Card Creation**: Upload images, add metadata, generate watermarks
- **Database Management**: PostgreSQL with full card tracking
- **Dashboard**: Statistics and recent cards overview
- **Card Browser**: View all cards with pagination
- **Scan History**: Track who scanned what and when

### **Core Files**:
- `webapp_server.py` - Main Flask application
- `database.py` - SQLAlchemy models (TradingCard, ScanHistory)
- `templates/` - HTML templates (Bootstrap-based)
- `static/` - CSS and JavaScript assets
- `requirements-webapp.txt` - Python dependencies

### **Database Schema**:
```sql
-- Trading Cards Table
CREATE TABLE trading_cards (
    watermark_id VARCHAR(5) PRIMARY KEY,
    card_name VARCHAR(255) NOT NULL,
    description TEXT,
    series VARCHAR(100),
    rarity VARCHAR(50),
    creator_address VARCHAR(42),
    image_url TEXT,
    watermarked_image_url TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    owner_address VARCHAR(42),
    nft_token_id BIGINT,
    minted_at TIMESTAMP,
    scan_count INTEGER DEFAULT 0
);

-- Scan History Table
CREATE TABLE scan_history (
    id SERIAL PRIMARY KEY,
    watermark_id VARCHAR(5) REFERENCES trading_cards(watermark_id),
    scanner_address VARCHAR(42),
    scanned_at TIMESTAMP DEFAULT NOW(),
    was_first_scan BOOLEAN DEFAULT FALSE
);
```

### **API Endpoints**:
- `GET /` - Web dashboard
- `GET /create` - Card creation form
- `GET /cards` - Card browser
- `GET /card/{id}` - Card details
- `POST /api/cards` - Create new card
- `GET /api/cards` - List cards (JSON)
- `POST /api/scan` - Enhanced scanning with database lookup
- `POST /api/scan/manual` - Manual corner scanning
- `GET /api/health` - System health check

## ☁️ Render Deployment

### **Service Configuration**:
- **Service Name**: `yys-sqr-render`
- **URL**: `https://yys-sqr-render.onrender.com`
- **Plan**: Starter ($7/month) - Required for memory and database
- **Build Command**: `pip install -r requirements-webapp.txt`
- **Start Command**: `python webapp_server.py`

### **Database Configuration**:
- **Service Name**: `yys-sqr-db`
- **Type**: PostgreSQL
- **Plan**: Starter ($7/month)
- **Database**: `yys_sqr_trading_cards`
- **Connection**: Via `DATABASE_URL` environment variable

### **Environment Variables**:
```
DATABASE_URL=postgresql://username:password@hostname:port/database
SECRET_KEY=your-secret-key-here
PYTHON_VERSION=3.11.4
```

### **Deployment Steps**:
1. **Create Web Service**:
   - Connect GitHub repo: `psyberchaser/yys-sqr-render`
   - Branch: `master`
   - Build: `pip install -r requirements-webapp.txt`
   - Start: `python webapp_server.py`

2. **Create PostgreSQL Database**:
   - Name: `yys-sqr-db`
   - Plan: Starter
   - Region: Same as web service

3. **Connect Database**:
   - Add `DATABASE_URL` environment variable
   - Link to PostgreSQL external URL
   - Redeploy service

4. **Verify Deployment**:
   - Visit web interface
   - Check `/api/health` endpoint
   - Test card creation

## 🔄 System Workflow

### **Card Creation (Web App)**:
1. Creator uploads image + metadata
2. System generates unique 5-character watermark ID
3. TrustMark embeds invisible watermark in image
4. Card stored in PostgreSQL database
5. Watermarked image ready for physical printing

### **Card Scanning (Mobile App)**:
1. User scans physical card with mobile app
2. App tries automatic corner detection first
3. If fails, offers manual 4-corner selection
4. Server processes image and extracts watermark
5. Database lookup returns full card metadata
6. User sees rich card details + NFT status

### **Digital Twinning Logic**:
- **First Scanner**: Gets to mint the NFT (first-to-scan-owns)
- **Subsequent Scanners**: See "Already Owned" + owner info
- **Scan History**: All scans tracked with timestamps
- **NFT Ready**: Database prepared for blockchain integration

## 🛠️ Technical Stack

### **Frontend (Mobile)**:
- React Native + Expo SDK 53
- Camera: `expo-camera` (CameraView)
- Image Processing: `expo-image-manipulator`
- Navigation: `@react-navigation/stack`
- HTTP: `axios`

### **Frontend (Web)**:
- HTML5 + Bootstrap 5
- JavaScript (ES6+)
- Responsive design
- File upload with preview

### **Backend**:
- Python 3.11
- Flask 2.3+ (Web framework)
- SQLAlchemy (ORM)
- PostgreSQL (Database)
- OpenCV (Image processing)
- TrustMark (Watermarking)
- PyTorch (ML models)

### **Infrastructure**:
- Render (Cloud hosting)
- PostgreSQL (Database)
- GitHub (Version control)
- EAS (Mobile deployment)

## 🔧 Key Algorithms

### **Watermark Embedding**:
- BCH Super error correction
- Invisible frequency domain embedding
- 5-character alphanumeric IDs
- Robust to compression and printing

### **Corner Detection**:
- Multiple detection methods
- Automatic perspective correction
- Manual 4-point fallback
- Coordinate scaling for different resolutions

### **Image Processing Pipeline**:
1. Image capture/upload
2. Resize to optimal dimensions
3. Corner detection (auto or manual)
4. Perspective transformation
5. Watermark extraction
6. Database lookup and response

## 📊 Performance Optimizations

### **Mobile App**:
- Multiple image sizes for detection (1024px, 800px, 600px)
- Progressive quality reduction
- Efficient coordinate scaling
- Proper error handling and retries

### **Server**:
- Image compression and resizing
- Database indexing on watermark_id
- Connection pooling
- Caching for static assets

### **Database**:
- Primary key on watermark_id
- Indexes on frequently queried fields
- Efficient pagination
- Scan history tracking

## 🚀 Future Enhancements Ready

### **Blockchain Integration**:
- Smart contract for NFT minting
- Ethereum/Polygon integration
- Proof of Scan contract
- Royalty distribution

### **Advanced Features**:
- Batch card creation
- Series management
- Rarity algorithms
- Trading marketplace
- User authentication
- Social features

## 📝 Maintenance Notes

### **Regular Tasks**:
- Monitor Render service health
- Database backup and maintenance
- Update dependencies
- Monitor scan success rates
- Review error logs

### **Scaling Considerations**:
- Upgrade Render plans for higher traffic
- Database optimization for large datasets
- CDN for image assets
- Load balancing for high availability

## 🎉 Success Metrics

The system successfully provides:
- ✅ **Web-based card creation** with rich metadata
- ✅ **Mobile scanning** with automatic and manual modes
- ✅ **Database integration** with full tracking
- ✅ **Digital twinning** ready for NFT minting
- ✅ **Scalable architecture** on cloud infrastructure
- ✅ **OTA updates** for instant mobile app updates
- ✅ **Production-ready** deployment on Render

This complete system transforms physical trading cards into digital assets with secure, invisible watermarking technology.