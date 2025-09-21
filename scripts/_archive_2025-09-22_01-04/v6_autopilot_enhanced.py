#!/usr/bin/env python3
"""
Enhanced V6 Autopilot - Lebendiges Learning mit LLM
=====================================================
Verbesserte Version mit:
- Kreativen Facts statt langweiligen Wiederholungen
- LLM-Integration aktiviert
- Dynamische Fact-Generierung
"""

import os
import sys
import time
import json
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any, List

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

# Import creative generator
try:
    from creative_fact_generator import CreativeFactGenerator
except:
    CreativeFactGenerator = None

import requests
import v6_safe_boost as v6

API_BASE = os.environ.get('V6_API_BASE', 'http://127.0.0.1:5002')
LOG_DIR = ROOT / 'logs'
LOG_DIR.mkdir(parents=True, exist_ok=True)

# KRITISCH: LLM API Keys setzen für Boosting!
def ensure_llm_keys():
    """Ensure LLM API keys are loaded"""
    suite_env = ROOT.parent / 'HAK_GAL_SUITE' / '.env'
    if suite_env.exists():
        print("📋 Loading LLM API keys...")
        for line in suite_env.read_text(encoding='utf-8').splitlines():
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '=' in line:
                key, val = line.split('=', 1)
                key = key.strip()
                val = val.strip().strip('"').strip("'")
                if 'API_KEY' in key and key not in os.environ:
                    os.environ[key] = val
                    print(f"  ✅ {key[:20]}...")
    
    # Force LLM to be enabled in v6
    os.environ['V6_USE_LLM'] = 'true'
    print("  ✅ LLM Boosting activated")


