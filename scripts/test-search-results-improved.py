#!/usr/bin/env python3
"""
Verbessertes Test-Skript um die intelligentere Suche zu testen
"""

import requests
import json
import time

# API Configuration
API_URL = "http://localhost:5002"
API_KEY = "hg_sk_4f9a8e1b7d2c5f6a8b3d9e0c1a7b4f9d"  # From .env

headers = {
    "Content-Type": "application/json",
    "X-API-Key": API_KEY
}

print("=" * 60)
print("INTELLIGENTERE SUCHE TEST - Nach Backend-Fix")
print("=" * 60)

# Test 1: Direct search endpoint mit mehr Facts
print("\n=== Test 1: Suche nach 'HasPart(Computer, CPU).' ===")
search_payload = {
    "query": "HasPart(Computer, CPU).",
    "limit": 20  # Request more facts
}

response = requests.post(f"{API_URL}/api/search", json=search_payload, headers=headers)
if response.status_code == 200:
    data = response.json()
    print(f"Query: {data.get('query')}")
    print(f"Count: {data.get('count')}")
    print(f"Results found: {len(data.get('results', []))}")
    print("\nFacts found:")
    for i, fact in enumerate(data.get('results', [])):
        print(f"  {i+1}. {fact.get('statement')}")
else:
    print(f"Error: {response.status_code} - {response.text}")

# Test 2: Teste verschiedene Such-Varianten
print("\n=== Test 2: Verschiedene Such-Varianten ===")
test_queries = [
    "HasPart(Computer, CPU)",  # Ohne Punkt
    "Computer",                 # Nur Entity
    "CPU",                     # Andere Entity
    "HasPart",                 # Nur Prädikat
    "HasCPU",                  # Ähnliches Prädikat
]

for test_query in test_queries:
    search_payload = {"query": test_query, "limit": 5}
    response = requests.post(f"{API_URL}/api/search", json=search_payload, headers=headers)
    if response.status_code == 200:
        data = response.json()
        print(f"\nQuery '{test_query}': {data.get('count')} facts")
        for fact in data.get('results', [])[:3]:
            print(f"  - {fact.get('statement')}")

# Test 3: Test case-insensitive search
print("\n=== Test 3: Case-Insensitive Test ===")
test_cases = [
    "haspart(computer, cpu)",
    "HASPART(COMPUTER, CPU)",
    "machine learning",
    "MachineLearning",
    "MACHINELEARNING"
]

for test_case in test_cases:
    search_payload = {"query": test_case, "limit": 3}
    response = requests.post(f"{API_URL}/api/search", json=search_payload, headers=headers)
    if response.status_code == 200:
        data = response.json()
        print(f"\nQuery '{test_case}': {data.get('count')} facts found")

# Test 4: Check LLM with context facts
print("\n=== Test 4: LLM mit Context Facts ===")

# Erst Facts sammeln
search_payload = {"query": "HasPart(Computer, CPU)", "limit": 10}
response = requests.post(f"{API_URL}/api/search", json=search_payload, headers=headers)
context_facts = []
if response.status_code == 200:
    data = response.json()
    context_facts = [f.get('statement') for f in data.get('results', [])]
    print(f"Context facts collected: {len(context_facts)}")

# Dann LLM mit context facts aufrufen
llm_payload = {
    "topic": "HasPart(Computer, CPU).",
    "context_facts": context_facts
}

response = requests.post(f"{API_URL}/api/llm/get-explanation", json=llm_payload, headers=headers)
if response.status_code == 200:
    data = response.json()
    print(f"\nLLM Provider: {data.get('llm_provider')}")
    print(f"Response time: {data.get('response_time')}")
    print(f"Context facts provided: {len(llm_payload['context_facts'])}")
    print(f"Suggested facts count: {len(data.get('suggested_facts', []))}")
    
    # Zeige die ersten paar Context Facts
    print("\nContext facts sent to LLM:")
    for i, fact in enumerate(context_facts[:5]):
        print(f"  {i+1}. {fact}")
    if len(context_facts) > 5:
        print(f"  ... and {len(context_facts) - 5} more")
    
    # Prüfe ob LLM die Facts erwähnt
    explanation = data.get('explanation', '')
    facts_mentioned = sum(1 for fact in context_facts if fact in explanation)
    print(f"\nFacts mentioned in explanation: {facts_mentioned}/{len(context_facts)}")
else:
    print(f"Error: {response.status_code} - {response.text}")

# Test 5: Performance Test
print("\n=== Test 5: Performance Test ===")
start_time = time.time()
search_payload = {"query": "HasPart(Computer, CPU).", "limit": 20}
response = requests.post(f"{API_URL}/api/search", json=search_payload, headers=headers)
search_time = (time.time() - start_time) * 1000
print(f"Search response time: {search_time:.2f}ms")

print("\n" + "=" * 60)
print("TEST ABGESCHLOSSEN")
print("=" * 60)
