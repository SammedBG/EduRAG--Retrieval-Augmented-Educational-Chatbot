"""
RAG Chatbot Package
A Retrieval-Augmented Generation system for document querying
"""

from .chatbot import generate_answer
from .retrieval import retrieve
from .embeddings import create_embeddings
from .ingestion import load_documents
from .preprocessing import preprocess_documents

__version__ = "1.0.0"
__author__ = "RAG Chatbot Team"

__all__ = [
    "generate_answer",
    "retrieve", 
    "create_embeddings",
    "load_documents",
    "preprocess_documents"
]
