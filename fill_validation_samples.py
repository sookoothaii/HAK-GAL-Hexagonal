#!/usr/bin/env python3
"""
FÜLLE VALIDATION SAMPLES
Holt echte Fakten aus der DB für die Pipeline
"""

import sqlite3
import json
import random
from pathlib import Path

def fill_validation_samples():
    """Fülle die leeren Sample-Dateien mit echten Fakten"""
    
    conn = sqlite3.connect('hexagonal_kb.db')
    cursor = conn.cursor()
    
    # Erstelle Sample-Verzeichnisse
    samples_dir = Path('validation_samples')
    samples_dir.mkdir(exist_ok=True)
    stratified_dir = samples_dir / 'stratified'
    stratified_dir.mkdir(exist_ok=True)
    
    print("FÜLLE VALIDATION SAMPLES")
    print("="*60)
    
    # 1. TOP: Die ersten 200 häufigsten Fakten (oft fehlerhaft)
    print("\n1. TOP 200 (häufige/problematische Fakten)...")
    cursor.execute("""
        SELECT statement FROM facts 
        WHERE statement LIKE 'API(%' 
        OR statement LIKE 'ConsistsOf(%'
        OR statement LIKE 'HasProperty(%'
        LIMIT 200
    """)
    top_facts = [row[0] for row in cursor.fetchall()]
    
    with open(stratified_dir / 'top.json', 'w') as f:
        json.dump(top_facts, f, indent=2)
    print(f"   ✓ {len(top_facts)} Top-Fakten gespeichert")
    
    # 2. RARE: Seltene/ungewöhnliche Prädikate
    print("\n2. RARE (seltene Prädikate)...")
    cursor.execute("""
        SELECT statement FROM facts 
        WHERE statement NOT LIKE 'API(%'
        AND statement NOT LIKE 'ConsistsOf(%'
        AND statement NOT LIKE 'HasProperty(%'
        AND statement NOT LIKE 'Uses(%'
        AND statement NOT LIKE 'IsTypeOf(%'
        ORDER BY RANDOM()
        LIMIT 50
    """)
    rare_facts = [row[0] for row in cursor.fetchall()]
    
    with open(stratified_dir / 'rare.json', 'w') as f:
        json.dump(rare_facts, f, indent=2)
    print(f"   ✓ {len(rare_facts)} Rare-Fakten gespeichert")
    
    # 3. RESERVE: Zufällige Stichprobe
    print("\n3. RESERVE (zufällige Stichprobe)...")
    cursor.execute("""
        SELECT statement FROM facts 
        ORDER BY RANDOM()
        LIMIT 200
    """)
    reserve_facts = [row[0] for row in cursor.fetchall()]
    
    with open(stratified_dir / 'reserve.json', 'w') as f:
        json.dump(reserve_facts, f, indent=2)
    print(f"   ✓ {len(reserve_facts)} Reserve-Fakten gespeichert")
    
    # 4. CHEMISTRY: Chemie-Fakten für DeepSeek
    print("\n4. CHEMISTRY (für DeepSeek-Spezialisierung)...")
    cursor.execute("""
        SELECT statement FROM facts 
        WHERE statement LIKE '%H2O%' 
        OR statement LIKE '%NH3%'
        OR statement LIKE '%CO2%'
        OR statement LIKE '%molecule%'
        OR statement LIKE '%atom%'
        OR statement LIKE '%chemical%'
        LIMIT 100
    """)
    chemistry_facts = [row[0] for row in cursor.fetchall()]
    
    with open(samples_dir / 'deepseek_chemistry.json', 'w') as f:
        json.dump({
            'provider': 'deepseek',
            'category': 'chemistry',
            'facts': chemistry_facts
        }, f, indent=2)
    print(f"   ✓ {len(chemistry_facts)} Chemie-Fakten für DeepSeek")
    
    # 5. BIO/PHYSICS: Für Gemini
    print("\n5. BIO/PHYSICS (für Gemini)...")
    cursor.execute("""
        SELECT statement FROM facts 
        WHERE statement LIKE '%cell%'
        OR statement LIKE '%DNA%'
        OR statement LIKE '%protein%'
        OR statement LIKE '%electron%'
        OR statement LIKE '%photon%'
        OR statement LIKE '%force%'
        LIMIT 100
    """)
    bio_phys_facts = [row[0] for row in cursor.fetchall()]
    
    with open(samples_dir / 'gemini_bio_phys.json', 'w') as f:
        json.dump({
            'provider': 'gemini',
            'category': 'biology_physics',
            'facts': bio_phys_facts
        }, f, indent=2)
    print(f"   ✓ {len(bio_phys_facts)} Bio/Physik-Fakten für Gemini")
    
    # 6. GENERAL: Allgemeine Fakten
    print("\n6. GENERAL (gemischte Kategorien)...")
    cursor.execute("""
        SELECT statement FROM facts 
        WHERE statement LIKE '%Uses(%'
        OR statement LIKE '%IsTypeOf(%'
        OR statement LIKE '%HasPurpose(%'
        LIMIT 100
    """)
    general_facts = [row[0] for row in cursor.fetchall()]
    
    with open(samples_dir / 'self_generic.json', 'w') as f:
        json.dump({
            'provider': 'self',
            'category': 'general',
            'facts': general_facts
        }, f, indent=2)
    print(f"   ✓ {len(general_facts)} General-Fakten")
    
    conn.close()
    
    print("\n" + "="*60)
    print("✅ VALIDATION SAMPLES GEFÜLLT!")
    print("\nJetzt können Sie validieren:")
    print("  python deepseek_reasoning_validator.py --input validation_samples/stratified/top.json")
    print("  python deepseek_reasoning_validator.py --input validation_samples/deepseek_chemistry.json")

if __name__ == "__main__":
    fill_validation_samples()
