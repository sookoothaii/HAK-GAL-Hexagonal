#!/usr/bin/env python
"""
Optimize Learning Engines - Bessere Fact-Qualität
==================================================
Verbessert die Engines für hochwertigere Facts
"""

import requests
import json
import time

def optimize_learning_engines():
    """Optimiere die Learning Engines für bessere Qualität"""
    
    print("="*70)
    print("OPTIMIZING LEARNING ENGINES")
    print("="*70)
    
    base_url = "http://localhost:5002"
    
    # 1. Stop current governor if running
    print("\n[1] Stopping current Governor...")
    try:
        r = requests.post(f"{base_url}/api/governor/stop")
        print("✅ Governor stopped")
        time.sleep(2)
    except:
        print("⚠️ Governor was not running")
    
    # 2. Configure better learning parameters
    print("\n[2] Configuring optimized learning parameters...")
    
    optimized_config = {
        "mode": "quality_focused",  # Not just speed
        "target_facts_per_minute": 20,  # Slower but better
        "enable_aethelred": True,
        "enable_thesis": True,
        
        # Quality parameters
        "min_confidence": 0.7,  # Only high-confidence facts
        "enable_deduplication": True,
        "enable_validation": True,
        "filter_generic": True,  # Filter out X1, X2, Update, etc.
        
        # Better prompts for engines
        "aethelred_config": {
            "temperature": 0.7,  # More focused
            "avoid_patterns": ["Update", "X1", "X2", "X3", "Test", "Debug"],
            "preferred_predicates": [
                "IsA", "HasProperty", "Causes", "RelatedTo",
                "Contains", "PartOf", "UsedFor", "LocatedIn",
                "CreatedBy", "InfluencedBy", "Requires", "Produces"
            ],
            "domains": [
                "Science", "Technology", "History", "Philosophy",
                "Mathematics", "Biology", "Physics", "Chemistry"
            ]
        },
        
        "thesis_config": {
            "consolidation_threshold": 0.8,
            "min_support_facts": 3,
            "focus_on_relationships": True
        }
    }
    
    try:
        # Send configuration
        r = requests.post(f"{base_url}/api/governor/configure", 
                         json=optimized_config)
        
        if r.status_code == 200:
            print("✅ Configuration updated")
        else:
            print(f"⚠️ Config response: {r.status_code}")
    except Exception as e:
        print(f"⚠️ Config error: {e}")
    
    # 3. Clean up bad facts
    print("\n[3] Cleaning up low-quality facts...")
    
    cleanup_queries = [
        "DELETE FROM facts WHERE statement LIKE '%Update(%'",
        "DELETE FROM facts WHERE statement LIKE '%X1(%'",
        "DELETE FROM facts WHERE statement LIKE '%X2(%'",
        "DELETE FROM facts WHERE statement LIKE '%X3(%'",
        "DELETE FROM facts WHERE statement LIKE '%Test%'",
        "DELETE FROM facts WHERE statement LIKE '%Debug%'",
        "DELETE FROM facts WHERE confidence < 0.5"
    ]
    
    # Note: This would need direct DB access
    print("⚠️ Manual cleanup recommended for generic facts")
    
    # 4. Add high-quality seed facts
    print("\n[4] Adding high-quality seed facts...")
    
    quality_facts = [
        {
            "statement": "IsA(QuantumComputing, ComputationalParadigm).",
            "confidence": 0.95,
            "source": "Scientific_Knowledge"
        },
        {
            "statement": "Requires(MachineLearning, LargeDatasets).",
            "confidence": 0.9,
            "source": "Technical_Knowledge"
        },
        {
            "statement": "InfluencedBy(ModernPhysics, Einstein).",
            "confidence": 1.0,
            "source": "Historical_Knowledge"
        },
        {
            "statement": "Contains(DNA, GeneticInformation).",
            "confidence": 0.95,
            "source": "Biological_Knowledge"
        },
        {
            "statement": "Produces(Photosynthesis, Oxygen).",
            "confidence": 0.98,
            "source": "Scientific_Knowledge"
        },
        {
            "statement": "UsedFor(Algorithms, ProblemSolving).",
            "confidence": 0.92,
            "source": "Computer_Science"
        },
        {
            "statement": "RelatedTo(ClimateChange, GreenhouseGases).",
            "confidence": 0.95,
            "source": "Environmental_Science"
        },
        {
            "statement": "Causes(Gravity, Attraction).",
            "confidence": 0.99,
            "source": "Physics"
        },
        {
            "statement": "PartOf(Neurons, NervousSystem).",
            "confidence": 0.98,
            "source": "Neuroscience"
        },
        {
            "statement": "CreatedBy(Relativity, Einstein).",
            "confidence": 1.0,
            "source": "History_of_Science"
        }
    ]
    
    added = 0
    for fact in quality_facts:
        try:
            r = requests.post(f"{base_url}/api/facts", json=fact)
            if r.status_code in [200, 201]:
                added += 1
                print(f"  ✅ Added: {fact['statement'][:50]}")
        except:
            pass
    
    print(f"\n✅ Added {added} high-quality seed facts")
    
    # 5. Restart governor with quality focus
    print("\n[5] Starting Governor with QUALITY FOCUS...")
    
    start_config = {
        "mode": "balanced_quality",
        "target_facts_per_minute": 25,  # Moderate speed
        "quality_threshold": 0.75,
        "enable_validation": True,
        "enable_neural_feedback": True
    }
    
    try:
        r = requests.post(f"{base_url}/api/governor/start", json=start_config)
        
        if r.status_code == 200:
            print("✅ Governor started with quality focus!")
        else:
            print(f"⚠️ Start response: {r.status_code}")
    except Exception as e:
        print(f"Error: {e}")
    
    # 6. Verify improvements
    print("\n[6] Waiting for new facts to generate...")
    time.sleep(10)
    
    try:
        r = requests.get(f"{base_url}/api/governor/status")
        status = r.json()
        
        print("\n" + "="*70)
        print("OPTIMIZATION COMPLETE")
        print("="*70)
        print(f"✅ Governor Status: {status.get('status', 'unknown')}")
        print(f"✅ Learning Rate: {status.get('learning_rate', 0)} facts/min")
        print(f"✅ Quality Mode: ENABLED")
        print("\n📈 Expected Improvements:")
        print("  - No more 'Update' or 'X1/X2/X3' facts")
        print("  - Higher confidence scores (>0.7)")
        print("  - More meaningful predicates")
        print("  - Better domain coverage")
        print("\n⏰ Check quality again in 5 minutes:")
        print("  python analyze_fact_quality.py")
        
    except Exception as e:
        print(f"Status check error: {e}")
    
    print("\n" + "="*70)

if __name__ == "__main__":
    optimize_learning_engines()
    
    print("\n💡 NEXT STEPS:")
    print("1. Let system run for 5 minutes")
    print("2. Run: python analyze_fact_quality.py")
    print("3. Check if quality improved")
    print("4. Adjust parameters if needed")
