import re

def clean_text(text):
    # Remove extra spaces, new lines, and unwanted characters
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def split_text(text, chunk_size=500, overlap=50):
    words = text.split()
    chunks = []
    start = 0
    while start < len(words):
        end = start + chunk_size
        chunk = " ".join(words[start:end])
        chunks.append(chunk)
        start += chunk_size - overlap
    return chunks

def preprocess_documents(documents, chunk_size=500, overlap=50):
    all_chunks = []
    for doc in documents:
        cleaned = clean_text(doc['text'])
        chunks = split_text(cleaned, chunk_size, overlap)
        for chunk in chunks:
            all_chunks.append({
                "file": doc["file"],
                "chunk": chunk
            })
    return all_chunks

if __name__ == "__main__":
    from .ingestion import load_documents
    docs = load_documents()
    chunks = preprocess_documents(docs)
    print(f"Created {len(chunks)} chunks.")
