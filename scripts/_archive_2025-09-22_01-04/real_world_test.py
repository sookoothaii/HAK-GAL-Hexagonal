#!/usr/bin/env python3
"""
REAL WORLD TEST - Simuliert echte Browser-Anfragen
"""

import requests
import time
import threading
from datetime import datetime

def test_with_real_headers():
    """Test mit echten Browser-Headers"""
    print("🌐 REAL WORLD TEST - Mit Browser-Headers")
    print("=" * 50)
    
    # Echte Browser-Headers
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'de-DE,de;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache'
    }
    
    # Test HAK/GAL Dashboard
    print("🔍 Testing HAK/GAL Dashboard mit Browser-Headers:")
    for i in range(5):
        start = time.time()
        try:
            r = requests.get('http://127.0.0.1:5000/api/health', 
                           headers=headers, 
                           timeout=10)
            end = time.time()
            response_time = (end - start) * 1000
            
            print(f"Request {i+1}: {response_time:.2f}ms")
            print(f"  Status: {r.status_code}")
            print(f"  Cache: {r.headers.get('X-From-Cache', 'Not Set')}")
            print(f"  Response Size: {len(r.content)} bytes")
            print()
            
        except Exception as e:
            print(f"Request {i+1}: ERROR - {e}")

def test_with_session():
    """Test mit Session (wie Browser)"""
    print("🌐 SESSION TEST - Wie echter Browser")
    print("=" * 50)
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Connection': 'keep-alive'
    })
    
    # Test HAK/GAL Dashboard
    print("🔍 Testing mit Session:")
    for i in range(5):
        start = time.time()
        try:
            r = session.get('http://127.0.0.1:5000/api/health', timeout=10)
            end = time.time()
            response_time = (end - start) * 1000
            
            print(f"Request {i+1}: {response_time:.2f}ms")
            print(f"  Status: {r.status_code}")
            print(f"  Cache: {r.headers.get('X-From-Cache', 'Not Set')}")
            print()
            
        except Exception as e:
            print(f"Request {i+1}: ERROR - {e}")

def test_concurrent_requests():
    """Test mit gleichzeitigen Requests"""
    print("🌐 CONCURRENT TEST - Mehrere Requests gleichzeitig")
    print("=" * 50)
    
    def make_request(request_id):
        start = time.time()
        try:
            r = requests.get('http://127.0.0.1:5000/api/health', timeout=10)
            end = time.time()
            response_time = (end - start) * 1000
            print(f"Request {request_id}: {response_time:.2f}ms (Status: {r.status_code})")
        except Exception as e:
            print(f"Request {request_id}: ERROR - {e}")
    
    # Starte 5 gleichzeitige Requests
    threads = []
    for i in range(5):
        thread = threading.Thread(target=make_request, args=(i+1,))
        threads.append(thread)
        thread.start()
    
    # Warte auf alle Threads
    for thread in threads:
        thread.join()

def test_different_endpoints():
    """Test verschiedene Endpoints"""
    print("🌐 ENDPOINT TEST - Verschiedene URLs")
    print("=" * 50)
    
    endpoints = [
        'http://127.0.0.1:5000/',
        'http://127.0.0.1:5000/api/health',
        'http://127.0.0.1:5000/api/metrics'
    ]
    
    for endpoint in endpoints:
        print(f"\n🔍 Testing: {endpoint}")
        for i in range(3):
            start = time.time()
            try:
                r = requests.get(endpoint, timeout=10)
                end = time.time()
                response_time = (end - start) * 1000
                
                print(f"  Request {i+1}: {response_time:.2f}ms")
                print(f"  Status: {r.status_code}")
                print(f"  Cache: {r.headers.get('X-From-Cache', 'Not Set')}")
                
            except Exception as e:
                print(f"  Request {i+1}: ERROR - {e}")

def main():
    """Main test function"""
    print("🚀 REAL WORLD PERFORMANCE TEST")
    print("=" * 60)
    print("Simuliert echte Browser-Anfragen")
    print("=" * 60)
    
    test_with_real_headers()
    print("\n" + "=" * 60)
    
    test_with_session()
    print("\n" + "=" * 60)
    
    test_concurrent_requests()
    print("\n" + "=" * 60)
    
    test_different_endpoints()
    
    print("\n" + "=" * 60)
    print("🎯 FAZIT:")
    print("Wenn hier 500ms+ gemessen werden, dann ist das Problem real!")
    print("=" * 60)

if __name__ == "__main__":
    main()


