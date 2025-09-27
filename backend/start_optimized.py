"""
Optimized startup script for Render deployment
Handles memory optimization and graceful fallbacks
"""

import os
import sys
import gc
import psutil
from pathlib import Path

# Add the rag_chatbot module to the path
sys.path.append(str(Path(__file__).parent.parent))

def optimize_memory():
    """Optimize memory usage for free tier"""
    try:
        # Force garbage collection
        gc.collect()
        
        # Get memory info
        memory = psutil.virtual_memory()
        print(f"Available memory: {memory.available / (1024**3):.2f} GB")
        
        # Set environment variables for memory optimization
        os.environ['PYTORCH_CUDA_ALLOC_CONF'] = 'max_split_size_mb:128'
        os.environ['TOKENIZERS_PARALLELISM'] = 'false'
        
        # Limit OpenMP threads
        os.environ['OMP_NUM_THREADS'] = '1'
        os.environ['MKL_NUM_THREADS'] = '1'
        
        print("Memory optimization applied")
        
    except Exception as e:
        print(f"Memory optimization failed: {e}")

def check_dependencies():
    """Check if all required dependencies are available"""
    missing_deps = []
    
    try:
        import fastapi
        import uvicorn
        import websockets
        import boto3
        import requests
        import numpy
        print("✅ Core dependencies available")
    except ImportError as e:
        missing_deps.append(str(e))
    
    # Check ML dependencies (optional)
    ml_deps_available = True
    try:
        import torch
        import transformers
        import sentence_transformers
        import faiss
        print("✅ ML dependencies available")
    except ImportError as e:
        print(f"⚠️ ML dependencies missing: {e}")
        ml_deps_available = False
    
    if missing_deps:
        print(f"❌ Missing core dependencies: {missing_deps}")
        return False
    
    return True, ml_deps_available

def main():
    """Main startup function"""
    print("🚀 Starting RAG Chatbot Backend (Optimized)")
    
    # Optimize memory
    optimize_memory()
    
    # Check dependencies
    deps_ok, ml_available = check_dependencies()
    if not deps_ok:
        print("❌ Critical dependencies missing. Exiting.")
        sys.exit(1)
    
    if not ml_available:
        print("⚠️ Running in API-only mode (no local ML models)")
        os.environ['ML_MODELS_DISABLED'] = 'true'
    else:
        print("✅ Full ML mode enabled")
        os.environ['ML_MODELS_DISABLED'] = 'false'
    
    # Import and start the app
    try:
        from main import app
        import uvicorn
        
        # Get port from environment (Render requirement)
        port = int(os.environ.get('PORT', 8000))
        
        print(f"🌐 Starting server on port {port}")
        print("📊 Health check: http://localhost:{}/health".format(port))
        
        # Start with optimized settings
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=port,
            workers=1,  # Single worker for free tier
            log_level="info",
            access_log=True
        )
        
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
