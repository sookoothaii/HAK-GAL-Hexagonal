#!/usr/bin/env python3
"""
Performance Bottleneck Analysis for HAK-GAL Hexagonal API
=========================================================
"""

import time
import sys
import requests
from pathlib import Path

# Timing decorator
def time_it(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        elapsed = (time.time() - start) * 1000
        print(f"  [{func.__name__}] took {elapsed:.1f}ms")
        return result
    return wrapper

print("=" * 60)
print("PERFORMANCE BOTTLENECK ANALYSIS")
print("=" * 60)

# Test 1: Import timing
print("\n[TEST 1] Import Timing")
start = time.time()
sys.path.insert(0, str(Path(__file__).parent / 'src_hexagonal'))
print(f"  Path setup: {(time.time() - start) * 1000:.1f}ms")

start = time.time()
from adapters import legacy_adapters
print(f"  Import legacy_adapters: {(time.time() - start) * 1000:.1f}ms")

start = time.time()
from legacy_wrapper import legacy_proxy
print(f"  Import legacy_proxy: {(time.time() - start) * 1000:.1f}ms")

# Test 2: Legacy system initialization
print("\n[TEST 2] Legacy System Initialization")

@time_it
def test_k_assistant_init():
    return legacy_proxy.initialize_k_assistant()

@time_it
def test_hrm_init():
    return legacy_proxy.initialize_hrm()

@time_it
def test_full_init():
    return legacy_proxy.initialize()

# Reset proxy to test fresh initialization
legacy_proxy._k_assistant_initialized = False
legacy_proxy._hrm_initialized = False
legacy_proxy._initialized = False

k_result = test_k_assistant_init()
print(f"  K-Assistant init: {k_result}")

hrm_result = test_hrm_init()
print(f"  HRM init: {hrm_result}")

# Test 3: Repository operations
print("\n[TEST 3] Repository Operations")

@time_it
def test_count_with_cache():
    repo = legacy_adapters.LegacyFactRepository()
    # First call (no cache)
    count1 = repo.count()
    # Second call (should use cache)
    count2 = repo.count()
    return count1, count2

counts = test_count_with_cache()
print(f"  Facts count: {counts[0]}")

# Test 4: Direct API calls
print("\n[TEST 4] Direct API Response Times")

# Start backend process in background
import subprocess
import os

print("  Starting backend...")
env = os.environ.copy()
env['PYTHONIOENCODING'] = 'utf-8'
backend_process = subprocess.Popen(
    [sys.executable, "src_hexagonal/hexagonal_api_enhanced.py"],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    env=env
)

# Wait for startup
time.sleep(3)

# Test endpoints
endpoints = [
    ('/health', 'GET'),
    ('/api/status?light=1', 'GET'),  # Light mode
    ('/api/status', 'GET'),  # Full mode
    ('/api/facts/count', 'GET')
]

for endpoint, method in endpoints:
    try:
        start = time.time()
        if method == 'GET':
            response = requests.get(f"http://localhost:5001{endpoint}", timeout=5)
        elapsed = (time.time() - start) * 1000
        print(f"  {endpoint}: {elapsed:.1f}ms (status: {response.status_code})")
    except Exception as e:
        print(f"  {endpoint}: Failed - {e}")

# Test 5: Consecutive calls (should benefit from cache)
print("\n[TEST 5] Consecutive Calls (Cache Test)")
for i in range(3):
    start = time.time()
    response = requests.get("http://localhost:5001/api/facts/count", timeout=5)
    elapsed = (time.time() - start) * 1000
    print(f"  Call {i+1}: {elapsed:.1f}ms")

# Cleanup
print("\n[INFO] Stopping backend...")
backend_process.terminate()

print("\n" + "=" * 60)
print("ANALYSIS COMPLETE")
print("=" * 60)