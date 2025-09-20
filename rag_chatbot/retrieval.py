import pickle
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
import os

# Global variables for lazy loading
model = None
index = None
texts = []
files = []

def _load_embeddings():
    """Load embeddings and build index if available"""
    global model, index, texts, files
    
    if model is not None:
        return  # Already loaded
    
    # Load the model
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    # Check if embeddings file exists
    embeddings_file = "embeddings/vector_index.pkl"
    if not os.path.exists(embeddings_file):
        print("No embeddings found. Please upload documents first.")
        return
    
    try:
        # Load the saved embeddings
        with open(embeddings_file, "rb") as f:
            data = pickle.load(f)
        
        # Extract vectors and texts
        vectors = np.array([item['vector'] for item in data]).astype('float32')
        texts = [item['chunk'] for item in data]
        files = [item['file'] for item in data]
        
        # Build the FAISS index
        index = faiss.IndexFlatL2(vectors.shape[1])
        index.add(vectors)
        print(f"FAISS index built with {index.ntotal} vectors.")
        
    except Exception as e:
        print(f"Error loading embeddings: {e}")
        model = None
        index = None
        texts = []
        files = []

def retrieve(query, top_k=3):
    """Retrieve relevant chunks for a query"""
    # Load embeddings if not already loaded
    _load_embeddings()
    
    # Check if embeddings are available
    if model is None or index is None:
        return []
    
    try:
        query_vector = model.encode(query).astype('float32')
        distances, indices = index.search(np.expand_dims(query_vector, axis=0), top_k)
        results = []
        for idx in indices[0]:
            results.append({
                "file": files[idx],
                "chunk": texts[idx]
            })
        return results
    except Exception as e:
        print(f"Error during retrieval: {e}")
        return []

if __name__ == "__main__":
    # Load embeddings first
    _load_embeddings()
    
    if model is None or index is None:
        print("No embeddings available. Please run the ingestion process first.")
        exit(1)
    
    while True:
        query = input("\nEnter your question (or 'exit' to quit): ")
        if query.lower() in ["exit", "quit"]:
            break
        results = retrieve(query)
        for i, res in enumerate(results, 1):
            print(f"\nResult {i} (from {res['file']}):\n{res['chunk']}")
