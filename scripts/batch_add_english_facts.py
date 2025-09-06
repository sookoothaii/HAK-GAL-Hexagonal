#!/usr/bin/env python3
"""
Batch add English replacements for German entities
"""

import requests
import json
import time

# API endpoint
API_URL = "http://127.0.0.1:5000/api/command"
AUTH_TOKEN = "515f57956e7bd15ddc3817573598f190"

# English facts to add (replacing German versions)
ENGLISH_FACTS = [
    "ConsistsOf(ModernPhilosophy, Ethics).",
    "IsSimilarTo(KantIdeas, ModernEpistemology).",
    "HasProperty(KantIdeas, InfluenceOnLaterThinkers).",
    "ConsistsOf(ModernPhilosophy, Metaphysics).",
    "ConsistsOf(ModernPhilosophy, Epistemology).",
    "HasProperty(CriticalPhilosophy, KnowledgeBeginsWithExperience).",
    "HasProperty(AutonomyOfReason, MoralDutyArisesFromSelfGivenReasonLaws).",
    "IsSimilarTo(KantIdeas, ModernEthics).",
    "HasProperty(Aesthetics, RootedInDisinterestedPleasure).",
    "ImpliesUniversally(IsHuman, IsMortal)."
]

def add_fact(statement):
    """Add a single fact via API"""
    payload = {
        "command": "add_fact",
        "statement": statement,
        "source": "entity_migration",
        "tags": ["migration", "english", "complete"],
        "auth_token": AUTH_TOKEN
    }
    
    try:
        response = requests.post(API_URL, json=payload)
        if response.status_code == 200:
            print(f"✅ Added: {statement}")
            return True
        else:
            print(f"❌ Failed: {statement} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error: {statement} - {e}")
        return False

def main():
    print("Starting batch English fact addition...")
    print(f"Adding {len(ENGLISH_FACTS)} facts...")
    
    success = 0
    failed = 0
    
    for fact in ENGLISH_FACTS:
        if add_fact(fact):
            success += 1
        else:
            failed += 1
        time.sleep(0.1)  # Small delay to avoid overwhelming the API
    
    print("\n" + "="*60)
    print(f"MIGRATION COMPLETE")
    print(f"✅ Successfully added: {success} facts")
    if failed > 0:
        print(f"❌ Failed: {failed} facts")
    print("="*60)

if __name__ == "__main__":
    main()
