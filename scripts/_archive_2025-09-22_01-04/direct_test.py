#!/usr/bin/env python3
"""
DIRECT TEST - Simuliert curl für genaue Zeitmessung
"""

import requests
import time

def test_direct():
    """Direkter Test ohne Debugger-Overhead"""
    print("=== DIRECT CURL-LIKE TEST ===")
    print("=" * 40)
    
    # Test HAK/GAL Dashboard
    print("🌐 Testing HAK/GAL Dashboard (Port 5000):")
    for i in range(5):
        start = time.time()
        try:
            r = requests.get('http://127.0.0.1:5000/api/health', timeout=5)
            end = time.time()
            response_time = (end - start) * 1000
            
            print(f"Request {i+1}: {response_time:.2f}ms")
            print(f"  Status: {r.status_code}")
            print(f"  Cache: {r.headers.get('X-From-Cache', 'Not Set')}")
            print(f"  Response: {r.json()}")
            print()
            
        except Exception as e:
            print(f"Request {i+1}: ERROR - {e}")
    
    print("=" * 40)
    
    # Test Minimal Server
    print("🌐 Testing Minimal Server (Port 5555):")
    for i in range(5):
        start = time.time()
        try:
            r = requests.get('http://127.0.0.1:5555/api/health', timeout=5)
            end = time.time()
            response_time = (end - start) * 1000
            
            print(f"Request {i+1}: {response_time:.2f}ms")
            print(f"  Status: {r.status_code}")
            print(f"  Response: {r.json()}")
            print()
            
        except Exception as e:
            print(f"Request {i+1}: ERROR - {e}")

if __name__ == "__main__":
    test_direct()


