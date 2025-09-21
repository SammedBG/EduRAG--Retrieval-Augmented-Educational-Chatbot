"""
Lightweight embeddings module optimized for 512MB RAM
Uses smaller models and memory-efficient processing
"""

import pickle
import numpy as np
from pathlib import Path
from sentence_transformers import SentenceTransformer
import faiss
import gc
import os

# Use a smaller, more memory-efficient model
MODEL_NAME = "all-MiniLM-L6-v2"  # Much smaller than default models
EMBEDDINGS_FILE = Path("embeddings/vector_index.pkl")

def get_lightweight_model():
    """Get a memory-efficient sentence transformer model"""
    try:
        # Use a smaller model that fits in 512MB RAM
        model = SentenceTransformer(MODEL_NAME)
        print(f"Loaded lightweight model: {MODEL_NAME}")
        return model
    except Exception as e:
        print(f"Error loading model: {e}")
        # Fallback to even smaller model
        try:
            model = SentenceTransformer("paraphrase-MiniLM-L3-v2")
            print("Loaded fallback model: paraphrase-MiniLM-L3-v2")
            return model
        except Exception as e2:
            print(f"Fallback model failed: {e2}")
            return None

def create_embeddings_lightweight(chunks, batch_size=8):
    """
    Create embeddings with memory optimization
    Processes in small batches to reduce memory usage
    """
    print(f"Creating embeddings for {len(chunks)} chunks with lightweight model...")
    
    # Get lightweight model
    model = get_lightweight_model()
    if not model:
        raise Exception("Could not load any embedding model")
    
    try:
        # Process in small batches to save memory
        all_embeddings = []
        chunk_texts = [chunk['chunk'] for chunk in chunks]
        
        for i in range(0, len(chunk_texts), batch_size):
            batch = chunk_texts[i:i + batch_size]
            print(f"Processing batch {i//batch_size + 1}/{(len(chunk_texts) + batch_size - 1)//batch_size}")
            
            # Create embeddings for this batch
            batch_embeddings = model.encode(batch, show_progress_bar=False)
            all_embeddings.append(batch_embeddings)
            
            # Force garbage collection after each batch
            gc.collect()
        
        # Combine all embeddings
        embeddings = np.vstack(all_embeddings)
        print(f"Created embeddings shape: {embeddings.shape}")
        
        # Create FAISS index with memory optimization
        dimension = embeddings.shape[1]
        index = faiss.IndexFlatIP(dimension)  # Inner product for cosine similarity
        
        # Normalize embeddings for cosine similarity
        faiss.normalize_L2(embeddings)
        index.add(embeddings.astype('float32'))
        
        # Save embeddings and metadata
        EMBEDDINGS_FILE.parent.mkdir(exist_ok=True)
        
        embeddings_data = {
            'index': index,
            'chunks': chunks,
            'model_name': MODEL_NAME,
            'embeddings_shape': embeddings.shape
        }
        
        with open(EMBEDDINGS_FILE, 'wb') as f:
            pickle.dump(embeddings_data, f)
        
        print(f"Saved embeddings to {EMBEDDINGS_FILE}")
        
        # Clean up memory
        del embeddings, index, all_embeddings
        gc.collect()
        
        return True
        
    except Exception as e:
        print(f"Error creating embeddings: {e}")
        # Clean up on error
        gc.collect()
        return False
    finally:
        # Always clean up model
        if 'model' in locals():
            del model
        gc.collect()

def load_embeddings_lightweight():
    """Load embeddings with memory optimization"""
    if not EMBEDDINGS_FILE.exists():
        return None, None
    
    try:
        with open(EMBEDDINGS_FILE, 'rb') as f:
            data = pickle.load(f)
        
        index = data['index']
        chunks = data['chunks']
        
        print(f"Loaded embeddings: {len(chunks)} chunks, model: {data.get('model_name', 'unknown')}")
        return index, chunks
        
    except Exception as e:
        print(f"Error loading embeddings: {e}")
        return None, None

def search_embeddings_lightweight(query, top_k=3):
    """Search embeddings with memory optimization"""
    index, chunks = load_embeddings_lightweight()
    if not index or not chunks:
        return []
    
    try:
        # Get lightweight model for query encoding
        model = get_lightweight_model()
        if not model:
            return []
        
        # Encode query
        query_embedding = model.encode([query])
        faiss.normalize_L2(query_embedding)
        
        # Search
        scores, indices = index.search(query_embedding.astype('float32'), top_k)
        
        # Format results
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < len(chunks):
                results.append({
                    'chunk': chunks[idx]['chunk'],
                    'file': chunks[idx]['file'],
                    'score': float(score)
                })
        
        # Clean up
        del model, query_embedding
        gc.collect()
        
        return results
        
    except Exception as e:
        print(f"Error searching embeddings: {e}")
        gc.collect()
        return []

