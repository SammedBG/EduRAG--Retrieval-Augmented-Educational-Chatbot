"""
RAG Chatbot Package
A Retrieval-Augmented Generation system for document querying
"""

__version__ = "1.0.0"
__author__ = "RAG Chatbot Team"

# Lazy imports to avoid dependency issues during deployment
def get_generate_answer():
    from .chatbot import generate_answer
    return generate_answer

def get_retrieve():
    from .retrieval import retrieve
    return retrieve

def get_create_embeddings():
    from .embeddings import create_embeddings
    return create_embeddings

def get_load_documents():
    from .ingestion import load_documents
    return load_documents

def get_preprocess_documents():
    from .preprocessing import preprocess_documents
    return preprocess_documents

__all__ = [
    "get_generate_answer",
    "get_retrieve", 
    "get_create_embeddings",
    "get_load_documents",
    "get_preprocess_documents"
]
