import pickle
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

# Load the model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Load the saved embeddings
with open("embeddings/vector_index.pkl", "rb") as f:
    data = pickle.load(f)

# Extract vectors and texts
vectors = np.array([item['vector'] for item in data]).astype('float32')
texts = [item['chunk'] for item in data]
files = [item['file'] for item in data]

# Build the FAISS index
index = faiss.IndexFlatL2(vectors.shape[1])
index.add(vectors)
print(f"FAISS index built with {index.ntotal} vectors.")

def retrieve(query, top_k=3):
    query_vector = model.encode(query).astype('float32')
    distances, indices = index.search(np.expand_dims(query_vector, axis=0), top_k)
    results = []
    for idx in indices[0]:
        results.append({
            "file": files[idx],
            "chunk": texts[idx]
        })
    return results

if __name__ == "__main__":
    while True:
        query = input("\nEnter your question (or 'exit' to quit): ")
        if query.lower() in ["exit", "quit"]:
            break
        results = retrieve(query)
        for i, res in enumerate(results, 1):
            print(f"\nResult {i} (from {res['file']}):\n{res['chunk']}")
