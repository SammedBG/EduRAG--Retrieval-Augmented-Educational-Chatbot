#!/usr/bin/env python3
"""
Simple launcher for the RAG Chatbot
"""

import subprocess
import sys
import os

def main():
    """Launch the RAG Chatbot"""
    print("🚀 Starting RAG Chatbot...")
    
    # Check if virtual environment is activated (simplified check)
    venv_path = os.path.join(os.getcwd(), '.venv')
    if not os.path.exists(venv_path):
        print("⚠️  Virtual environment not found.")
        print("   Please create and activate your virtual environment first:")
        print("   python -m venv .venv")
        print("   .venv\\Scripts\\activate  (Windows)")
        print("   source .venv/bin/activate  (Linux/Mac)")
        return
    
    # Run the main chatbot
    try:
        subprocess.run([sys.executable, "main.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running chatbot: {e}")
    except KeyboardInterrupt:
        print("\n👋 Chatbot stopped.")

if __name__ == "__main__":
    main()
