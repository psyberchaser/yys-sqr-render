# 🎯 YYS-SQR Watermarking API

**Advanced watermarking system with automatic corner detection and mobile app support**

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

## 🚀 Quick Deploy to Render

### Option 1: Basic Deployment (Always Works)
- **Build Command:** `pip install -r requirements-minimal.txt`
- **Start Command:** `python basic_server.py`
- **Perfect for:** Getting started quickly, testing mobile app integration

### Option 2: Full Deployment (All Features)
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `python render_server.py`
- **Perfect for:** Complete watermarking functionality

## 📱 Features

- **🔍 Auto Corner Detection** - 4 different detection methods
- **🔒 BCH Super Watermarking** - Maximum error correction
- **📱 Mobile App Ready** - React Native app included
- **🌐 Always Online** - Cloud deployment ready
- **🔧 Multiple Deployment Options** - Basic to full functionality

## 🛠 API Endpoints

- `GET /` - API status and information
- `GET /api/health` - Health check with component status
- `POST /api/scan` - Scan watermark with auto corner detection
- `POST /api/embed` - Embed watermark with BCH Super encoding
- `GET /api/capacity` - Get watermark capacity information
- `GET /api/docs` - Complete API documentation

## 📖 Documentation

See [RENDER_DEPLOYMENT_GUIDE.md](RENDER_DEPLOYMENT_GUIDE.md) for complete deployment instructions.

## 🎯 Mobile App

React Native mobile app included in `mobile_app_rn/` directory.

Update the API URL in `mobile_app_rn/src/services/YYSApiService.js`:
```javascript
const API_BASE_URL = 'https://your-app.onrender.com/api';
```

## 🔧 Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run full server
python render_server.py

# Or run basic server
pip install -r requirements-minimal.txt
python basic_server.py
```

## 🌟 Deploy Now

1. **Fork this repository**
2. **Go to [Render.com](https://render.com)**
3. **Create new Web Service**
4. **Connect your GitHub repo**
5. **Deploy!**

Your API will be live at `https://your-app.onrender.com` 🎉