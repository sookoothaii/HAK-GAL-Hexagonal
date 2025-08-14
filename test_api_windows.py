#!/usr/bin/env python3
"""
Hexagonal API Test Client - Windows Compatible
===============================================
Testet alle Endpoints der Hexagonal API ohne Unicode-Zeichen
"""

import requests
import json
import time
import sys

# Set UTF-8 encoding for Windows
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE_URL = "http://localhost:5001"

def test_health():
    """Test Health Endpoint"""
    print("\n[TEST] Testing /health...")
    try:
        start = time.time()
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        elapsed = (time.time() - start) * 1000
        
        if response.status_code == 200:
            data = response.json()
            print(f"  [OK] Status: {data['status']}")
            print(f"  [OK] Architecture: {data['architecture']}")
            print(f"  [OK] Response time: {elapsed:.1f}ms")
            return True
    except requests.exceptions.ConnectionError:
        print("  [ERROR] API not running on port 5001")
    except requests.exceptions.Timeout:
        print("  [ERROR] Request timed out")
    except Exception as e:
        print(f"  [ERROR] {e}")
    return False

def test_status():
    """Test Status Endpoint"""
    print("\n[TEST] Testing /api/status...")
    try:
        start = time.time()
        response = requests.get(f"{BASE_URL}/api/status", timeout=5)
        elapsed = (time.time() - start) * 1000
        
        if response.status_code == 200:
            data = response.json()
            print(f"  [OK] Status: {data['status']}")
            print(f"  [OK] Facts Count: {data.get('fact_count', 'N/A')}")
            print(f"  [OK] Repository: {data['repository_type']}")
            print(f"  [OK] Response time: {elapsed:.1f}ms")
            return True
    except Exception as e:
        print(f"  [ERROR] {e}")
    return False

def test_reasoning():
    """Test Reasoning Endpoint"""
    print("\n[TEST] Testing POST /api/reason...")
    try:
        payload = {"query": "What is matter?"}
        start = time.time()
        response = requests.post(
            f"{BASE_URL}/api/reason",
            json=payload,
            timeout=10
        )
        elapsed = (time.time() - start) * 1000
        
        if response.status_code == 200:
            data = response.json()
            print(f"  [OK] Success: {data.get('success', False)}")
            print(f"  [OK] Confidence: {data.get('confidence', 0):.3f}")
            print(f"  [OK] Device: {data.get('device', 'unknown')}")
            print(f"  [OK] Response time: {elapsed:.1f}ms")
            return True
    except Exception as e:
        print(f"  [ERROR] {e}")
    return False

def test_facts_count():
    """Test Facts Count"""
    print("\n[TEST] Testing GET /api/facts/count...")
    try:
        start = time.time()
        response = requests.get(f"{BASE_URL}/api/facts/count", timeout=5)
        elapsed = (time.time() - start) * 1000
        
        if response.status_code == 200:
            data = response.json()
            print(f"  [OK] Count: {data.get('count', 0)}")
            print(f"  [OK] Response time: {elapsed:.1f}ms")
            return True
    except Exception as e:
        print(f"  [ERROR] {e}")
    return False

def main():
    print("=" * 60)
    print("HAK-GAL HEXAGONAL API TEST SUITE")
    print("=" * 60)
    print(f"Target: {BASE_URL}")
    print("Nach HAK/GAL Verfassung Artikel 6: Empirische Validierung")
    
    # Start hexagonal backend
    print("\n[INFO] Starting Hexagonal Backend...")
    import subprocess
    import os
    
    # Kill any existing process on port 5001
    try:
        if sys.platform == "win32":
            subprocess.run("netstat -ano | findstr :5001", shell=True, capture_output=True)
            subprocess.run("taskkill /F /PID $(netstat -ano | findstr :5001 | awk '{print $5}')", shell=True, capture_output=True)
    except:
        pass
    
    # Start backend
    env = os.environ.copy()
    env['PYTHONIOENCODING'] = 'utf-8'
    backend_process = subprocess.Popen(
        [sys.executable, "src_hexagonal/hexagonal_api_enhanced.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env
    )
    
    # Wait for startup
    print("[INFO] Waiting for backend to start...")
    time.sleep(3)
    
    # Run tests
    results = {}
    tests = [
        ("Health", test_health),
        ("Status", test_status),
        ("Reasoning", test_reasoning),
        ("Facts Count", test_facts_count)
    ]
    
    for test_name, test_func in tests:
        results[test_name] = test_func()
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "[PASS]" if result else "[FAIL]"
        print(f"  {status} {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    # Performance check with cache
    if results["Status"]:
        print("\n[TEST] Cache Performance Test...")
        times = []
        for i in range(5):
            start = time.time()
            response = requests.get(f"{BASE_URL}/api/status", timeout=5)
            elapsed = (time.time() - start) * 1000
            times.append(elapsed)
            print(f"  Request {i+1}: {elapsed:.1f}ms")
        
        avg_time = sum(times) / len(times)
        print(f"\n  Average response time: {avg_time:.1f}ms")
        
        if avg_time < 100:
            print("  [OK] Performance is good with caching!")
        else:
            print("  [WARNING] Performance could be improved")
    
    # Cleanup
    print("\n[INFO] Stopping backend...")
    backend_process.terminate()
    
    return 0 if passed == total else 1

if __name__ == "__main__":
    sys.exit(main())