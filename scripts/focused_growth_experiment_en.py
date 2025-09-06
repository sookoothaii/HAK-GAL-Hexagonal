#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
HAK-GAL Focused Growth Experiment - ENGLISH VERSION
Generates new facts for the knowledge base using LLM
Enhanced with 'all' and 'random' topic support
"""

import requests
import json
import time
import re
from typing import List, Dict, Any
import random

# --- CONFIGURATION ---

# 1. API Endpoints
API_BASE_URL = "http://localhost:5002/api"
LLM_EXPLAIN_URL = f"{API_BASE_URL}/llm/get-explanation"
FACTS_URL = f"{API_BASE_URL}/facts"
SEARCH_URL = f"{API_BASE_URL}/search"

# 2. Authentication
API_KEY = "hg_sk_4f9a8e1b7d2c5f6a8b3d9e0c1a7b4f9d"

# 3. Available Topics (ALL IN ENGLISH)
TOPICS = {
    "ai": {
        "name": "Artificial Intelligence",
        "seed_facts": [
            "IsA(MachineLearning, ArtificialIntelligence).",
            "Uses(DeepLearning, NeuralNetworks).",
            "EnabledBy(ComputerVision, ConvolutionalNeuralNetworks)."
        ]
    },
    "quantum": {
        "name": "Quantum Computing",
        "seed_facts": [
            "Uses(QuantumComputer, Qubits).",
            "Enables(QuantumEntanglement, QuantumTeleportation).",
            "DifferentFrom(QuantumComputing, ClassicalComputing)."
        ]
    },
    "rome": {
        "name": "Roman Empire",
        "seed_facts": [
            "FoundedIn(RomanRepublic, 509BC).",
            "EndedWith(RomanRepublic, RiseOfAugustus).",
            "HadSocialClasses(RomanRepublic, PatriciansAndPlebeians)."
        ]
    },
    "space": {
        "name": "Space Exploration",
        "seed_facts": [
            "FirstHumanIn(Space, YuriGagarin).",
            "LandedOn(Apollo11, Moon).",
            "Orbits(InternationalSpaceStation, Earth)."
        ]
    },
    "biology": {
        "name": "Molecular Biology",
        "seed_facts": [
            "Contains(DNA, GeneticInformation).",
            "ProducesProteinsFrom(Ribosome, RNA).",
            "ControlsCell(Nucleus, CellularActivities)."
        ]
    },
    "climate": {
        "name": "Climate Science",
        "seed_facts": [
            "CausedBy(GlobalWarming, GreenhouseGases).",
            "Affects(ClimateChange, WeatherPatterns).",
            "ReducedBy(CarbonEmissions, RenewableEnergy)."
        ]
    },
    "blockchain": {
        "name": "Blockchain Technology",
        "seed_facts": [
            "Uses(Bitcoin, Blockchain).",
            "Enables(SmartContracts, DecentralizedApplications).",
            "SecuredBy(Blockchain, Cryptography)."
        ]
    },
    "medicine": {
        "name": "Modern Medicine",
        "seed_facts": [
            "Uses(CRISPR, GeneEditing).",
            "Treats(Antibiotics, BacterialInfections).",
            "EnabledBy(MRI, MagneticResonance)."
        ]
    }
}

# 4. Experiment Parameters
CYCLES = 5
MAX_FACTS_PER_CYCLE = 20  # Limit to prevent overwhelming the system
CYCLES_PER_TOPIC_IN_ALL = 3  # Reduced cycles when running all topics

# --- HELPER FUNCTIONS ---

def call_hakgal_api(endpoint_url: str, method: str = 'POST', payload: dict = None) -> dict:
    """Generic function to call HAK/GAL API endpoints"""
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": API_KEY
    }
    
    print(f"    [API Call] Target: {endpoint_url}, Method: {method}")

    try:
        response = requests.request(
            method, endpoint_url, 
            headers=headers, 
            json=payload, 
            timeout=300 # Erhöht für lokale LLMs wie Ollama
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"    [API Error] Communication error: {e}")
        return {"error": str(e)}

def validate_fact_format(fact: str) -> bool:
    """Validate that a fact follows the correct format"""
    # Must match: Predicate(Entity1, Entity2).
    pattern = r"^[A-Z][A-Za-z0-9]*\([A-Za-z0-9_]+,\s*[A-Za-z0-9_]+\)\.$"
    return bool(re.match(pattern, fact))

def clean_fact(fact: str) -> str:
    """Clean and normalize a fact string"""
    # Remove extra spaces
    fact = re.sub(r'\s+', ' ', fact.strip())
    
    # Ensure it ends with a period
    if not fact.endswith('.'):
        fact += '.'
    
    # Remove spaces around parentheses and commas
    fact = re.sub(r'\s*\(\s*', '(', fact)
    fact = re.sub(r'\s*\)\s*', ')', fact)
    fact = re.sub(r'\s*,\s*', ', ', fact)
    
    return fact

# --- MAIN EXPERIMENT ---

def run_single_experiment(topic_key: str, cycles: int = CYCLES):
    """Run experiment for a single topic"""
    
    if topic_key not in TOPICS:
        print(f"⚠️ Unknown topic: {topic_key}")
        return None
    
    topic_config = TOPICS[topic_key]
    TOPIC = topic_config["name"]
    SEED_FACTS = topic_config["seed_facts"]
    
    print(f"\n{'='*70}")
    print(f"TOPIC: {TOPIC} ({topic_key})")
    print(f"{'='*70}")
    print(f"Cycles: {cycles}")
    print(f"Max facts per cycle: {MAX_FACTS_PER_CYCLE}")

    # Initialize knowledge base with seed facts
    print("\n[INITIALIZATION]")
    for fact in SEED_FACTS:
        print(f"  → Seed: \"{fact}\"")
        add_payload = {"statement": fact, "source": f"seed_{topic_key}"}
        result = call_hakgal_api(FACTS_URL, payload=add_payload)
        if "error" not in result:
            print(f"    ✅ Added")
        else:
            print(f"    ⏭️ Exists")
    
    time.sleep(1)
    
    frontier = list(SEED_FACTS)
    known_facts_set = set(SEED_FACTS)
    stats = {
        "added": 0, 
        "rejected_redundant": 0, 
        "rejected_invalid": 0,
        "llm_providers_used": set()
    }

    # Main growth cycles
    for cycle_num in range(1, cycles + 1):
        print(f"\n[CYCLE {cycle_num}/{cycles}]")
        
        if not frontier:
            print("  ⚠️ Knowledge frontier empty")
            break
            
        base_fact = frontier.pop(0)
        print(f"  🔬 Expanding: \"{base_fact[:50]}...\"" if len(base_fact) > 50 else f"  🔬 Expanding: \"{base_fact}\"")

        # 1. Generate new facts via LLM
        llm_payload = {
            "topic": TOPIC, 
            "context_facts": [base_fact]
        }
        
        print(f"  📡 Calling LLM...")
        response = call_hakgal_api(LLM_EXPLAIN_URL, payload=llm_payload)

        if not response or "suggested_facts" not in response:
            print(f"  ❌ No facts from LLM")
            stats["rejected_invalid"] += 1
            continue

        candidate_facts = response["suggested_facts"]
        llm_provider = response.get("llm_provider", "Unknown")
        response_time = response.get("response_time", "N/A")
        
        print(f"  ✅ Got {len(candidate_facts)} from {llm_provider} ({response_time})")
        stats["llm_providers_used"].add(llm_provider)

        # 2. Validate and add facts
        facts_added_this_cycle = 0
        
        for candidate in candidate_facts[:MAX_FACTS_PER_CYCLE]:
            # Clean the candidate
            candidate = clean_fact(candidate)
            
            # Validate format
            if not validate_fact_format(candidate):
                stats["rejected_invalid"] += 1
                continue

            # Check for duplicates
            if candidate in known_facts_set:
                stats["rejected_redundant"] += 1
                continue

            # Add to knowledge base
            add_payload = {
                "statement": candidate, 
                "source": f"cycle_{cycle_num}_{llm_provider.lower()}"
            }
            add_result = call_hakgal_api(FACTS_URL, payload=add_payload)
            
            if add_result and add_result.get("success"):
                stats["added"] += 1
                facts_added_this_cycle += 1
                frontier.append(candidate)
                known_facts_set.add(candidate)
                print(f"    + {candidate[:60]}..." if len(candidate) > 60 else f"    + {candidate}")
            else:
                message = add_result.get('message', '')
                if "exists" in message.lower():
                    stats["rejected_redundant"] += 1
                else:
                    stats["rejected_invalid"] += 1
        
        print(f"  📊 Added {facts_added_this_cycle} facts this cycle")
        time.sleep(1)

    # Return statistics for this topic
    return {
        "topic": TOPIC,
        "topic_key": topic_key,
        "stats": stats,
        "new_facts": list(known_facts_set - set(SEED_FACTS))
    }

def run_all_topics():
    """Run experiment for all topics sequentially"""
    print("=" * 70)
    print("HAK/GAL GROWTH EXPERIMENT - ALL TOPICS MODE")
    print("=" * 70)
    print(f"Topics to explore: {', '.join(TOPICS.keys())}")
    print(f"Cycles per topic: {CYCLES_PER_TOPIC_IN_ALL}")
    print("=" * 70)
    
    all_results = []
    total_stats = {
        "added": 0,
        "rejected_redundant": 0,
        "rejected_invalid": 0,
        "llm_providers": set()
    }
    
    for topic_key in TOPICS.keys():
        result = run_single_experiment(topic_key, cycles=CYCLES_PER_TOPIC_IN_ALL)
        if result:
            all_results.append(result)
            total_stats["added"] += result["stats"]["added"]
            total_stats["rejected_redundant"] += result["stats"]["rejected_redundant"]
            total_stats["rejected_invalid"] += result["stats"]["rejected_invalid"]
            total_stats["llm_providers"].update(result["stats"]["llm_providers_used"])
            
            # Short pause between topics
            time.sleep(3)
    
    # Final comprehensive report
    print("\n" + "=" * 70)
    print("ALL TOPICS COMPLETED - FINAL REPORT")
    print("=" * 70)
    
    print("\n📊 TOTAL METRICS:")
    print(f"  ✅ Total facts added: {total_stats['added']}")
    print(f"  ⏭️ Total rejected (duplicate): {total_stats['rejected_redundant']}")
    print(f"  ❌ Total rejected (invalid): {total_stats['rejected_invalid']}")
    print(f"  🤖 LLM providers used: {', '.join(total_stats['llm_providers'])}")
    
    print("\n📈 BREAKDOWN BY TOPIC:")
    for result in all_results:
        print(f"\n  {result['topic']} ({result['topic_key']}):")
        print(f"    Added: {result['stats']['added']}")
        print(f"    Sample fact: {result['new_facts'][0][:50]}..." if result['new_facts'] else "    No new facts")
    
    print("\n" + "=" * 70)
    print("💡 Knowledge base has been enriched across all domains!")
    print("=" * 70)

def run_random_topics(num_cycles: int = 10):
    """Run experiment with random topic selection each cycle"""
    print("=" * 70)
    print("HAK/GAL GROWTH EXPERIMENT - RANDOM MODE")
    print("=" * 70)
    print(f"Total cycles: {num_cycles}")
    print(f"Topics will be selected randomly")
    print("=" * 70)
    
    stats = {
        "added": 0,
        "rejected_redundant": 0, 
        "rejected_invalid": 0,
        "topics_used": [],
        "llm_providers": set()
    }
    
    for cycle in range(1, num_cycles + 1):
        # Random topic selection
        topic_key = random.choice(list(TOPICS.keys()))
        topic_config = TOPICS[topic_key]
        
        print(f"\n[RANDOM CYCLE {cycle}/{num_cycles}] Topic: {topic_config['name']}")
        
        # Run single cycle for this topic
        result = run_single_experiment(topic_key, cycles=1)
        
        if result:
            stats["added"] += result["stats"]["added"]
            stats["rejected_redundant"] += result["stats"]["rejected_redundant"]
            stats["rejected_invalid"] += result["stats"]["rejected_invalid"]
            stats["topics_used"].append(topic_key)
            stats["llm_providers"].update(result["stats"]["llm_providers_used"])
        
        time.sleep(2)
    
    # Final report
    print("\n" + "=" * 70)
    print("RANDOM MODE COMPLETED - FINAL REPORT")
    print("=" * 70)
    print("\n📊 METRICS:")
    print(f"  ✅ Facts added: {stats['added']}")
    print(f"  ⏭️ Rejected (duplicate): {stats['rejected_redundant']}")
    print(f"  ❌ Rejected (invalid): {stats['rejected_invalid']}")
    print(f"  🎲 Topics explored: {', '.join(set(stats['topics_used']))}")
    print(f"  🤖 LLM providers: {', '.join(stats['llm_providers'])}")
    print("=" * 70)

def main():
    """Main entry point with argument parsing"""
    import argparse
    
    # Extended choices including 'all' and 'random'
    topic_choices = list(TOPICS.keys()) + ['all', 'random']
    
    parser = argparse.ArgumentParser(
        description='HAK-GAL Knowledge Growth Experiment (English)'
    )
    parser.add_argument(
        '--topic', 
        choices=topic_choices,
        help='Topic to explore: ' + ', '.join(topic_choices)
    )
    parser.add_argument(
        '--list-topics',
        action='store_true',
        help='List all available topics'
    )
    parser.add_argument(
        '--cycles',
        type=int,
        default=None,
        help='Number of cycles (default: 5 for single topic, varies for all/random)'
    )
    
    args = parser.parse_args()
    
    if args.list_topics:
        print("\n📚 AVAILABLE TOPICS:")
        print("=" * 50)
        for key, config in TOPICS.items():
            print(f"  {key:12} - {config['name']}")
            print(f"               Sample: {config['seed_facts'][0]}")
        print("\nSPECIAL MODES:")
        print("  all          - Run all topics sequentially")
        print("  random       - Random topic selection each cycle")
        print("=" * 50)
        print("\nUsage:")
        print("  python focused_growth_experiment_en.py --topic ai")
        print("  python focused_growth_experiment_en.py --topic all")
        print("  python focused_growth_experiment_en.py --topic random")
    elif args.topic == 'all':
        run_all_topics()
    elif args.topic == 'random':
        cycles = args.cycles or 10
        run_random_topics(num_cycles=cycles)
    elif args.topic:
        cycles = args.cycles or CYCLES
        result = run_single_experiment(args.topic, cycles=cycles)
        
        # Print final report for single topic
        if result:
            print("\n" + "=" * 70)
            print("EXPERIMENT COMPLETED - FINAL REPORT")
            print("=" * 70)
            print(f"Topic: {result['topic']}")
            print(f"Topic Key: {result['topic_key']}")
            print("\n📊 METRICS:")
            print(f"  ✅ New facts added: {result['stats']['added']}")
            print(f"  ⏭️ Rejected (duplicate): {result['stats']['rejected_redundant']}")
            print(f"  ❌ Rejected (invalid): {result['stats']['rejected_invalid']}")
            print(f"  🤖 LLM providers used: {', '.join(result['stats']['llm_providers_used'])}")
            
            if result['new_facts']:
                print("\n📝 NEW KNOWLEDGE (Sample):")
                for i, fact in enumerate(result['new_facts'][:10], 1):
                    print(f"  {i}. {fact}")
                if len(result['new_facts']) > 10:
                    print(f"  ... and {len(result['new_facts']) - 10} more facts")
            print("=" * 70)
    else:
        # No topic specified - run random single topic
        topic_key = random.choice(list(TOPICS.keys()))
        print(f"No topic specified - randomly selected: {topic_key}")
        result = run_single_experiment(topic_key)

if __name__ == "__main__":
    main()
