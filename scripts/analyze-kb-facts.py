#!/usr/bin/env python3
"""
Test der Knowledge Base Suche - Zeigt alle Computer/CPU Facts
"""

import requests
import json
from collections import defaultdict

# API Configuration
API_URL = "http://localhost:5002"
API_KEY = "hg_sk_4f9a8e1b7d2c5f6a8b3d9e0c1a7b4f9d"

headers = {
    "Content-Type": "application/json",
    "X-API-Key": API_KEY
}

print("=" * 80)
print("KNOWLEDGE BASE ANALYSE: Computer/CPU Facts")
print("=" * 80)

# Sammle alle relevanten Facts
all_facts = defaultdict(list)

# Test 1: Direkte Computer Facts
search_queries = [
    ("Computer", "Alle Computer-bezogenen Facts"),
    ("CPU", "Alle CPU-bezogenen Facts"),
    ("HasPart", "Alle HasPart Relationen"),
    ("HasCPU", "HasCPU Relationen"),
    ("Processor", "Processor-bezogene Facts"),
    ("Memory", "Memory-bezogene Facts"),
    ("Motherboard", "Motherboard-bezogene Facts")
]

for query, description in search_queries:
    print(f"\n=== {description} (Query: '{query}') ===")
    
    response = requests.post(
        f"{API_URL}/api/search",
        json={"query": query, "limit": 30},
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        facts = data.get('results', [])
        print(f"Gefunden: {len(facts)} Facts")
        
        # Gruppiere nach Relevanz für Computer/CPU
        for fact in facts:
            statement = fact.get('statement', '')
            
            # Kategorisiere
            if 'Computer' in statement and 'CPU' in statement:
                all_facts['Computer+CPU'].append(statement)
            elif 'Computer' in statement:
                all_facts['Computer'].append(statement)
            elif 'CPU' in statement:
                all_facts['CPU'].append(statement)
            elif 'Processor' in statement:
                all_facts['Processor'].append(statement)
            else:
                all_facts['Andere'].append(statement)
        
        # Zeige die ersten relevanten
        relevant = [f for f in facts if ('Computer' in f.get('statement', '') or 'CPU' in f.get('statement', ''))]
        if relevant:
            print("\nRelevante Facts:")
            for i, fact in enumerate(relevant[:10]):
                print(f"  {i+1}. {fact.get('statement')}")
    else:
        print(f"Fehler: {response.status_code}")

# Zusammenfassung
print("\n" + "=" * 80)
print("ZUSAMMENFASSUNG: Alle Computer/CPU-relevanten Facts")
print("=" * 80)

for category, facts in sorted(all_facts.items()):
    if facts and category != 'Andere':
        print(f"\n{category} ({len(set(facts))} unique Facts):")
        for fact in sorted(set(facts)):
            print(f"  - {fact}")

# Empfehlungen für bessere Suche
print("\n" + "=" * 80)
print("EMPFOHLENE FACTS FÜR KNOWLEDGE BASE:")
print("=" * 80)

recommendations = [
    "HasPart(Laptop, CPU).",
    "HasPart(Server, CPU).",
    "HasPart(Smartphone, CPU).",
    "IsA(CPU, Processor).",
    "IsA(Processor, ComputerComponent).",
    "ProcessesData(CPU, BinaryData).",
    "ConnectsVia(CPU, Socket, Motherboard).",
    "HasSpeed(CPU, GHz).",
    "ManufacturedBy(CPU, Intel).",
    "ManufacturedBy(CPU, AMD).",
    "Contains(CPU, Cores).",
    "Contains(CPU, Cache).",
    "RequiresPower(CPU, Electricity).",
    "GeneratesHeat(CPU, Heat).",
    "CooledBy(CPU, Heatsink)."
]

print("\nFacts die die Suche verbessern würden:")
for rec in recommendations:
    print(f"  - {rec}")

# Test spezifische Queries
print("\n" + "=" * 80)
print("TEST: Spezifische Query-Kombinationen")
print("=" * 80)

specific_tests = [
    "HasPart(Computer, CPU).",
    "HasPart(Computer, CPU)",
    "Computer CPU",
    "Computer, CPU",
    "(Computer, CPU)"
]

for test_query in specific_tests:
    response = requests.post(
        f"{API_URL}/api/search",
        json={"query": test_query, "limit": 5},
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"\nQuery '{test_query}': {data.get('count')} Facts")
        for fact in data.get('results', [])[:3]:
            print(f"  - {fact.get('statement')}")
