# Railway Deployment Guide

## 🚀 Why Railway?

- **1GB RAM** (vs Render's 512MB)
- **1GB Storage** (persistent)
- **Free tier** with generous limits
- **Auto-deploy** from GitHub
- **Perfect for ML models**

## 📋 Step-by-Step Deployment

### 1. Prepare Your Repository

Your repo is already ready! The files are in place:
- ✅ `railway.json` - Railway configuration
- ✅ `nixpacks.toml` - Build configuration
- ✅ `backend/requirements.txt` - Dependencies
- ✅ AWS S3 integration for storage

### 2. Deploy to Railway

1. **Go to**: [railway.app](https://railway.app)
2. **Sign up** with your GitHub account
3. **Click**: "New Project"
4. **Select**: "Deploy from GitHub repo"
5. **Choose**: Your RAG_CHATBOT repository
6. **Click**: "Deploy Now"

### 3. Configure Environment Variables

In Railway dashboard, go to your service → Variables tab and add:

```env
# LLM API Keys (Required)
GROQ_API_KEY=your_groq_api_key_here
HF_API_TOKEN=your_huggingface_token_here

# AWS S3 (Optional - for persistent storage)
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_DEFAULT_REGION=us-east-1
AWS_S3_BUCKET=your_bucket_name

# Railway will auto-set PORT
```

### 4. Get Your API Keys

#### Groq API (Free - 14,400 requests/day)
1. Go to [console.groq.com](https://console.groq.com)
2. Sign up with Google/GitHub
3. Create API key
4. Copy the key

#### Hugging Face API (Free - 1,000 requests/month)
1. Go to [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)
2. Create new token
3. Copy the token

### 5. Deploy Frontend to Vercel

1. **Go to**: [vercel.com](https://vercel.com)
2. **Import** your GitHub repo
3. **Set root directory** to `frontend`
4. **Add environment variable**:
   ```
   REACT_APP_API_URL=https://your-railway-app.railway.app
   ```
5. **Deploy**

## 🔧 Railway Features

### Auto-Deploy
- **Push to main branch** → Auto-deploy
- **Pull requests** → Preview deployments
- **Rollback** with one click

### Monitoring
- **Logs** in real-time
- **Metrics** (CPU, RAM, requests)
- **Health checks** on `/health`

### Scaling
- **Free tier**: 1GB RAM, 1GB storage
- **Pro tier**: $5/month for more resources

## 📊 Resource Usage

Your RAG chatbot will use:
- **~400MB RAM** for models
- **~200MB** for dependencies
- **~100MB** for application
- **Total**: ~700MB (fits in 1GB free tier!)

## 🚨 Troubleshooting

### Build Fails
- Check `railway.json` syntax
- Verify `requirements.txt` has all dependencies
- Check Railway logs for errors

### App Crashes
- Check environment variables are set
- Verify API keys are valid
- Check logs for error messages

### Out of Memory
- Railway will auto-restart
- Consider upgrading to Pro ($5/month)
- Or optimize model loading

## 🎯 Next Steps

1. **Deploy backend** to Railway
2. **Deploy frontend** to Vercel
3. **Test the full application**
4. **Share your RAG chatbot!**

## 💡 Pro Tips

- **Use Railway's CLI** for local development
- **Set up monitoring** for production use
- **Use custom domains** (free on Railway)
- **Enable auto-scaling** if needed

Your RAG chatbot will be live and accessible worldwide! 🌍
