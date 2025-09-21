#!/usr/bin/env python3
"""
DEEPSEEK PIPELINE VALIDATOR
Integriert mit der Validierungs-Pipeline
"""

import os
import json
import sqlite3
import requests
import time
from pathlib import Path

def validate_with_deepseek(facts_batch, batch_name="batch"):
    """Validiere Fakten mit DeepSeek"""
    
    api_key = os.environ.get('DEEPSEEK_API_KEY')
    if not api_key:
        print("❌ DEEPSEEK_API_KEY nicht gesetzt!")
        return None
    
    # Formatiere Fakten
    facts_text = "\n".join([f"{i+1}. {fact}" for i, fact in enumerate(facts_batch)])
    
    prompt = f"""Validiere diese {len(facts_batch)} wissenschaftlichen Fakten.
{facts_text}

Antworte mit JSON Array. Für JEDEN Fakt:
[{{
  "id": 1,
  "fact": "der originale Fakt",
  "valid": true oder false,
  "confidence": 0.0 bis 1.0,
  "category": "chemistry|biology|physics|computer_science|mathematics|general|invalid",
  "issues": ["Liste von Problemen wenn invalid"],
  "correction": null oder "korrigierter Fakt"
}}]"""

    print(f"  → Sende {len(facts_batch)} Fakten an DeepSeek...")
    start = time.time()
    
    try:
        response = requests.post(
            'https://api.deepseek.com/v1/chat/completions',
            headers={
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            },
            json={
                'model': 'deepseek-chat',
                'messages': [
                    {'role': 'system', 'content': 'Du bist ein wissenschaftlicher Faktprüfer. Antworte NUR mit JSON Array.'},
                    {'role': 'user', 'content': prompt}
                ],
                'temperature': 0.1,
                'max_tokens': 4000
            }
        )
        
        elapsed = time.time() - start
        print(f"  ✓ Antwort in {elapsed:.1f}s")
        
        if response.status_code == 200:
            result = response.json()
            content = result['choices'][0]['message']['content']
            
            # Parse JSON
            import re
            json_match = re.search(r'\[.*\]', content, re.DOTALL)
            if json_match:
                validations = json.loads(json_match.group())
                return validations
        else:
            print(f"  ✗ API Error: {response.status_code}")
            
    except Exception as e:
        print(f"  ✗ Fehler: {str(e)[:100]}")
    
    return None

def main():
    print("="*60)
    print("DEEPSEEK VALIDIERUNGS-PIPELINE")
    print("="*60)
    
    # Lade Fakten aus DB
    conn = sqlite3.connect('hexagonal_kb.db')
    cursor = conn.cursor()
    
    # Hole verschiedene Kategorien
    categories = {
        'chemistry': "statement LIKE '%ConsistsOf%' OR statement LIKE '%H2O%' OR statement LIKE '%molecule%'",
        'biology': "statement LIKE '%cell%' OR statement LIKE '%DNA%' OR statement LIKE '%protein%'",
        'physics': "statement LIKE '%electron%' OR statement LIKE '%force%' OR statement LIKE '%energy%'",
        'computer_science': "statement LIKE '%algorithm%' OR statement LIKE '%TCP%' OR statement LIKE '%hash%'",
        'general': "statement NOT LIKE '%ConsistsOf%' AND statement NOT LIKE '%cell%' AND statement NOT LIKE '%electron%'"
    }
    
    all_validations = []
    
    for category, condition in categories.items():
        print(f"\n📦 Kategorie: {category}")
        print("-"*40)
        
        # Hole 20 Fakten pro Kategorie
        cursor.execute(f"""
            SELECT rowid, statement 
            FROM facts 
            WHERE {condition}
            LIMIT 20
        """)
        
        facts = cursor.fetchall()
        if facts:
            fact_texts = [f[1] for f in facts]
            
            validations = validate_with_deepseek(fact_texts, category)
            
            if validations:
                # Füge rowids hinzu
                for i, val in enumerate(validations):
                    if i < len(facts):
                        val['rowid'] = facts[i][0]
                        val['original_fact'] = facts[i][1]
                
                all_validations.extend(validations)
                
                # Statistik
                valid = sum(1 for v in validations if v.get('valid'))
                print(f"  ✓ {valid}/{len(validations)} valid")
                
                # Zeige erste invalide
                for v in validations:
                    if not v.get('valid'):
                        print(f"    ❌ {v.get('fact', '')[:50]}...")
                        break
    
    conn.close()
    
    # Speichere Gesamtergebnis
    print(f"\n💾 Speichere Ergebnisse...")
    
    output_dir = Path('validation_results')
    output_dir.mkdir(exist_ok=True)
    
    result = {
        'provider': 'deepseek',
        'timestamp': time.time(),
        'total_facts': len(all_validations),
        'validations': all_validations,
        'statistics': {
            'valid': sum(1 for v in all_validations if v.get('valid')),
            'invalid': sum(1 for v in all_validations if not v.get('valid')),
            'categories': {}
        }
    }
    
    # Kategorie-Statistiken
    for cat in ['chemistry', 'biology', 'physics', 'computer_science', 'general', 'invalid']:
        cat_vals = [v for v in all_validations if v.get('category') == cat]
        result['statistics']['categories'][cat] = len(cat_vals)
    
    # Speichere
    output_file = output_dir / 'deepseek_validation.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Gespeichert in: {output_file}")
    
    # Zeige Zusammenfassung
    print(f"\n📊 ZUSAMMENFASSUNG:")
    print(f"  Total: {len(all_validations)} Fakten")
    print(f"  Valid: {result['statistics']['valid']} ({result['statistics']['valid']/len(all_validations)*100:.1f}%)")
    print(f"  Invalid: {result['statistics']['invalid']} ({result['statistics']['invalid']/len(all_validations)*100:.1f}%)")
    
    print(f"\n📈 Nach Kategorie:")
    for cat, count in result['statistics']['categories'].items():
        if count > 0:
            print(f"  {cat:20} {count:4} Fakten")
    
    # Erstelle Cleanup-Vorschläge
    if result['statistics']['invalid'] > 0:
        print(f"\n🔧 Erstelle Cleanup SQL...")
        
        cleanup_file = output_dir / 'cleanup_proposals.sql'
        with open(cleanup_file, 'w') as f:
            f.write("-- DeepSeek Validierungs-Cleanup\n")
            f.write(f"-- Generiert: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"-- Invalid: {result['statistics']['invalid']} Fakten\n\n")
            
            f.write("BEGIN TRANSACTION;\n\n")
            
            for val in all_validations:
                if not val.get('valid'):
                    rowid = val.get('rowid')
                    if rowid:
                        f.write(f"-- {val.get('fact', '')[:60]}...\n")
                        if val.get('issues'):
                            f.write(f"-- Issue: {val['issues'][0]}\n")
                        f.write(f"DELETE FROM facts WHERE rowid = {rowid};\n")
                        
                        if val.get('correction'):
                            f.write(f"INSERT INTO facts (statement) VALUES ('{val['correction']}');\n")
                        f.write("\n")
            
            f.write("COMMIT;\n")
        
        print(f"✅ Cleanup SQL: {cleanup_file}")

if __name__ == "__main__":
    main()
