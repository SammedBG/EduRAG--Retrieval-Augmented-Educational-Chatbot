#!/usr/bin/env python3
"""
FastAPI Backend for RAG Chatbot
Handles file uploads, document processing, and chat API
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, Response
import uvicorn
import os
import shutil
import asyncio
from pathlib import Path
import json
from typing import List, Optional
import sys
import time


# Add the rag_chatbot module to the path
sys.path.append(str(Path(__file__).parent.parent))

# Lazy imports to reduce memory usage
def _lazy_import():
    """Import modules only when needed to reduce startup memory"""
    from rag_chatbot.ingestion import load_documents
    from rag_chatbot.preprocessing import preprocess_documents
    from rag_chatbot.embeddings import create_embeddings
    from rag_chatbot.retrieval import retrieve
    from rag_chatbot.chatbot import generate_answer
    return load_documents, preprocess_documents, create_embeddings, retrieve, generate_answer

# S3 Storage Handler (inline to avoid import issues)
import boto3
from botocore.exceptions import ClientError, NoCredentialsError

class S3Storage:
    def __init__(self):
        self.bucket_name = os.getenv('AWS_S3_BUCKET_NAME', 'edurag-chatbot-files')
        self.region = os.getenv('AWS_REGION', 'us-east-1')
        
        # Initialize S3 client
        try:
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
                region_name=self.region
            )
            self.available = True
            print("✅ S3 storage initialized successfully")
        except NoCredentialsError:
            print("⚠️ AWS credentials not found. S3 storage disabled.")
            self.available = False
        except Exception as e:
            print(f"⚠️ S3 initialization failed: {e}")
            self.available = False
    
    def upload_file(self, file_content: bytes, filename: str) -> bool:
        """Upload file to S3"""
        if not self.available:
            return False
            
        try:
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=f"course_notes/{filename}",
                Body=file_content,
                ContentType='application/pdf'
            )
            print(f"✅ Uploaded {filename} to S3")
            return True
        except ClientError as e:
            print(f"❌ Failed to upload {filename} to S3: {e}")
            return False
    
    def list_files(self) -> List[dict]:
        """List all PDF files in S3"""
        if not self.available:
            return []
            
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix='course_notes/'
            )
            
            files = []
            for obj in response.get('Contents', []):
                if obj['Key'].endswith('.pdf'):
                    filename = obj['Key'].split('/')[-1]
                    files.append({
                        'name': filename,
                        'size': obj['Size'],
                        'uploaded': obj['LastModified'].timestamp()
                    })
            return files
        except ClientError as e:
            print(f"❌ Failed to list files from S3: {e}")
            return []
    
    def delete_file(self, filename: str) -> bool:
        """Delete file from S3"""
        if not self.available:
            return False
            
        try:
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=f"course_notes/{filename}"
            )
            print(f"✅ Deleted {filename} from S3")
            return True
        except ClientError as e:
            print(f"❌ Failed to delete {filename} from S3: {e}")
            return False
    
    def download_all_files(self, local_dir: Path) -> List[str]:
        """Download all files from S3 to local directory for processing"""
        if not self.available:
            return []
            
        files = self.list_files()
        downloaded_files = []
        
        for file_info in files:
            filename = file_info['name']
            try:
                response = self.s3_client.get_object(
                    Bucket=self.bucket_name,
                    Key=f"course_notes/{filename}"
                )
                content = response['Body'].read()
                local_path = local_dir / filename
                with open(local_path, 'wb') as f:
                    f.write(content)
                downloaded_files.append(filename)
                print(f"✅ Downloaded {filename} for processing")
            except ClientError as e:
                print(f"❌ Failed to download {filename}: {e}")
        
        return downloaded_files

# Global S3 instance
s3_storage = S3Storage()

app = FastAPI(
    title="RAG Chatbot API",
    description="AI-powered document querying system",
    version="1.0.0"
)

# CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for production
    allow_credentials=False,  # Set to False when using wildcard origins
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Additional CORS headers for all responses
@app.middleware("http")
async def add_cors_headers(request, call_next):
    # Handle preflight requests
    if request.method == "OPTIONS":
        response = Response()
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "*"
        response.headers["Access-Control-Max-Age"] = "86400"
        return response
    
    response = await call_next(request)
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "*"
    response.headers["Access-Control-Max-Age"] = "86400"
    return response

# Create necessary directories
UPLOAD_DIR = Path("uploads")
DATA_DIR = Path("data/course_notes")
EMBEDDINGS_DIR = Path("embeddings")

for directory in [UPLOAD_DIR, DATA_DIR, EMBEDDINGS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# ------- Embeddings auto-detect/reindex helpers -------
EMBEDDINGS_FILE = Path("embeddings/vector_index.pkl")

def _latest_pdf_mtime() -> float:
    latest = 0.0
    if DATA_DIR.exists():
        for file_path in DATA_DIR.glob("*.pdf"):
            try:
                latest = max(latest, file_path.stat().st_mtime)
            except Exception:
                continue
    return latest

def _needs_reindex() -> bool:
    """Return True when embeddings are missing or older than newest PDF."""
    if not EMBEDDINGS_FILE.exists():
        return True
    try:
        emb_mtime = EMBEDDINGS_FILE.stat().st_mtime
    except Exception:
        return True
    return _latest_pdf_mtime() > emb_mtime

def _reindex_documents() -> None:
    load_documents, preprocess_documents, create_embeddings, _, _ = _lazy_import()
    docs = load_documents()
    if not docs:
        # If no docs, remove embeddings file if present
        if EMBEDDINGS_FILE.exists():
            try:
                EMBEDDINGS_FILE.unlink()
            except Exception:
                pass
        return
    chunks = preprocess_documents(docs)
    create_embeddings(chunks)

# Skip auto-detect on startup to reduce memory usage
# Will be done on first request instead

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
            await connection.send_text(message)

manager = ConnectionManager()

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "RAG Chatbot API is running!", "status": "healthy"}


@app.get("/health")
async def health_check():
    """Health check endpoint with on-demand reindex if needed.

    Returns fields in both snake_case and camelCase to match the frontend.
    """
    try:
        # Simple health check without heavy imports
        ready = EMBEDDINGS_FILE.exists()
        return {
            "status": "healthy",
            "healthy": True,
            "embeddings_ready": ready,
            "embeddingsReady": ready,
            "message": "Backend is running successfully"
        }
    except Exception as e:
        # Fallback health response
        return {
            "status": "healthy",
            "healthy": True,
            "embeddings_ready": False,
            "embeddingsReady": False,
            "message": f"Backend is running (limited mode): {str(e)}"
        }


@app.post("/upload")
async def upload_files(files: List[UploadFile] = File(...)):
    """Upload PDF files for processing"""
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded")
    
    uploaded_files = []
    processed_files = []
    
    try:
        # Upload files to S3
        for file in files:
            if not file.filename.lower().endswith('.pdf'):
                raise HTTPException(status_code=400, detail=f"Only PDF files are allowed. Got: {file.filename}")
            
            # Read file content
            file_content = await file.read()
            
            # Upload to S3
            if s3_storage.upload_file(file_content, file.filename):
                uploaded_files.append(file.filename)
            else:
                raise HTTPException(status_code=500, detail=f"Failed to upload {file.filename} to storage")
        
        # Process documents and create embeddings
        await manager.broadcast(json.dumps({
            "type": "processing_start",
            "message": "Processing uploaded documents..."
        }))
        
        # Download files from S3 for processing
        temp_dir = Path("temp_processing")
        temp_dir.mkdir(exist_ok=True)
        
        try:
            # Download all files from S3
            downloaded_files = s3_storage.download_all_files(temp_dir)
            
            if downloaded_files:
                # Load and process documents
                load_documents, preprocess_documents, create_embeddings, _, _ = _lazy_import()
                docs = load_documents()
                chunks = preprocess_documents(docs)
                create_embeddings(chunks)
                
                processed_files = [f for f in uploaded_files]
            else:
                raise HTTPException(status_code=500, detail="No files could be downloaded for processing")
                
        finally:
            # Clean up temp directory
            if temp_dir.exists():
                shutil.rmtree(temp_dir, ignore_errors=True)
        
        await manager.broadcast(json.dumps({
            "type": "processing_complete",
            "message": f"Successfully processed {len(processed_files)} files",
            "files": processed_files
        }))
        
        return {
            "message": f"Successfully uploaded and processed {len(processed_files)} files",
            "uploaded_files": uploaded_files,
            "processed_files": processed_files,
            "embeddings_created": True,
            "storage": "AWS S3" if s3_storage.available else "Local (fallback)"
        }
        
    except Exception as e:
        # Clean up uploaded files on error
        for filename in uploaded_files:
            s3_storage.delete_file(filename)
        
        raise HTTPException(status_code=500, detail=f"Error processing files: {str(e)}")

@app.post("/chat")
async def chat_endpoint(message: dict):
    """Chat endpoint for querying documents"""
    query = message.get("message", "").strip()
    
    if not query:
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    
    try:
        # Ensure embeddings are current
        if _needs_reindex():
            _reindex_documents()

        # Check if embeddings exist
        if not EMBEDDINGS_FILE.exists():
            raise HTTPException(status_code=400, detail="No documents processed yet. Please upload files first.")
        
        # Retrieve relevant chunks
        _, _, _, retrieve, generate_answer = _lazy_import()
        results = retrieve(query, top_k=3)
        
        if not results:
            return {
                "answer": "I couldn't find relevant information in the uploaded documents.",
                "sources": [],
                "status": "no_results"
            }
        
        # Generate answer
        answer = generate_answer(results, query)
        
        # Prepare sources
        sources = []
        for result in results:
            sources.append({
                "file": result["file"],
                "chunk": result["chunk"][:200] + "..." if len(result["chunk"]) > 200 else result["chunk"]
            })
        
        return {
            "answer": answer,
            "sources": sources,
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time chat"""
    await manager.connect(websocket)
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            query = message_data.get("message", "").strip()
            
            if not query:
                await manager.send_personal_message(json.dumps({
                    "type": "error",
                    "message": "Message cannot be empty"
                }), websocket)
                continue
            
            # Send processing status
            await manager.send_personal_message(json.dumps({
                "type": "processing",
                "message": "Searching documents..."
            }), websocket)
            
            try:
                # Check if embeddings exist
                if not Path("embeddings/vector_index.pkl").exists():
                    await manager.send_personal_message(json.dumps({
                        "type": "error",
                        "message": "No documents processed yet. Please upload files first."
                    }), websocket)
                    continue
                
                # Retrieve relevant chunks
                _, _, _, retrieve, generate_answer = _lazy_import()
                results = retrieve(query, top_k=3)
                
                if not results:
                    await manager.send_personal_message(json.dumps({
                        "type": "response",
                        "answer": "I couldn't find relevant information in the uploaded documents.",
                        "sources": []
                    }), websocket)
                    continue
                
                # Send sources
                sources = []
                for result in results:
                    sources.append({
                        "file": result["file"],
                        "chunk": result["chunk"][:200] + "..." if len(result["chunk"]) > 200 else result["chunk"]
                    })
                
                await manager.send_personal_message(json.dumps({
                    "type": "sources",
                    "sources": sources
                }), websocket)
                
                # Generate and send answer
                await manager.send_personal_message(json.dumps({
                    "type": "generating",
                    "message": "Generating answer..."
                }), websocket)
                
                answer = generate_answer(results, query)
                
                await manager.send_personal_message(json.dumps({
                    "type": "response",
                    "answer": answer,
                    "sources": sources
                }), websocket)
                
            except Exception as e:
                await manager.send_personal_message(json.dumps({
                    "type": "error",
                    "message": f"Error processing query: {str(e)}"
                }), websocket)
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.get("/files")
async def list_files():
    """List uploaded files"""
    try:
        if s3_storage.available:
            # Get files from S3
            files = s3_storage.list_files()
            return {"files": files, "storage": "AWS S3"}
        else:
            # Fallback to local storage
            files = []
            if DATA_DIR.exists():
                for file_path in DATA_DIR.glob("*.pdf"):
                    files.append({
                        "name": file_path.name,
                        "size": file_path.stat().st_size,
                        "uploaded": file_path.stat().st_mtime
                    })
            return {"files": files, "storage": "Local (fallback)"}
    except Exception as e:
        return {"files": [], "error": str(e), "storage": "Error"}

@app.delete("/files/{filename}")
async def delete_file(filename: str):
    """Delete a specific file"""
    try:
        if s3_storage.available:
            # Delete from S3
            if s3_storage.delete_file(filename):
                # Recreate embeddings after file deletion
                _reindex_documents()
                return {"message": f"File {filename} deleted successfully from S3"}
            else:
                raise HTTPException(status_code=404, detail="File not found in S3")
        else:
            # Fallback to local storage
            file_path = DATA_DIR / filename
            if not file_path.exists():
                raise HTTPException(status_code=404, detail="File not found")
            
            file_path.unlink()
            
            # Recreate embeddings after file deletion
            _reindex_documents()
            
            return {"message": f"File {filename} deleted successfully from local storage"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting file: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
