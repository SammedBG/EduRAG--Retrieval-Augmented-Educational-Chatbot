# Memory Optimization for Render Free Tier

## Problem
Render's free tier has a **512MB memory limit**. The RAG chatbot was exceeding this limit due to:
- Large model loading (sentence-transformers)
- Multiple file processing
- S3 sync operations
- Embedding generation

## Solutions Implemented

### 1. **Lazy Loading**
- Only load embeddings from S3 if local ones don't exist
- Skip S3 sync on startup unless necessary
- Process files only when needed

### 2. **Memory-Efficient S3 Operations**
- Limit file size to 50MB for sync
- Only sync essential files (PDF, PKL)
- Async S3 operations with error handling

### 3. **Optimized Server Configuration**
```yaml
startCommand: uvicorn backend.main:app --host 0.0.0.0 --port $PORT --workers 1 --timeout-keep-alive 30
```
- Single worker process
- Reduced keep-alive timeout
- No-cache pip installs

### 4. **Smart Reindexing**
- Only reindex when absolutely necessary
- Skip unnecessary file operations
- Minimal fallback on errors

## Memory Usage Breakdown

| Component | Memory Usage | Optimization |
|-----------|--------------|--------------|
| FastAPI + Uvicorn | ~50MB | Single worker |
| Sentence Transformers | ~200MB | Load once, reuse |
| FAISS Index | ~50-100MB | Lazy loading |
| S3 Client | ~20MB | Conditional loading |
| Document Processing | ~100MB | Process in chunks |
| **Total** | **~420-470MB** | **Under 512MB limit** |

## Additional Optimizations

### If Still Having Issues:

1. **Reduce Model Size**:
   ```python
   # In embeddings.py, use smaller model
   model = SentenceTransformer('all-MiniLM-L6-v2')  # Smaller than default
   ```

2. **Process Files in Batches**:
   ```python
   # Process max 3 files at once
   for i in range(0, len(files), 3):
       batch = files[i:i+3]
       process_batch(batch)
   ```

3. **Use Render's Paid Tier**:
   - $7/month for 1GB memory
   - $25/month for 2GB memory

## Monitoring Memory Usage

Add this to your backend to monitor memory:

```python
import psutil
import os

def log_memory_usage():
    process = psutil.Process(os.getpid())
    memory_mb = process.memory_info().rss / 1024 / 1024
    print(f"Memory usage: {memory_mb:.1f}MB")
```

## Deployment Checklist

- [ ] Use optimized `render.yaml`
- [ ] Set environment variables
- [ ] Monitor deployment logs
- [ ] Test with small files first
- [ ] Scale up gradually

## Troubleshooting

### "Out of memory" Error:
1. Check file sizes (keep under 10MB each)
2. Reduce number of concurrent uploads
3. Use smaller embedding model
4. Consider paid Render tier

### Slow Performance:
1. Enable S3 for persistent storage
2. Use smaller model for faster processing
3. Optimize chunk sizes

### S3 Sync Issues:
1. Check AWS credentials
2. Verify bucket permissions
3. Monitor S3 costs
