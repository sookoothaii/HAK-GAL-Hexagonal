#!/usr/bin/env python3
"""
MAXIMALE LLM-FAKTEN-VALIDIERUNG
================================
Nutzt Token-Limits voll aus für effiziente Batch-Validierung
Optimiert für DeepSeek API mit großen Kontextfenstern

Features:
- GROSSE Batches (100-500 Fakten pro Request)
- Parallel-Verarbeitung möglich
- Detaillierte Validierungsberichte
- Automatische Fehlerkorrektur-Vorschläge
"""

import sqlite3
import json
import time
import os
import sys
import requests
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from datetime import datetime
from collections import defaultdict
import threading
import queue

# Add paths for imports
sys.path.insert(0, str(Path(__file__).parent / 'src_hexagonal'))
sys.path.insert(0, str(Path(__file__).parent / 'adapters'))

class MaximalFactValidator:
    def __init__(self, db_path: str = "hexagonal_kb.db", batch_size: int = 200):
        self.db_path = db_path
        self.batch_size = batch_size  # Große Batches für maximale Effizienz
        self.progress_file = "validation_progress_max.json"
        self.results_file = f"validation_results_max_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        # Statistiken
        self.stats = defaultdict(int)
        self.invalid_facts = []
        self.corrected_facts = []
        
        # Progress tracking
        self.progress = self._load_progress()
        
        # Validation prompt - MAXIMAL detailliert
        self.validation_prompt_template = """
Du bist ein wissenschaftlicher Faktprüfer. Analysiere die folgenden {count} Fakten aus einer Knowledge Base.

PRÜFKRITERIEN:
1. SYNTAKTISCHE KORREKTHEIT
   - Format: Predicate(Arg1, Arg2, ...).
   - Konsistente Schreibweise
   - Keine Tippfehler

2. SEMANTISCHE SINNHAFTIGKEIT
   - Macht die Relation logisch Sinn?
   - Sind die Argumente passend zum Prädikat?
   - Beispiel schlecht: HasProperty(water, Tuesday) - Eigenschaft passt nicht

3. WISSENSCHAFTLICHE KORREKTHEIT
   - Ist die Aussage faktisch richtig?
   - Entspricht sie dem aktuellen Wissensstand?
   - Beispiel falsch: ConsistsOf(NH3, oxygen) - NH3 enthält keinen Sauerstoff

4. KONSISTENZ
   - Widerspricht der Fakt anderen bekannten Fakten?
   - Ist die Argumentreihenfolge logisch?

5. KATEGORISIERUNG
   - chemistry: Chemische Fakten (Moleküle, Reaktionen, Elemente)
   - biology: Biologische Fakten (Zellen, Organismen, DNA)
   - physics: Physikalische Fakten (Teilchen, Kräfte, Energie)
   - computer_science: Informatik (Algorithmen, Datenstrukturen, Netzwerke)
   - mathematics: Mathematik (Calculus, Algebra, Geometrie)
   - general: Allgemeinwissen
   - invalid: Fehlerhafte/unsinnige Fakten

FAKTEN ZUM VALIDIEREN:
{facts}

ANTWORT-FORMAT (JSON Array):
Gib für JEDEN Fakt eine detaillierte Analyse. Nutze dieses Format:

[
  {{
    "id": 1,
    "fact": "HasProperty(water, liquid).",
    "valid": true,
    "confidence": 0.95,
    "category": "chemistry",
    "issues": [],
    "correction": null,
    "explanation": "Korrekt: Wasser ist bei Raumtemperatur flüssig"
  }},
  {{
    "id": 2,
    "fact": "ConsistsOf(NH3, oxygen).",
    "valid": false,
    "confidence": 1.0,
    "category": "chemistry",
    "issues": ["Faktisch falsch: NH3 (Ammoniak) besteht aus Stickstoff und Wasserstoff, nicht Sauerstoff"],
    "correction": "ConsistsOf(NH3, nitrogen, hydrogen).",
    "explanation": "NH3 ist die chemische Formel für Ammoniak: 1 Stickstoff + 3 Wasserstoff"
  }}
]

Analysiere ALLE {count} Fakten gründlich. Sei kritisch aber fair.
"""
    
    def _load_progress(self) -> Dict:
        """Lade gespeicherten Fortschritt"""
        if os.path.exists(self.progress_file):
            with open(self.progress_file, 'r') as f:
                return json.load(f)
        return {
            'last_id': 0,
            'total_validated': 0,
            'batches_processed': 0,
            'invalid_found': 0,
            'start_time': datetime.now().isoformat()
        }
    
    def _save_progress(self):
        """Speichere Fortschritt"""
        with open(self.progress_file, 'w') as f:
            json.dump(self.progress, f, indent=2)
    
    def _save_results(self):
        """Speichere Validierungsergebnisse"""
        results = {
            'timestamp': datetime.now().isoformat(),
            'statistics': dict(self.stats),
            'progress': self.progress,
            'invalid_facts': self.invalid_facts,
            'corrections': self.corrected_facts,
            'summary': {
                'total_validated': self.progress['total_validated'],
                'invalid_found': len(self.invalid_facts),
                'corrections_suggested': len(self.corrected_facts),
                'categories': dict(self.stats)
            }
        }
        
        with open(self.results_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"\n📊 Ergebnisse gespeichert in: {self.results_file}")
    
    def get_facts_batch(self, offset: int, limit: int) -> List[Tuple[int, str]]:
        """Hole einen Batch von Fakten aus der DB"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT rowid, statement 
            FROM facts 
            ORDER BY rowid 
            LIMIT ? OFFSET ?
        """, (limit, offset))
        
        facts = cursor.fetchall()
        conn.close()
        return facts
    
    def validate_with_deepseek(self, facts_batch: List[Tuple[int, str]]) -> Optional[List[Dict]]:
        """Validiere einen großen Batch mit DeepSeek API"""
        
        print(f"   📝 Bereite {len(facts_batch)} Fakten vor...")
        
        # Formatiere Fakten für Prompt
        facts_text = "\n".join([f"{i+1}. {fact}" for i, (_, fact) in enumerate(facts_batch)])
        
        prompt = self.validation_prompt_template.format(
            count=len(facts_batch),
            facts=facts_text
        )
        
        print(f"   📏 Prompt-Größe: {len(prompt):,} Zeichen (~{len(prompt)//4:,} Tokens)")
        
        try:
            # DeepSeek API aufrufen
            deepseek_api_key = os.environ.get('DEEPSEEK_API_KEY')
            if not deepseek_api_key:
                print("   ⚠️  DEEPSEEK_API_KEY nicht gesetzt! Nutze Fallback...")
                return self.validate_with_fallback(facts_batch)
            
            print(f"   🔑 API Key: {deepseek_api_key[:15]}...")
            print(f"   🌐 Sende an DeepSeek (kann 30-60s dauern)...")
            
            start_time = time.time()
            
            # KEIN TIMEOUT - warte auf Antwort
            response = requests.post(
                'https://api.deepseek.com/v1/chat/completions',
                headers={
                    'Authorization': f'Bearer {deepseek_api_key}',
                    'Content-Type': 'application/json'
                },
                json={
                    'model': 'deepseek-chat',
                    'messages': [
                        {'role': 'system', 'content': 'Du bist ein präziser wissenschaftlicher Faktprüfer. Antworte NUR mit validem JSON.'},
                        {'role': 'user', 'content': prompt}
                    ],
                    'temperature': 0.1,
                    'max_tokens': 8000
                }
                # KEIN TIMEOUT!
            )
            
            elapsed = time.time() - start_time
            print(f"   ⏱️  Antwort in {elapsed:.1f}s")
            
            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content']
                
                print(f"   📦 Response: {len(content):,} Zeichen")
                
                # Parse JSON response
                try:
                    # Versuche direkt zu parsen
                    validations = json.loads(content)
                    if isinstance(validations, dict) and 'validations' in validations:
                        validations = validations['validations']
                    
                    print(f"   ✅ {len(validations)} Fakten validiert")
                    
                    # Füge Original-IDs hinzu
                    for i, validation in enumerate(validations):
                        if i < len(facts_batch):
                            validation['original_id'] = facts_batch[i][0]
                            validation['original_fact'] = facts_batch[i][1]
                    
                    return validations
                    
                except json.JSONDecodeError:
                    # Fallback: Extrahiere JSON aus Text
                    print(f"   🔍 Extrahiere JSON...")
                    import re
                    json_match = re.search(r'\[.*\]', content, re.DOTALL)
                    if json_match:
                        try:
                            validations = json.loads(json_match.group())
                            print(f"   ✅ {len(validations)} Fakten extrahiert")
                            
                            for i, validation in enumerate(validations):
                                if i < len(facts_batch):
                                    validation['original_id'] = facts_batch[i][0]
                                    validation['original_fact'] = facts_batch[i][1]
                            
                            return validations
                        except:
                            print(f"   ❌ JSON-Parsing fehlgeschlagen")
                            return None
                    return None
                    
            else:
                print(f"   ❌ DeepSeek Error: {response.status_code}")
                print(f"   Details: {response.text[:200]}")
                return None
                
        except requests.exceptions.ConnectionError as e:
            print(f"   ❌ Verbindungsfehler: {str(e)[:100]}")
            return None
        except Exception as e:
            print(f"   ❌ Fehler: {str(e)[:100]}")
            return None
    
    def validate_with_fallback(self, facts_batch: List[Tuple[int, str]]) -> Optional[List[Dict]]:
        """Fallback Validierung mit Gemini, Claude oder Ollama"""
        print("   🔄 Verwende Fallback-Provider...")
        
        # Versuche Gemini zuerst
        try:
            gemini_key = os.environ.get('GEMINI_API_KEY') or os.environ.get('GOOGLE_API_KEY')
            if gemini_key:
                print(f"   🌟 Verwende Gemini (Key: {gemini_key[:10]}...)")
                
                import google.generativeai as genai
                genai.configure(api_key=gemini_key)
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                # Kleinerer Batch für Gemini
                if len(facts_batch) > 100:
                    print(f"   ✂️ Reduziere Batch von {len(facts_batch)} auf 100 für Gemini")
                    facts_batch = facts_batch[:100]
                
                facts_text = "\n".join([f"{i+1}. {fact}" for i, (_, fact) in enumerate(facts_batch)])
                prompt = self.validation_prompt_template.format(
                    count=len(facts_batch),
                    facts=facts_text
                )
                
                print(f"   📡 Sende an Gemini API...")
                response = model.generate_content(prompt)
                
                if response.text:
                    print(f"   ✅ Gemini Antwort erhalten")
                    # Parse JSON aus Response
                    import re
                    json_match = re.search(r'\[.*\]', response.text, re.DOTALL)
                    if json_match:
                        validations = json.loads(json_match.group())
                        
                        # Füge Original-IDs hinzu
                        for i, validation in enumerate(validations):
                            if i < len(facts_batch):
                                validation['original_id'] = facts_batch[i][0]
                                validation['original_fact'] = facts_batch[i][1]
                        
                        print(f"   ✅ {len(validations)} Fakten via Gemini validiert")
                        return validations
        except Exception as e:
            print(f"   ❌ Gemini fehlgeschlagen: {e}")
        
        # Versuche Ollama als letzten Fallback
        try:
            print(f"   🦙 Versuche lokales Ollama...")
            from adapters.ollama_adapter import OllamaProvider
            llm = OllamaProvider(model="qwen2.5:7b")
            
            if llm.is_available():
                # Sehr kleiner Batch für lokales Modell
                if len(facts_batch) > 20:
                    print(f"   ✂️ Reduziere Batch von {len(facts_batch)} auf 20 für Ollama")
                    facts_batch = facts_batch[:20]
                
                facts_text = "\n".join([f"{i+1}. {fact}" for i, (_, fact) in enumerate(facts_batch)])
                prompt = self.validation_prompt_template.format(
                    count=len(facts_batch),
                    facts=facts_text
                )
                
                print(f"   📡 Sende an lokales Ollama...")
                response = llm.generate_response(prompt)
                if isinstance(response, tuple):
                    response = response[0]
                
                # Parse response
                import re
                json_match = re.search(r'\[.*\]', response, re.DOTALL)
                if json_match:
                    validations = json.loads(json_match.group())
                    
                    for i, validation in enumerate(validations):
                        if i < len(facts_batch):
                            validation['original_id'] = facts_batch[i][0]
                            validation['original_fact'] = facts_batch[i][1]
                    
                    print(f"   ✅ {len(validations)} Fakten via Ollama validiert")
                    return validations
        except Exception as e:
            print(f"   ❌ Ollama fehlgeschlagen: {e}")
        
        # Letzter Fallback: Einfache Regel-basierte Validierung
        print("   ⚠️ Nutze regel-basierte Validierung als letzten Fallback")
        return self.simple_rule_validation(facts_batch)
    
    def simple_rule_validation(self, facts_batch: List[Tuple[int, str]]) -> List[Dict]:
        """Einfache regel-basierte Validierung als Fallback"""
        validations = []
        
        # Bekannte Fehler
        known_errors = [
            ('NH3', 'oxygen'),
            ('H2O', 'carbon'),
            ('CO2', 'hydrogen'),
            ('CH4', 'oxygen'),
            ('API(', ''),  # API mit mehreren Argumenten ist meist falsch
        ]
        
        for fact_id, fact in facts_batch:
            issues = []
            valid = True
            category = 'general'
            
            # Prüfe bekannte Fehler
            for error_pair in known_errors:
                if error_pair[0] in fact and error_pair[1] in fact:
                    if error_pair[1]:  # Spezifischer Fehler
                        issues.append(f"Bekannter chemischer Fehler: {error_pair[0]} enthält kein {error_pair[1]}")
                    else:  # Allgemeiner Fehler
                        issues.append(f"Verdächtiges Muster: {error_pair[0]}")
                    valid = False
            
            # Kategorisierung
            if any(x in fact.lower() for x in ['h2o', 'co2', 'nh3', 'molecule', 'atom']):
                category = 'chemistry'
            elif any(x in fact.lower() for x in ['cell', 'dna', 'protein', 'virus']):
                category = 'biology'
            elif any(x in fact.lower() for x in ['electron', 'photon', 'gravity']):
                category = 'physics'
            elif any(x in fact.lower() for x in ['algorithm', 'tcp', 'http', 'hash']):
                category = 'computer_science'
            
            validations.append({
                'original_id': fact_id,
                'original_fact': fact,
                'valid': valid,
                'confidence': 0.7 if valid else 0.9,
                'category': category,
                'issues': issues,
                'correction': None,
                'explanation': 'Regel-basierte Validierung'
            })
        
        return validations
    
    def process_validation_results(self, validations: List[Dict]):
        """Verarbeite Validierungsergebnisse"""
        for val in validations:
            # Update Statistiken
            self.stats[val.get('category', 'unknown')] += 1
            
            if not val.get('valid', True):
                self.invalid_facts.append({
                    'id': val.get('original_id'),
                    'fact': val.get('original_fact'),
                    'issues': val.get('issues', []),
                    'confidence': val.get('confidence', 0),
                    'category': val.get('category')
                })
                
                if val.get('correction'):
                    self.corrected_facts.append({
                        'original': val.get('original_fact'),
                        'correction': val.get('correction'),
                        'explanation': val.get('explanation')
                    })
                
                self.stats['invalid'] += 1
            else:
                self.stats['valid'] += 1
    
    def run_validation(self, max_facts: Optional[int] = None, start_from: Optional[int] = None):
        """Hauptvalidierungsprozess"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Gesamtzahl der Fakten
        cursor.execute("SELECT COUNT(*) FROM facts")
        total_facts = cursor.fetchone()[0]
        conn.close()
        
        if max_facts:
            total_facts = min(total_facts, max_facts)
        
        offset = start_from if start_from else self.progress['last_id']
        
        print(f"\n{'='*80}")
        print(f"MAXIMALE FAKTEN-VALIDIERUNG")
        print(f"{'='*80}")
        print(f"Datenbankpfad: {self.db_path}")
        print(f"Gesamte Fakten: {total_facts:,}")
        print(f"Batch-Größe: {self.batch_size}")
        print(f"Start bei ID: {offset}")
        print(f"Geschätzte Batches: {(total_facts - offset) // self.batch_size}")
        print(f"{'='*80}\n")
        
        batch_num = 0
        
        while offset < total_facts:
            batch_num += 1
            remaining = total_facts - offset
            current_batch_size = min(self.batch_size, remaining)
            
            print(f"\n📦 Batch {batch_num} | Fakten {offset+1}-{offset+current_batch_size} von {total_facts}")
            print("-" * 40)
            
            # Hole Fakten-Batch
            facts_batch = self.get_facts_batch(offset, current_batch_size)
            
            if not facts_batch:
                print("Keine weiteren Fakten zu validieren.")
                break
            
            # Validiere Batch
            print(f"🔍 Sende {len(facts_batch)} Fakten zur Validierung...")
            start_time = time.time()
            
            validations = self.validate_with_deepseek(facts_batch)
            
            if validations:
                elapsed = time.time() - start_time
                print(f"✅ Validierung abgeschlossen in {elapsed:.1f}s")
                
                # Verarbeite Ergebnisse
                self.process_validation_results(validations)
                
                # Zeige Batch-Statistik
                batch_invalid = sum(1 for v in validations if not v.get('valid', True))
                print(f"📊 Batch-Ergebnis: {batch_invalid} ungültige von {len(validations)} Fakten")
                
                if batch_invalid > 0:
                    print(f"❌ Beispiele ungültiger Fakten:")
                    for v in validations[:3]:  # Erste 3 ungültige
                        if not v.get('valid', True):
                            print(f"   • {v.get('original_fact', 'N/A')}")
                            if v.get('issues'):
                                print(f"     → {v['issues'][0]}")
            else:
                print("⚠️ Validierung fehlgeschlagen, überspringe Batch")
            
            # Update Progress
            offset += current_batch_size
            self.progress['last_id'] = offset
            self.progress['total_validated'] = offset
            self.progress['batches_processed'] = batch_num
            self.progress['invalid_found'] = len(self.invalid_facts)
            self._save_progress()
            
            # Zwischenspeicherung alle 5 Batches
            if batch_num % 5 == 0:
                self._save_results()
                print(f"\n💾 Zwischenstand gespeichert")
                print(f"   Validiert: {offset:,}/{total_facts:,} ({offset/total_facts*100:.1f}%)")
                print(f"   Ungültig: {len(self.invalid_facts):,} ({len(self.invalid_facts)/offset*100:.1f}%)")
            
            # Rate limiting
            time.sleep(1)  # Kurze Pause zwischen Batches
        
        # Finale Ergebnisse
        self._save_results()
        self._print_final_report()
    
    def _print_final_report(self):
        """Zeige finalen Bericht"""
        print("\n" + "="*80)
        print("VALIDIERUNG ABGESCHLOSSEN")
        print("="*80)
        
        total = self.progress['total_validated']
        invalid = len(self.invalid_facts)
        
        print(f"\n📊 GESAMTSTATISTIK:")
        print(f"   Validierte Fakten: {total:,}")
        print(f"   Ungültige Fakten: {invalid:,} ({invalid/total*100:.1f}%)")
        print(f"   Korrekturvorschläge: {len(self.corrected_facts):,}")
        
        print(f"\n📈 KATEGORIEN:")
        for category, count in sorted(self.stats.items(), key=lambda x: x[1], reverse=True):
            if category != 'valid' and category != 'invalid':
                print(f"   {category:20} {count:6,} Fakten")
        
        if self.invalid_facts:
            print(f"\n❌ TOP FEHLERHAFTE FAKTEN:")
            for fact in self.invalid_facts[:10]:
                print(f"   • {fact['fact'][:80]}...")
                if fact.get('issues'):
                    print(f"     → {fact['issues'][0][:70]}...")
        
        print(f"\n📁 Ergebnisse gespeichert in:")
        print(f"   • {self.results_file}")
        print(f"   • {self.progress_file}")
        
        print("\n" + "="*80)
    
    def generate_cleanup_script(self):
        """Generiere SQL-Script zum Bereinigen der Datenbank"""
        if not self.invalid_facts:
            print("Keine ungültigen Fakten zum Bereinigen gefunden.")
            return
        
        cleanup_file = f"cleanup_invalid_facts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sql"
        
        with open(cleanup_file, 'w', encoding='utf-8') as f:
            f.write("-- SQL Script zum Bereinigen ungültiger Fakten\n")
            f.write(f"-- Generiert: {datetime.now().isoformat()}\n")
            f.write(f"-- Ungültige Fakten: {len(self.invalid_facts)}\n\n")
            
            f.write("BEGIN TRANSACTION;\n\n")
            
            # Delete statements
            f.write("-- Lösche ungültige Fakten\n")
            for fact in self.invalid_facts:
                if fact.get('id'):
                    f.write(f"DELETE FROM facts WHERE rowid = {fact['id']}; -- {fact['fact'][:50]}...\n")
            
            f.write("\n-- Füge korrigierte Versionen hinzu\n")
            for correction in self.corrected_facts:
                f.write(f"INSERT INTO facts (statement) VALUES ('{correction['correction']}');\n")
                f.write(f"-- Korrektur für: {correction['original'][:50]}...\n\n")
            
            f.write("\nCOMMIT;\n")
        
        print(f"\n🔧 Bereinigungs-Script erstellt: {cleanup_file}")


def main():
    """Hauptfunktion"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Maximale LLM-basierte Fakten-Validierung')
    parser.add_argument('--batch-size', type=int, default=200, 
                       help='Anzahl Fakten pro Batch (Standard: 200)')
    parser.add_argument('--max-facts', type=int, 
                       help='Maximale Anzahl zu validierender Fakten')
    parser.add_argument('--start-from', type=int, 
                       help='Start-ID (überschreibt gespeicherten Fortschritt)')
    parser.add_argument('--cleanup', action='store_true',
                       help='Generiere SQL-Cleanup-Script nach Validierung')
    
    args = parser.parse_args()
    
    # Prüfe DeepSeek API Key
    if not os.environ.get('DEEPSEEK_API_KEY'):
        print("\n⚠️  WARNUNG: DEEPSEEK_API_KEY nicht gesetzt!")
        print("   Setze die Umgebungsvariable für beste Ergebnisse:")
        print("   export DEEPSEEK_API_KEY='dein-api-key'")
        print("\n   Nutze Fallback-Provider...\n")
        time.sleep(3)
    
    validator = MaximalFactValidator(batch_size=args.batch_size)
    
    try:
        validator.run_validation(
            max_facts=args.max_facts,
            start_from=args.start_from
        )
        
        if args.cleanup:
            validator.generate_cleanup_script()
            
    except KeyboardInterrupt:
        print("\n\n⚠️ Validierung unterbrochen!")
        print("Fortschritt wurde gespeichert. Starte erneut zum Fortsetzen.")
        validator._save_results()


if __name__ == "__main__":
    main()
