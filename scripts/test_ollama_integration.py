#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test Ollama Integration
"""

from src_hexagonal.adapters.llm_governor_adapter import LLMGovernorAdapter, LLMProvider
import time

def test_ollama_integration():
    print('🧪 Testing Real Ollama Integration...')
    governor = LLMGovernorAdapter(LLMProvider.OLLAMA)

    # Test fact
    fact = 'Water boils at 100 degrees Celsius at sea level.'
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
    test_ollama_integration()