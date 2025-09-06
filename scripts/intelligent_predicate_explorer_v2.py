#!/usr/bin/env python3
"""
HAK-GAL Intelligent Predicate Explorer V2
==========================================
FIXED VERSION mit semantischem Verständnis und besserer Fact-Generierung

Nach HAK/GAL Verfassung Artikel 6: Empirische Validierung
"""

import requests
import json
import sqlite3
import time
from typing import Dict, List, Tuple, Set
from collections import defaultdict

BACKEND_URL = 'http://localhost:5002'
DATABASE_PATH = r'D:\MCP Mods\HAK_GAL_HEXAGONAL\hexagonal_kb.db'

class IntelligentPredicateExplorer:
    """
    Verbesserte Version mit semantischem Prädikat-Verständnis
    """
    
    def __init__(self):
        # Prädikat-Semantik definieren
        self.predicate_semantics = {
            # Person-bezogene Prädikate
            'BornIn': {
                'domain': 'Person',
                'range': 'Location',
                'examples': [
                    'BornIn(Einstein, Germany)',
                    'BornIn(Shakespeare, England)',
                    'BornIn(Confucius, China)'
                ],
                'mapping': 'LocatedIn'
            },
            'StudentOf': {
                'domain': 'Person',
                'range': 'Person',
                'examples': [
                    'StudentOf(Plato, Socrates)',
                    'StudentOf(Aristotle, Plato)',
                    'StudentOf(Alexander, Aristotle)'
                ],
                'mapping': 'LearnsFrom'
            },
            'TeacherOf': {
                'domain': 'Person',
                'range': 'Person',
                'examples': [
                    'TeacherOf(Socrates, Plato)',
                    'TeacherOf(Plato, Aristotle)',
                    'TeacherOf(Kant, Fichte)'
                ],
                'mapping': 'Teaches'
            },
            
            # Struktur-bezogene Prädikate
            'SubFieldOf': {
                'domain': 'Field',
                'range': 'Field',
                'examples': [
                    'SubFieldOf(Algebra, Mathematics)',
                    'SubFieldOf(Genetics, Biology)',
                    'SubFieldOf(Thermodynamics, Physics)'
                ],
                'mapping': 'IsPartOf'
            },
            'ConnectsTo': {
                'domain': 'Entity',
                'range': 'Entity',
                'examples': [
                    'ConnectsTo(France, Spain)',
                    'ConnectsTo(CPU, Memory)',
                    'ConnectsTo(Heart, Lungs)'
                ],
                'mapping': 'IsConnectedTo'
            },
            
            # Action-bezogene Prädikate
            'Creates': {
                'domain': 'Agent',
                'range': 'Object',
                'examples': [
                    'Creates(Artist, Painting)',
                    'Creates(Programmer, Software)',
                    'Creates(Nature, Beauty)'
                ],
                'mapping': 'Causes'
            },
            'Influences': {
                'domain': 'Entity',
                'range': 'Entity',
                'examples': [
                    'Influences(Socrates, WesternPhilosophy)',
                    'Influences(Darwin, ModernBiology)',
                    'Influences(Einstein, Physics)'
                ],
                'mapping': 'Causes'
            }
        }
        
        # Bekannte gute Entitäten aus der DB
        self.known_entities = {
            'persons': ['Socrates', 'Plato', 'Aristotle', 'Napoleon', 'Einstein', 
                       'Darwin', 'Newton', 'Kant', 'Descartes', 'Galileo'],
            'places': ['Germany', 'France', 'Greece', 'Athens', 'Berlin', 
                      'Paris', 'Rome', 'London', 'Tokyo', 'China'],
            'fields': ['Philosophy', 'Mathematics', 'Physics', 'Biology', 
                      'Chemistry', 'Computer Science', 'Psychology', 'Economics'],
            'concepts': ['Democracy', 'Evolution', 'Gravity', 'Energy', 
                        'Knowledge', 'Truth', 'Justice', 'Freedom'],
            'objects': ['Computer', 'CPU', 'Software', 'Internet', 
                       'Book', 'Theory', 'Language', 'Art']
        }
        
        # Performance tracking
        self.successful_facts = []
        self.failed_facts = []
        
    def generate_semantic_facts(self, predicate: str) -> List[str]:
        """
        Generiert semantisch korrekte Facts basierend auf Prädikat-Typ
        """
        facts = []
        
        # Verwende Semantik wenn bekannt
        if predicate in self.predicate_semantics:
            sem = self.predicate_semantics[predicate]
            
            # Wähle passende Entitäten basierend auf Domain/Range
            if sem['domain'] == 'Person':
                subjects = self.known_entities['persons']
            elif sem['domain'] == 'Field':
                subjects = self.known_entities['fields']
            else:
                subjects = (self.known_entities['concepts'] + 
                          self.known_entities['objects'])
            
            if sem['range'] == 'Location':
                objects = self.known_entities['places']
            elif sem['range'] == 'Person':
                objects = self.known_entities['persons']
            elif sem['range'] == 'Field':
                objects = self.known_entities['fields']
            else:
                objects = (self.known_entities['concepts'] + 
                         self.known_entities['objects'])
            
            # Generiere plausible Kombinationen
            for i in range(min(5, len(subjects))):
                subj = subjects[i % len(subjects)]
                obj = objects[(i + 1) % len(objects)]
                
                # Verhindere selbst-referenzen
                if subj != obj:
                    fact = f"{predicate}({subj}, {obj})."
                    facts.append(fact)
            
            # Füge Beispiele hinzu wenn verfügbar
            facts.extend(sem.get('examples', [])[:2])
            
        else:
            # Fallback für unbekannte Prädikate
            # Analysiere Prädikat-Name für Hinweise
            if 'Has' in predicate or 'Contains' in predicate:
                # Property-like
                facts.append(f"{predicate}(Computer, Memory).")
                facts.append(f"{predicate}(Human, Intelligence).")
                facts.append(f"{predicate}(Science, Method).")
                
            elif 'Is' in predicate:
                # Type/Category-like
                facts.append(f"{predicate}(Socrates, Philosopher).")
                facts.append(f"{predicate}(Mathematics, Science).")
                facts.append(f"{predicate}(Berlin, City).")
                
            else:
                # Action-like
                facts.append(f"{predicate}(Science, Progress).")
                facts.append(f"{predicate}(Philosophy, Understanding).")
                facts.append(f"{predicate}(Technology, Innovation).")
        
        return facts[:5]  # Max 5 facts
    
    def test_and_learn(self, predicate: str) -> Dict:
        """
        Testet Facts und lernt aus Ergebnissen
        """
        print(f"\n🧪 Testing predicate: {predicate}")
        
        # Generiere semantisch korrekte Facts
        facts = self.generate_semantic_facts(predicate)
        
        if not facts:
            print("  ⚠️ No facts generated")
            return {'success': False}
        
        results = []
        total_confidence = 0
        
        for fact in facts[:3]:  # Teste max 3
            try:
                # Test mit HRM
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
                    
                    # Visualisierung
                    if confidence > 0.7:
                        print(f"  ✅ {fact[:50]}: {confidence:.1%}")
                        self.successful_facts.append(fact)
                    elif confidence > 0.3:
                        print(f"  ⚠️ {fact[:50]}: {confidence:.1%}")
                    else:
                        print(f"  ❌ {fact[:50]}: {confidence:.1%}")
                        self.failed_facts.append(fact)
                        
            except Exception as e:
                print(f"  ❌ Error testing {fact[:30]}: {e}")
        
        # Analysiere Ergebnisse
        avg_confidence = total_confidence / len(results) if results else 0
        
        # Entscheide über Mapping
        if avg_confidence > 0.5:
            print(f"  🎯 {predicate} works well! (avg: {avg_confidence:.1%})")
            
            # Füge erfolgreiche Facts zur DB hinzu
            for fact, conf in results:
                if conf > 0.6:
                    self._add_fact_to_db(fact, 'intelligent_exploration', conf)
                    
        elif predicate in self.predicate_semantics:
            # Verwende vordefiniertes Mapping
            mapping = self.predicate_semantics[predicate]['mapping']
            print(f"  🔄 Mapping {predicate} → {mapping}")
            
            # Teste Mapping
            mapped_facts = [f.replace(predicate, mapping) for f in facts[:2]]
            for mf in mapped_facts:
                self.test_fact_confidence(mf)
        
        return {
            'predicate': predicate,
            'avg_confidence': avg_confidence,
            'facts_tested': len(results),
            'success': avg_confidence > 0.3
        }
    
    def test_fact_confidence(self, fact: str) -> float:
        """Testet einzelnen Fact"""
        try:
            response = requests.post(
                f"{BACKEND_URL}/api/reason",
                json={'query': fact},
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.ok:
                return response.json().get('confidence', 0.0)
        except:
            pass
        return 0.0
    
    def _add_fact_to_db(self, fact: str, source: str, confidence: float):
        """Fügt Fact zur DB hinzu"""
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
                print(f"    💾 Added to KB: {fact[:40]}...")
                return True
        except:
            pass
        return False
    
    def explore_predicates(self, limit: int = 5):
        """
        Hauptfunktion: Exploriert neue Prädikate intelligent
        """
        print("\n" + "="*60)
        print("🚀 INTELLIGENT PREDICATE EXPLORATION V2")
        print("="*60)
        
        # Finde unbekannte Prädikate
        unknown_predicates = self._discover_predicates()
        
        if not unknown_predicates:
            print("No unknown predicates found")
            return
        
        # Priorisiere Prädikate die wir verstehen
        prioritized = []
        for pred in unknown_predicates:
            if pred in self.predicate_semantics:
                prioritized.insert(0, pred)  # Bekannte zuerst
            else:
                prioritized.append(pred)
        
        # Exploriere
        results = []
        for i, predicate in enumerate(prioritized[:limit], 1):
            print(f"\n[{i}/{min(limit, len(prioritized))}] Exploring: {predicate}")
            print("-"*40)
            
            result = self.test_and_learn(predicate)
            results.append(result)
            
            time.sleep(0.5)  # Rate limiting
        
        # Zusammenfassung
        self._print_summary(results)
    
    def _discover_predicates(self) -> List[str]:
        """Findet unbekannte Prädikate in DB"""
        try:
            conn = sqlite3.connect(DATABASE_PATH)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT DISTINCT
                    SUBSTR(statement, 1, INSTR(statement, '(') - 1) as predicate
                FROM facts
                WHERE statement LIKE '%(%'
                AND predicate != ''
            """)
            
            predicates = [row[0] for row in cursor.fetchall()]
            conn.close()
            
            # Filter bekannte
            known = ['HasProperty', 'HasPart', 'Causes', 'IsA', 'Uses']
            unknown = [p for p in predicates if p not in known]
            
            print(f"Found {len(unknown)} unknown predicates")
            return unknown[:20]  # Max 20
            
        except Exception as e:
            print(f"Error discovering predicates: {e}")
            return []
    
    def _print_summary(self, results: List[Dict]):
        """Druckt Zusammenfassung"""
        print("\n" + "="*60)
        print("📊 EXPLORATION SUMMARY")
        print("="*60)
        
        successful = [r for r in results if r.get('success', False)]
        
        print(f"\n✅ Successful predicates: {len(successful)}/{len(results)}")
        for r in successful:
            print(f"  • {r['predicate']}: {r['avg_confidence']:.1%}")
        
        print(f"\n📈 Facts added to KB: {len(self.successful_facts)}")
        print(f"❌ Failed facts: {len(self.failed_facts)}")
        
        if self.successful_facts:
            print("\n🏆 Best discoveries:")
            for fact in self.successful_facts[:3]:
                print(f"  • {fact}")

def main():
    """Main execution"""
    print("\n🤖 INTELLIGENT PREDICATE EXPLORER V2")
    print("="*60)
    print("FIXES:")
    print("✅ Semantic fact generation")
    print("✅ Domain/Range awareness")
    print("✅ Uses known entities")
    print("✅ Intelligent mappings")
    print("="*60)
    
    explorer = IntelligentPredicateExplorer()
    
    # Menu
    print("\nOptions:")
    print("1. Quick exploration (5 predicates)")
    print("2. Full exploration (10 predicates)")
    print("3. Test specific predicate")
    
    choice = input("\nChoice (1-3): ")
    
    if choice == '1':
        explorer.explore_predicates(limit=5)
    elif choice == '2':
        explorer.explore_predicates(limit=10)
    elif choice == '3':
        pred = input("Enter predicate name: ")
        explorer.test_and_learn(pred)
    
    print("\n✅ Exploration complete!")

if __name__ == "__main__":
    main()
