# Render Free Tier Optimization Guide

## Memory Constraints
- **512MB RAM** total
- **1GB disk space** (ephemeral)
- **No persistent storage** on free tier

## Optimizations Applied

### 1. Minimal Dependencies (`requirements-minimal.txt`)
```
# Removed heavy dependencies:
- websockets (not needed for basic chat)
- scikit-learn (not used in core functionality)
- uvicorn[standard] → uvicorn (lighter)

# Kept only essential:
- FastAPI core
- sentence-transformers (lightweight model)
- faiss-cpu (efficient vector search)
- boto3 (S3 integration)
- PyPDF2 (PDF processing)
```

### 2. Lightweight Embeddings (`embeddings_lightweight.py`)
- **Model**: `all-MiniLM-L6-v2` (22MB vs 420MB+ for larger models)
- **Batch processing**: Process documents in small batches (8 at a time)
- **Memory cleanup**: Force garbage collection after each batch
- **Fallback model**: `paraphrase-MiniLM-L3-v2` if primary fails

### 3. Memory Management
- **Garbage collection**: Explicit `gc.collect()` after heavy operations
- **Model cleanup**: Delete models from memory when not needed
- **Batch processing**: Avoid loading all data at once

### 4. Render Configuration (`render.yaml`)
```yaml
buildCommand: |
  pip install --no-cache-dir --upgrade pip setuptools wheel
  pip install --no-cache-dir -r backend/requirements-minimal.txt
startCommand: uvicorn backend.main:app --host 0.0.0.0 --port $PORT --workers 1 --timeout-keep-alive 30
```

## Deployment Steps

### 1. Prepare Repository
```bash
# Remove heavy files
rm -rf .git/hooks
rm -rf __pycache__
rm -rf .pytest_cache

# Ensure .gitignore is correct
```

### 2. Deploy to Render
1. Connect GitHub repo to Render
2. Use `render.yaml` configuration
3. Set environment variables:
   ```
   GROQ_API_KEY=your_key
   AWS_ACCESS_KEY_ID=your_key
   AWS_SECRET_ACCESS_KEY=your_secret
   AWS_S3_BUCKET=your_bucket
   ```

### 3. Monitor Memory Usage
- Check Render logs for memory warnings
- Monitor build process for OOM errors
- Use S3 for file storage to reduce local disk usage

## Expected Performance

### Memory Usage Breakdown
- **Base Python**: ~50MB
- **FastAPI + Dependencies**: ~100MB
- **Sentence Transformer Model**: ~100MB
- **FAISS Index**: ~50MB (depends on document count)
- **Application Code**: ~50MB
- **Buffer**: ~160MB
- **Total**: ~510MB (fits in 512MB limit)

### Limitations
- **Small document collections** (recommended: <50 PDFs)
- **No WebSocket support** (removed to save memory)
- **Single worker** (no horizontal scaling)
- **Slower processing** (due to memory constraints)

## Troubleshooting

### Build Fails with OOM
```bash
# Reduce batch size in embeddings_lightweight.py
batch_size=4  # instead of 8
```

### Runtime Memory Issues
```bash
# Check logs for memory warnings
# Consider reducing document count
# Use smaller embedding model
```

### Slow Performance
- Expected on free tier
- Consider upgrading to paid tier for better performance
- Use S3 for file storage to reduce local processing

## Alternative: Paid Tier
If you need better performance:
- **Starter Plan**: $7/month, 512MB RAM, 1GB disk
- **Standard Plan**: $25/month, 2GB RAM, 10GB disk
- **Pro Plan**: $85/month, 8GB RAM, 50GB disk

The optimizations will work on all tiers, but paid tiers will be much faster.