def fetch_creative_candidates(limit: int) -> List[str]:
    """Generate creative, diverse candidates"""
    if CreativeFactGenerator:
        print("🎨 Generating creative facts...")
        generator = CreativeFactGenerator()
        facts = generator.generate_batch(limit, diversity=0.8)
        
        # Add some themed facts for variety
        themes = ['ai_revolution', 'biological_systems', 'digital_transformation']
        theme = random.choice(themes)
        themed = generator.generate_themed_batch(theme, limit // 4)
        facts.extend(themed)
        
        # Shuffle for variety
        random.shuffle(facts)
        print(f"  ✅ Generated {len(facts)} creative facts")
        return facts[:limit]
    else:
        # Fallback to varied examples
        templates = [
            "IsA({}, {})",
            "HasPart({}, {})",
            "Enables({}, {})",
            "Causes({}, {})",
            "RequiresFor({}, {})",
            "DependsOn({}, {})",
            "Influences({}, {})",
            "Transforms({}, {})"
        ]
        
        entities = [
            'QuantumComputing', 'MachineLearning', 'Blockchain', 'NeuralNetwork',
            'DNA', 'Protein', 'Cell', 'Evolution', 'Consciousness', 'Ethics',
            'Innovation', 'Strategy', 'Ecosystem', 'Climate', 'Energy'
        ]
        
        facts = []
        for _ in range(limit):
            template = random.choice(templates)
            e1, e2 = random.sample(entities, 2)
            fact = template.format(e1, e2) + "."
            facts.append(fact)
        
        return facts


def fetch_mixed_candidates(limit: int) -> List[str]:
    """Mix creative new facts with some DB facts for variety"""
    candidates = []
    
    # 70% creative new facts
    creative_count = int(limit * 0.7)
    candidates.extend(fetch_creative_candidates(creative_count))
    
    # 30% from DB (if available) for testing recall
    db_count = limit - creative_count
    try:
        r = requests.get(f"{API_BASE}/api/facts", params={'limit': db_count}, timeout=5)
        if r.status_code == 200:
            facts = r.json().get('facts', [])
            for f in facts:
                if isinstance(f, dict) and 'statement' in f:
                    candidates.append(f['statement'])
                elif isinstance(f, str):
                    candidates.append(f)
    except:
        pass
    
    # Shuffle for good mix
    random.shuffle(candidates)
    return candidates[:limit]


def run_enhanced_cycle(candidates: List[str], episodes: int, threshold: float, auto: bool) -> Dict[str, Any]:
    """Enhanced cycle with better logging"""
    print(f"\n🔄 Processing {episodes} candidates...")
    print(f"  Mode: {'AUTO-ADD' if auto else 'SHADOW'}")
    print(f"  Threshold: {threshold}")
    print(f"  LLM: {'ENABLED' if os.environ.get('V6_USE_LLM') else 'DISABLED'}")
    
    # Show sample of what we're testing
    print("\n📝 Sample candidates:")
    for fact in candidates[:3]:
        print(f"  • {fact}")
    
    # Configure v6
    v6.MIN_COMBINED = float(threshold)
    v6.SHADOW_MODE = (not auto)
    
    # Ensure LLM is used
    if hasattr(v6, 'USE_LLM'):
        v6.USE_LLM = True
    
    start = time.time()
    v6.process_statements(candidates, episodes=episodes, v5_style=True, quiet_items=True, json_summary=False)
    dur = time.time() - start
    
    return {"duration_sec": dur}


def main():
    print("\n================= V6 AUTOPILOT ENHANCED =================")
    print("Lebendiges Learning mit kreativen Facts und LLM-Boosting")
    print("=========================================================")
    
    # Ensure LLM keys are loaded
    ensure_llm_keys()
    
    # Simplified choices
    print("\nSchnellauswahl:")
    print("1. Test-Run (5 min, Shadow-Mode, kreative Facts)")
    print("2. Learning-Run (30 min, Auto-Mode, gemischte Facts)")
    print("3. Power-Run (1h, Auto-Mode, maximale Vielfalt)")
    print("4. Custom (eigene Einstellungen)")
    
    choice = input("\nAuswahl (1-4) [1]: ").strip() or "1"
    
    if choice == "1":
        mode, hours, episodes, source = "shadow", 0.083, 10, "creative"
        threshold = 0.65
    elif choice == "2":
        mode, hours, episodes, source = "auto", 0.5, 30, "mixed"
        threshold = 0.70
    elif choice == "3":
        mode, hours, episodes, source = "auto", 1.0, 50, "mixed"
        threshold = 0.75
    else:
        # Custom settings
        mode = input("Mode (shadow/auto) [shadow]: ").strip() or "shadow"
        hours = float(input("Duration in hours [0.25]: ").strip() or "0.25")
        episodes = int(input("Episodes per round [20]: ").strip() or "20")
        source = input("Source (creative/mixed/db) [creative]: ").strip() or "creative"
        threshold = float(input("Threshold (0.5-0.9) [0.70]: ").strip() or "0.70")
    
    print(f"\n📋 Configuration:")
    print(f"  Mode: {'AUTO-ADD' if mode == 'auto' else 'SHADOW'}")
    print(f"  Duration: {hours}h")
    print(f"  Episodes/Round: {episodes}")
    print(f"  Threshold: {threshold}")
    print(f"  Source: {source}")
    
    # Get candidates
    total_needed = int(episodes * hours * 60 / 2)  # Assume 2 min per round
    total_needed = max(total_needed, 100)
    
    if source == "creative":
        candidates = fetch_creative_candidates(total_needed)
    elif source == "mixed":
        candidates = fetch_mixed_candidates(total_needed)
    else:
        # Try DB first
        candidates = []
        try:
            r = requests.get(f"{API_BASE}/api/facts", params={'limit': total_needed}, timeout=5)
            if r.status_code == 200:
                facts = r.json().get('facts', [])
                candidates = [f.get('statement', '') for f in facts if f.get('statement')]
        except:
            pass
        
        if not candidates:
            print("⚠️ No DB facts available, using creative generator")
            candidates = fetch_creative_candidates(total_needed)
    
    print(f"\n✅ Prepared {len(candidates)} candidates")
    
    # Get initial count
    start_count = None
    try:
        r = requests.get(f"{API_BASE}/api/facts/count", timeout=5)
        if r.status_code == 200:
            start_count = r.json().get('count')
            print(f"📊 Starting facts: {start_count}")
    except:
        pass
    
    # Run cycles
    end_time = datetime.now() + timedelta(hours=hours)
    cycle_no = 0
    idx = 0
    results = []
    
    while datetime.now() < end_time and idx < len(candidates):
        cycle_no += 1
        print(f"\n{'='*60}")
        print(f"CYCLE {cycle_no} - {datetime.now().strftime('%H:%M:%S')}")
        print('='*60)
        
        # Get batch (non-repeating)
        batch = candidates[idx:idx + episodes]
        if not batch:
            print("✅ All candidates processed")
            break
        
        idx += episodes
        
        # Run cycle
        result = run_enhanced_cycle(batch, len(batch), threshold, mode == 'auto')
        results.append(result)
        
        # Check count change
        try:
            r = requests.get(f"{API_BASE}/api/facts/count", timeout=5)
            if r.status_code == 200:
                current = r.json().get('count')
                if start_count and current:
                    delta = current - start_count
                    print(f"\n📈 Net gain so far: +{delta} facts")
        except:
            pass
        
        # Pause between rounds
        if datetime.now() < end_time:
            print("\n⏸️ Pausing 1 minute...")
            time.sleep(60)
    
    # Final summary
    print(f"\n{'='*60}")
    print("FINAL SUMMARY")
    print('='*60)
    print(f"Cycles completed: {cycle_no}")
    print(f"Facts processed: {idx}")
    
    try:
        r = requests.get(f"{API_BASE}/api/facts/count", timeout=5)
        if r.status_code == 200:
            end_count = r.json().get('count')
            if start_count and end_count:
                total_gain = end_count - start_count
                print(f"📊 Start: {start_count}")
                print(f"📊 End: {end_count}")
                print(f"📈 TOTAL GAIN: +{total_gain} facts")
    except:
        pass
    
    # Save summary
    summary = {
        'timestamp': datetime.now().isoformat(),
        'config': {
            'mode': mode,
            'hours': hours,
            'episodes': episodes,
            'threshold': threshold,
            'source': source
        },
        'results': {
            'cycles': cycle_no,
            'facts_processed': idx,
            'start_count': start_count
        }
    }
    
    summary_file = LOG_DIR / f"autopilot_enhanced_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    summary_file.write_text(json.dumps(summary, indent=2), encoding='utf-8')
    print(f"\n📁 Summary saved: {summary_file}")


if __name__ == '__main__':
    main()
