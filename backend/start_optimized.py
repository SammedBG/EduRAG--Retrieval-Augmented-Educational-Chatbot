"""
Memory-optimized startup script for Render free tier
"""

import os
import gc
import sys
from pathlib import Path

# Set memory optimization environment variables
os.environ['PYTHONHASHSEED'] = '0'
os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
os.environ['PYTHONUNBUFFERED'] = '1'

# Force garbage collection
gc.collect()

# Add the rag_chatbot module to the path
sys.path.append(str(Path(__file__).parent.parent))

def main():
    """Start the FastAPI app with memory optimization"""
    try:
        import uvicorn
        from main import app
        
        # Additional memory optimization
        gc.collect()
        
        # Start with minimal workers and memory settings
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=int(os.environ.get("PORT", 8000)),
            workers=1,
            timeout_keep_alive=30,
            access_log=False,  # Disable access logs to save memory
            log_level="warning"  # Reduce logging to save memory
        )
    except Exception as e:
        print(f"Failed to start application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
