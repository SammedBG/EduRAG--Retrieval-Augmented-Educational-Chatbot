#!/usr/bin/env python3
"""
Startup script for backend with error handling
"""
import sys
import os
from pathlib import Path

def main():
    try:
        print("Starting RAG Chatbot Backend...")
        print(f"Python version: {sys.version}")
        print(f"Working directory: {os.getcwd()}")
        
        # Check if required directories exist
        required_dirs = ["data/course_notes", "embeddings"]
        for dir_path in required_dirs:
            Path(dir_path).mkdir(parents=True, exist_ok=True)
            print(f"✓ Directory created: {dir_path}")
        
        # Test imports
        print("Testing imports...")
        sys.path.append(str(Path(__file__).parent))
        
        from rag_chatbot.ingestion import load_documents
        print("✓ Ingestion module imported")
        
        from rag_chatbot.preprocessing import preprocess_documents
        print("✓ Preprocessing module imported")
        
        from rag_chatbot.embeddings import create_embeddings
        print("✓ Embeddings module imported")
        
        from rag_chatbot.retrieval import retrieve
        print("✓ Retrieval module imported")
        
        from rag_chatbot.chatbot import generate_answer
        print("✓ Chatbot module imported")
        
        # Start the server
        print("Starting FastAPI server...")
        import uvicorn
        uvicorn.run(
            "backend.main:app",
            host="0.0.0.0",
            port=int(os.getenv("PORT", 8000)),
            workers=1,
            timeout_keep_alive=30,
            log_level="info"
        )
        
    except Exception as e:
        print(f"❌ Error starting backend: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()