#!/usr/bin/env python3
"""
Minimal test version to isolate startup issues
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI(title="RAG Chatbot API Test")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Test API is running", "status": "ok"}

@app.get("/health")
async def health():
    return {"status": "healthy", "message": "Test endpoint working"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
