# 🚀 Deploy YYS-SQR to Render

## Step 1: Create Render Account
1. Go to https://render.com
2. Sign up with GitHub account
3. Connect your GitHub repository

## Step 2: Create Web Service
1. Click "New +" → "Web Service"
2. Connect your GitHub repo containing yys-sqr
3. Use these settings:

**Basic Settings:**
- **Name**: `yys-sqr-api`
- **Region**: `Oregon (US West)` or closest to you
- **Branch**: `main` (or your branch name)
- **Root Directory**: `yys-sqr` (if in subdirectory)

**Build & Deploy:**
- **Runtime**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `python render_server.py`

**Environment Variables:**
- `FLASK_ENV` = `production`
- `PORT` = `10000` (Render default)

## Step 3: Deploy
1. Click "Create Web Service"
2. Wait for build (5-10 minutes)
3. Get your URL: `https://yys-sqr-api.onrender.com`

## Step 4: Update Mobile App
Edit `mobile_app_rn/src/services/YYSApiService.js`:

```javascript
const API_BASE_URL = 'https://yys-sqr-api.onrender.com/api';
```

## Step 5: Test
Visit your URL to see:
```json
{
  "message": "🎉 YYS-SQR API is running on Render!",
  "status": "healthy",
  "components": {
    "auto_corner_detection": true,
    "trustmark_watermarking": true
  }
}
```

## Render Benefits:
- ✅ Free tier (750 hours/month)
- ✅ Automatic HTTPS
- ✅ Better Python support
- ✅ Reliable builds
- ✅ Easy GitHub integration
- ✅ Automatic deployments

## Cost:
- **Free**: 750 hours/month (enough for testing)
- **Paid**: $7/month for always-on service