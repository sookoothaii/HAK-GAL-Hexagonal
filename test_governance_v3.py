#!/usr/bin/env python3
"""
Test Script for Governance V3
Tests the new PragmaticGovernance implementation
"""

import os
import sys
import sqlite3
import json
import time
from datetime import datetime

# Add project to path
sys.path.insert(0, r"D:\MCP Mods\HAK_GAL_HEXAGONAL")
sys.path.insert(0, r"D:\MCP Mods\HAK_GAL_HEXAGONAL\src_hexagonal")

# Force V3
os.environ['GOVERNANCE_VERSION'] = 'v3'

print("=" * 60)
print("GOVERNANCE V3 TEST SUITE")
print("=" * 60)
print()

# Import the engine
from src_hexagonal.application.transactional_governance_engine import TransactionalGovernanceEngine

# Test scenarios
test_scenarios = [
    {
        'name': 'Normal User - Add Facts',
        'facts': ['IsA(TestEntity, Entity)', 'HasPart(TestEntity, TestComponent)'],
        'context': {'source': 'user', 'user_role': 'user'},
        'expected': True
    },
    {
        'name': 'Trusted System - Add Facts',
        'facts': ['DependsOn(ComponentA, ComponentB)'],
        'context': {'source': 'trusted_system'},
        'expected': True
    },
    {
        'name': 'Admin - Delete Operation',
        'facts': ['Delete(OldFact)'],  # This will be classified as delete
        'context': {'user_role': 'admin'},
        'expected': True  # Admin can delete
    },
    {
        'name': 'User - Delete Operation',
        'facts': ['Delete(SomeFact)'],
        'context': {'source': 'user'},
        'expected': False  # User cannot delete
    },
    {
        'name': 'Bypass Active',
        'facts': ['AnyFact(A, B)'],
        'context': {'bypass_governance': True, 'bypass_authorization': 'test_auth'},
        'expected': True
    }
]

def test_governance_v3():
    """Test the new Governance V3"""
    
    # Initialize engine
    print("Initializing TransactionalGovernanceEngine with V3...")
    engine = TransactionalGovernanceEngine()
    
    # Check which governance is active
    if hasattr(engine, 'governance_v3') and engine.governance_v3:
        print("[OK] Governance V3 is active")
    else:
        print("[ERROR] Governance V3 not active!")
        return False
    
    print()
    
    # Run test scenarios
    passed = 0
    failed = 0
    
    for scenario in test_scenarios:
        print(f"Test: {scenario['name']}")
        print(f"  Facts: {scenario['facts']}")
        print(f"  Context: {scenario['context']}")
        
        try:
            # Add externally_legal for all tests
            scenario['context']['externally_legal'] = True
            
            result = engine.governed_add_facts_atomic(
                scenario['facts'], 
                scenario['context']
            )
            
            success = result > 0
            
            if success == scenario['expected']:
                print(f"  Result: PASS (Added {result} facts)")
                passed += 1
            else:
                print(f"  Result: FAIL (Expected {'success' if scenario['expected'] else 'failure'}, got {'success' if success else 'failure'})")
                failed += 1
                
        except Exception as e:
            print(f"  Result: ERROR - {e}")
            failed += 1
        
        print()
    
    # Summary
    print("=" * 60)
    print(f"SUMMARY: {passed} passed, {failed} failed")
    print("=" * 60)
    
    return failed == 0

def test_bypass_mode():
    """Test bypass functionality"""
    print("\n" + "=" * 60)
    print("TESTING BYPASS MODE")
    print("=" * 60)
    
    # Set bypass
    os.environ['GOVERNANCE_BYPASS'] = 'true'
    
    engine = TransactionalGovernanceEngine()
    
    # This should work even with "dangerous" operations
    dangerous_facts = [
        'ExecuteCode(rm -rf /)',  # Would normally be blocked
        'DeleteAll(Everything)',   # Would normally be blocked
        'SystemOverride(Admin)'     # Would normally be blocked
    ]
    
    context = {'source': 'test'}
    
    result = engine.governed_add_facts_atomic(dangerous_facts, context)
    
    if result > 0:
        print(f"[OK] Bypass mode worked - Added {result} facts")
    else:
        print("[ERROR] Bypass mode failed!")
    
    # Disable bypass
    os.environ['GOVERNANCE_BYPASS'] = 'false'
    
    return result > 0

def test_performance():
    """Test V3 performance"""
    print("\n" + "=" * 60)
    print("PERFORMANCE TEST")
    print("=" * 60)
    
    os.environ['GOVERNANCE_VERSION'] = 'v3'
    engine = TransactionalGovernanceEngine()
    
    # Generate test facts
    test_facts = []
    for i in range(100):
        test_facts.append(f"IsA(Entity_{i}, TestEntity)")
    
    context = {'source': 'trusted_system', 'bulk_operation': True}
    
    start = time.perf_counter()
    result = engine.governed_add_facts_atomic(test_facts, context)
    duration = time.perf_counter() - start
    
    throughput = len(test_facts) / duration if duration > 0 else 0
    
    print(f"Facts attempted: {len(test_facts)}")
    print(f"Facts added: {result}")
    print(f"Duration: {duration:.3f}s")
    print(f"Throughput: {throughput:.1f} facts/s")
    print(f"Avg latency: {(duration / len(test_facts)) * 1000:.2f}ms per fact")
    
    return result > 0

if __name__ == "__main__":
    # Run all tests
    all_passed = True
    
    # Test V3 functionality
    if not test_governance_v3():
        all_passed = False
    
    # Test bypass mode
    if not test_bypass_mode():
        all_passed = False
    
    # Test performance
    if not test_performance():
        all_passed = False
    
    # Final result
    print("\n" + "=" * 60)
    if all_passed:
        print("ALL TESTS PASSED - Governance V3 is ready!")
    else:
        print("SOME TESTS FAILED - Check the output above")
    print("=" * 60)
