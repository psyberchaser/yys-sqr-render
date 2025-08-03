# 🚀 YYS-SQR Render Deployment Guide

## 🎯 Quick Start (Recommended)

### Option 1: Basic Deployment (Always Works)
**Perfect for getting started quickly!**

1. **Go to [Render.com](https://render.com)** and create account
2. **Click "New +" → "Web Service"**
3. **Connect your GitHub repo** or upload this folder
4. **Configure:**
   - **Name:** `yys-sqr-basic`
   - **Build Command:** `pip install -r requirements-minimal.txt`
   - **Start Command:** `python basic_server.py`
   - **Environment:** `Python 3`

**✅ What you get:**
- Always-online API at `https://your-app.onrender.com`
- Basic image processing
- Health monitoring
- Ready to upgrade to full features

### Option 2: Full Deployment (All Features)
**Complete watermarking functionality**

1. **Same setup as above, but use:**
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python render_server.py`

**✅ What you get:**
- Full watermark embedding with TrustMark
- Auto corner detection (4 methods)
- Complete API functionality

## 🧪 Test Your Deployment

```bash
# Health check
curl https://your-app.onrender.com/api/health

# API info
curl https://your-app.onrender.com

# Test endpoint
curl -X POST https://your-app.onrender.com/api/test \
  -H "Content-Type: application/json" \
  -d '{"message": "test"}'
```

## 📱 Update Your Mobile App

After deployment, update your mobile app:

```javascript
// mobile_app_rn/src/services/YYSApiService.js
const API_BASE_URL = 'https://your-app-name.onrender.com/api';
```

## 🔄 Upgrade Path

**Start with Basic → Upgrade to Full when ready**

1. **Deploy Basic first** (guaranteed to work)
2. **Test your mobile app** with the basic API
3. **Upgrade to Full** when you need watermarking

To upgrade:
- Change build command to use `requirements.txt`
- Change start command to `python render_server.py`
- Redeploy

## 📋 Available Configurations

### Basic Server (`basic_server.py`)
```yaml
buildCommand: pip install -r requirements-minimal.txt
startCommand: python basic_server.py
```
- ✅ Always works
- ✅ Fast deployment
- ✅ Basic image processing
- ❌ No watermarking yet

### Full Server (`render_server.py`)
```yaml
buildCommand: pip install -r requirements.txt
startCommand: python render_server.py
```
- ✅ Complete functionality
- ✅ Auto corner detection
- ✅ Watermark embedding
- ⚠️  Larger dependencies

## 🛠 Troubleshooting

### If Full Deployment Fails:
1. **Use Basic deployment first**
2. **Check build logs** in Render dashboard
3. **Try minimal requirements**
4. **Contact support** with logs

### If Basic Deployment Fails:
- Check Python version (should be 3.8+)
- Verify file paths
- Check Render service logs

## 💰 Cost

**Render Free Tier:**
- ✅ 750 hours/month free
- ✅ Automatic HTTPS
- ✅ Custom domains
- ✅ Perfect for development

**Your API will be:**
- Always online
- Professionally hosted
- Ready for production
- Free to start!

## 🎉 Success!

Once deployed, you'll have:
- **Professional API URL:** `https://your-app.onrender.com`
- **Always-online backend** for your mobile app
- **Automatic HTTPS** and monitoring
- **Easy updates** via git push

**Your mobile app can now work from anywhere!** 📱🌍