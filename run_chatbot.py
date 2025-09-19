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
    
    # Check if virtual environment is activated
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("⚠️  Virtual environment not detected.")
        print("   Please activate your virtual environment first:")
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
