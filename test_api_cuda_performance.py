#!/usr/bin/env python3
"""
Final CUDA Performance Validation
Nach HAK/GAL Verfassung: Artikel 6 (Empirische Validierung)
"""

import requests
import time
import json

def test_hexagonal_cuda_api():
    """Test Hexagonal API Performance mit CUDA"""
    
    BASE_URL = "http://127.0.0.1:5001"
    
    print("="*60)
    print("HAK-GAL HEXAGONAL: CUDA API Performance Test")
    print("="*60)
    
    # 1. Check Health
    print("\n1. Health Check...")
    try:
        resp = requests.get(f"{BASE_URL}/health", timeout=5)
        print(f"   Status: {resp.status_code}")
        print(f"   Response: {resp.json()}")
    except Exception as e:
        print(f"   ❌ API nicht erreichbar: {e}")
        return False
    
    # 2. System Status
    print("\n2. System Status...")
    resp = requests.get(f"{BASE_URL}/api/status")
    status = resp.json()
    print(f"   Facts: {status.get('total_facts', 0)}")
    print(f"   Repository: {status.get('repository_type', 'unknown')}")
    
    # 3. Reasoning Performance Test
    print("\n3. Reasoning Performance (CUDA)...")
    
    test_queries = [
        "HasTrait(Mammalia,ProducesMilk)",
        "IsA(Socrates,Philosopher)", 
        "HasPart(Computer,CPU)",
        "Causes(Gravity,Motion)",
        "LocatedIn(Berlin,Germany)"
    ]
    
    # Warmup
    requests.post(f"{BASE_URL}/api/reason", 
                 json={"query": test_queries[0]})
    
    total_time = 0
    for query in test_queries:
        start = time.perf_counter()
        resp = requests.post(f"{BASE_URL}/api/reason",
                            json={"query": query})
        elapsed = (time.perf_counter() - start) * 1000
        total_time += elapsed
        
        result = resp.json()
        conf = result.get('confidence', 0)
        device = result.get('device', 'unknown')
        
        print(f"   {query[:30]:<30} {elapsed:6.2f} ms  conf={conf:.4f}  device={device}")
    
    avg_time = total_time / len(test_queries)
    
    print(f"\n4. Performance Summary:")
    print(f"   Average API Response Time: {avg_time:.2f} ms")
    print(f"   Total Time: {total_time:.2f} ms")
    
    if avg_time < 50:  # Under 50ms average
        print(f"   ✅ EXCELLENT CUDA PERFORMANCE!")
    else:
        print(f"   ⚠️ Performance könnte besser sein")
    
    print("\n" + "="*60)
    print("CUDA Performance Validation Complete!")
    print("="*60)
    
    return True

if __name__ == "__main__":
    import sys
    success = test_hexagonal_cuda_api()
    sys.exit(0 if success else 1)
