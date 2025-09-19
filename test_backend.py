#!/usr/bin/env python3
"""
Test script to verify backend is working
"""
import requests
import json

def test_backend():
    # Test local backend
    local_url = "http://localhost:8000"
    
    try:
        print("Testing local backend...")
        
        # Test root endpoint
        response = requests.get(f"{local_url}/")
        print(f"Root endpoint: {response.status_code}")
        print(f"Response: {response.json()}")
        
        # Test health endpoint
        response = requests.get(f"{local_url}/health")
        print(f"Health endpoint: {response.status_code}")
        print(f"Response: {response.json()}")
        
        # Test CORS headers
        response = requests.options(f"{local_url}/health")
        print(f"CORS headers: {response.headers.get('Access-Control-Allow-Origin', 'Not set')}")
        
    except Exception as e:
        print(f"Local backend test failed: {e}")
    
    # Test production backend
    prod_url = "https://edurag-retrieval-augmented-educational.onrender.com"
    
    try:
        print("\nTesting production backend...")
        
        # Test root endpoint
        response = requests.get(f"{prod_url}/")
        print(f"Root endpoint: {response.status_code}")
        print(f"Response: {response.json()}")
        
        # Test health endpoint
        response = requests.get(f"{prod_url}/health")
        print(f"Health endpoint: {response.status_code}")
        print(f"Response: {response.json()}")
        
        # Test CORS headers
        response = requests.options(f"{prod_url}/health")
        print(f"CORS headers: {response.headers.get('Access-Control-Allow-Origin', 'Not set')}")
        
    except Exception as e:
        print(f"Production backend test failed: {e}")

if __name__ == "__main__":
    test_backend()
