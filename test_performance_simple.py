#!/usr/bin/env python3
"""
Simple Performance Test without Unicode issues
==============================================
"""

import time
import sys
import os

# Set UTF-8 encoding
os.environ['PYTHONIOENCODING'] = 'utf-8'

print("=" * 60)
print("SIMPLE PERFORMANCE TEST")
print("=" * 60)

# Test direct startup time
print("\n[TEST] API Startup Time")
start_time = time.time()

# Import the API
sys.path.insert(0, 'src_hexagonal')
from hexagonal_api_enhanced import create_app

# Create app instance
app = create_app(use_legacy=True, enable_all=False)  # Disable extra features
creation_time = (time.time() - start_time) * 1000
print(f"  App creation: {creation_time:.1f}ms")

# Test with minimal features
print("\n[TEST] Minimal API (no WebSocket, no Governor)")
start_time = time.time()
app_minimal = create_app(use_legacy=False, enable_all=False)  # SQLite, no extras
minimal_time = (time.time() - start_time) * 1000
print(f"  Minimal app creation: {minimal_time:.1f}ms")

print("\n[ANALYSIS]")
print(f"  Legacy system adds: {creation_time - minimal_time:.1f}ms overhead")

if creation_time > 1000:
    print("  [WARNING] Startup time exceeds 1 second!")
    print("  The legacy system initialization is the bottleneck")
else:
    print("  [OK] Startup time is acceptable")

print("\n" + "=" * 60)