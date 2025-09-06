#!/usr/bin/env python3
"""
HAK-GAL Autonomous Predicate Explorer & Learning Loop
======================================================
Automatischer Kreislauf der neue Prädikate erkennt, exploriert und lernt
Implementiert echtes selbstlernendes Verhalten

Nach HAK/GAL Verfassung:
- Artikel 1: Komplementäre Intelligenz (LLM + HRM zusammen)
- Artikel 4: Bewusstes Grenzüberschreiten (neue Gebiete explorieren)
- Artikel 7: Konjugierte Zustände (Neural + Symbolic lernen)
"""

import requests
import json
import sqlite3
import time
import random
from datetime import datetime
from typing import Dict, List, Tuple, Set
from collections import defaultdict

BACKEND_URL = 'http://localhost:5002'
DATABASE_PATH = r'D:\MCP Mods\HAK_GAL_HEXAGONAL\hexagonal_kb.db'
EXPLORATION_LOG = 'predicate_exploration_log.json'

class AutonomousPredicateExplorer:
    """
    Selbstlernender Kreislauf für neue Prädikate
    
    WORKFLOW:
    1. DISCOVER: Findet neue Prädikate in der KB
    2. EXPLORE: Generiert Facts mit neuen Prädikaten via LLM
    3. TEST: Testet HRM Confidence für neue Facts
    4. LEARN: Fügt erfolgreiche Facts hinzu
    5. ADAPT: Mappt schlechte Prädikate zu guten
    6. EVOLVE: Wiederholt mit verbessertem Wissen
    """
    
    def __init__(self):
        # Bekannte gute Prädikate (>70% HRM confidence)
        self.known_good_predicates = {
            'HasProperty': 0.85,
            'HasPart': 0.80,
            'Causes': 0.75,
            'IsA': 0.90,
            'Uses': 0.70,
        }
        
        # Unbekannte/neue Prädikate zum Explorieren
        self.unknown_predicates = set()
        
        # Predicate Performance Tracking
        self.predicate_scores = defaultdict(list)
        
        # Learning History
        self.exploration_history = []
        
        # Adaptive Mappings (learned over time)
        self.learned_mappings = {}
        
        # Statistics
        self.stats = {
            'predicates_discovered': 0,
            'facts_generated': 0,
            'facts_accepted': 0,
            'confidence_improvements': 0,
            'new_domains_explored': set()
        }
    
    def discover_new_predicates(self) -> Set[str]:
        """
        Phase 1: DISCOVER
        Findet neue Prädikate in der Datenbank
        """
        print("\n🔍 PHASE 1: DISCOVERING NEW PREDICATES...")
        print("="*60)
        
        try:
            conn = sqlite3.connect(DATABASE_PATH)
            cursor = conn.cursor()
            
            # Alle Prädikate finden
            cursor.execute("""
                SELECT DISTINCT
                    SUBSTR(statement, 1, INSTR(statement, '(') - 1) as predicate,
                    COUNT(*) as count
                FROM facts
                WHERE statement LIKE '%(%'
                AND predicate != ''
                GROUP BY predicate
            """)
            
            all_predicates = cursor.fetchall()
            conn.close()
            
            new_predicates = set()
            for pred, count in all_predicates:
                if pred and pred not in self.known_good_predicates:
                    new_predicates.add(pred)
                    if count < 10:  # Seltene Prädikate sind interessant
                        print(f"  🆕 Rare predicate found: {pred} ({count} facts)")
                    else:
                        print(f"  📝 Unknown predicate: {pred} ({count} facts)")
            
            self.unknown_predicates = new_predicates
            self.stats['predicates_discovered'] = len(new_predicates)
            
            print(f"\n  Found {len(new_predicates)} unknown predicates to explore")
            
            return new_predicates
            
        except Exception as e:
            print(f"  ❌ Error discovering predicates: {e}")
            return set()
    
    def explore_predicate_with_llm(self, predicate: str) -> List[str]:
        """
        Phase 2: EXPLORE
        Nutzt LLM um neue Facts mit dem Prädikat zu generieren
        """
        print(f"\n  🤖 Exploring '{predicate}' with LLM...")
        
        # Erstelle exploratory prompt
        exploration_prompt = f"""
        Generate 5 diverse facts using the predicate '{predicate}'.
        Examples of what {predicate} might mean:
        - If it's about relationships: {predicate}(EntityA, EntityB)
        - If it's about properties: {predicate}(Entity, Property)
        - If it's about actions: {predicate}(Actor, Target)
        
        Generate creative but plausible facts that explore different domains:
        philosophy, science, technology, geography, history.
        """
        
        try:
            # LLM API call
            response = requests.post(
                f"{BACKEND_URL}/api/llm/get-explanation",
                json={
                    'topic': exploration_prompt,
                    'context_facts': []
                },
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            if response.ok:
                data = response.json()
                suggested_facts = []
                
                # Extract facts from LLM response
                for fact_obj in data.get('suggested_facts', []):
                    if isinstance(fact_obj, dict):
                        fact = fact_obj.get('fact', '')
                    else:
                        fact = str(fact_obj)
                    
                    # Ensure it uses our predicate
                    if fact and predicate in fact:
                        suggested_facts.append(fact)
                
                # If no facts with our predicate, create some
                if not suggested_facts:
                    domains = ['Philosophy', 'Technology', 'Science', 'Geography', 'History']
                    entities = ['Quantum', 'Democracy', 'Evolution', 'Internet', 'Renaissance']
                    
                    for i in range(3):
                        entity1 = random.choice(entities)
                        entity2 = random.choice(domains)
                        fact = f"{predicate}({entity1}, {entity2})."
                        suggested_facts.append(fact)
                
                print(f"    Generated {len(suggested_facts)} exploratory facts")
                return suggested_facts
                
            else:
                print(f"    ⚠️ LLM response failed: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"    ❌ LLM exploration error: {e}")
            return []
    
    def test_fact_confidence(self, fact: str) -> float:
        """
        Phase 3: TEST
        Testet HRM Confidence für einen Fact
        """
        try:
            response = requests.post(
                f"{BACKEND_URL}/api/reason",
                json={'query': fact},
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.ok:
                confidence = response.json().get('confidence', 0.0)
                return confidence
            return 0.0
            
        except:
            return 0.0
    
    def learn_from_exploration(self, predicate: str, test_results: List[Tuple[str, float]]):
        """
        Phase 4: LEARN
        Lernt aus den Test-Ergebnissen
        """
        print(f"\n  📚 Learning from {predicate} exploration...")
        
        # Analysiere Ergebnisse
        confidences = [conf for _, conf in test_results]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0
        
        # Update predicate score
        self.predicate_scores[predicate].append(avg_confidence)
        
        # Entscheide basierend auf Confidence
        if avg_confidence > 0.7:
            print(f"    ✅ {predicate} is GOOD (avg: {avg_confidence:.1%})")
            self.known_good_predicates[predicate] = avg_confidence
            
            # Füge erfolgreiche Facts zur DB hinzu
            for fact, conf in test_results:
                if conf > 0.6:
                    self._add_fact_to_db(fact, 'autonomous_exploration', conf)
                    
        elif avg_confidence > 0.3:
            print(f"    ⚠️ {predicate} is MEDIOCRE (avg: {avg_confidence:.1%})")
            # Versuche Mapping zu finden
            self._find_better_mapping(predicate, test_results)
            
        else:
            print(f"    ❌ {predicate} is UNKNOWN to HRM (avg: {avg_confidence:.1%})")
            # Erstelle Mapping zu bekanntem Prädikat
            self._create_adaptive_mapping(predicate)
    
    def _add_fact_to_db(self, fact: str, source: str, confidence: float):
        """Fügt Fact zur Datenbank hinzu"""
        try:
            response = requests.post(
                f"{BACKEND_URL}/api/facts",
                json={
                    'statement': fact,
                    'source': source,
                    'confidence': confidence
                },
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.ok and response.json().get('success'):
                self.stats['facts_accepted'] += 1
                print(f"      💾 Added: {fact[:50]}...")
                return True
                
        except:
            pass
        return False
    
    def _find_better_mapping(self, bad_predicate: str, test_results: List[Tuple[str, float]]):
        """
        Phase 5: ADAPT
        Findet bessere Mappings für schlechte Prädikate
        """
        print(f"    🔄 Finding better mapping for {bad_predicate}...")
        
        # Teste alternative Prädikate
        alternatives = list(self.known_good_predicates.keys())
        best_mapping = None
        best_score = 0
        
        for alt_predicate in alternatives:
            # Teste einen Beispiel-Fact mit alternativem Prädikat
            if test_results:
                original_fact = test_results[0][0]
                # Ersetze Prädikat
                if '(' in original_fact:
                    args = original_fact[original_fact.index('('):]
                    alt_fact = alt_predicate + args
                    
                    alt_confidence = self.test_fact_confidence(alt_fact)
                    
                    if alt_confidence > best_score:
                        best_score = alt_confidence
                        best_mapping = alt_predicate
        
        if best_mapping and best_score > 0.5:
            self.learned_mappings[bad_predicate] = best_mapping
            print(f"      ✅ Learned: {bad_predicate} → {best_mapping} ({best_score:.1%})")
            self.stats['confidence_improvements'] += 1
    
    def _create_adaptive_mapping(self, unknown_predicate: str):
        """Erstellt adaptives Mapping für unbekanntes Prädikat"""
        # Analysiere Prädikat-Name für Hinweise
        if 'Has' in unknown_predicate or 'Property' in unknown_predicate:
            self.learned_mappings[unknown_predicate] = 'HasProperty'
        elif 'Is' in unknown_predicate or 'Type' in unknown_predicate:
            self.learned_mappings[unknown_predicate] = 'IsA'
        elif 'Cause' in unknown_predicate or 'Lead' in unknown_predicate:
            self.learned_mappings[unknown_predicate] = 'Causes'
        elif 'Part' in unknown_predicate or 'Contains' in unknown_predicate:
            self.learned_mappings[unknown_predicate] = 'HasPart'
        else:
            # Default fallback
            self.learned_mappings[unknown_predicate] = 'HasProperty'
        
        print(f"      📝 Created mapping: {unknown_predicate} → {self.learned_mappings[unknown_predicate]}")
    
    def run_exploration_cycle(self, max_predicates: int = 5):
        """
        Phase 6: EVOLVE
        Führt einen kompletten Explorations-Zyklus durch
        """
        print(f"\n{'='*60}")
        print("🚀 STARTING AUTONOMOUS EXPLORATION CYCLE")
        print(f"{'='*60}")
        
        # 1. Discover
        new_predicates = self.discover_new_predicates()
        
        if not new_predicates:
            print("\n⚠️ No new predicates to explore")
            return
        
        # 2. Select predicates to explore
        predicates_to_explore = list(new_predicates)[:max_predicates]
        
        print(f"\n📊 Exploring {len(predicates_to_explore)} predicates...")
        
        for i, predicate in enumerate(predicates_to_explore, 1):
            print(f"\n[{i}/{len(predicates_to_explore)}] Exploring: {predicate}")
            print("-"*40)
            
            # 2. Explore with LLM
            suggested_facts = self.explore_predicate_with_llm(predicate)
            
            if not suggested_facts:
                continue
            
            # 3. Test each fact
            test_results = []
            for fact in suggested_facts[:3]:  # Test max 3 facts per predicate
                confidence = self.test_fact_confidence(fact)
                test_results.append((fact, confidence))
                print(f"    Test: {fact[:50]}... → {confidence:.1%}")
            
            # 4. Learn from results
            self.learn_from_exploration(predicate, test_results)
            
            # Small delay
            time.sleep(0.5)
        
        # Save exploration history
        self._save_exploration_log()
        
        # Print summary
        self._print_summary()
    
    def _save_exploration_log(self):
        """Speichert Explorations-Historie"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'predicates_discovered': self.stats['predicates_discovered'],
            'facts_generated': self.stats['facts_generated'],
            'facts_accepted': self.stats['facts_accepted'],
            'learned_mappings': self.learned_mappings,
            'predicate_scores': dict(self.predicate_scores),
            'known_good_predicates': self.known_good_predicates
        }
        
        try:
            # Load existing log
            try:
                with open(EXPLORATION_LOG, 'r') as f:
                    log = json.load(f)
            except:
                log = []
            
            # Append new entry
            log.append(log_entry)
            
            # Save updated log
            with open(EXPLORATION_LOG, 'w') as f:
                json.dump(log, f, indent=2)
                
            print(f"\n💾 Exploration log saved to {EXPLORATION_LOG}")
            
        except Exception as e:
            print(f"\n⚠️ Could not save log: {e}")
    
    def _print_summary(self):
        """Druckt Zusammenfassung"""
        print(f"\n{'='*60}")
        print("📊 EXPLORATION SUMMARY")
        print(f"{'='*60}")
        
        print(f"\n🔍 Discovered: {self.stats['predicates_discovered']} new predicates")
        print(f"📝 Generated: {self.stats['facts_generated']} exploratory facts")
        print(f"✅ Accepted: {self.stats['facts_accepted']} facts into KB")
        print(f"📈 Improvements: {self.stats['confidence_improvements']} confidence boosts")
        
        if self.learned_mappings:
            print(f"\n🧠 LEARNED MAPPINGS:")
            for bad, good in self.learned_mappings.items():
                print(f"  {bad} → {good}")
        
        if self.known_good_predicates:
            print(f"\n✨ GOOD PREDICATES (>70% confidence):")
            for pred, score in sorted(self.known_good_predicates.items(), 
                                     key=lambda x: x[1], reverse=True)[:5]:
                print(f"  {pred}: {score:.1%}")
        
        print(f"\n{'='*60}")
    
    def run_continuous_learning(self, cycles: int = 3, delay_minutes: int = 5):
        """
        Kontinuierliches Lernen über mehrere Zyklen
        """
        print(f"\n🔄 STARTING CONTINUOUS LEARNING ({cycles} cycles)")
        print(f"   Delay between cycles: {delay_minutes} minutes")
        print("="*60)
        
        for cycle in range(1, cycles + 1):
            print(f"\n\n{'='*60}")
            print(f"🔄 CYCLE {cycle}/{cycles}")
            print(f"{'='*60}")
            
            # Run exploration
            self.run_exploration_cycle()
            
            # Evolve: Das System wird mit jedem Zyklus schlauer
            print(f"\n💭 System has learned {len(self.learned_mappings)} mappings")
            print(f"   Known good predicates: {len(self.known_good_predicates)}")
            
            if cycle < cycles:
                print(f"\n⏱️ Waiting {delay_minutes} minutes before next cycle...")
                time.sleep(delay_minutes * 60)
        
        print(f"\n\n{'='*60}")
        print("✅ CONTINUOUS LEARNING COMPLETE")
        print(f"{'='*60}")

def main():
    """Main execution"""
    print("\n🤖 HAK-GAL AUTONOMOUS PREDICATE EXPLORER")
    print("="*60)
    print("This system autonomously:")
    print("1. Discovers new predicates")
    print("2. Explores them with LLM")
    print("3. Tests HRM confidence")
    print("4. Learns successful patterns")
    print("5. Adapts and evolves")
    print("="*60)
    
    explorer = AutonomousPredicateExplorer()
    
    # Menu
    print("\n🎯 Choose exploration mode:")
    print("1. Single exploration cycle (quick)")
    print("2. Continuous learning (3 cycles)")
    print("3. 24/7 autonomous mode (runs forever)")
    
    choice = input("\nEnter choice (1-3): ")
    
    if choice == '1':
        explorer.run_exploration_cycle(max_predicates=5)
        
    elif choice == '2':
        cycles = int(input("Number of cycles (default 3): ") or "3")
        delay = int(input("Minutes between cycles (default 5): ") or "5")
        explorer.run_continuous_learning(cycles=cycles, delay_minutes=delay)
        
    elif choice == '3':
        print("\n🔄 AUTONOMOUS MODE - Press Ctrl+C to stop")
        try:
            while True:
                explorer.run_exploration_cycle(max_predicates=10)
                print("\n⏱️ Waiting 10 minutes before next exploration...")
                time.sleep(600)  # 10 minutes
        except KeyboardInterrupt:
            print("\n⏹️ Autonomous exploration stopped")
    
    print("\n✅ Exploration complete!")
    print(f"   Check {EXPLORATION_LOG} for detailed history")

if __name__ == "__main__":
    main()
