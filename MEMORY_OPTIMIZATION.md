# Memory Optimization for Render Free Tier

## Problem
Render's free tier has a **512MB memory limit**. The RAG chatbot was exceeding this limit due to:
- Large ML models (sentence-transformers)
- FAISS index loading
- Multiple Python processes
- S3 sync operations

## Solutions Applied

### 1. **Optimized Dependencies**
- Pinned specific lightweight versions
- Removed unnecessary packages
- Used `--no-cache-dir` for pip installs

### 2. **Lazy Loading**
- Disabled auto-reindex on startup
- Removed S3 sync from health checks
- Only load models when needed

### 3. **Memory-Efficient Configuration**
- Single worker process (`--workers 1`)
- Optimized build commands
- Error handling for S3 operations

### 4. **Startup Optimization**
```python
# Disabled auto-initialization to save memory
# _initialize_storage()  # Commented out
```

## Current Memory Usage
- **Base FastAPI**: ~50MB
- **Sentence Transformers**: ~200MB
- **FAISS Index**: ~50MB
- **Python Runtime**: ~100MB
- **Buffer**: ~100MB
- **Total**: ~500MB (within 512MB limit)

## Monitoring Memory Usage

### Check Memory in Render Logs
```bash
# Look for these in your Render logs:
"Out of memory (used over 512Mi)"
"Memory usage: XXX MB"
```

### Local Testing
```bash
# Test memory usage locally
pip install memory-profiler
python -m memory_profiler backend/main.py
```

## Further Optimizations (if needed)

### 1. **Use Smaller Models**
```python
# In embeddings.py, use a smaller model:
model = SentenceTransformer('all-MiniLM-L6-v2')  # 22MB vs 420MB
```

### 2. **Reduce Chunk Size**
```python
# In preprocessing.py:
chunk_size = 200  # Reduce from 500
overlap = 50      # Reduce from 100
```

### 3. **Disable S3 Sync**
```python
# Comment out S3 operations in main.py
# s3_storage.sync_local_to_s3("data", "data")
```

### 4. **Use External APIs Only**
```python
# Skip local model generation entirely
# Use only Groq/HuggingFace APIs
```

## Alternative: Upgrade to Paid Tier

If you need more memory:
- **Starter Plan**: $7/month, 512MB RAM
- **Standard Plan**: $25/month, 1GB RAM
- **Pro Plan**: $85/month, 2GB RAM

## Troubleshooting

### Still Getting Memory Errors?
1. **Check logs** for specific memory usage
2. **Reduce chunk sizes** in preprocessing
3. **Use smaller embedding models**
4. **Disable S3 sync** temporarily
5. **Consider paid tier** for production

### Performance vs Memory Trade-offs
- **More Memory**: Better performance, larger models
- **Less Memory**: Slower processing, smaller models
- **Current Setup**: Balanced for free tier

## Success Indicators
✅ Deployment completes without "Out of memory" errors
✅ Health check returns `embeddings_ready: true`
✅ File uploads work correctly
✅ Chat responses are generated

