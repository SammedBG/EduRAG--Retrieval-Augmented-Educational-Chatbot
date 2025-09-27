"""
Simple startup script for Render deployment (no psutil dependency)
"""

import os
import sys
from pathlib import Path

# Add the rag_chatbot module to the path
sys.path.append(str(Path(__file__).parent.parent))

def main():
    """Main startup function"""
    print("🚀 Starting RAG Chatbot Backend (Simple)")
    
    # Set environment variables for optimization
    os.environ['PYTORCH_CUDA_ALLOC_CONF'] = 'max_split_size_mb:128'
    os.environ['TOKENIZERS_PARALLELISM'] = 'false'
    os.environ['OMP_NUM_THREADS'] = '1'
    os.environ['MKL_NUM_THREADS'] = '1'
    
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
