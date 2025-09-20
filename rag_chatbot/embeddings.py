import os
import pickle
from sentence_transformers import SentenceTransformer
from .preprocessing import preprocess_documents
from .ingestion import load_documents

# Load the SentenceTransformer model
model = SentenceTransformer('all-MiniLM-L6-v2')  # Lightweight and good for local use

def create_embeddings(chunks, save_path="embeddings/vector_index.pkl"):
    vectors = []
    for chunk in chunks:
        embedding = model.encode(chunk['chunk'])
        vectors.append({
            "file": chunk["file"],
            "chunk": chunk["chunk"],
            "vector": embedding
        })
    # Ensure directory exists
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    with open(save_path, "wb") as f:
        pickle.dump(vectors, f)
    print(f"Saved {len(vectors)} embeddings at {save_path}")

if __name__ == "__main__":
    docs = load_documents()
    chunks = preprocess_documents(docs)
    create_embeddings(chunks)
