#!/usr/bin/env python3
"""
Direct Knowledge Base Search for HAK_GAL
"""

import json
from pathlib import Path

def search_kb(query: str, limit: int = 10):
    """Search the HAK_GAL knowledge base directly"""
    
    kb_path = Path("D:/MCP Mods/HAK_GAL_HEXAGONAL/data/k_assistant.kb.jsonl")
    
    facts = []
    with open(kb_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                fact = json.loads(line)
                facts.append(fact)
    
    # Simple search
    query_lower = query.lower()
    results = []
    
    for fact in facts:
        statement = fact.get('statement', '')
        if query_lower in statement.lower():
            results.append(statement)
            if len(results) >= limit:
                break
    
    return results

# Example searches
print("=" * 60)
print("HAK_GAL Knowledge Base Direct Search")
print("=" * 60)

print("\n1. Search for 'neural':")
neural_facts = search_kb('neural', 5)
for i, fact in enumerate(neural_facts, 1):
    print(f"   {i}. {fact}")

print("\n2. Search for 'quantum':")
quantum_facts = search_kb('quantum', 5)
for i, fact in enumerate(quantum_facts, 1):
    print(f"   {i}. {fact}")

print("\n3. Search for 'kant':")
kant_facts = search_kb('kant', 5)
for i, fact in enumerate(kant_facts, 1):
    print(f"   {i}. {fact}")

print("\n4. Count facts by predicate:")
predicates = {}
with open("D:/MCP Mods/HAK_GAL_HEXAGONAL/data/k_assistant.kb.jsonl", 'r', encoding='utf-8') as f:
    for line in f:
        if line.strip():
            fact = json.loads(line)
            statement = fact.get('statement', '')
            if '(' in statement:
                predicate = statement.split('(')[0]
                predicates[predicate] = predicates.get(predicate, 0) + 1

print("\nTop 10 predicates:")
for pred, count in sorted(predicates.items(), key=lambda x: x[1], reverse=True)[:10]:
    print(f"   {pred}: {count} facts")

print(f"\nTotal facts in KB: {sum(predicates.values())}")
