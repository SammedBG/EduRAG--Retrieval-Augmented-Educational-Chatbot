# Deployment Fix for Import Error

## Problem
```
ImportError: cannot import name 'cached_download' from 'huggingface_hub'
```

## Root Cause
Version incompatibility between:
- `sentence-transformers==2.2.2` (expects old API)
- `huggingface-hub` (newer version with renamed functions)

## Solution Applied

### 1. **Pinned Compatible Versions**
```txt
sentence-transformers==2.2.2
huggingface-hub==0.16.4  # Compatible version
```

### 2. **Upgraded Build Process**
```yaml
buildCommand: |
  pip install --no-cache-dir --upgrade pip
  pip install --no-cache-dir -r backend/requirements.txt
```

## Why This Fixes It

- **`huggingface-hub==0.16.4`** has the `cached_download` function
- **`sentence-transformers==2.2.2`** expects this function
- **Compatible versions** prevent import errors

## Alternative Solutions (if needed)

### Option 1: Use Newer sentence-transformers
```txt
sentence-transformers==2.7.0
huggingface-hub==0.20.0
```

### Option 2: Use Different Embedding Model
```python
# In embeddings.py, use a different approach
from transformers import AutoModel, AutoTokenizer
```

### Option 3: Use External API Only
```python
# Skip local embeddings entirely
# Use only Groq/HuggingFace APIs
```

## Testing the Fix

1. **Local Test**:
   ```bash
   pip install -r backend/requirements.txt
   python -c "from sentence_transformers import SentenceTransformer; print('OK')"
   ```

2. **Deploy Test**:
   - Push changes to GitHub
   - Deploy on Render
   - Check logs for import errors

## Expected Result
✅ No more `ImportError: cannot import name 'cached_download'`
✅ App starts successfully
✅ All functionality works as expected

## If Still Failing

Try this alternative requirements.txt:
```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-multipart==0.0.6
websockets==12.0
python-dotenv==1.0.0
aiofiles==23.2.1
boto3==1.34.0
# Alternative: Use newer compatible versions
sentence-transformers==2.7.0
huggingface-hub==0.20.0
faiss-cpu==1.7.4
PyPDF2==3.0.1
requests==2.31.0
```
