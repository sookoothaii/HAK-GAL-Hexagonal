#!/usr/bin/env python3
"""
Test Hexagonal API - Facts Count Fix Verification
Nach HAK/GAL Verfassung Artikel 3: Externe Verifikation
"""

import requests
import json
from typing import Dict, Any

def test_hexagonal_api(base_url: str = "http://127.0.0.1:5001") -> Dict[str, Any]:
    """Test alle kritischen Endpoints der Hexagonal API"""
    
    results = {
        "health": False,
        "status": False,
        "facts_count": 0,
        "facts_list": False,
        "reasoning": False,
        "cuda_active": False
    }
    
    print("=" * 60)
    print("🔍 HEXAGONAL API TEST - Facts Count Fix Verification")
    print("=" * 60)
    
    # 1. Health Check
    try:
        resp = requests.get(f"{base_url}/health", timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            results["health"] = True
            print(f"✅ Health Check: {data.get('status')}")
            print(f"   Architecture: {data.get('architecture')}")
            print(f"   Repository: {data.get('repository')}")
    except Exception as e:
        print(f"❌ Health Check failed: {e}")
    
    # 2. System Status
    try:
        resp = requests.get(f"{base_url}/api/status", timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            results["status"] = True
            fact_count = data.get('fact_count', 0)
            results["facts_count"] = fact_count
            print(f"\n📊 System Status:")
            print(f"   Facts Count: {fact_count}")
            
            # CRITICAL CHECK
            if fact_count == 0:
                print("   ⚠️ WARNING: Facts count is 0 - BUG NOT FIXED!")
            elif fact_count == 3080:
                print("   ✅ SUCCESS: Facts count is correct (3080)!")
            else:
                print(f"   🔍 Facts count: {fact_count} (unexpected)")
    except Exception as e:
        print(f"❌ Status Check failed: {e}")
    
    # 3. Facts List
    try:
        resp = requests.get(f"{base_url}/api/facts?limit=5", timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            results["facts_list"] = True
            count = data.get('count', 0)
            total = data.get('total', 0)
            print(f"\n📚 Facts List:")
            print(f"   Retrieved: {count} facts")
            print(f"   Total Available: {total}")
            
            # CRITICAL CHECK
            if total == 0:
                print("   ⚠️ WARNING: Total facts is 0 - COUNT BUG!")
            elif total == 3080:
                print("   ✅ SUCCESS: Total facts correct!")
            
            # Show sample facts
            facts = data.get('facts', [])
            if facts:
                print("   Sample Facts:")
                for i, fact in enumerate(facts[:3], 1):
                    print(f"   {i}. {fact.get('statement', 'N/A')[:60]}...")
    except Exception as e:
        print(f"❌ Facts List failed: {e}")
    
    # 4. HRM Reasoning Test
    try:
        test_query = "HasTrait(Mammalia,ProducesMilk)"
        resp = requests.post(
            f"{base_url}/api/reason",
            json={"query": test_query},
            timeout=5
        )
        if resp.status_code == 200:
            data = resp.json()
            results["reasoning"] = True
            confidence = data.get('confidence', 0)
            device = data.get('device', 'unknown')
            
            print(f"\n🧠 HRM Reasoning Test:")
            print(f"   Query: {test_query}")
            print(f"   Confidence: {confidence:.4f}")
            print(f"   Device: {device}")
            
            if 'cuda' in device.lower():
                results["cuda_active"] = True
                print("   ✅ CUDA Acceleration Active!")
            else:
                print("   ⚠️ No CUDA acceleration detected")
    except Exception as e:
        print(f"❌ Reasoning Test failed: {e}")
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY:")
    print("=" * 60)
    
    if results["facts_count"] == 3080:
        print("✅ FACTS COUNT BUG: FIXED!")
    else:
        print(f"❌ FACTS COUNT BUG: NOT FIXED (got {results['facts_count']})")
    
    if results["cuda_active"]:
        print("✅ CUDA: Active")
    else:
        print("⚠️ CUDA: Not detected")
    
    if results["health"] and results["status"]:
        print("✅ API: Operational")
    else:
        print("❌ API: Issues detected")
    
    return results

def compare_with_original():
    """Vergleiche Hexagonal (5001) mit Original (5000)"""
    print("\n" + "=" * 60)
    print("🔄 COMPARING HEXAGONAL vs ORIGINAL")
    print("=" * 60)
    
    # Test Original API
    try:
        resp = requests.get("http://127.0.0.1:5000/api/knowledge-base/status", timeout=5)
        if resp.status_code == 200:
            original_data = resp.json()
            original_count = original_data.get('fact_count', 0)
            print(f"Original API (5000): {original_count} facts")
    except:
        print("Original API not available")
        original_count = 0
    
    # Test Hexagonal API
    try:
        resp = requests.get("http://127.0.0.1:5001/api/status", timeout=5)
        if resp.status_code == 200:
            hexa_data = resp.json()
            hexa_count = hexa_data.get('fact_count', 0)
            print(f"Hexagonal API (5001): {hexa_count} facts")
    except:
        print("Hexagonal API not available")
        hexa_count = 0
    
    if original_count == hexa_count and original_count > 0:
        print("✅ Both APIs report same fact count!")
    else:
        print(f"⚠️ Mismatch: Original={original_count}, Hexagonal={hexa_count}")

if __name__ == "__main__":
    # Test Hexagonal API
    results = test_hexagonal_api()
    
    # Compare with Original if both are running
    compare_with_original()
    
    # Exit code based on success
    import sys
    if results["facts_count"] == 3080:
        print("\n✅ TEST PASSED - Facts count bug is fixed!")
        sys.exit(0)
    else:
        print("\n❌ TEST FAILED - Facts count bug persists!")
        sys.exit(1)
