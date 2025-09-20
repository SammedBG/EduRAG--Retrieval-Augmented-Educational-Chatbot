# Startup Fix for Missing Embeddings

## Problem
```
FileNotFoundError: [Errno 2] No such file or directory: 'embeddings/vector_index.pkl'
```

## Root Cause
The `retrieval.py` module was trying to load embeddings immediately on import, but the file doesn't exist on first deployment.

## Solution Applied

### ✅ **Lazy Loading in retrieval.py**
```python
# OLD: Immediate loading on import
with open("embeddings/vector_index.pkl", "rb") as f:
    data = pickle.load(f)

# NEW: Lazy loading when needed
def _load_embeddings():
    if not os.path.exists(embeddings_file):
        print("No embeddings found. Please upload documents first.")
        return
```

### ✅ **Error Handling**
```python
def retrieve(query, top_k=3):
    _load_embeddings()  # Load only when needed
    
    if model is None or index is None:
        return []  # Graceful fallback
```

### ✅ **Better Health Check**
```python
return {
    "embeddings_ready": ready,
    "message": "Upload documents to create embeddings" if not ready else "Ready for queries"
}
```

## How It Works Now

### **1. Startup (No Embeddings)**
- ✅ App starts successfully
- ✅ Health check returns `embeddings_ready: false`
- ✅ Frontend shows "Upload documents first"

### **2. After Upload**
- ✅ Documents get processed
- ✅ Embeddings get created
- ✅ Health check returns `embeddings_ready: true`
- ✅ Chat becomes available

### **3. Chat Functionality**
- ✅ If embeddings exist: Normal retrieval
- ✅ If no embeddings: Returns empty results gracefully

## Benefits

1. **No Startup Crashes**: App starts even without embeddings
2. **Graceful Degradation**: Chat works but returns empty results
3. **Clear User Feedback**: Health check tells user what to do
4. **Memory Efficient**: Only loads embeddings when needed

## Testing

### Local Test:
```bash
# Should start without errors
python backend/main.py

# Health check should return:
# {"embeddings_ready": false, "message": "Upload documents to create embeddings"}
```

### Deploy Test:
1. Deploy to Render
2. Check health endpoint: `/health`
3. Should return `embeddings_ready: false`
4. Upload documents
5. Should return `embeddings_ready: true`

## Expected Result
✅ App starts successfully on Render
✅ No more FileNotFoundError
✅ Health check works correctly
✅ User can upload documents to create embeddings
✅ Chat works after embeddings are created
