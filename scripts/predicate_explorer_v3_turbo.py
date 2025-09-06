#!/usr/bin/env python3
"""
HAK-GAL Predicate Explorer V3 TURBO
====================================
MAXIMALE ERFOLGSRATE durch:
- Extraktion realer Entitäten aus der KB
- Konkrete statt abstrakte Facts
- Erfolgreiche Pattern-Replikation

Nach HAK/GAL Verfassung Artikel 4: Bewusstes Grenzüberschreiten
"""

import requests
import json
import sqlite3
import time
import random
from typing import Dict, List, Tuple, Set
from collections import defaultdict

BACKEND_URL = 'http://localhost:5002'
DATABASE_PATH = r'D:\MCP Mods\HAK_GAL_HEXAGONAL\hexagonal_kb.db'

class PredicateExplorerV3Turbo:
    """
    V3 TURBO: Maximale Erfolgsrate durch KB-Mining
    """
    
    def __init__(self):
        # Extrahiere ECHTE Entitäten aus der KB!
        self.real_entities = self.extract_entities_from_kb()
        
        # Erfolgreiche Patterns aus V2
        self.winning_patterns = {
            'IsType': 'IsA',      # 99.6% Erfolg!
            'IsTypeOf': 'IsA',    # 100% Erfolg!
            'TypeOf': 'IsA',
            'InstanceOf': 'IsA',
            'SubClassOf': 'IsPartOf',
            'SubFieldOf': 'IsPartOf',
            'MemberOf': 'IsPartOf',
            'BelongsTo': 'IsPartOf'
        }
        
        # Prädikat-spezifische Strategien
        self.predicate_strategies = {
            # Requires-Familie
            'Requires': [
                ('Computer', 'CPU'),
                ('Computer', 'Memory'),
                ('Software', 'Hardware'),
                ('Plant', 'Water'),
                ('Engine', 'Fuel'),
                ('Life', 'Energy'),
                ('Democracy', 'Voting'),
                ('Science', 'Method')
            ],
            'DependsOn': [
                ('Software', 'Hardware'),
                ('Economy', 'Trade'),
                ('Society', 'Communication'),
                ('Plant', 'Sunlight'),
                ('Computer', 'Electricity')
            ],
            
            # Location-Familie
            'LocatedAt': [
                ('Berlin', 'Germany'),
                ('CPU', 'Computer'),
                ('Heart', 'Body'),
                ('Earth', 'SolarSystem')
            ],
            'LocatedIn': [
                ('Berlin', 'Germany'),
                ('Paris', 'France'),
                ('Tokyo', 'Japan'),
                ('Athens', 'Greece')
            ],
            
            # Creation-Familie
            'Creates': [
                ('Artist', 'Art'),
                ('Writer', 'Book'),
                ('Programmer', 'Software'),
                ('Sun', 'Light'),
                ('Plant', 'Oxygen')
            ],
            'Produces': [
                ('Factory', 'Product'),
                ('Sun', 'Energy'),
                ('Plant', 'Oxygen'),
                ('Volcano', 'Lava')
            ],
            'GeneratedBy': [
                ('Electricity', 'Generator'),
                ('Heat', 'Sun'),
                ('Wave', 'Wind'),
                ('Code', 'Programmer')
            ],
            
            # Influence-Familie
            'Influences': [
                ('Socrates', 'Philosophy'),
                ('Einstein', 'Physics'),
                ('Darwin', 'Biology'),
                ('Newton', 'Science')
            ],
            'Affects': [
                ('Temperature', 'Weather'),
                ('Gravity', 'Motion'),
                ('Supply', 'Demand'),
                ('Education', 'Society')
            ],
            
            # Reduction-Familie
            'Reduces': [
                ('Medicine', 'Pain'),
                ('Education', 'Ignorance'),
                ('Exercise', 'Stress'),
                ('Insulation', 'HeatLoss')
            ],
            'Prevents': [
                ('Vaccine', 'Disease'),
                ('Lock', 'Theft'),
                ('Firewall', 'Hacking'),
                ('Education', 'Ignorance')
            ]
        }
        
        self.stats = {
            'total_tested': 0,
            'successful': 0,
            'facts_added': 0,
            'best_confidence': 0,
            'best_fact': ''
        }
    
    def extract_entities_from_kb(self) -> Dict[str, Set[str]]:
        """
        Extrahiert ECHTE Entitäten direkt aus der KB
        """
        print("🔍 Mining entities from Knowledge Base...")
        
        entities = {
            'all': set(),
            'frequent': set(),  # Entities that appear > 5 times
            'persons': set(),
            'places': set(),
            'concepts': set(),
            'objects': set()
        }
        
        try:
            conn = sqlite3.connect(DATABASE_PATH)
            cursor = conn.cursor()
            
            # Hole alle Facts
            cursor.execute("SELECT statement FROM facts WHERE statement LIKE '%(%'")
            facts = cursor.fetchall()
            
            entity_counts = defaultdict(int)
            
            for (fact,) in facts:
                # Extrahiere Entitäten aus Facts
                if '(' in fact and ')' in fact:
                    content = fact[fact.index('(')+1:fact.rindex(')')]
                    parts = content.split(',')
                    
                    for part in parts:
                        entity = part.strip()
                        if entity and not entity.startswith('"'):
                            entities['all'].add(entity)
                            entity_counts[entity] += 1
                            
                            # Kategorisiere
                            if entity in ['Socrates', 'Plato', 'Aristotle', 'Napoleon', 
                                         'Einstein', 'Darwin', 'Newton', 'Kant']:
                                entities['persons'].add(entity)
                            elif entity in ['Germany', 'France', 'Berlin', 'Paris', 
                                           'Athens', 'Tokyo', 'Japan', 'Greece']:
                                entities['places'].add(entity)
                            elif entity in ['Computer', 'CPU', 'Memory', 'Software', 
                                           'Hardware', 'Internet']:
                                entities['objects'].add(entity)
                            else:
                                entities['concepts'].add(entity)
            
            # Finde häufige Entitäten
            for entity, count in entity_counts.items():
                if count > 5:
                    entities['frequent'].add(entity)
            
            conn.close()
            
            print(f"  ✅ Found {len(entities['all'])} unique entities")
            print(f"  ✅ {len(entities['frequent'])} frequent entities (>5 occurrences)")
            
            return entities
            
        except Exception as e:
            print(f"  ❌ Error mining entities: {e}")
            # Fallback zu Standard-Entitäten
            return {
                'all': {'Socrates', 'Computer', 'Berlin', 'Science', 'Philosophy'},
                'frequent': {'Socrates', 'Computer'},
                'persons': {'Socrates', 'Plato', 'Einstein'},
                'places': {'Berlin', 'Germany', 'Paris'},
                'concepts': {'Science', 'Philosophy', 'Democracy'},
                'objects': {'Computer', 'CPU', 'Software'}
            }
    
    def generate_smart_facts(self, predicate: str) -> List[str]:
        """
        Generiert SMARTE Facts basierend auf KB-Wissen
        """
        facts = []
        
        # 1. Check für vordefinierte Strategien
        if predicate in self.predicate_strategies:
            # Nutze bewährte Entity-Paare
            for subj, obj in self.predicate_strategies[predicate]:
                fact = f"{predicate}({subj}, {obj})."
                facts.append(fact)
            return facts[:5]
        
        # 2. Check für Winning Patterns (IsType, etc.)
        if predicate in self.winning_patterns:
            # Repliziere erfolgreiche Patterns
            if 'Is' in predicate or 'Type' in predicate:
                # Nutze Person-Kategorie Patterns
                facts.extend([
                    f"{predicate}(Socrates, Philosopher).",
                    f"{predicate}(Einstein, Scientist).",
                    f"{predicate}(Berlin, City).",
                    f"{predicate}(Germany, Country).",
                    f"{predicate}(Computer, Machine)."
                ])
            return facts[:5]
        
        # 3. Intelligente Heuristik basierend auf Prädikat-Name
        
        # Nutze HÄUFIGE Entitäten aus der KB
        frequent = list(self.real_entities.get('frequent', []))
        if len(frequent) >= 2:
            # Kombiniere häufige Entitäten
            for i in range(min(3, len(frequent)-1)):
                subj = frequent[i]
                obj = frequent[i+1]
                if subj != obj:
                    facts.append(f"{predicate}({subj}, {obj}).")
        
        # 4. Analyse des Prädikat-Namens
        predicate_lower = predicate.lower()
        
        if 'has' in predicate_lower or 'contains' in predicate_lower:
            # Part-Whole Beziehungen
            facts.extend([
                f"{predicate}(Computer, CPU).",
                f"{predicate}(Germany, Berlin).",
                f"{predicate}(Body, Heart).",
                f"{predicate}(SolarSystem, Earth).",
                f"{predicate}(Book, Chapter)."
            ])
            
        elif 'is' in predicate_lower:
            # Kategorisierung
            facts.extend([
                f"{predicate}(Socrates, Human).",
                f"{predicate}(Berlin, Capital).",
                f"{predicate}(Water, Liquid).",
                f"{predicate}(Seven, Number).",
                f"{predicate}(Philosophy, Science)."
            ])
            
        elif any(word in predicate_lower for word in ['create', 'make', 'produce', 'generate']):
            # Creation
            facts.extend([
                f"{predicate}(Sun, Light).",
                f"{predicate}(Plant, Oxygen).",
                f"{predicate}(Cloud, Rain).",
                f"{predicate}(Fire, Heat).",
                f"{predicate}(Artist, Art)."
            ])
            
        elif any(word in predicate_lower for word in ['locate', 'place', 'position']):
            # Location
            facts.extend([
                f"{predicate}(Berlin, Germany).",
                f"{predicate}(Eiffel Tower, Paris).",
                f"{predicate}(CPU, Motherboard).",
                f"{predicate}(Heart, Chest).",
                f"{predicate}(Sun, SolarSystem)."
            ])
            
        elif any(word in predicate_lower for word in ['connect', 'link', 'relate']):
            # Connection
            facts.extend([
                f"{predicate}(France, Spain).",
                f"{predicate}(CPU, Memory).",
                f"{predicate}(Heart, Lungs).",
                f"{predicate}(Cause, Effect).",
                f"{predicate}(Theory, Practice)."
            ])
            
        else:
            # Fallback: Nutze Top-Entitäten aus KB
            top_entities = list(self.real_entities.get('frequent', []))[:10]
            if not top_entities:
                top_entities = ['Computer', 'Socrates', 'Germany', 'Science', 'Philosophy']
            
            # Erstelle plausible Kombinationen
            for i in range(min(5, len(top_entities)-1)):
                subj = top_entities[i]
                obj = top_entities[(i+2) % len(top_entities)]
                if subj != obj:
                    facts.append(f"{predicate}({subj}, {obj}).")
        
        return facts[:5]
    
    def test_predicate(self, predicate: str) -> Dict:
        """
        Testet Prädikat mit smarten Facts
        """
        print(f"\n🧪 Testing: {predicate}")
        
        # Generiere smarte Facts
        facts = self.generate_smart_facts(predicate)
        
        results = []
        total_confidence = 0
        high_confidence_facts = []
        
        for fact in facts[:3]:  # Teste max 3
            try:
                response = requests.post(
                    f"{BACKEND_URL}/api/reason",
                    json={'query': fact},
                    headers={'Content-Type': 'application/json'},
                    timeout=10
                )
                
                if response.ok:
                    confidence = response.json().get('confidence', 0.0)
                    results.append((fact, confidence))
                    total_confidence += confidence
                    self.stats['total_tested'] += 1
                    
                    # Update best
                    if confidence > self.stats['best_confidence']:
                        self.stats['best_confidence'] = confidence
                        self.stats['best_fact'] = fact
                    
                    # Visualisierung
                    if confidence > 0.7:
                        print(f"  ✅ {fact[:50]}: {confidence:.1%}")
                        high_confidence_facts.append((fact, confidence))
                        self.stats['successful'] += 1
                    elif confidence > 0.3:
                        print(f"  ⚠️ {fact[:50]}: {confidence:.1%}")
                    else:
                        print(f"  ❌ {fact[:50]}: {confidence:.1%}")
                        
            except Exception as e:
                print(f"  ❌ Error: {e}")
        
        avg_confidence = total_confidence / len(results) if results else 0
        
        # Füge erfolgreiche Facts zur KB hinzu
        if avg_confidence > 0.5:
            print(f"  🎯 SUCCESS! Average: {avg_confidence:.1%}")
            
            for fact, conf in high_confidence_facts:
                if conf > 0.7:
                    self._add_fact_to_kb(fact, 'v3_turbo_exploration', conf)
        
        return {
            'predicate': predicate,
            'avg_confidence': avg_confidence,
            'success': avg_confidence > 0.3,
            'high_confidence_count': len(high_confidence_facts)
        }
    
    def _add_fact_to_kb(self, fact: str, source: str, confidence: float):
        """Fügt Fact zur KB hinzu"""
        try:
            response = requests.post(
                f"{BACKEND_URL}/api/facts",
                json={
                    'statement': fact,
                    'source': source,
                    'confidence': confidence
                },
                timeout=10
            )
            
            if response.ok and response.json().get('success'):
                self.stats['facts_added'] += 1
                print(f"    💾 Added to KB: {fact[:40]}...")
                return True
        except:
            pass
        return False
    
    def turbo_exploration(self, limit: int = 10):
        """
        TURBO MODE: Maximale Erfolgsrate
        """
        print("\n" + "="*60)
        print("🚀 PREDICATE EXPLORER V3 TURBO")
        print("="*60)
        print("FEATURES:")
        print("✅ Real entity extraction from KB")
        print("✅ Smart fact generation")
        print("✅ Proven pattern replication")
        print("✅ Predicate-specific strategies")
        print("="*60)
        
        # Finde unbekannte Prädikate
        unknown = self._discover_predicates()
        
        if not unknown:
            print("No unknown predicates found")
            return
        
        # Priorisiere vielversprechende Prädikate
        prioritized = []
        
        # 1. Winning patterns zuerst
        for pred in unknown:
            if pred in self.winning_patterns:
                prioritized.insert(0, pred)
        
        # 2. Dann Prädikate mit Strategien
        for pred in unknown:
            if pred in self.predicate_strategies and pred not in prioritized:
                prioritized.insert(len([p for p in prioritized if p in self.winning_patterns]), pred)
        
        # 3. Rest
        for pred in unknown:
            if pred not in prioritized:
                prioritized.append(pred)
        
        # Exploriere
        results = []
        for i, predicate in enumerate(prioritized[:limit], 1):
            print(f"\n[{i}/{min(limit, len(prioritized))}] Predicate: {predicate}")
            print("-"*40)
            
            result = self.test_predicate(predicate)
            results.append(result)
            
            time.sleep(0.3)
        
        # Zusammenfassung
        self._print_turbo_summary(results)
    
    def _discover_predicates(self) -> List[str]:
        """Findet unbekannte Prädikate"""
        try:
            conn = sqlite3.connect(DATABASE_PATH)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT DISTINCT
                    SUBSTR(statement, 1, INSTR(statement, '(') - 1) as predicate,
                    COUNT(*) as count
                FROM facts
                WHERE statement LIKE '%(%'
                AND predicate != ''
                GROUP BY predicate
                ORDER BY count DESC
            """)
            
            all_predicates = cursor.fetchall()
            conn.close()
            
            # Filter bekannte
            known = ['HasProperty', 'HasPart', 'Causes', 'IsA', 'Uses']
            unknown = [p for p, c in all_predicates if p not in known]
            
            print(f"Found {len(unknown)} unknown predicates")
            return unknown
            
        except Exception as e:
            print(f"Error: {e}")
            return []
    
    def _print_turbo_summary(self, results: List[Dict]):
        """Druckt TURBO Zusammenfassung"""
        print("\n" + "="*60)
        print("🏁 TURBO EXPLORATION COMPLETE")
        print("="*60)
        
        successful = [r for r in results if r.get('success', False)]
        success_rate = (len(successful) / len(results) * 100) if results else 0
        
        print(f"\n📊 STATISTICS:")
        print(f"  Success Rate: {success_rate:.1f}% ({len(successful)}/{len(results)})")
        print(f"  Facts Tested: {self.stats['total_tested']}")
        print(f"  Successful Tests: {self.stats['successful']}")
        print(f"  Facts Added to KB: {self.stats['facts_added']}")
        print(f"  Best Confidence: {self.stats['best_confidence']:.1%}")
        
        if self.stats['best_fact']:
            print(f"\n🏆 BEST DISCOVERY:")
            print(f"  {self.stats['best_fact']}")
        
        if successful:
            print(f"\n✅ SUCCESSFUL PREDICATES:")
            for r in sorted(successful, key=lambda x: x['avg_confidence'], reverse=True)[:5]:
                print(f"  • {r['predicate']}: {r['avg_confidence']:.1%}")
        
        # Ziel-Bewertung
        print(f"\n🎯 GOAL ASSESSMENT:")
        if success_rate >= 80:
            print("  ⭐⭐⭐ EXCELLENT! Goal exceeded!")
        elif success_rate >= 50:
            print("  ⭐⭐ GOOD! Significant improvement!")
        elif success_rate >= 30:
            print("  ⭐ OK! Some progress made.")
        else:
            print("  💪 Keep optimizing...")

def main():
    """Main execution"""
    print("\n🤖 PREDICATE EXPLORER V3 TURBO")
    print("="*60)
    print("TARGET: 80%+ Success Rate")
    print("METHOD: Smart fact generation with KB entities")
    print("="*60)
    
    explorer = PredicateExplorerV3Turbo()
    
    print("\nOptions:")
    print("1. TURBO exploration (10 predicates)")
    print("2. MEGA TURBO (20 predicates)")
    print("3. Test specific predicate")
    
    choice = input("\nChoice (1-3): ")
    
    if choice == '1':
        explorer.turbo_exploration(limit=10)
    elif choice == '2':
        explorer.turbo_exploration(limit=20)
    elif choice == '3':
        pred = input("Predicate name: ")
        result = explorer.test_predicate(pred)
        print(f"\nResult: {result['avg_confidence']:.1%} confidence")
    
    print("\n✅ V3 TURBO complete!")

if __name__ == "__main__":
    main()
