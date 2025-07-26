# 🎯 Production Deployment Checklist

## Before You Deploy

### ✅ **Critical Requirements**
- [ ] **Cloudinary Account**: Get real credentials from [cloudinary.com](https://cloudinary.com)
  - Cloud Name: `_____________`
  - API Key: `_____________`  
  - API Secret: `_____________`

- [ ] **Domain/URL**: Decide on your production domain
  - Heroku: `https://your-app-name.herokuapp.com`
  - Custom domain: `https://your-domain.com`

- [ ] **Git Repository**: Ensure all code is committed
  ```bash
  git add .
  git commit -m "Ready for production deployment"
  ```

### ✅ **Deployment Platform Choice**

**Option 1: Heroku (Easiest - Recommended for beginners)**
- [ ] Install Heroku CLI: `brew install heroku/brew/heroku`
- [ ] Run deployment script: `./deploy_to_heroku.sh`
- [ ] Set Cloudinary credentials manually

**Option 2: Railway (Modern alternative)**
- [ ] Sign up at [railway.app](https://railway.app)
- [ ] Connect GitHub repository
- [ ] Set environment variables in dashboard

**Option 3: VPS/Server (Advanced)**
- [ ] Server setup (Ubuntu/Debian)
- [ ] Nginx reverse proxy
- [ ] SSL certificate (Let's Encrypt)
- [ ] PM2 process management

---

## 🚀 **Quick Start: Heroku Deployment**

### **Step 1: Install Heroku CLI**
```bash
brew install heroku/brew/heroku
```

### **Step 2: Get Cloudinary Credentials**
1. Go to [cloudinary.com](https://cloudinary.com)
2. Sign up/login
3. Go to Console → Settings → API Keys
4. Copy: Cloud Name, API Key, API Secret

### **Step 3: Run Deployment Script**
```bash
./deploy_to_heroku.sh
```
Follow the prompts and enter your app name.

### **Step 4: Set Cloudinary Credentials**
```bash
# Replace with your actual credentials
heroku config:set CLOUDINARY_CLOUD_NAME="your_cloud_name" --app your-app-name
heroku config:set CLOUDINARY_API_KEY="your_api_key" --app your-app-name  
heroku config:set CLOUDINARY_API_SECRET="your_api_secret" --app your-app-name
```

### **Step 5: Test Your API**
```bash
curl https://your-app-name.herokuapp.com/api/v1/
```

---

## 📱 **Update Your React Native App**

After deployment, update your frontend config:

```javascript
// config.js or constants.js
const Config = {
  API_BASE_URL: __DEV__ 
    ? 'http://192.168.86.29:8000/api/v1'  // Development
    : 'https://your-app-name.herokuapp.com/api/v1'  // Production
};

export default Config;
```

---

## 🔍 **Testing Your Production API**

### **Test Authentication**
```bash
# Health check
curl https://your-app-name.herokuapp.com/

# Test registration
curl -X POST https://your-app-name.herokuapp.com/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@example.com","password":"testpass123"}'
```

### **Monitor Logs**
```bash
# Real-time logs
heroku logs --app your-app-name --tail

# Recent logs
heroku logs --app your-app-name
```

---

## 🔧 **Common Issues & Solutions**

### **Issue: App won't start**
```bash
# Check logs
heroku logs --app your-app-name

# Common fixes:
# 1. Check Procfile exists
# 2. Verify requirements.txt
# 3. Check environment variables
```

### **Issue: CORS errors**
```bash
# Update CORS origins
heroku config:set CORS_ORIGINS="https://your-frontend-domain.com,https://your-app-name.herokuapp.com" --app your-app-name
```

### **Issue: Database connection**
```bash
# Verify MongoDB URL
heroku config:get MONGODB_URL --app your-app-name
```

---

## 🎉 **You're Ready When...**

- [ ] API responds at production URL
- [ ] Authentication works (register/login)
- [ ] Image uploads work (Cloudinary configured)
- [ ] Mobile app connects successfully
- [ ] No CORS errors in browser/app

---

## 📞 **Support Commands**

```bash
# App info
heroku info --app your-app-name

# Open in browser
heroku open --app your-app-name

# Database connection test
heroku run python -c "import database; print('DB connection OK')" --app your-app-name

# Restart app
heroku restart --app your-app-name
```

**Your Rod Royale API will be production-ready! 🎣🚀**
