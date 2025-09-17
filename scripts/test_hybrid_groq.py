#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test Hybrid Governor with Groq Integration
"""

from src_hexagonal.adapters.hybrid_llm_governor import HybridLLMGovernor
from src_hexagonal.adapters.llm_governor_adapter import LLMProvider
import time

def test_hybrid_groq():
    print('🧪 Testing Hybrid Governor with Groq Cloud...')
    
    # Initialize hybrid governor with Groq
    governor = HybridLLMGovernor(
        epsilon=0.5,  # 50% exploration for testing
        llm_provider=LLMProvider.GROQ
    )
    
    # Test critical domain facts (should use LLM)
    test_facts = [
        "The speed of light in vacuum is approximately 299,792,458 meters per second.",  # Physics
        "Water boils at 100 degrees Celsius at sea level.",  # Chemistry
        "The human brain contains approximately 86 billion neurons.",  # Neuroscience
        "E=mc² represents the mass-energy equivalence principle.",  # Physics
        "Color(Red)",  # Trivial - should use Thompson
    ]
    
    print(f"\n📊 Testing {len(test_facts)} facts with Groq integration...")
    
    total_time = 0
    for i, fact in enumerate(test_facts, 1):
        print(f"\n{i}. Fact: {fact}")
        start_time = time.time()
        decision = governor.evaluate_fact(fact)
        duration = time.time() - start_time
        total_time += duration
        
        print(f"   Decision: {decision.decision_type.value}")
        print(f"   Score: {decision.score:.3f}")
        print(f"   Confidence: {decision.confidence:.3f}")
        print(f"   Time: {duration:.2f}s")
        print(f"   Provider: {decision.metadata.get('provider', 'unknown')}")
        print(f"   Model: {decision.metadata.get('model', 'unknown')}")
    
    # Show statistics
    stats = governor.get_statistics()
    print(f"\n📈 Hybrid Governor Statistics:")
    print(f"   Total Decisions: {stats['total_decisions']}")
    print(f"   Thompson: {stats['thompson_decisions']}")
    print(f"   LLM: {stats['llm_decisions']}")
    print(f"   Batch LLM: {stats['batch_decisions']}")
    print(f"   Rejected Short: {stats['rejected_short']}")
    print(f"   Epsilon: {stats['epsilon']}")
    print(f"   Avg Time: {stats['average_decision_time_ms']:.1f}ms")
    print(f"   Total Time: {total_time:.2f}s")
    
    # Health check
    health = governor.health_check()
    print(f"\n🏥 Health Check: {health['status']}")
    print(f"   LLM Provider: {health['llm_governor']['provider']}")
    print(f"   Provider Status: {health['llm_governor']['provider_status']}")
    
    print("\n✅ Hybrid Governor with Groq test completed!")

if __name__ == "__main__":
    test_hybrid_groq()