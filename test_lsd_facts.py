"""
Test Script for LSD Chemical Formula Facts
===========================================
"""

# Stelle sicher, dass Cache gelöscht wurde
import sys
import os

# Füge src_hexagonal zum Path hinzu
sys.path.insert(0, r'D:\MCP Mods\HAK_GAL_HEXAGONAL\src_hexagonal')

# Importiere den aktualisierten fact_extractor
from adapters.fact_extractor_universal import extract_facts_from_llm

# Simuliere LLM Response für LSD Query
llm_response = """
# Chemical Formula of LSD

LSD (Lysergic acid diethylamide) is a potent hallucinogenic compound with the chemical formula **C₂₀H₂₅N₃O**.

## Step-by-Step Explanation

1. **Full chemical name**: LSD stands for Lysergic acid diethylamide.

2. **Molecular composition**:
   - 20 carbon atoms (C₂₀)
   - 25 hydrogen atoms (H₂₅)
   - 3 nitrogen atoms (N₃)
   - 1 oxygen atom (O)

3. **Structural details**: LSD is a semi-synthetic compound derived from ergot alkaloids. It has a complex structure that includes:
   - An indole structure (a bicyclic structure consisting of a benzene ring fused to a pyrrole ring)
   - A tetracyclic ring system
   - A diethylamide group attached to the carboxylic acid portion of lysergic acid

4. **History**: LSD was first synthesized in 1938 by Swiss chemist Albert Hofmann while researching derivatives of ergot alkaloids at Sandoz Laboratories.

5. **Classification**: LSD is classified as a Schedule I controlled substance in the United States and is similarly restricted in many countries worldwide due to its high potential for abuse and lack of accepted medical use.

## Suggested Additional Facts
ChemicalFormula(LSD, "C₂₀H₂₅N₃O")
AlternativeName(LSD, "Lysergic acid diethylamide")
MolecularWeight(LSD, 323.4)
Discoverer(LSD, "Albert Hofmann")
DiscoveryYear(LSD, 1938)
DrugClass(LSD, "Hallucinogen")
DrugClass(LSD, "Psychedelic")
LegalStatus(LSD, "Schedule I controlled substance")
DerivedFrom(LSD, "Ergot alkaloids")
Contains(LSD, "Indole structure")
PotencyUnit(LSD, "Microgram")
"""

# Test mit der Query
query = "what is the chemical formula of lsd"

# Extrahiere Facts
facts = extract_facts_from_llm(llm_response, query)

print("="*60)
print("EXTRAHIERTE FACTS FÜR LSD QUERY:")
print("="*60)
print(f"Query: {query}")
print(f"Anzahl Facts gefunden: {len(facts)}")
print("\nGenerierte Facts:")
print("-"*60)

for i, fact in enumerate(facts, 1):
    print(f"{i}. {fact}")

print("\n" + "="*60)

# Prüfe ob wissenschaftliche n-äre Facts dabei sind
nary_facts = [f for f in facts if 'ChemicalFormula' in f or 'MolecularStructure' in f or 'ChemicalReaction' in f]
print(f"\nWissenschaftliche n-äre Facts gefunden: {len(nary_facts)}")
if nary_facts:
    print("N-äre Facts:")
    for f in nary_facts:
        print(f"  - {f}")
else:
    print("⚠️ KEINE n-ären Facts gefunden!")

# Teste auch eine generische Chemistry Query ohne explizite Facts im Text
simple_response = """
LSD is a powerful psychedelic drug with complex chemical properties.
It affects serotonin receptors in the brain and causes hallucinations.
"""

print("\n" + "="*60)
print("TEST MIT EINFACHER ANTWORT (ohne explizite Facts):")
print("="*60)

facts2 = extract_facts_from_llm(simple_response, query)
print(f"Anzahl Facts: {len(facts2)}")
print("\nGenerierte Facts:")
for i, fact in enumerate(facts2[:10], 1):  # Zeige nur erste 10
    print(f"{i}. {fact}")
