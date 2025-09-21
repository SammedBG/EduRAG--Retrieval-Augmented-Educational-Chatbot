# 400MB Memory Optimization Guide

## Problem Analysis
The previous deployment failed because:
1. **Wrong requirements file**: Used `requirements.txt` (3GB+) instead of minimal version
2. **PyTorch with CUDA**: Downloaded 2.8GB of CUDA libraries
3. **Heavy dependencies**: transformers, accelerate, scikit-learn

## Solution: Ultra-Minimal Stack

### 1. Ultra-Minimal Requirements (`requirements-ultra-minimal.txt`)
```
# Core web framework: ~50MB
fastapi==0.104.1
uvicorn==0.24.0
python-multipart==0.0.6
python-dotenv==1.0.0
aiofiles==23.2.1
boto3==1.34.0

# Minimal ML: ~150MB
sentence-transformers==2.2.2  # Older, lighter version
faiss-cpu==1.7.4             # CPU-only, no CUDA
numpy==1.24.3                # Lighter version

# File processing: ~10MB
PyPDF2==3.0.1
requests==2.31.0
```

### 2. Memory Breakdown (Target: 400MB)
- **Base Python**: ~30MB
- **FastAPI + Dependencies**: ~50MB
- **Sentence Transformers**: ~80MB (L3-v2 model)
- **FAISS Index**: ~30MB (depends on docs)
- **Application Code**: ~30MB
- **Buffer**: ~180MB
- **Total**: ~400MB ✅

### 3. Optimizations Applied

#### Model Selection
- **Primary**: `all-MiniLM-L3-v2` (80MB vs 420MB for larger models)
- **Fallback**: `paraphrase-MiniLM-L3-v2` (even smaller)

#### Batch Processing
- **Batch size**: 4 documents (reduced from 8)
- **Memory cleanup**: Force garbage collection after each batch
- **Model cleanup**: Delete models from memory when not needed

#### Startup Optimization
- **Access logs disabled**: Saves ~20MB
- **Log level**: Warning only (saves ~10MB)
- **Environment variables**: Memory optimization flags

### 4. Render Configuration
```yaml
buildCommand: |
  pip install --no-cache-dir --upgrade pip setuptools wheel
  pip install --no-cache-dir -r backend/requirements-ultra-minimal.txt
startCommand: cd backend && python start_optimized.py
```

### 5. Expected Performance
- **Startup time**: 30-60 seconds
- **Memory usage**: 350-400MB
- **Document limit**: 20-30 PDFs (recommended)
- **Response time**: 2-5 seconds per query

## Deployment Steps

### 1. Commit Changes
```bash
git add .
git commit -m "Ultra-minimal requirements for 400MB limit"
git push origin main
```

### 2. Deploy on Render
1. Go to Render dashboard
2. Connect your GitHub repo
3. Use the `render.yaml` configuration
4. Set environment variables:
   ```
   GROQ_API_KEY=your_key
   AWS_ACCESS_KEY_ID=your_key
   AWS_SECRET_ACCESS_KEY=your_secret
   AWS_S3_BUCKET=your_bucket
   ```

### 3. Monitor Deployment
- Watch build logs for memory usage
- Check if it stays under 400MB
- Monitor startup time

## Troubleshooting

### Still Getting OOM?
1. **Reduce batch size** to 2 in `embeddings_lightweight.py`
2. **Use even smaller model**: `paraphrase-MiniLM-L3-v2`
3. **Limit documents**: Process max 10 PDFs

### Slow Performance?
- Expected on free tier
- Consider upgrading to paid tier for better performance
- Use S3 for file storage to reduce local processing

### Build Fails?
- Check if all dependencies are in `requirements-ultra-minimal.txt`
- Verify no CUDA dependencies are being installed
- Monitor build logs for memory spikes

## Alternative: No ML Dependencies
If still failing, we can create a version that:
- Uses external embedding APIs (OpenAI, Cohere)
- No local ML models
- Even smaller memory footprint (~200MB)

This ultra-minimal setup should work within the 400MB limit!
