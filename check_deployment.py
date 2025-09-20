#!/usr/bin/env python3
"""
Check deployment status and provide debugging info
"""
import requests
import time

def check_deployment():
    backend_url = "https://edurag-retrieval-augmented-educational.onrender.com"
    
    print("🔍 Checking Render Deployment Status")
    print("=" * 50)
    
    # Test different endpoints with longer timeout
    endpoints = ["/", "/health"]
    
    for endpoint in endpoints:
        print(f"\n📡 Testing {endpoint}...")
        try:
            response = requests.get(f"{backend_url}{endpoint}", timeout=30)
            print(f"✅ Status: {response.status_code}")
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"📄 Response: {data}")
                except:
                    print(f"📄 Response: {response.text[:200]}...")
            else:
                print(f"❌ Error response: {response.text[:200]}...")
        except requests.exceptions.Timeout:
            print("⏰ Request timed out (30s) - service may be starting up")
        except requests.exceptions.ConnectionError:
            print("🔌 Connection error - service may be down")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("💡 Troubleshooting Tips:")
    print("1. Check Render dashboard for build logs")
    print("2. Verify environment variables are set")
    print("3. Check if service is sleeping (free tier)")
    print("4. Look for memory/timeout issues in logs")

if __name__ == "__main__":
    check_deployment()