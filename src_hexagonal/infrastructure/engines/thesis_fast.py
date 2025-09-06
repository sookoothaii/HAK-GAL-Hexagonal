#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
THESIS ENGINE FAST - Direkte SQLite-Analyse ohne API
"""

import sys
import os
import sqlite3
import time
import random
import argparse
from collections import defaultdict
from typing import List, Set, Dict, Tuple

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

class ThesisEngineFast:
    def __init__(self):
        self.db_path = r"D:\MCP Mods\HAK_GAL_HEXAGONAL\hexagonal_kb.db"
        self.facts_by_predicate = defaultdict(list)
        self.facts_by_entity = defaultdict(list)
        self.existing_facts = set()
        
    def load_and_analyze_facts(self):
        """Lade und analysiere Fakten DIREKT aus SQLite"""
        print("[FAST] Loading facts from SQLite...")
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Lade alle Fakten
            cursor.execute("SELECT statement FROM facts LIMIT 5000")
            facts = cursor.fetchall()
            conn.close()
            
            print(f"[FAST] Loaded {len(facts)} facts from DB")
            
            # Analysiere Fakten
            for (fact_str,) in facts:
                self.existing_facts.add(fact_str)
                self.analyze_fact(fact_str)
            
            print(f"[ANALYSIS] Found {len(self.facts_by_predicate)} predicates")
            print(f"[ANALYSIS] Found {len(self.facts_by_entity)} entities")
            
            return True
            
        except Exception as e:
            print(f"[ERROR] DB load failed: {e}")
            return False
    
    def analyze_fact(self, fact: str):
        """Analysiere einzelnen Fakt"""
        import re
        
        # Pattern: Predicate(Subject, Object).
        match = re.match(r'^([A-Za-z0-9_]+)\(([^,)]+)(?:,\s*([^)]+))?\)\.$', fact)
        if not match:
            return
            
        predicate = match.group(1)
        subject = match.group(2).strip() if match.group(2) else ""
        obj = match.group(3).strip() if match.group(3) else ""
        
        # Speichere Analyse
        if subject:
            self.facts_by_predicate[predicate].append((subject, obj))
            self.facts_by_entity[subject].append((predicate, obj))
            if obj:
                self.facts_by_entity[obj].append((predicate, subject))
    
    def generate_meta_facts(self) -> List[str]:
        """Generiere Meta-Fakten über die Knowledge Base"""
        facts = []
        
        # KB Statistiken - keine zusammengeklebten Zahlen!
        total_facts = len(self.existing_facts)
        total_predicates = len(self.facts_by_predicate)
        total_entities = len(self.facts_by_entity)
        
        # Generiere saubere kategorische Fakten statt Zahlen
        if total_facts > 5000:
            facts.append(f"HasSize(KnowledgeBase, Large).")
        elif total_facts > 1000:
            facts.append(f"HasSize(KnowledgeBase, Medium).")
        else:
            facts.append(f"HasSize(KnowledgeBase, Small).")
        
        # Top Prädikate ohne Zahlen
        for pred, instances in list(self.facts_by_predicate.items())[:3]:
            if len(instances) > 100:
                facts.append(f"FrequentPredicate({pred}, VeryCommon).")
            elif len(instances) > 20:
                facts.append(f"FrequentPredicate({pred}, Common).")
        
        # Gut vernetzte Entities ohne ConnectionCount
        entities_sorted = sorted(self.facts_by_entity.items(), 
                                key=lambda x: len(x[1]), reverse=True)
        
        for entity, connections in entities_sorted[:3]:
            # Filtere schlechte Entity-Namen
            if '"' in entity or len(entity) > 50:
                continue
            if len(connections) > 50:
                facts.append(f"HighlyConnected({entity}, VeryHigh).")
            elif len(connections) > 10:
                facts.append(f"WellConnected({entity}, High).")
        
        return facts
    
    def find_transitive_relations(self) -> List[str]:
        """Finde transitive Beziehungen (A→B, B→C => A→C)"""
        facts = []
        
        # IsA Transitivität
        isa_facts = self.facts_by_predicate.get('IsA', [])[:50]
        
        # Baue Graph
        isa_graph = defaultdict(set)
        for subject, obj in isa_facts:
            if obj:
                isa_graph[subject].add(obj)
        
        # Finde transitive Beziehungen
        for entity in list(isa_graph.keys())[:20]:
            for direct_type in list(isa_graph[entity])[:3]:
                if direct_type in isa_graph:
                    for indirect_type in list(isa_graph[direct_type])[:2]:
                        new_fact = f"IsA({entity}, {indirect_type})."
                        if new_fact not in self.existing_facts:
                            facts.append(new_fact)
                            if len(facts) >= 10:
                                return facts
        
        return facts
    
    def find_symmetric_relations(self) -> List[str]:
        """Vervollständige symmetrische Beziehungen"""
        facts = []
        
        symmetric_preds = ['RelatesTo', 'ConnectsTo', 'SimilarTo']
        
        for pred in symmetric_preds:
            pairs = self.facts_by_predicate.get(pred, [])[:10]
            
            for subject, obj in pairs:
                if obj and subject != obj:
                    reverse = f"{pred}({obj}, {subject})."
                    if reverse not in self.existing_facts:
                        facts.append(reverse)
                        if len(facts) >= 5:
                            return facts
        
        return facts
    
    def add_fact_to_db(self, fact):
        """Füge Fakt direkt zur DB hinzu"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO facts (statement) VALUES (?)", (fact,))
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            return False  # Duplikat
        except Exception as e:
            print(f"[ERROR] Insert failed: {e}")
            return False
    
    def run(self, duration_minutes=5):
        """Hauptschleife"""
        print(f"[START] Thesis Engine FAST - {duration_minutes} minutes")
        print("[INFO] Using direct SQLite access")
        
        start_time = time.time()
        end_time = start_time + (duration_minutes * 60)
        facts_added = 0
        round_num = 0
        
        while time.time() < end_time:
            round_num += 1
            print(f"\n=== Analysis Round {round_num} ===")
            
            # Lade und analysiere KB
            if not self.load_and_analyze_facts():
                print("[SKIP] Analysis failed")
                time.sleep(10)
                continue
            
            # Generiere verschiedene Faktentypen
            all_new_facts = []
            
            # Meta-Fakten
            meta = self.generate_meta_facts()
            all_new_facts.extend(meta)
            print(f"[META] Generated {len(meta)} meta-facts")
            
            # Transitive Beziehungen
            trans = self.find_transitive_relations()
            all_new_facts.extend(trans)
            print(f"[TRANS] Found {len(trans)} transitive relations")
            
            # Symmetrische Beziehungen
            sym = self.find_symmetric_relations()
            all_new_facts.extend(sym)
            print(f"[SYM] Found {len(sym)} symmetric relations")
            
            # Füge neue Fakten hinzu
            added_this_round = 0
            for fact in all_new_facts:
                if fact not in self.existing_facts:
                    if self.add_fact_to_db(fact):
                        added_this_round += 1
                        facts_added += 1
                        print(f"[+] {fact}")
            
            print(f"[STATS] Added {added_this_round} facts, Total: {facts_added}")
            
            # Pause zwischen Runden
            if time.time() < end_time:
                time.sleep(15)
        
        print(f"\n[DONE] Added {facts_added} facts in {round_num} rounds")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--duration", type=float, default=0.1)
    parser.add_argument("-p", "--port", type=int, default=5002)
    args = parser.parse_args()
    
    engine = ThesisEngineFast()
    engine.run(duration_minutes=args.duration * 60)

if __name__ == "__main__":
    main()
