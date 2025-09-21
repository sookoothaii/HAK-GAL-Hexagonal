#!/usr/bin/env python3
"""
Test Script für Multi-Argument Fact Generation
===============================================
Testet ob der fact_extractor_universal.py korrekt Multi-Argument Facts generiert
"""

import sys
import os
sys.path.append(r'D:\MCP Mods\HAK_GAL_HEXAGONAL\src_hexagonal')

from adapters.fact_extractor_universal import extract_facts_from_llm

def test_multi_arg_generation():
    """Test Multi-Argument Fact Generation"""
    
    # Test 1: Chemistry domain
    text1 = "Let me explain chemical reactions and molecular geometry in chemistry."
    facts1 = extract_facts_from_llm(text1, "Chemistry")
    
    print("Test 1 - Chemistry Domain:")
    print(f"Input: {text1}")
    print(f"Generated {len(facts1)} facts:")
    for fact in facts1:
        arg_count = fact.count(',') + 1
        print(f"  [{arg_count} args] {fact}")
    
    # Test 2: AI domain  
    text2 = "Artificial intelligence uses machine learning and neural networks."
    facts2 = extract_facts_from_llm(text2, "AI")
    
    print("\nTest 2 - AI Domain:")
    print(f"Input: {text2}")
    print(f"Generated {len(facts2)} facts:")
    for fact in facts2:
        arg_count = fact.count(',') + 1
        print(f"  [{arg_count} args] {fact}")
    
    # Test 3: Physics domain
    text3 = "Quantum physics studies energy transfer and particle motion."
    facts3 = extract_facts_from_llm(text3, "QuantumPhysics")
    
    print("\nTest 3 - Physics Domain:")
    print(f"Input: {text3}")
    print(f"Generated {len(facts3)} facts:")
    for fact in facts3:
        arg_count = fact.count(',') + 1
        print(f"  [{arg_count} args] {fact}")
    
    # Analyze results
    all_facts = facts1 + facts2 + facts3
    multi_arg_facts = [f for f in all_facts if f.count(',') >= 2]
    
    print("\n" + "="*60)
    print("ANALYSIS:")
    print(f"Total facts generated: {len(all_facts)}")
    print(f"Multi-argument facts (3+ args): {len(multi_arg_facts)}")
    print(f"Percentage multi-arg: {len(multi_arg_facts)/len(all_facts)*100:.1f}%")
    
    # Count by argument number
    arg_counts = {}
    for fact in all_facts:
        arg_num = fact.count(',') + 1
        arg_counts[arg_num] = arg_counts.get(arg_num, 0) + 1
    
    print("\nDistribution by argument count:")
    for args in sorted(arg_counts.keys()):
        print(f"  {args} arguments: {arg_counts[args]} facts")
    
    # Validate success
    if len(multi_arg_facts) > len(all_facts) * 0.5:
        print("\n✅ SUCCESS: Multi-argument fact generation is working!")
        return True
    else:
        print("\n❌ FAILURE: Still generating mostly 2-argument facts")
        return False

if __name__ == "__main__":
    success = test_multi_arg_generation()
    sys.exit(0 if success else 1)
