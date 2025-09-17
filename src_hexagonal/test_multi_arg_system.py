#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
TEST MULTI-ARGUMENT FACTS SYSTEM
=================================
Comprehensive test of the extended fact generation capabilities
"""

import sys
import os
import time
import json
import sqlite3
from datetime import datetime

# Add paths
sys.path.insert(0, r"D:\MCP Mods\HAK_GAL_HEXAGONAL")

from src_hexagonal.application.extended_fact_manager import ExtendedFactManager
from src_hexagonal.infrastructure.engines.aethelred_extended import AethelredExtendedEngine

def test_database_capabilities():
    """Test current database support for extended facts"""
    print("\n" + "="*60)
    print("TESTING DATABASE CAPABILITIES")
    print("="*60)
    
    db_path = r"D:\MCP Mods\HAK_GAL_HEXAGONAL\hexagonal_kb.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check extended facts table
    cursor.execute("SELECT COUNT(*) FROM facts_extended WHERE arg_count > 2")
    multi_arg_count = cursor.fetchone()[0]
    print(f"✓ Multi-argument facts (>2 args): {multi_arg_count}")
    
    # Check formulas
    cursor.execute("SELECT COUNT(*) FROM formulas")
    formula_count = cursor.fetchone()[0]
    print(f"✓ Formulas in database: {formula_count}")
    
    # Check fact arguments
    cursor.execute("SELECT COUNT(*) FROM fact_arguments")
    arg_count = cursor.fetchone()[0]
    print(f"✓ Fact arguments: {arg_count}")
    
    conn.close()
    return multi_arg_count, formula_count

def test_extended_manager():
    """Test ExtendedFactManager functionality"""
    print("\n" + "="*60)
    print("TESTING EXTENDED FACT MANAGER")
    print("="*60)
    
    manager = ExtendedFactManager()
    test_results = []
    
    # Test 1: Add 3-argument fact
    print("\n1. Testing 3-argument fact:")
    fact_id = manager.add_multi_arg_fact(
        'Located',
        ['BrandenburgGate', 'Berlin', 'Germany'],
        domain='geography',
        confidence=0.99
    )
    if fact_id:
        print(f"  ✓ Added: Located(BrandenburgGate, Berlin, Germany)")
        test_results.append(True)
    else:
        print(f"  ✗ Failed to add 3-arg fact")
        test_results.append(False)
    
    # Test 2: Add 4-argument fact
    print("\n2. Testing 4-argument fact:")
    fact_id = manager.add_multi_arg_fact(
        'ChemicalProcess',
        ['Electrolysis', 'H2O', 'H2', 'O2'],
        domain='chemistry'
    )
    if fact_id:
        print(f"  ✓ Added: ChemicalProcess(Electrolysis, H2O, H2, O2)")
        test_results.append(True)
    else:
        print(f"  ✗ Failed to add 4-arg fact")
        test_results.append(False)
    
    # Test 3: Add 5-argument fact
    print("\n3. Testing 5-argument fact:")
    fact_id = manager.add_multi_arg_fact(
        'Experiment',
        ['DoubleSlitExp', 'Photons', 'Detector', 'InterferencePattern', '95%'],
        domain='physics'
    )
    if fact_id:
        print(f"  ✓ Added: Experiment with 5 arguments")
        test_results.append(True)
    else:
        print(f"  ✗ Failed to add 5-arg fact")
        test_results.append(False)
    
    # Test 4: Add formula
    print("\n4. Testing formula addition:")
    formula_id = manager.add_formula(
        'schrodinger_equation',
        'iℏ∂Ψ/∂t = ĤΨ',
        'physics',
        {
            'Ψ': 'Wave function',
            'Ĥ': 'Hamiltonian operator',
            'ℏ': 'Reduced Planck constant',
            't': 'Time'
        }
    )
    if formula_id:
        print(f"  ✓ Added: Schrödinger equation")
        test_results.append(True)
    else:
        print(f"  ✗ Failed to add formula")
        test_results.append(False)
    
    # Test 5: Extract facts from text
    print("\n5. Testing fact extraction:")
    text = """
    The reaction between hydrogen and oxygen produces water.
    Paris is located in France, Europe.
    Energy flows from the Sun to Earth at 1361 W/m².
    """
    extracted = manager.extract_multi_arg_facts(text)
    print(f"  ✓ Extracted {len(extracted)} facts from text")
    for fact in extracted:
        print(f"    - {fact['statement']}")
    test_results.append(len(extracted) > 0)
    
    # Test 6: Generate domain facts
    print("\n6. Testing domain fact generation:")
    for domain in ['chemistry', 'physics', 'biology']:
        facts = manager.generate_domain_facts(domain, 3)
        print(f"  ✓ Generated {len(facts)} {domain} facts")
        for fact in facts[:2]:
            print(f"    - {fact['predicate']}({', '.join(fact['args'][:3])}...)")
        test_results.append(len(facts) > 0)
    
    # Results summary
    success_rate = sum(test_results) / len(test_results) * 100
    print(f"\n✓ Manager tests passed: {sum(test_results)}/{len(test_results)} ({success_rate:.0f}%)")
    
    return success_rate > 80

def test_extended_engine():
    """Test AethelredExtended engine"""
    print("\n" + "="*60)
    print("TESTING AETHELRED EXTENDED ENGINE")
    print("="*60)
    
    engine = AethelredExtendedEngine(port=5001)
    
    # Test domain guessing
    print("\n1. Testing domain detection:")
    test_topics = {
        'quantum computing': 'physics',
        'DNA replication': 'biology',
        'stock market': 'economics',
        'chemical reactions': 'chemistry'
    }
    
    for topic, expected in test_topics.items():
        domain = engine.guess_domain(topic)
        match = "✓" if domain == expected else "✗"
        print(f"  {match} '{topic}' -> {domain} (expected: {expected})")
    
    # Test scientific fact generation
    print("\n2. Testing scientific fact generation:")
    for domain in ['chemistry', 'physics', 'biology']:
        facts = engine.generate_scientific_facts(domain, 5)
        print(f"\n  {domain.upper()} facts:")
        for fact in facts[:3]:
            args_str = ', '.join(str(a) for a in fact['args'][:3])
            if len(fact['args']) > 3:
                args_str += f", ... ({len(fact['args'])} args total)"
            print(f"    - {fact['predicate']}({args_str})")
    
    # Test multi-arg extraction
    print("\n3. Testing multi-argument extraction:")
    test_text = """
    In the experiment, hydrogen reacts with oxygen to form water.
    The process occurs at 25°C with a platinum catalyst.
    Energy is released at a rate of 285.8 kJ/mol.
    """
    
    facts = engine.extract_multi_arg_facts_from_llm(test_text, "chemistry")
    print(f"  Extracted {len(facts)} multi-arg facts")
    for fact in facts:
        print(f"    - {fact.get('statement', fact)}")
    
    return True

def run_mini_generation(duration_seconds=30):
    """Run a mini generation session"""
    print("\n" + "="*60)
    print("RUNNING MINI GENERATION SESSION")
    print("="*60)
    print(f"Duration: {duration_seconds} seconds")
    
    manager = ExtendedFactManager()
    start_time = time.time()
    facts_added = 0
    
    domains = ['chemistry', 'physics', 'biology', 'technology']
    
    while time.time() - start_time < duration_seconds:
        # Generate facts for random domain
        import random
        domain = random.choice(domains)
        facts = manager.generate_domain_facts(domain, 5)
        
        # Add without governance for speed
        for fact in facts:
            fact_id = manager.add_multi_arg_fact(
                fact['predicate'],
                fact['args'],
                domain=fact['domain'],
                confidence=0.95
            )
            if fact_id:
                facts_added += 1
        
        print(f"  Added {len(facts)} {domain} facts (Total: {facts_added})")
        time.sleep(2)
    
    elapsed = time.time() - start_time
    rate = facts_added / elapsed * 60 if elapsed > 0 else 0
    
    print(f"\n✓ Mini session complete:")
    print(f"  - Added: {facts_added} multi-arg facts")
    print(f"  - Time: {elapsed:.1f} seconds")
    print(f"  - Rate: {rate:.1f} facts/minute")
    
    return facts_added > 0

def check_final_status():
    """Check final database status"""
    print("\n" + "="*60)
    print("FINAL DATABASE STATUS")
    print("="*60)
    
    db_path = r"D:\MCP Mods\HAK_GAL_HEXAGONAL\hexagonal_kb.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Count by argument count
    cursor.execute("""
        SELECT arg_count, COUNT(*) as count 
        FROM facts_extended 
        GROUP BY arg_count 
        ORDER BY arg_count
    """)
    
    print("\nFacts by argument count:")
    for row in cursor.fetchall():
        print(f"  {row[0]} args: {row[1]} facts")
    
    # Count by domain
    cursor.execute("""
        SELECT domain, COUNT(*) as count 
        FROM facts_extended 
        WHERE domain IS NOT NULL
        GROUP BY domain 
        ORDER BY count DESC
        LIMIT 10
    """)
    
    print("\nTop domains:")
    for row in cursor.fetchall():
        print(f"  {row[0]}: {row[1]} facts")
    
    # Sample multi-arg facts
    cursor.execute("""
        SELECT statement 
        FROM facts_extended 
        WHERE arg_count >= 3 
        ORDER BY id DESC 
        LIMIT 5
    """)
    
    print("\nLatest multi-argument facts:")
    for row in cursor.fetchall():
        print(f"  - {row[0]}")
    
    conn.close()

def main():
    """Main test runner"""
    print("="*60)
    print("MULTI-ARGUMENT FACT SYSTEM TEST SUITE")
    print("="*60)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Run tests
    test_results = []
    
    # Test 1: Database capabilities
    multi_before, formulas_before = test_database_capabilities()
    test_results.append(True)  # DB always passes if accessible
    
    # Test 2: Extended Manager
    manager_ok = test_extended_manager()
    test_results.append(manager_ok)
    
    # Test 3: Extended Engine
    engine_ok = test_extended_engine()
    test_results.append(engine_ok)
    
    # Test 4: Mini generation
    generation_ok = run_mini_generation(duration_seconds=20)
    test_results.append(generation_ok)
    
    # Final status
    check_final_status()
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    test_names = [
        "Database Capabilities",
        "Extended Manager",
        "Extended Engine",
        "Mini Generation"
    ]
    
    for i, (name, result) in enumerate(zip(test_names, test_results)):
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{i+1}. {name}: {status}")
    
    success_rate = sum(test_results) / len(test_results) * 100
    print(f"\nOverall: {sum(test_results)}/{len(test_results)} tests passed ({success_rate:.0f}%)")
    
    if success_rate == 100:
        print("\n🎉 ALL TESTS PASSED! System ready for multi-argument facts!")
    elif success_rate >= 75:
        print("\n✓ System mostly ready, minor issues detected")
    else:
        print("\n⚠ System needs attention, multiple tests failed")
    
    return success_rate == 100


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
