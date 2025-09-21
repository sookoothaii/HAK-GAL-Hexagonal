#!/usr/bin/env python3
"""
DEEPSEEK R1 REASONING VALIDATOR
Optimiert für DeepSeeks Reasoning Mode
"""

import os
import json
import time
import requests

def validate_with_deepseek_reasoning(facts_batch, timeout=600):
    """
    Validiere mit DeepSeek R1 - gibt ihm Zeit zum Nachdenken!
    timeout=600 = 10 Minuten für gründliches Reasoning
    """
    
    api_key = os.environ.get('DEEPSEEK_API_KEY')
    if not api_key:
        return None
    
    facts_text = "\n".join([f"{i+1}. {fact}" for i, fact in enumerate(facts_batch)])
    
    # Explizit um gründliches Reasoning bitten
    prompt = f"""Du hast Zeit zum Nachdenken. Analysiere diese {len(facts_batch)} wissenschaftlichen Fakten GRÜNDLICH.

FAKTEN:
{facts_text}

AUFGABE:
1. Denke über jeden Fakt nach
2. Prüfe wissenschaftliche Korrektheit
3. Identifiziere subtile Fehler
4. Schlage präzise Korrekturen vor

Antworte mit einem JSON Array. Für JEDEN Fakt:
```json
[
  {{
    "id": 1,
    "fact": "der originale Fakt",
    "valid": true/false,
    "confidence": 0.0-1.0,
    "reasoning": "Deine Überlegungen",
    "category": "chemistry|biology|physics|computer_science|mathematics|general",
    "issues": ["Liste spezifischer Probleme"],
    "correction": null oder "korrigierter Fakt"
  }}
]
```"""

    print(f"🧠 DeepSeek R1 Reasoning für {len(facts_batch)} Fakten...")
    print(f"   (Erwarte 3-10 Minuten für gründliche Analyse)")
    
    start = time.time()
    
    try:
        response = requests.post(
            'https://api.deepseek.com/v1/chat/completions',
            headers={
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            },
            json={
                'model': 'deepseek-chat',  # oder 'deepseek-reasoner' falls verfügbar
                'messages': [
                    {
                        'role': 'system', 
                        'content': 'Du bist ein gründlicher wissenschaftlicher Faktprüfer. Nimm dir Zeit zum Nachdenken. Antworte mit JSON im Code-Block.'
                    },
                    {'role': 'user', 'content': prompt}
                ],
                'temperature': 0.1,
                'max_tokens': 8000,
                'stream': False  # Kein Streaming für Reasoning
            },
            timeout=timeout  # 10 Minuten für Reasoning
        )
        
        elapsed = time.time() - start
        print(f"✅ Antwort nach {elapsed:.1f}s ({elapsed/60:.1f} Minuten)")
        
        if response.status_code == 200:
            result = response.json()
            content = result['choices'][0]['message']['content']
            
            # Parse JSON aus Code-Block
            import re
            
            # Suche nach ```json ... ```
            json_match = re.search(r'```json\s*(.*?)```', content, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
                validations = json.loads(json_str)
                print(f"✅ {len(validations)} Fakten validiert mit Reasoning")
                return validations
            
            # Fallback: Suche beliebiges Array
            json_match = re.search(r'\[.*?\]', content, re.DOTALL)
            if json_match:
                validations = json.loads(json_match.group())
                print(f"✅ {len(validations)} Fakten validiert")
                return validations
                
            # Debug wenn nichts gefunden
            print(f"❌ Kein JSON gefunden. Response-Start: {content[:200]}...")
            with open(f'debug_deepseek_{int(time.time())}.txt', 'w', encoding='utf-8') as f:
                f.write(content)
                
    except requests.exceptions.Timeout:
        print(f"⏱️ Timeout nach {timeout}s - DeepSeek braucht mehr Zeit")
    except Exception as e:
        print(f"❌ Fehler: {e}")
    
    return None


def main():
    """Hauptfunktion mit Argument-Support"""
    import argparse
    import json
    from pathlib import Path
    
    parser = argparse.ArgumentParser(description='DeepSeek R1 Reasoning Validator')
    parser.add_argument('--input', type=str, help='Input JSON file mit Fakten')
    parser.add_argument('--batch-size', type=int, default=20, help='Fakten pro Batch')
    parser.add_argument('--output', type=str, help='Output JSON file')
    args = parser.parse_args()
    
    # Lade Fakten
    if args.input and Path(args.input).exists():
        print(f"Lade Fakten aus: {args.input}")
        with open(args.input, 'r') as f:
            data = json.load(f)
            
            # Handle verschiedene JSON-Strukturen
            if isinstance(data, list):
                facts = data
            elif isinstance(data, dict):
                facts = data.get('facts', data.get('statements', []))
            else:
                facts = []
                
        print(f"Gefunden: {len(facts)} Fakten")
    else:
        # Fallback: Test-Fakten
        print("Verwende Test-Fakten (kein --input angegeben)")
        facts = [
            "ConsistsOf(NH3, oxygen).",  # FALSCH
            "HasProperty(water, liquid).",
            "Uses(TCP, three_way_handshake).",
            "ConsistsOf(H2O, hydrogen, oxygen).",
            "IsTypeOf(electron, lepton)."
        ]
    
    print("="*60)
    print("DEEPSEEK R1 REASONING VALIDATOR")
    print("="*60)
    
    # Verarbeite in Batches
    if not facts:
        print("⚠️ Keine Fakten zu validieren!")
        return
        
    batch_size = min(args.batch_size, len(facts))
    if batch_size == 0:
        batch_size = len(facts)
        
    total_validations = []
    
    for i in range(0, len(facts), batch_size):
        batch = facts[i:i+batch_size]
        print(f"\n📦 Batch {i//batch_size + 1}: Fakten {i+1}-{min(i+batch_size, len(facts))}")
        print("-"*40)
        
        validations = validate_with_deepseek_reasoning(batch)
        
        if validations:
            total_validations.extend(validations)
            
            # Statistik
            valid = sum(1 for v in validations if v.get('valid'))
            print(f"✅ {valid}/{len(validations)} valid")
            
            # Zeige erste Fehler
            for v in validations[:3]:
                if not v.get('valid'):
                    print(f"  ❌ {v.get('fact', '')[:50]}...")
                    if v.get('issues'):
                        print(f"     → {v['issues'][0]}")
    
    # Speichere Ergebnisse
    if args.output or total_validations:
        output_file = args.output or f"deepseek_validation_{int(time.time())}.json"
        
        result = {
            'provider': 'deepseek-r1',
            'timestamp': time.time(),
            'source_file': args.input,
            'total_facts': len(total_validations),
            'validations': total_validations,
            'statistics': {
                'valid': sum(1 for v in total_validations if v.get('valid')),
                'invalid': sum(1 for v in total_validations if not v.get('valid'))
            }
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Gespeichert: {output_file}")
        print(f"📊 Total: {len(total_validations)} validiert")
        print(f"   Valid: {result['statistics']['valid']}")
        print(f"   Invalid: {result['statistics']['invalid']}")


if __name__ == "__main__":
    main()
