# YYS-SQR Production Deployment Guide

## 🚀 **Deployment Options**

### **Option 1: Railway (Easiest - Recommended)**

Railway is perfect for Python apps and handles everything automatically.

#### **Steps:**

1. **Create Railway account**: https://railway.app
2. **Install Railway CLI**:
   ```bash
   npm install -g @railway/cli
   ```

3. **Login and deploy**:
   ```bash
   cd yys-sqr
   railway login
   railway init
   railway up
   ```

4. **Set environment variables** in Railway dashboard:
   ```
   FLASK_ENV=production
   SECRET_KEY=your-secret-key-here
   ```

5. **Get your URL**: Railway provides a URL like `https://your-app.railway.app`

**Cost**: ~$5/month, scales automatically

---

### **Option 2: Render (Also Easy)**

1. **Create Render account**: https://render.com
2. **Connect GitHub repo**
3. **Create Web Service** with these settings:
   - **Build Command**: `pip install -r deployment/requirements-production.txt`
   - **Start Command**: `python deployment/production_api_server.py`
   - **Environment**: `FLASK_ENV=production`

**Cost**: Free tier available, $7/month for paid

---

### **Option 3: DigitalOcean App Platform**

1. **Create DigitalOcean account**
2. **Create App** from GitHub
3. **Configure**:
   - **Source**: Your GitHub repo
   - **Build Command**: `pip install -r deployment/requirements-production.txt`
   - **Run Command**: `python deployment/production_api_server.py`

**Cost**: $5/month minimum

---

### **Option 4: AWS/Google Cloud (Advanced)**

For high-scale production use.

#### **AWS Elastic Beanstalk**:
```bash
# Install EB CLI
pip install awsebcli

# Initialize and deploy
cd yys-sqr
eb init
eb create production
eb deploy
```

#### **Google Cloud Run**:
```bash
# Build and deploy
gcloud builds submit --tag gcr.io/PROJECT-ID/yys-sqr
gcloud run deploy --image gcr.io/PROJECT-ID/yys-sqr --platform managed
```

---

### **Option 5: Docker + VPS (Most Control)**

Deploy to any VPS (DigitalOcean, Linode, etc.)

#### **Steps:**

1. **Get a VPS** ($5/month DigitalOcean droplet)

2. **Install Docker**:
   ```bash
   curl -fsSL https://get.docker.com -o get-docker.sh
   sh get-docker.sh
   ```

3. **Clone and deploy**:
   ```bash
   git clone your-repo
   cd yys-sqr/deployment
   docker-compose up -d
   ```

4. **Setup domain** (optional):
   - Point domain to VPS IP
   - Use Cloudflare for SSL

---

## 🔧 **Production Configuration**

### **Environment Variables**

Set these in your deployment platform:

```bash
# Required
FLASK_ENV=production
SECRET_KEY=your-super-secret-key-change-this

# Optional
SENTRY_DSN=https://your-sentry-dsn  # Error tracking
PORT=5000  # Usually auto-set by platform
```

### **Mobile App Configuration**

Update your mobile app's API URL:

```javascript
// In mobile_app_rn/src/services/YYSApiService.js
const API_BASE_URL = 'https://your-deployed-app.railway.app/api';
```

---

## 📊 **Monitoring & Maintenance**

### **Health Monitoring**

Your API includes a health endpoint:
```
GET https://your-app.com/api/health
```

### **Error Tracking**

Add Sentry for error monitoring:
1. Create account at https://sentry.io
2. Get DSN
3. Set `SENTRY_DSN` environment variable

### **Logs**

Check logs in your platform:
- **Railway**: `railway logs`
- **Render**: View in dashboard
- **Docker**: `docker-compose logs`

### **Scaling**

Most platforms auto-scale, but you can configure:
- **Memory**: 1-2GB recommended
- **CPU**: 1 core minimum
- **Instances**: Start with 1, scale as needed

---

## 💰 **Cost Comparison**

| Platform | Free Tier | Paid | Pros | Cons |
|----------|-----------|------|------|------|
| **Railway** | $5 credit | $5/month | Easiest, auto-scaling | Newer platform |
| **Render** | 750 hours | $7/month | Reliable, good docs | Can be slow |
| **DigitalOcean** | None | $5/month | Full control | More setup |
| **AWS/GCP** | Free tier | Variable | Enterprise-grade | Complex |

---

## 🚀 **Quick Start (Railway)**

**Fastest way to get your backend online:**

```bash
# 1. Install Railway CLI
npm install -g @railway/cli

# 2. Deploy from your yys-sqr directory
cd yys-sqr
railway login
railway init
railway up

# 3. Set environment variables in Railway dashboard
# FLASK_ENV=production
# SECRET_KEY=your-secret-key

# 4. Get your URL and update mobile app
# Update API_BASE_URL in mobile app
```

**Your backend will be live at**: `https://your-app.railway.app`

**Update mobile app**:
```javascript
const API_BASE_URL = 'https://your-app.railway.app/api';
```

**Done!** Your mobile app now works with a production backend that's always online! 🎉

---

## 🔒 **Security Checklist**

- ✅ Change default SECRET_KEY
- ✅ Use HTTPS (handled by platforms)
- ✅ Set up error monitoring
- ✅ Enable health checks
- ✅ Limit file upload sizes
- ✅ Add rate limiting (if needed)
- ✅ Monitor resource usage

---

## 📱 **Mobile App Updates**

After deploying, update your mobile app:

1. **Change API URL** in `YYSApiService.js`
2. **Test thoroughly** with the new backend
3. **Deploy mobile app** to app stores
4. **Monitor usage** and performance

Your users can now scan watermarks anywhere with a reliable, always-online backend! 🌍