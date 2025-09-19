# RAG Chatbot Deployment Guide

## Quick Fix for Current Issues

### 1. Memory Optimization Applied
- ✅ Lazy loading of heavy ML libraries
- ✅ Removed WebSocket support (memory intensive)
- ✅ Optimized requirements.txt
- ✅ Added memory management environment variables

### 2. CORS Fixed
- ✅ Updated to allow all origins for production
- ✅ Frontend now points to correct Render URL

## Deployment Steps

### Backend (Render)
1. **Push to GitHub** with the optimized code
2. **Connect to Render**:
   - Go to https://render.com
   - Connect your GitHub repo
   - Select "New Web Service"
   - Choose your repo
3. **Configure Render**:
   - **Name**: `edurag-backend`
   - **Environment**: `Python 3`
   - **Build Command**: 
     ```bash
     pip install --no-cache-dir -r requirements.txt && pip install --no-cache-dir -r backend/requirements.txt
     ```
   - **Start Command**: 
     ```bash
     uvicorn backend.main:app --host 0.0.0.0 --port $PORT --workers 1
     ```
4. **Add Environment Variables**:
   - `GROQ_API_KEY`: Your Groq API key
   - `HF_API_TOKEN`: Your Hugging Face token
   - `PYTHONUNBUFFERED`: `1`
   - `MALLOC_TRIM_THRESHOLD_`: `131072`
   - `MALLOC_MMAP_THRESHOLD_`: `131072`

### Frontend (Vercel)
1. **Push to GitHub** (same repo)
2. **Connect to Vercel**:
   - Go to https://vercel.com
   - Import your GitHub repo
3. **Configure Vercel**:
   - **Framework Preset**: `Create React App`
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `build`
4. **Add Environment Variable**:
   - `REACT_APP_API_URL`: `https://your-render-backend-url.onrender.com`

## Expected Results
- ✅ Backend should start without memory errors
- ✅ Frontend should connect to backend successfully
- ✅ CORS errors should be resolved
- ✅ Chat functionality should work

## Troubleshooting
If backend still crashes:
1. Check Render logs for specific error
2. Try reducing `top_k` in retrieval (change from 3 to 2)
3. Consider using smaller embedding model

## Free Tier Limitations
- **Render**: 512MB RAM, no persistent storage
- **Vercel**: 100GB bandwidth/month
- **Files**: Will be lost on restart (no disk storage)

## Next Steps (Optional)
1. Add external storage (Backblaze B2, AWS S3)
2. Implement file persistence
3. Add user authentication
4. Scale to paid tiers for production use
