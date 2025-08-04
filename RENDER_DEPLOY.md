# 🚀 Deploy YYS-SQR to Render

## Quick Deploy (Recommended)

1. **Go to [Render.com](https://render.com)** and sign up/login
2. **Click "New +" → "Web Service"**
3. **Connect your GitHub repo** (or upload this folder)
4. **Configure the service:**
   - **Name:** `yys-sqr-api`
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python render_server.py`
   - **Port:** `10000` (auto-detected)

## Advanced Configuration

### Environment Variables
```
FLASK_ENV=production
PORT=10000
```

### Health Check
- **Path:** `/api/health`
- **Expected Status:** `200`

## What You Get

✅ **Full API with all features:**
- `/api/scan` - Auto corner detection with 4 methods
- `/api/embed` - BCH Super watermark embedding  
- `/api/capacity` - Watermark capacity info
- `/api/health` - Component status
- `/api/docs` - Full documentation

✅ **Production ready:**
- Automatic HTTPS
- Custom domain support
- Auto-scaling
- Health monitoring
- Error logging

## Test Your Deployment

Once deployed, test with:

```bash
# Health check
curl https://your-app.onrender.com/api/health

# Full API info
curl https://your-app.onrender.com

# API documentation
curl https://your-app.onrender.com/api/docs
```

## Render vs Railway

**Render Advantages:**
- Better Python dependency handling
- More reliable builds
- Better logging and monitoring
- Free tier with good limits
- Automatic HTTPS and custom domains

**Your API will be available at:**
`https://your-app-name.onrender.com`

## Mobile App Update

After deployment, update your mobile app:

```javascript
// mobile_app_rn/src/services/YYSApiService.js
const API_BASE_URL = 'https://your-app-name.onrender.com/api';
```

## Troubleshooting

If build fails:
1. Check the build logs in Render dashboard
2. Verify all dependencies in requirements.txt
3. Check that render_server.py exists
4. Ensure Python version compatibility

**Your $0 investment gets you a production-ready API!** 🎉