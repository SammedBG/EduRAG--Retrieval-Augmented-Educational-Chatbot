#!/usr/bin/env python3
"""
RAG Chatbot - Main Entry Point
A Retrieval-Augmented Generation chatbot for querying research documents
"""

import os
import sys
from pathlib import Path

# Add the rag_chatbot module to the path
sys.path.append(str(Path(__file__).parent))

from rag_chatbot.retrieval import retrieve
from rag_chatbot.chatbot import generate_answer

def print_banner():
    """Print a welcome banner"""
    print("=" * 60)
    print("🤖 RAG CHATBOT - Research Document Assistant")
    print("=" * 60)
    print("📚 Query your research documents with AI-powered answers")
    print("💡 Type 'help' for commands, 'exit' to quit")
    print("=" * 60)

def print_help():
    """Print help information"""
    print("\n📖 Available Commands:")
    print("  help     - Show this help message")
    print("  exit     - Exit the chatbot")
    print("  quit     - Exit the chatbot")
    print("  clear    - Clear the screen")
    print("  status   - Show system status")
    print("\n💡 Example Questions:")
    print("  • What is Parkinson's disease?")
    print("  • How is Parkinson's disease detected?")
    print("  • What are the symptoms of Parkinson's?")
    print("  • What machine learning methods are used?")

def show_status():
    """Show system status"""
    print("\n🔍 System Status:")
    
    # Check if embeddings exist
    embeddings_path = Path("embeddings/vector_index.pkl")
    if embeddings_path.exists():
        print("  ✅ Document embeddings: Ready")
    else:
        print("  ❌ Document embeddings: Not found")
        print("     Run: python rag_chatbot/embeddings.py")
    
    # Check data directories
    data_dirs = ["data/course_notes", "data/past_papers"]
    for dir_path in data_dirs:
        if Path(dir_path).exists() and any(Path(dir_path).iterdir()):
            file_count = len(list(Path(dir_path).glob("*")))
            print(f"  ✅ {dir_path}: {file_count} files")
        else:
            print(f"  ❌ {dir_path}: No files found")
    
    # Check API keys
    from dotenv import load_dotenv
    load_dotenv()
    
    groq_key = os.getenv("GROQ_API_KEY")
    hf_token = os.getenv("HF_API_TOKEN")
    
    print(f"  🔑 Groq API: {'✅ Configured' if groq_key else '❌ Not set'}")
    print(f"  🔑 Hugging Face API: {'✅ Configured' if hf_token else '❌ Not set'}")

def main():
    """Main chatbot loop"""
    print_banner()
    
    # Check if embeddings exist
    if not Path("embeddings/vector_index.pkl").exists():
        print("\n⚠️  Warning: Document embeddings not found!")
        print("   Please run: python rag_chatbot/embeddings.py")
        print("   This will process your documents and create embeddings.")
        print("\n   Continue anyway? (y/n): ", end="")
        if input().lower() != 'y':
            print("Exiting...")
            return
    
    print("\n🚀 RAG Chatbot is ready! Ask me anything about your research documents.")
    
    while True:
        try:
            # Get user input
            query = input("\n💬 Your question: ").strip()
            
            # Handle commands
            if query.lower() in ["exit", "quit"]:
                print("\n👋 Thank you for using RAG Chatbot! Goodbye!")
                break
            elif query.lower() == "help":
                print_help()
                continue
            elif query.lower() == "clear":
                os.system('cls' if os.name == 'nt' else 'clear')
                print_banner()
                continue
            elif query.lower() == "status":
                show_status()
                continue
            elif not query:
                print("Please enter a question or command.")
                continue
            
            # Process the query
            print("\n🔍 Searching documents...")
            results = retrieve(query, top_k=3)
            
            if not results:
                print("❌ No relevant information found in the documents.")
                continue
            
            # Show retrieved chunks
            print(f"\n📄 Found {len(results)} relevant sections:")
            for i, result in enumerate(results, 1):
                print(f"  {i}. From {result['file']}: {result['chunk'][:80]}...")
            
            # Generate answer
            print("\n🤖 Generating answer...")
            answer = generate_answer(results, query)
            
            # Display answer
            print(f"\n💡 Answer:\n{answer}")
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            print("Please try again or type 'help' for assistance.")

if __name__ == "__main__":
    main()
