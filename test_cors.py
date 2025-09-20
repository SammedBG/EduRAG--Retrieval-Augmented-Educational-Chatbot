#!/usr/bin/env python3
"""
Test CORS configuration
"""
import requests

def test_cors():
    backend_url = "https://edurag-retrieval-augmented-educational.onrender.com"
    frontend_origin = "https://edu-rag-retrieval-augmented-educati.vercel.app"
    
    # Test preflight request (OPTIONS)
    headers = {
        'Origin': frontend_origin,
        'Access-Control-Request-Method': 'POST',
        'Access-Control-Request-Headers': 'Content-Type'
    }
    
    try:
        print("Testing CORS preflight request...")
        response = requests.options(f"{backend_url}/upload", headers=headers)
        print(f"Status: {response.status_code}")
        print(f"CORS Headers:")
        for header, value in response.headers.items():
            if 'access-control' in header.lower():
                print(f"  {header}: {value}")
        
        # Test actual request
        print("\nTesting actual health request...")
        response = requests.get(f"{backend_url}/health", headers={'Origin': frontend_origin})
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_cors()