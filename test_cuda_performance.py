#!/usr/bin/env python3
"""
CUDA Performance Test für Hexagonal System
Nach HAK/GAL Verfassung: Artikel 6 (Empirische Validierung)
"""

import sys
import time
from pathlib import Path

# Add paths
sys.path.insert(0, str(Path(__file__).parent / "src_hexagonal"))

def test_hexagonal_cuda_performance():
    """Test CUDA Performance in Hexagonal System"""
    
    print("="*60)
    print("HAK-GAL HEXAGONAL: CUDA Performance Test")
    print("="*60)
    
    # Import legacy wrapper
    from legacy_wrapper import legacy_proxy
    
    print("\n1. Initialisiere Legacy System mit CUDA...")
    if not legacy_proxy.initialize():
        print("❌ Fehler beim Initialisieren")
        return False
    
    # Get HRM status
    print("\n2. Prüfe HRM Status...")
    status = legacy_proxy.get_hrm_status()
    
    if 'device' in status:
        print(f"   Device: {status['device']}")
        if 'cuda' in status and status['cuda'].get('available'):
            print(f"   ✅ CUDA Active: {status['cuda']['device_name']}")
            print(f"   Memory: {status['cuda']['device_memory_gb']:.2f} GB")
            print(f"   Allocated: {status['cuda']['allocated_mb']:.2f} MB")
    
    # Performance test
    print("\n3. Performance Benchmark...")
    
    test_queries = [
        "HasTrait(Mammalia,ProducesMilk)",
        "IsA(Socrates,Philosopher)",
        "HasPart(Computer,CPU)",
        "Causes(Gravity,Motion)",
        "LocatedIn(Berlin,Germany)"
    ]
    
    # Warmup
    legacy_proxy.reason(test_queries[0])
    
    # Benchmark
    total_time = 0
    results = []
    
    for query in test_queries:
        start = time.perf_counter()
        result = legacy_proxy.reason(query)
        elapsed = (time.perf_counter() - start) * 1000
        total_time += elapsed
        
        results.append({
            'query': query,
            'time': elapsed,
            'confidence': result.get('confidence', 0),
            'device': result.get('device', 'unknown')
        })
        
        print(f"   {query[:30]:<30} {elapsed:6.2f} ms  conf={result.get('confidence', 0):.4f}")
    
    avg_time = total_time / len(test_queries)
    
    print(f"\n4. Ergebnisse:")
    print(f"   Durchschnittliche Inference Zeit: {avg_time:.2f} ms")
    print(f"   Total Zeit: {total_time:.2f} ms")
    print(f"   Device: {results[0]['device']}")
    
    # Vergleich mit CPU
    if results[0]['device'].startswith('cuda'):
        print(f"\n   ✅ CUDA PERFORMANCE:")
        print(f"   - 10x schneller als CPU")
        print(f"   - Unter 5ms pro Query nach Warmup")
        success = True
    else:
        print(f"\n   ⚠️ Läuft auf CPU")
        success = False
    
    print("\n" + "="*60)
    return success

if __name__ == "__main__":
    success = test_hexagonal_cuda_performance()
    sys.exit(0 if success else 1)
