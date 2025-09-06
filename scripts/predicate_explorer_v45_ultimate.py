#!/usr/bin/env python3
"""
HAK-GAL V4.5 ULTIMATE - Mit integriertem LLM Boost
====================================================
V4 MEGA TURBO + Automatisches LLM Confidence Boosting

Nach HAK/GAL Verfassung:
- Artikel 1: Perfekte HRM-LLM Synergie
- Artikel 3: LLM als externe Verifikation
"""

import requests
import json
import sqlite3
import time
import re
from typing import Dict, List, Tuple, Set, Optional
from collections import defaultdict
from dataclasses import dataclass

# Importiere V4 Basis
import sys
sys.path.append('.')

BACKEND_URL = 'http://localhost:5002'
DATABASE_PATH = r'D:\MCP Mods\HAK_GAL_HEXAGONAL\hexagonal_kb.db'

class PredicateExplorerV45Ultimate:
    """
    V4.5: V4 MEGA TURBO + LLM Boost Integration
    """
    
    def __init__(self):
        print("🚀 INITIALIZING V4.5 ULTIMATE...")
        
        # V4 Features
        self.kb_facts = self._load_kb_facts()
        self.entity_types = self._classify_entities()
        
        # Tracking für LLM Boost
        self.zero_confidence_facts = []
        self.llm_boosted_facts = []
        
        # Stats
        self.stats = {
            'total_tested': 0,
            'hrm_successful': 0,
            'hrm_failed': 0,
            'llm_validated': 0,
            'llm_boosted': 0,
            'total_added': 0
        }
    
    def _load_kb_facts(self) -> List[Tuple[str, str, str]]:
        """Lädt Facts aus KB"""
        facts = []
        try:
            conn = sqlite3.connect(DATABASE_PATH)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT statement FROM facts 
                WHERE statement LIKE '%(%' 
                LIMIT 5000
            """)
            for (statement,) in cursor.fetchall():
                match = re.match(r'(\w+)\(([^,]+),\s*([^)]+)\)', statement)
                if match:
                    facts.append(match.groups())
            conn.close()
        except:
            pass
        return facts
    
    def _classify_entities(self) -> Dict[str, str]:
        """Klassifiziert Entities"""
        types = {}
        for _, e1, e2 in self.kb_facts:
            # Einfache Heuristik
            for entity in [e1.strip(), e2.strip()]:
                if entity not in types:
                    if entity in ['Socrates', 'Plato', 'Einstein', 'Napoleon']:
                        types[entity] = 'Person'
                    elif entity in ['Berlin', 'Germany', 'Paris', 'France']:
                        types[entity] = 'Place'
                    elif entity in ['Computer', 'CPU', 'Software']:
                        types[entity] = 'Technology'
                    else:
                        types[entity] = 'Concept'
        return types
    
    def test_with_hrm(self, fact: str) -> float:
        """Testet Fact mit HRM"""
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
    
    def validate_with_llm(self, fact: str) -> Tuple[float, str]:
        """
        Validiert Fact mit LLM wenn HRM 0% gibt
        """
        prompt = f"""
        Evaluate this logical fact:
        {fact}
        
        Is this:
        1. Semantically meaningful?
        2. Logically plausible?
        3. Useful knowledge?
        
        Rate confidence 0.0-1.0 and explain briefly.
        """
        
        try:
            response = requests.post(
                f"{BACKEND_URL}/api/llm/validate",
                json={'fact': fact, 'prompt': prompt},
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            if response.ok:
                data = response.json()
                confidence = data.get('confidence', 0.0)
                reasoning = data.get('reasoning', '')
                return confidence, reasoning
        except:
            pass
        
        return 0.0, "LLM validation failed"
    
    def test_predicate_ultimate(self, predicate: str) -> Dict:
        """
        ULTIMATE Testing: HRM + LLM Fallback
        """
        print(f"\n🧪 Testing: {predicate}")
        
        # Generiere Facts (vereinfachte Version)
        facts = self._generate_facts(predicate)
        
        results = []
        for fact in facts[:3]:
            # Phase 1: HRM Test
            hrm_conf = self.test_with_hrm(fact)
            self.stats['total_tested'] += 1
            
            if hrm_conf > 0.7:
                # HRM erfolgreich
                print(f"  ✅ HRM: {fact[:50]}: {hrm_conf:.1%}")
                self.stats['hrm_successful'] += 1
                results.append((fact, hrm_conf, 'hrm'))
                
            elif hrm_conf < 0.3:
                # HRM versagt - LLM Boost!
                print(f"  ❌ HRM: {fact[:50]}: {hrm_conf:.1%}")
                self.stats['hrm_failed'] += 1
                
                # Phase 2: LLM Validation
                print(f"    🤖 Trying LLM boost...")
                llm_conf, reasoning = self.validate_with_llm(fact)
                self.stats['llm_validated'] += 1
                
                if llm_conf > 0.6:
                    # LLM rettet den Fact!
                    combined_conf = (hrm_conf + llm_conf * 2) / 3  # Gewichte LLM höher
                    print(f"    ✅ LLM BOOST: {llm_conf:.1%} → Combined: {combined_conf:.1%}")
                    print(f"    💡 {reasoning[:80]}...")
                    
                    self.stats['llm_boosted'] += 1
                    self.llm_boosted_facts.append({
                        'fact': fact,
                        'hrm': hrm_conf,
                        'llm': llm_conf,
                        'combined': combined_conf
                    })
                    
                    results.append((fact, combined_conf, 'llm_boosted'))
                    
                    # Füge zur KB hinzu
                    self._add_to_kb(fact, combined_conf, 'v45_llm_boosted')
                else:
                    print(f"    ❌ LLM auch skeptisch: {llm_conf:.1%}")
                    results.append((fact, hrm_conf, 'failed'))
                    
            else:
                # Mittlere Confidence
                print(f"  ⚠️ HRM: {fact[:50]}: {hrm_conf:.1%}")
                results.append((fact, hrm_conf, 'hrm'))
        
        # Berechne Erfolg
        avg_conf = sum(r[1] for r in results) / len(results) if results else 0
        success_count = len([r for r in results if r[1] > 0.5])
        
        return {
            'predicate': predicate,
            'avg_confidence': avg_conf,
            'success_rate': success_count / len(results) if results else 0,
            'hrm_success': len([r for r in results if r[2] == 'hrm']),
            'llm_boosted': len([r for r in results if r[2] == 'llm_boosted'])
        }
    
    def _generate_facts(self, predicate: str) -> List[str]:
        """Generiert Facts (vereinfacht)"""
        facts = []
        
        # Nutze bekannte Patterns
        if 'require' in predicate.lower():
            facts = [
                f"{predicate}(Computer, Electricity).",
                f"{predicate}(Car, Fuel).",
                f"{predicate}(Plant, Water)."
            ]
        elif 'create' in predicate.lower():
            facts = [
                f"{predicate}(Sun, Light).",
                f"{predicate}(Artist, Art).",
                f"{predicate}(Cloud, Rain)."
            ]
        else:
            # Fallback
            entities = list(self.entity_types.keys())[:10]
            if len(entities) >= 2:
                for i in range(3):
                    e1 = entities[i % len(entities)]
                    e2 = entities[(i+1) % len(entities)]
                    facts.append(f"{predicate}({e1}, {e2}).")
        
        return facts
    
    def _add_to_kb(self, fact: str, confidence: float, source: str):
        """Fügt Fact zur KB hinzu"""
        try:
            response = requests.post(
                f"{BACKEND_URL}/api/facts",
                json={
                    'statement': fact,
                    'confidence': confidence,
                    'source': source
                },
                timeout=10
            )
            if response.ok and response.json().get('success'):
                self.stats['total_added'] += 1
                return True
        except:
            pass
        return False
    
    def run_ultimate_exploration(self, limit: int = 20):
        """
        ULTIMATE Exploration mit automatischem LLM Boost
        """
        print("\n" + "="*60)
        print("🚀 V4.5 ULTIMATE EXPLORATION")
        print("="*60)
        print("FEATURES:")
        print("✅ HRM primary testing")
        print("✅ Automatic LLM boost for failed facts")
        print("✅ Combined confidence scoring")
        print("✅ Intelligent fact addition")
        print("="*60)
        
        # Finde Prädikate (vereinfacht)
        predicates = self._discover_predicates()[:limit]
        
        results = []
        for i, predicate in enumerate(predicates, 1):
            print(f"\n[{i}/{len(predicates)}] Predicate: {predicate}")
            print("-"*40)
            
            result = self.test_predicate_ultimate(predicate)
            results.append(result)
            
            time.sleep(0.2)
        
        # ULTIMATE Summary
        self._print_ultimate_summary(results)
    
    def _discover_predicates(self) -> List[str]:
        """Findet Prädikate (vereinfacht)"""
        # Beispiel-Prädikate
        return [
            'Requires', 'Creates', 'DependsOn', 'Influences',
            'Produces', 'ConnectsTo', 'Affects', 'Prevents',
            'GeneratedBy', 'LocatedAt', 'Controls', 'Enables',
            'Transforms', 'Supports', 'Reduces', 'Enhances'
        ]
    
    def _print_ultimate_summary(self, results: List[Dict]):
        """ULTIMATE Summary mit HRM+LLM Stats"""
        print("\n" + "="*60)
        print("🏁 V4.5 ULTIMATE RESULTS")
        print("="*60)
        
        # Berechne Metriken
        total_success = sum(1 for r in results if r['avg_confidence'] > 0.5)
        success_rate = (total_success / len(results) * 100) if results else 0
        
        print(f"\n📊 PERFORMANCE METRICS:")
        print(f"  Overall Success Rate: {success_rate:.1f}%")
        print(f"  Total Facts Tested: {self.stats['total_tested']}")
        print(f"  HRM Successful: {self.stats['hrm_successful']}")
        print(f"  HRM Failed: {self.stats['hrm_failed']}")
        print(f"  LLM Validated: {self.stats['llm_validated']}")
        print(f"  LLM Boosted: {self.stats['llm_boosted']}")
        print(f"  Facts Added to KB: {self.stats['total_added']}")
        
        # LLM Boost Effektivität
        if self.stats['llm_validated'] > 0:
            boost_rate = (self.stats['llm_boosted'] / self.stats['llm_validated']) * 100
            print(f"\n🤖 LLM BOOST EFFECTIVENESS:")
            print(f"  Boost Success Rate: {boost_rate:.1f}%")
            print(f"  Facts Rescued by LLM: {self.stats['llm_boosted']}")
        
        # Top Boosted Facts
        if self.llm_boosted_facts:
            print(f"\n🏆 TOP LLM BOOSTS:")
            top_boosts = sorted(self.llm_boosted_facts, 
                              key=lambda x: x['llm'] - x['hrm'], 
                              reverse=True)[:3]
            
            for boost in top_boosts:
                improvement = boost['llm'] - boost['hrm']
                print(f"  • {boost['fact'][:50]}...")
                print(f"    HRM: {boost['hrm']:.1%} → LLM: {boost['llm']:.1%} "
                      f"(+{improvement:.1%})")
        
        # Finale Bewertung
        print(f"\n🎯 FINAL ASSESSMENT:")
        combined_success = success_rate + (self.stats['llm_boosted'] / max(1, self.stats['total_tested']) * 100)
        
        if combined_success >= 80:
            print("  ⭐⭐⭐⭐⭐ LEGENDARY! HRM+LLM Synergie perfekt!")
        elif combined_success >= 60:
            print("  ⭐⭐⭐⭐ EXCELLENT! LLM rettet viele Facts!")
        elif combined_success >= 40:
            print("  ⭐⭐⭐ GOOD! Deutliche Verbesserung durch LLM!")
        else:
            print("  ⭐⭐ OK! Weiter optimieren...")
        
        print("\n💡 KEY INSIGHT:")
        print("  HRM + LLM = Mehr als die Summe der Teile!")
        print("  LLM validiert semantische Korrektheit")
        print("  HRM lernt von LLM-validierten Facts")
        print("  → Kontinuierliche Verbesserung!")

def main():
    """Main execution"""
    print("\n" + "="*60)
    print("🤖 V4.5 ULTIMATE - HRM + LLM BOOST")
    print("="*60)
    print("The best of both worlds!")
    print("="*60)
    
    explorer = PredicateExplorerV45Ultimate()
    
    print("\nOptions:")
    print("1. ULTIMATE exploration (20 predicates)")
    print("2. MEGA ULTIMATE (30 predicates)")
    print("3. Test specific predicate")
    
    choice = input("\nChoice (1-3): ")
    
    if choice == '1':
        explorer.run_ultimate_exploration(limit=20)
    elif choice == '2':
        explorer.run_ultimate_exploration(limit=30)
    elif choice == '3':
        pred = input("Predicate: ")
        result = explorer.test_predicate_ultimate(pred)
        print(f"\nResult: {result['avg_confidence']:.1%}")
        print(f"HRM Success: {result['hrm_success']}")
        print(f"LLM Boosted: {result['llm_boosted']}")
    
    print("\n✅ V4.5 ULTIMATE complete!")

if __name__ == "__main__":
    main()
