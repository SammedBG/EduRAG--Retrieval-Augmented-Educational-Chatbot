#!/usr/bin/env python3
"""
Debug deployment status and CORS issues
"""
import requests
import json

def check_deployment_status():
    backend_url = "https://edurag-retrieval-augmented-educational.onrender.com"
    frontend_origin = "https://edu-rag-retrieval-augmented-educati.vercel.app"
    
    print("🔍 Debugging Deployment Status\n")
    
    # 1. Check if backend is responding
    try:
        print("1. Testing backend health...")
        response = requests.get(f"{backend_url}/health", timeout=10)
        print(f"   ✅ Status: {response.status_code}")
        print(f"   📊 Response: {response.json()}")
    except Exception as e:
        print(f"   ❌ Backend health check failed: {e}")
        return
    
    # 2. Check CORS headers on health endpoint
    try:
        print("\n2. Testing CORS on health endpoint...")
        response = requests.get(f"{backend_url}/health", 
                              headers={'Origin': frontend_origin}, 
                              timeout=10)
        cors_header = response.headers.get('Access-Control-Allow-Origin', 'NOT SET')
        print(f"   🌐 CORS Header: {cors_header}")
        
        if cors_header in ['*', frontend_origin]:
            print("   ✅ CORS configured correctly for health endpoint")
        else:
            print("   ❌ CORS not configured for health endpoint")
    except Exception as e:
        print(f"   ❌ CORS test failed: {e}")
    
    # 3. Test OPTIONS preflight for upload
    try:
        print("\n3. Testing OPTIONS preflight for upload...")
        response = requests.options(f"{backend_url}/upload",
                                  headers={
                                      'Origin': frontend_origin,
                                      'Access-Control-Request-Method': 'POST',
                                      'Access-Control-Request-Headers': 'Content-Type'
                                  },
                                  timeout=10)
        print(f"   📡 OPTIONS Status: {response.status_code}")
        
        cors_headers = {}
        for header, value in response.headers.items():
            if 'access-control' in header.lower():
                cors_headers[header] = value
        
        print("   🔧 CORS Headers:")
        for header, value in cors_headers.items():
            print(f"      {header}: {value}")
            
        if 'access-control-allow-origin' in cors_headers:
            print("   ✅ Preflight CORS configured")
        else:
            print("   ❌ Preflight CORS missing")
            
    except Exception as e:
        print(f"   ❌ OPTIONS test failed: {e}")
    
    # 4. Test actual upload endpoint (without file)
    try:
        print("\n4. Testing upload endpoint accessibility...")
        response = requests.post(f"{backend_url}/upload",
                               headers={'Origin': frontend_origin},
                               timeout=10)
        print(f"   📤 Upload Status: {response.status_code}")
        cors_header = response.headers.get('Access-Control-Allow-Origin', 'NOT SET')
        print(f"   🌐 Upload CORS Header: {cors_header}")
        
    except Exception as e:
        print(f"   ❌ Upload test failed: {e}")
    
    print("\n" + "="*50)
    print("🎯 DIAGNOSIS:")
    print("If CORS headers are missing, the backend deployment")
    print("hasn't updated yet. Wait 2-3 minutes and try again.")
    print("If CORS headers are present but wrong, check the")
    print("frontend domain spelling in backend/main.py")

if __name__ == "__main__":
    check_deployment_status()