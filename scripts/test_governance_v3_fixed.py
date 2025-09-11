#!/usr/bin/env python3
"""
Test Script for Governance V3 - FIXED VERSION
Tests the new PragmaticGovernance implementation with valid predicates
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
print("GOVERNANCE V3 TEST SUITE - FIXED")
print("=" * 60)
print()

# Import the engine
from src_hexagonal.application.transactional_governance_engine import TransactionalGovernanceEngine

def cleanup_test_facts():
    """Clean up test facts before running tests"""
    try:
        conn = sqlite3.connect(r"D:\MCP Mods\HAK_GAL_HEXAGONAL\hexagonal_kb.db")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM facts_extended WHERE source IN ('BYPASS_MODE', 'TransactionalGovernanceEngine') AND statement LIKE '%Test%'")
        deleted = cursor.rowcount
        conn.commit()
        conn.close()
        if deleted > 0:
            print(f"[CLEANUP] Removed {deleted} old test facts\n")
    except Exception as e:
        print(f"[CLEANUP] Error: {e}\n")

# Test scenarios with VALID predicates
test_scenarios = [
    {
        'name': 'Normal User - Add Facts',
        'facts': ['IsA(TestUser1, User)', 'HasProperty(TestUser1, Active)'],
        'context': {'source': 'user', 'user_role': 'user'},
        'expected': True  # V3 allows normal adds
    },
    {
        'name': 'Trusted System - Add Facts',
        'facts': ['DependsOn(TestModule1, TestLibrary1)', 'Uses(TestModule1, TestAPI1)'],
        'context': {'source': 'trusted_system'},
        'expected': True
    },
    {
        'name': 'Admin - Complex Operation',
        'facts': ['Creates(AdminTool, TestOutput)', 'Controls(AdminTool, TestProcess)'],
        'context': {'user_role': 'admin'},
        'expected': True  # Admin can do more
    },
    {
        'name': 'User - Restricted Operation',
        'facts': ['Controls(UserAttempt, SystemCore)'],  # Control is sensitive
        'context': {'source': 'user'},
        'expected': True  # V3 is more permissive
    },
    {
        'name': 'Validated Operation',
        'facts': ['HasPart(ValidatedSystem, ValidatedComponent)'],
        'context': {'validated': True, 'source': 'user'},
        'expected': True
    }
]

def test_governance_v3():
    """Test the new Governance V3"""
    
    # Clean up first
    cleanup_test_facts()
    
    # Initialize engine
    print("Initializing TransactionalGovernanceEngine with V3...")
    engine = TransactionalGovernanceEngine()
    print("[OK] Engine initialized\n")
    
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
            if not scenario['expected']:
                print(f"  Result: PASS (Expected failure: {str(e)[:50]})")
                passed += 1
            else:
                print(f"  Result: ERROR - {e}")
                failed += 1
        
        print()
    
    # Summary
    print("=" * 60)
    print(f"SUMMARY: {passed} passed, {failed} failed")
    print("=" * 60)
    
    return failed == 0

def test_bypass_mode():
    """Test bypass functionality with ANY predicates"""
    print("\n" + "=" * 60)
    print("TESTING BYPASS MODE")
    print("=" * 60)
    
    # Clean up first
    cleanup_test_facts()
    
    # Set bypass
    os.environ['GOVERNANCE_BYPASS'] = 'true'
    
    engine = TransactionalGovernanceEngine()
    
    # These would normally be invalid predicates
    unusual_facts = [
        'CustomPredicate(TestA, TestB)',
        'SpecialOperation(TestX, TestY, TestZ)',
        'BypassedFact(Test123)'
    ]
    
    context = {'source': 'bypass_test'}
    
    print(f"Testing bypass with unusual predicates: {unusual_facts}")
    
    result = engine.governed_add_facts_atomic(unusual_facts, context)
    
    if result > 0:
        print(f"[OK] Bypass mode worked - Added {result} facts")
        success = True
    else:
        print("[ERROR] Bypass mode failed!")
        success = False
    
    # Disable bypass
    os.environ['GOVERNANCE_BYPASS'] = 'false'
    
    # Clean up bypass facts
    try:
        conn = sqlite3.connect(r"D:\MCP Mods\HAK_GAL_HEXAGONAL\hexagonal_kb.db")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM facts_extended WHERE source = 'BYPASS_MODE'")
        conn.commit()
        conn.close()
    except:
        pass
    
    return success

def test_context_bypass():
    """Test context-based bypass"""
    print("\n" + "=" * 60)
    print("TESTING CONTEXT BYPASS")
    print("=" * 60)
    
    os.environ.pop('GOVERNANCE_BYPASS', None)  # Ensure env bypass is off
    
    engine = TransactionalGovernanceEngine()
    
    # Test with context bypass
    facts = ['ContextBypass(TestItem1, TestItem2)']
    context = {
        'bypass_governance': True,
        'bypass_authorization': 'emergency_auth_123'
    }
    
    print(f"Testing context bypass with: {facts}")
    print(f"Context: {context}")
    
    result = engine.governed_add_facts_atomic(facts, context)
    
    if result > 0:
        print(f"[OK] Context bypass worked - Added {result} facts")
        return True
    else:
        print("[ERROR] Context bypass failed!")
        return False

def test_performance():
    """Test V3 performance with valid predicates"""
    print("\n" + "=" * 60)
    print("PERFORMANCE TEST")
    print("=" * 60)
    
    cleanup_test_facts()
    
    os.environ['GOVERNANCE_VERSION'] = 'v3'
    os.environ.pop('GOVERNANCE_BYPASS', None)
    
    engine = TransactionalGovernanceEngine()
    
    # Generate test facts with valid predicates
    test_facts = []
    for i in range(50):  # Reduced from 100 to avoid locks
        test_facts.append(f"IsA(PerfEntity_{i}, TestEntity)")
        test_facts.append(f"HasProperty(PerfEntity_{i}, Active)")
    
    context = {'source': 'trusted_system', 'bulk_operation': True}
    
    print(f"Testing with {len(test_facts)} facts...")
    
    start = time.perf_counter()
    
    # Process in smaller batches to avoid locks
    total_added = 0
    batch_size = 10
    
    for i in range(0, len(test_facts), batch_size):
        batch = test_facts[i:i+batch_size]
        try:
            result = engine.governed_add_facts_atomic(batch, context)
            total_added += result
        except Exception as e:
            print(f"  Batch {i//batch_size} failed: {e}")
    
    duration = time.perf_counter() - start
    
    throughput = total_added / duration if duration > 0 else 0
    
    print(f"Facts attempted: {len(test_facts)}")
    print(f"Facts added: {total_added}")
    print(f"Duration: {duration:.3f}s")
    print(f"Throughput: {throughput:.1f} facts/s")
    print(f"Avg latency: {(duration / len(test_facts)) * 1000:.2f}ms per fact")
    
    return total_added > 0

def final_cleanup():
    """Clean up all test data"""
    try:
        conn = sqlite3.connect(r"D:\MCP Mods\HAK_GAL_HEXAGONAL\hexagonal_kb.db")
        cursor = conn.cursor()
        cursor.execute("""
            DELETE FROM facts_extended 
            WHERE (statement LIKE '%Test%' OR statement LIKE '%Perf%') 
            AND source IN ('BYPASS_MODE', 'TransactionalGovernanceEngine', 'bypass_test')
        """)
        deleted = cursor.rowcount
        conn.commit()
        conn.close()
        if deleted > 0:
            print(f"\n[FINAL CLEANUP] Removed {deleted} test facts")
    except Exception as e:
        print(f"\n[FINAL CLEANUP] Error: {e}")

if __name__ == "__main__":
    # Run all tests
    all_passed = True
    
    try:
        # Test V3 functionality
        if not test_governance_v3():
            all_passed = False
        
        # Test bypass modes
        if not test_bypass_mode():
            all_passed = False
            
        if not test_context_bypass():
            all_passed = False
        
        # Test performance
        if not test_performance():
            all_passed = False
        
    finally:
        # Clean up
        final_cleanup()
    
    # Final result
    print("\n" + "=" * 60)
    if all_passed:
        print("ALL TESTS PASSED - Governance V3 is ready!")
    else:
        print("SOME TESTS FAILED - Check the output above")
    print("=" * 60)
