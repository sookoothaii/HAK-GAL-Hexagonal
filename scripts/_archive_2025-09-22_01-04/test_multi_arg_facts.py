#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
TEST MULTI-ARGUMENT FACT GENERATION
====================================
Quick test to verify multi-argument fact generation is working
"""

import requests
import json
import time
import sys

# Configuration
AUTH_TOKEN = "515f57956e7bd15ddc3817573598f190"
API_URL = "http://localhost:5002/api/facts"

# Test facts with different argument counts
TEST_FACTS = [
    # 3 arguments
    "Located(BerlinWall, Berlin, Germany).",
    "ChemicalReaction(Ca, O2, CaO).",
    "DataFlow(Frontend, GraphQL, Backend).",
    
    # 4 arguments  
    "AcidBaseReaction(H2SO4, Mg(OH)2, MgSO4, H2O).",
    "EnergyTransfer(WindTurbine, Mechanical, 2MW, PowerGrid).",
    
    # 5 arguments
    "Combustion(C4H10, O2, CO2, H2O, pressure:2atm).",
    "BiologicalProcess(Algae, Photosynthesis, H2O, O2, Thylakoid).",
    
    # 6 arguments
    "MolecularGeometry(BeCl2, beryllium, chlorine, linear, sp, angle:180deg).",
    "CrystalStructure(Aluminum, Cubic, 4.050A, 4.050A, 4.050A, Fm3m).",
    
    # 7 arguments
    "Motion(harmonic, pendulum, 2Hz, rest, amplitude:10cm, damping:0.1, classical).",
    "ChemicalEquilibrium(Contact, SO2, O2, SO3, heat, Keq:50, catalyst:V2O5_T:450C).",
    "QuantumState(electron, 4, 2, -1, 0.5, -0.85eV, 4d)."
]

def test_add_fact(fact: str, index: int) -> bool:
    """Test adding a single multi-argument fact"""
    try:
        # Extract info from fact
        predicate = fact.split('(')[0]
        args = fact.split('(')[1].rstrip(').').split(', ')
        arg_count = len(args)
        
        print(f"\n[{index}] Testing {arg_count}-arg fact: {predicate}")
        print(f"    Fact: {fact[:80]}...")
        
        # Prepare request
        headers = {
            'Content-Type': 'application/json',
            'X-API-Key': AUTH_TOKEN
        }
        
        data = {
            'statement': fact,
            'context': {
                'source': 'MultiArgTest',
                'predicate': predicate,
                'argCount': arg_count,
                'test': True,
                'confidence': 0.95
            }
        }
        
        # Send request
        response = requests.post(API_URL, json=data, headers=headers, timeout=5)
        
        # Check response
        if response.status_code in [200, 201]:
            print(f"    ✅ SUCCESS: Fact added to KB")
            return True
        elif response.status_code == 409:
            print(f"    ⚠️ DUPLICATE: Fact already exists")
            return True  # Still counts as success (system works)
        elif response.status_code == 403:
            print(f"    ❌ AUTH ERROR: Check auth token")
            return False
        else:
            print(f"    ❌ FAILED: Status {response.status_code}")
            try:
                error = response.json()
                print(f"    Error: {error.get('message', 'Unknown')}")
            except:
                pass
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"    ❌ CONNECTION ERROR: Is backend running on port 5002?")
        return False
    except Exception as e:
        print(f"    ❌ ERROR: {e}")
        return False

def test_get_stats() -> dict:
    """Get current KB statistics"""
    try:
        response = requests.get("http://localhost:5002/api/facts/count")
        if response.ok:
            return response.json()
        return {}
    except:
        return {}

def main():
    """Run the multi-argument fact test suite"""
    print("=" * 70)
    print("MULTI-ARGUMENT FACT GENERATION TEST SUITE")
    print("=" * 70)
    print(f"API: {API_URL}")
    print(f"Auth Token: {AUTH_TOKEN[:8]}...")
    print(f"Test Facts: {len(TEST_FACTS)} facts (3-7 arguments)")
    
    # Get initial stats
    stats_before = test_get_stats()
    print(f"\nInitial KB size: {stats_before.get('count', 'unknown')} facts")
    
    # Test each fact
    print("\n" + "-" * 70)
    print("TESTING MULTI-ARGUMENT FACTS")
    print("-" * 70)
    
    success_count = 0
    arg_count_success = {i: 0 for i in range(3, 8)}
    
    for i, fact in enumerate(TEST_FACTS, 1):
        success = test_add_fact(fact, i)
        if success:
            success_count += 1
            arg_count = len(fact.split('(')[1].rstrip(').').split(', '))
            arg_count_success[arg_count] += 1
        time.sleep(0.5)  # Small delay between requests
    
    # Get final stats
    stats_after = test_get_stats()
    
    # Report
    print("\n" + "=" * 70)
    print("TEST RESULTS")
    print("=" * 70)
    print(f"Success Rate: {success_count}/{len(TEST_FACTS)} ({100*success_count/len(TEST_FACTS):.1f}%)")
    print("\nBy Argument Count:")
    for args in range(3, 8):
        test_count = sum(1 for f in TEST_FACTS if len(f.split('(')[1].rstrip(').').split(', ')) == args)
        if test_count > 0:
            print(f"  {args} args: {arg_count_success[args]}/{test_count} successful")
    
    print(f"\nKB Growth: {stats_before.get('count', 0)} -> {stats_after.get('count', 0)} facts")
    
    if success_count == len(TEST_FACTS):
        print("\n🎉 ALL TESTS PASSED! Multi-argument facts are working correctly.")
    elif success_count > 0:
        print(f"\n⚠️ PARTIAL SUCCESS: {success_count}/{len(TEST_FACTS)} tests passed.")
    else:
        print("\n❌ TESTS FAILED: Check backend connection and auth token.")
    
    print("=" * 70)

if __name__ == "__main__":
    main()
