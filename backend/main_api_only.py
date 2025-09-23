"""
FastAPI backend for RAG Chatbot - API-only version
No local ML models, uses external APIs for everything
"""

import os
import sys
import json
import pickle
from pathlib import Path
from typing import List, Optional
import asyncio
from datetime import datetime

from fastapi import FastAPI, File, UploadFile, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

# Add the rag_chatbot module to the path
sys.path.append(str(Path(__file__).parent.parent))

from rag_chatbot.ingestion import load_documents
from rag_chatbot.preprocessing import preprocess_documents
from s3_storage import s3_storage

app = FastAPI(
    title="RAG Chatbot API",
    description="AI-powered document querying system (API-only version)",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# File paths
UPLOAD_DIR = Path("data/course_notes")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Global variables
PROCESSING_STATUS = {"status": "idle", "message": "Ready to process documents"}
FILES_LIST = []

# Initialize S3 storage and sync on startup
def _initialize_storage():
    """Initialize storage and sync from S3 if available"""
    try:
        # Sync S3 to local on startup
        s3_storage.sync_s3_to_local("data", "data")
        print("S3 sync completed")
    except Exception as e:
        print(f"Storage initialization failed: {e}")

# Run initialization on startup
_initialize_storage()

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                # Remove disconnected connections
                self.active_connections.remove(connection)

manager = ConnectionManager()

@app.get("/")
async def root():
    return {"message": "RAG Chatbot API - API-only version"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check if we have any documents
        docs = load_documents()
        ready = len(docs) > 0
        
        return {
            "status": "healthy",
            "healthy": True,
            "embeddings_ready": ready,
            "embeddingsReady": ready,
            "documents_count": len(docs),
            "version": "api-only"
        }
    except Exception as e:
        return {
            "status": "error",
            "healthy": False,
            "error": str(e),
            "version": "api-only"
        }

@app.post("/upload")
async def upload_files(files: List[UploadFile] = File(...)):
    """Upload PDF files"""
    global PROCESSING_STATUS, FILES_LIST
    
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")
    
    uploaded_files = []
    
    try:
        for file in files:
            if not file.filename.lower().endswith('.pdf'):
                raise HTTPException(status_code=400, detail=f"File {file.filename} is not a PDF")
            
            # Save file
            file_path = UPLOAD_DIR / file.filename
            with open(file_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)
            
            uploaded_files.append({
                "name": file.filename,
                "size": len(content),
                "uploaded": datetime.now().timestamp()
            })
        
        # Update global files list
        FILES_LIST.extend(uploaded_files)
        
        # Sync to S3
        s3_storage.sync_local_to_s3("data", "data")
        
        return {
            "message": f"Successfully uploaded {len(uploaded_files)} files",
            "files": uploaded_files
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading files: {str(e)}")

@app.post("/chat")
async def chat_endpoint(request: dict):
    """Chat endpoint - API-only version"""
    query = request.get("query", "").strip()
    
    if not query:
        raise HTTPException(status_code=400, detail="Query is required")
    
    try:
        # Load documents
        docs = load_documents()
        if not docs:
            return {
                "answer": "No documents available. Please upload PDF files first.",
                "sources": []
            }
        
        # Simple text search (no embeddings)
        relevant_chunks = []
        query_lower = query.lower()
        
        for doc in docs:
            text = doc.get('content', '').lower()
            if any(word in text for word in query_lower.split()):
                # Extract relevant sentences
                sentences = doc.get('content', '').split('. ')
                for sentence in sentences:
                    if any(word in sentence.lower() for word in query_lower.split()):
                        relevant_chunks.append({
                            'chunk': sentence,
                            'file': doc.get('file', 'unknown')
                        })
                        if len(relevant_chunks) >= 3:  # Limit to 3 chunks
                            break
        
        # Generate answer using external API
        answer = generate_answer_api_only(relevant_chunks, query)
        
        return {
            "answer": answer,
            "sources": [{"file": chunk['file'], "content": chunk['chunk'][:100] + "..."} for chunk in relevant_chunks[:3]]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

def generate_answer_api_only(retrieved_chunks, query):
    """Generate answer using external APIs only"""
    import requests
    import os
    
    # Try Groq API first
    groq_api_key = os.getenv("GROQ_API_KEY")
    if groq_api_key and retrieved_chunks:
        try:
            context = "\n\n".join([f"From {chunk['file']}:\n{chunk['chunk']}" for chunk in retrieved_chunks])
            
            headers = {
                "Authorization": f"Bearer {groq_api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "messages": [
                    {
                        "role": "user",
                        "content": f"Based on the following context, please answer the question clearly and concisely.\n\nContext:\n{context}\n\nQuestion: {query}\n\nAnswer:"
                    }
                ],
                "model": "llama-3.1-8b-instant",
                "max_tokens": 200,
                "temperature": 0.7
            }
            
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content'].strip()
        except Exception as e:
            print(f"Groq API error: {e}")
    
    # Fallback to simple text response
    if retrieved_chunks:
        return f"Based on the documents, here's what I found about '{query}':\n\n" + "\n\n".join([chunk['chunk'] for chunk in retrieved_chunks[:2]])
    else:
        return f"I couldn't find specific information about '{query}' in the uploaded documents. Please try rephrasing your question or upload more relevant documents."

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time chat"""
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message.get("type") == "chat":
                query = message.get("query", "")
                
                # Send typing indicator
                await manager.send_personal_message(
                    json.dumps({"type": "typing", "message": "Thinking..."}),
                    websocket
                )
                
                # Process query
                try:
                    # Load documents
                    docs = load_documents()
                    if not docs:
                        await manager.send_personal_message(
                            json.dumps({
                                "type": "response",
                                "answer": "No documents available. Please upload PDF files first.",
                                "sources": []
                            }),
                            websocket
                        )
                        continue
                    
                    # Simple text search
                    relevant_chunks = []
                    query_lower = query.lower()
                    
                    for doc in docs:
                        text = doc.get('content', '').lower()
                        if any(word in text for word in query_lower.split()):
                            sentences = doc.get('content', '').split('. ')
                            for sentence in sentences:
                                if any(word in sentence.lower() for word in query_lower.split()):
                                    relevant_chunks.append({
                                        'chunk': sentence,
                                        'file': doc.get('file', 'unknown')
                                    })
                                    if len(relevant_chunks) >= 3:
                                        break
                    
                    # Generate answer
                    answer = generate_answer_api_only(relevant_chunks, query)
                    
                    await manager.send_personal_message(
                        json.dumps({
                            "type": "response",
                            "answer": answer,
                            "sources": [{"file": chunk['file'], "content": chunk['chunk'][:100] + "..."} for chunk in relevant_chunks[:3]]
                        }),
                        websocket
                    )
                    
                except Exception as e:
                    await manager.send_personal_message(
                        json.dumps({
                            "type": "error",
                            "message": f"Error processing query: {str(e)}"
                        }),
                        websocket
                    )
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.get("/files")
async def list_files():
    """List uploaded files"""
    try:
        files = []
        for file_path in UPLOAD_DIR.glob("*.pdf"):
            stat = file_path.stat()
            files.append({
                "name": file_path.name,
                "size": stat.st_size,
                "uploaded": stat.st_mtime
            })
        
        return {"files": files}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing files: {str(e)}")

@app.delete("/files/{filename}")
async def delete_file(filename: str):
    """Delete a specific file"""
    file_path = UPLOAD_DIR / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    try:
        file_path.unlink()
        
        # Sync to S3 after deletion
        s3_storage.sync_local_to_s3("data", "data")
        
        return {"message": f"File {filename} deleted successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting file: {str(e)}")

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "main_api_only:app",
        host="0.0.0.0",
        port=port,
        reload=False,
        log_level="info"
    )
