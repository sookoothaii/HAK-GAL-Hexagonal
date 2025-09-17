#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test Groq Integration
"""

from src_hexagonal.adapters.llm_governor_adapter import LLMGovernorAdapter, LLMProvider
import time
import os

def test_groq_integration():
    print('🧪 Testing Groq Cloud Integration...')
    
    # Check if API key is available
    if not os.environ.get('GROQ_API_KEY'):
        print('❌ GROQ_API_KEY not found in environment')
        print('   Set it with: export GROQ_API_KEY=your_key_here')
        return
    
    governor = LLMGovernorAdapter(LLMProvider.GROQ)

    # Test fact
    fact = 'The speed of light in vacuum is approximately 299,792,458 meters per second.'
    print(f'Testing fact: {fact}')

    start_time = time.time()
    result = governor.evaluate_fact(fact)
    duration = time.time() - start_time

    print(f'✅ Result:')
    print(f'   Score: {result.score:.3f}')
    print(f'   Confidence: {result.confidence:.3f}')
    print(f'   Provider: {result.provider}')
    print(f'   Model: {result.metadata.get("model", "unknown")}')
    print(f'   Duration: {duration:.2f}s')
    print(f'   Reasoning: {result.reasoning}')
    
    # Health check
    health = governor.health_check()
    print(f'\n🏥 Health Check:')
    print(f'   Status: {health["status"]}')
    print(f'   Provider Status: {health["provider_status"]}')

if __name__ == "__main__":
    test_groq_integration()