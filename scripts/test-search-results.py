#!/usr/bin/env python3
"""
Test-Skript um zu überprüfen, was die API tatsächlich zurückgibt
"""

import requests
import json

# API Configuration
API_URL = "http://localhost:5002"
API_KEY = "hg_sk_4f9a8e1b7d2c5f6a8b3d9e0c1a7b4f9d"  # From .env

headers = {
    "Content-Type": "application/json",
    "X-API-Key": API_KEY
}

# Test 1: Direct search endpoint
print("=== Test 1: Direct Search API ===")
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

# Test 2: Search for related terms
print("\n=== Test 2: Search for 'Computer' ===")
search_payload = {
    "query": "Computer",
    "limit": 20
}

response = requests.post(f"{API_URL}/api/search", json=search_payload, headers=headers)
if response.status_code == 200:
    data = response.json()
    cpu_related = [f for f in data.get('results', []) if 'CPU' in f.get('statement', '')]
    print(f"Total Computer facts: {len(data.get('results', []))}")
    print(f"CPU-related facts: {len(cpu_related)}")
    print("\nCPU-related facts:")
    for fact in cpu_related:
        print(f"  - {fact.get('statement')}")

# Test 3: Check what LLM endpoint returns
print("\n=== Test 3: LLM Get-Explanation ===")
llm_payload = {
    "topic": "HasPart(Computer, CPU).",
    "context_facts": []  # Let it search
}

response = requests.post(f"{API_URL}/api/llm/get-explanation", json=llm_payload, headers=headers)
if response.status_code == 200:
    data = response.json()
    print(f"LLM Provider: {data.get('llm_provider')}")
    print(f"Context facts used: {data.get('context_facts_used', 'N/A')}")
    print(f"Suggested facts count: {len(data.get('suggested_facts', []))}")
    
    # Check if context_facts are included
    if 'context_facts' in data:
        print(f"\nContext facts provided to LLM: {len(data.get('context_facts', []))}")
        for i, fact in enumerate(data.get('context_facts', [])[:5]):
            print(f"  {i+1}. {fact}")
else:
    print(f"Error: {response.status_code} - {response.text}")