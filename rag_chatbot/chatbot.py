import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Groq API configuration (Best free option - 14,400 requests/day)
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_API_KEY = os.getenv("GROQ_API_KEY")  # Set this in your .env file

# Alternative: Hugging Face API (1,000 requests/month free)
HF_API_URL = "https://api-inference.huggingface.co/models/microsoft/DialoGPT-large"
HF_API_TOKEN = os.getenv("HF_API_TOKEN")  # Alternative option

def generate_answer_with_groq(retrieved_chunks, query):
    """Generate answer using Groq API (free, fast, high quality)"""
    if not GROQ_API_KEY:
        return generate_answer_with_hf(retrieved_chunks, query)
    
    # Prepare context from retrieved chunks
    context = "\n\n".join([f"From {chunk['file']}:\n{chunk['chunk']}" for chunk in retrieved_chunks])
    
    # Create the prompt
    prompt = f"""Based on the following context, please answer the question clearly and concisely.

Context:
{context}

Question: {query}

Answer:"""
    
    # Prepare the API request
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "model": "llama-3.1-8b-instant",  # Use 8B model (more reliable)
        "max_tokens": 200,
        "temperature": 0.7,
        "top_p": 0.9,
        "stream": False
    }
    
    try:
        response = requests.post(GROQ_API_URL, headers=headers, json=data, timeout=30)
        
        if response.status_code != 200:
            print(f"Groq API error: {response.status_code} - {response.text}")
            return generate_answer_with_hf(retrieved_chunks, query)
        
        result = response.json()
        answer = result['choices'][0]['message']['content'].strip()
        
        if not answer:
            return generate_answer_with_hf(retrieved_chunks, query)
        
        return answer
        
    except Exception as e:
        print(f"Groq API error: {e}")
        return generate_answer_with_hf(retrieved_chunks, query)

def generate_answer_with_hf(retrieved_chunks, query):
    """Generate answer using Hugging Face API"""
    if not HF_API_TOKEN:
        return generate_answer_improved_fallback(retrieved_chunks, query)
    
    # Prepare context from retrieved chunks
    context = "\n\n".join([f"From {chunk['file']}:\n{chunk['chunk']}" for chunk in retrieved_chunks])
    
    # Create the prompt
    prompt = f"Context: {context}\n\nQuestion: {query}\n\nAnswer:"
    
    # Prepare the API request
    headers = {
        "Authorization": f"Bearer {HF_API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    data = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 150,
            "temperature": 0.7,
            "top_p": 0.9,
            "return_full_text": False
        }
    }
    
    try:
        response = requests.post(HF_API_URL, headers=headers, json=data, timeout=30)
        
        if response.status_code != 200:
            print(f"Hugging Face API error: {response.status_code} - {response.text}")
            return generate_answer_improved_fallback(retrieved_chunks, query)
        
        result = response.json()
        if isinstance(result, list) and len(result) > 0:
            answer = result[0].get('generated_text', '').strip()
        else:
            answer = str(result).strip()
        
        if not answer or len(answer) < 10:
            return generate_answer_improved_fallback(retrieved_chunks, query)
        
    return answer
        
    except Exception as e:
        print(f"Hugging Face API error: {e}")
        return generate_answer_improved_fallback(retrieved_chunks, query)

def generate_answer_improved_fallback(retrieved_chunks, query):
    """Improved fallback method that creates better answers"""
    if not retrieved_chunks:
        return "I couldn't find relevant information to answer your question."
    
    # Combine all relevant chunks
    all_text = " ".join([chunk['chunk'] for chunk in retrieved_chunks])
    
    # Look for key information about the query
    query_lower = query.lower()
    
    # Extract relevant sentences
    sentences = all_text.split('. ')
    relevant_sentences = []
    
    for sentence in sentences:
        sentence_lower = sentence.lower()
        # Check if sentence contains query keywords
        if any(keyword in sentence_lower for keyword in query_lower.split()):
            relevant_sentences.append(sentence.strip())
    
    # If no direct matches, look for related terms
    if not relevant_sentences:
        related_terms = {
            'parkinson': ['disease', 'pd', 'neurological', 'movement', 'disorder', 'symptoms'],
            'disease': ['condition', 'illness', 'disorder', 'syndrome', 'medical'],
            'detection': ['diagnosis', 'identification', 'recognition', 'analysis', 'prediction'],
            'handwriting': ['writing', 'drawing', 'spiral', 'pattern', 'motor'],
            'machine learning': ['ai', 'artificial intelligence', 'deep learning', 'neural network', 'algorithm']
        }
        
        for keyword in query_lower.split():
            if keyword in related_terms:
                for term in related_terms[keyword]:
                    for sentence in sentences:
                        if term in sentence.lower():
                            relevant_sentences.append(sentence.strip())
                            break
    
    # Create a comprehensive answer
    if relevant_sentences:
        # Remove duplicates and limit length
        unique_sentences = list(dict.fromkeys(relevant_sentences))[:3]
        
        answer = f"Based on the research documents, here's what I found about {query}:\n\n"
        for i, sentence in enumerate(unique_sentences, 1):
            # Clean up the sentence
            clean_sentence = sentence.replace('\n', ' ').strip()
            if clean_sentence and len(clean_sentence) > 20:
                answer += f"{i}. {clean_sentence}\n\n"
    else:
        # Fallback to first chunk with better formatting
        first_chunk = retrieved_chunks[0]['chunk']
        # Extract the most relevant part
        words = first_chunk.split()
        relevant_part = " ".join(words[:100])  # First 100 words
        
        answer = f"Based on the available research, here's relevant information:\n\n{relevant_part}..."
    
    return answer.strip()

def generate_answer(retrieved_chunks, query, max_new_tokens=80):
    """Main function that tries Groq API first, then fallback"""
    return generate_answer_with_groq(retrieved_chunks, query)

if __name__ == "__main__":
    from retrieval import retrieve
    print("RAG Chatbot is ready! Type 'exit' to quit.")
    while True:
        query = input("\nEnter your question: ")
        if query.lower() in ["exit", "quit"]:
            break
        
        # Retrieve relevant chunks
        results = retrieve(query, top_k=3)
        
        # Debug: Show what was retrieved
        print(f"\nRetrieved {len(results)} relevant chunks:")
        for i, result in enumerate(results, 1):
            print(f"{i}. From {result['file']}: {result['chunk'][:100]}...")
        
        # Generate answer
        print("\n🤖 Generating answer...")
        answer = generate_answer(results, query)
        print(f"\nGenerated Answer:\n{answer}")
