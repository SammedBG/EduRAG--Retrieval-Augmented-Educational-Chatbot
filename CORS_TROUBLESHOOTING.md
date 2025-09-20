# CORS Troubleshooting Guide

## Problem
Cross-Origin Resource Sharing (CORS) errors occur when the frontend and backend are on different domains.

## Current Configuration

### Backend (FastAPI)
- **Service Name**: `rag-chatbot-backend`
- **URL**: `https://rag-chatbot-backend.onrender.com`
- **CORS Origins**: 
  - `http://localhost:3000` (local development)
  - `https://rag-chatbot-backend.onrender.com`
  - `https://*.onrender.com` (all Render services)
  - `*` (allow all origins for development)

### Frontend (React)
- **Default API URL**: `https://rag-chatbot-backend.onrender.com`
- **Environment Variable**: `REACT_APP_API_URL`

## Common CORS Errors

### 1. "Access to fetch at 'URL' from origin 'URL' has been blocked by CORS policy"

**Solution**: Check if the frontend URL is in the backend's CORS origins list.

### 2. "Preflight request doesn't pass access control check"

**Solution**: Ensure OPTIONS method is allowed and preflight handler exists.

### 3. "Response to preflight request doesn't pass access control check"

**Solution**: Check that all required headers are allowed.

## Debugging Steps

### 1. Check Backend CORS Configuration
```python
# In backend/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://rag-chatbot-backend.onrender.com",
        "https://*.onrender.com",
        "*"  # Allow all origins for development
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)
```

### 2. Check Frontend API URL
```javascript
// In frontend/src/App.js
const API_BASE_URL = process.env.REACT_APP_API_URL || 'https://rag-chatbot-backend.onrender.com';
```

### 3. Test Backend Directly
Visit: `https://rag-chatbot-backend.onrender.com/health`

Should return:
```json
{
  "status": "healthy",
  "healthy": true,
  "embeddings_ready": true,
  "embeddingsReady": true,
  "message": "Backend is running successfully"
}
```

### 4. Check Browser Console
Look for CORS errors in the browser's developer console.

### 5. Test with curl
```bash
curl -H "Origin: https://your-frontend-url.com" \
     -H "Access-Control-Request-Method: GET" \
     -H "Access-Control-Request-Headers: X-Requested-With" \
     -X OPTIONS \
     https://rag-chatbot-backend.onrender.com/health
```

## Environment Variables

### For Local Development
Create `.env` file in frontend directory:
```env
REACT_APP_API_URL=http://localhost:8000
```

### For Production
Set in Vercel/Render dashboard:
```env
REACT_APP_API_URL=https://rag-chatbot-backend.onrender.com
```

## Quick Fixes

### 1. Allow All Origins (Development Only)
```python
allow_origins=["*"]
```

### 2. Add Specific Origin
```python
allow_origins=[
    "https://your-frontend-url.com",
    "https://*.vercel.app",
    "https://*.onrender.com"
]
```

### 3. Enable Credentials
```python
allow_credentials=True
```

## Testing Checklist

- [ ] Backend is running and accessible
- [ ] Frontend URL is in CORS origins
- [ ] OPTIONS method is allowed
- [ ] Required headers are allowed
- [ ] Environment variables are set correctly
- [ ] No typos in URLs
- [ ] Both services are deployed and running

## Common Issues

### 1. Wrong Service Name
- Check Render dashboard for actual service name
- Update CORS origins accordingly

### 2. HTTPS vs HTTP
- Ensure both frontend and backend use HTTPS in production
- Use HTTP only for local development

### 3. Environment Variables
- Check if `REACT_APP_API_URL` is set correctly
- Restart frontend after changing environment variables

### 4. Cache Issues
- Clear browser cache
- Hard refresh (Ctrl+F5)
- Restart both frontend and backend

## Still Having Issues?

1. Check Render logs for backend errors
2. Check Vercel logs for frontend errors
3. Use browser developer tools to inspect network requests
4. Test with Postman or curl to isolate the issue
