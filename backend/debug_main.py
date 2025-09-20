#!/usr/bin/env python3
"""
Minimal FastAPI Backend for debugging deployment issues
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sys
from pathlib import Path

# Add the rag_chatbot module to the path
sys.path.append(str(Path(__file__).parent.parent))

app = FastAPI(
    title="RAG Chatbot API - Debug",
    description="Minimal version for debugging",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Debug API is running!", "status": "healthy"}

@app.get("/health")
async def health_check():
    """Simple health check"""
    return {
        "status": "healthy",
        "healthy": True,
        "embeddings_ready": False,
        "embeddingsReady": False,
        "message": "Debug mode - minimal functionality"
    }

@app.get("/test")
async def test_imports():
    """Test if imports work"""
    try:
        from rag_chatbot.ingestion import load_documents
        from rag_chatbot.preprocessing import preprocess_documents
        from rag_chatbot.embeddings import create_embeddings
        from rag_chatbot.retrieval import retrieve
        from rag_chatbot.chatbot import generate_answer
        return {"imports": "success", "message": "All imports working"}
    except Exception as e:
        return {"imports": "failed", "error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "debug_main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )