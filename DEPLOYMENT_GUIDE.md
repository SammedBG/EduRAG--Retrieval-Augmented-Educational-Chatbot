# 🚀 Production Deployment Guide

## ✅ What's Been Optimized

### **Backend (Render)**
- ✅ **Ultra-minimal requirements** for free tier
- ✅ **Production CORS** configuration
- ✅ **Memory optimization** for free tier limits
- ✅ **AWS S3 integration** for persistent storage
- ✅ **Graceful fallbacks** when ML models unavailable
- ✅ **Optimized startup** script

### **Frontend (Vercel)**
- ✅ **Production API configuration**
- ✅ **Environment variables** setup
- ✅ **Vercel deployment** configuration
- ✅ **Build optimization**

## 🎯 Deployment Steps

### **1. Backend Deployment (Render)**

1. **Push to GitHub**:
   ```bash
   git add .
   git commit -m "Production-ready deployment"
   git push origin main
   ```

2. **Deploy on Render**:
   - Go to [Render Dashboard](https://dashboard.render.com)
   - Click "New" → "Web Service"
   - Connect your GitHub repo
   - Use these settings:
     - **Build Command**: `pip install --no-cache-dir --upgrade pip setuptools wheel && pip install --no-cache-dir -r backend/requirements-ultra-minimal.txt || pip install --no-cache-dir -r backend/requirements-fallback.txt`
     - **Start Command**: `cd backend && python start_optimized.py`
     - **Root Directory**: `.` (blank)

3. **Set Environment Variables**:
   ```
   GROQ_API_KEY=your_groq_key
   HF_API_TOKEN=your_hf_token
   AWS_ACCESS_KEY_ID=your_aws_key
   AWS_SECRET_ACCESS_KEY=your_aws_secret
   AWS_DEFAULT_REGION=us-east-1
   AWS_S3_BUCKET=your_bucket_name
   ```

4. **Get your Render URL**: `https://your-app-name.onrender.com`

### **2. Frontend Deployment (Vercel)**

1. **Update API URL**:
   ```bash
   # In frontend/src/App.js, replace:
   'https://your-render-backend-url.onrender.com'
   # with your actual Render URL
   ```

2. **Deploy on Vercel**:
   - Go to [Vercel Dashboard](https://vercel.com/dashboard)
   - Click "New Project"
   - Import your GitHub repo
   - Set **Root Directory**: `frontend`
   - Add Environment Variable:
     ```
     REACT_APP_API_URL=https://your-render-backend-url.onrender.com
     ```

3. **Get your Vercel URL**: `https://your-app-name.vercel.app`

### **3. Update CORS (Important!)**

1. **Update backend CORS** in `backend/main.py`:
   ```python
   ALLOWED_ORIGINS = [
       "http://localhost:3000",
       "http://127.0.0.1:3000", 
       "https://your-app-name.vercel.app",  # Add your Vercel URL
       "https://*.vercel.app",
       "https://*.onrender.com"
   ]
   ```

2. **Redeploy backend** after CORS update

## 🔧 Testing Checklist

### **Backend Tests**
- [ ] Health check: `GET /health`
- [ ] File upload: `POST /upload`
- [ ] Chat: `POST /chat`
- [ ] WebSocket: `WS /ws`
- [ ] File list: `GET /files`
- [ ] File delete: `DELETE /files/{filename}`

### **Frontend Tests**
- [ ] API connection status
- [ ] File upload functionality
- [ ] Chat interface
- [ ] Real-time WebSocket
- [ ] File management

### **Integration Tests**
- [ ] Upload PDF → Process → Chat
- [ ] Multiple file handling
- [ ] Error handling
- [ ] CORS working properly

## 🚨 Common Issues & Fixes

### **Render Deployment Issues**
- **Build timeout**: Use ultra-minimal requirements
- **Memory limit**: ML models disabled automatically
- **CORS errors**: Update ALLOWED_ORIGINS
- **Port issues**: Use `$PORT` environment variable

### **Vercel Deployment Issues**
- **Build fails**: Check Node.js version
- **API not found**: Verify REACT_APP_API_URL
- **CORS errors**: Update backend CORS settings

### **AWS S3 Issues**
- **Access denied**: Check IAM permissions
- **Bucket not found**: Verify bucket name and region
- **Credentials**: Ensure environment variables set

## 📊 Performance Optimization

### **Free Tier Limits**
- **Render**: 512MB RAM, 0.1 CPU
- **Vercel**: 100GB bandwidth/month
- **AWS S3**: 5GB storage, 20K requests/month

### **Optimizations Applied**
- Single worker process
- Memory-efficient model loading
- S3 for persistent storage
- Minimal dependencies
- Graceful fallbacks

## 🎉 Success Indicators

✅ **Backend**: Health check returns `200 OK`  
✅ **Frontend**: Loads without errors  
✅ **Upload**: PDFs process successfully  
✅ **Chat**: Generates relevant answers  
✅ **Storage**: Files persist across restarts  
✅ **CORS**: No cross-origin errors  

## 🔄 Maintenance

### **Regular Tasks**
- Monitor AWS S3 usage
- Check Render/Vercel logs
- Update API keys if needed
- Monitor free tier limits

### **Scaling Up**
- Upgrade to paid tiers for more resources
- Add more S3 storage
- Implement caching
- Add monitoring/analytics

---

**Your RAG Chatbot is now production-ready! 🚀**
