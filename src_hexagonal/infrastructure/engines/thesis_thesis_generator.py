#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
THESIS ENGINE - THESIS GENERATOR
===============================
Generiert logische Thesen aus Aethelred-Fakten und bereitet sie für LLM-Beweise vor
"""

import sys
import os
import sqlite3
import time
import random
import argparse
import re
from collections import defaultdict, Counter
from typing import List, Set, Dict, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

@dataclass
class Thesis:
    """Eine logische These"""
    statement: str
    supporting_facts: List[str]
    confidence: float
    category: str
    created_at: str
    status: str = "pending"  # pending, proven, disproven, needs_proof

class ThesisGenerator:
    """Generiert logische Thesen aus Fakten"""
    
    def __init__(self):
        self.db_path = r"D:\MCP Mods\HAK_GAL_HEXAGONAL\hexagonal_kb.db"
        self.facts_by_predicate = defaultdict(list)
        self.facts_by_entity = defaultdict(list)
        self.entity_connections = defaultdict(set)
        self.predicate_patterns = defaultdict(list)
        self.theses = []
        
    def load_recent_facts(self, limit: int = 1000) -> bool:
        """Lade die neuesten Fakten (von Aethelred generiert)"""
        print(f"[THESIS] Loading {limit} recent facts...")
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Lade neueste Fakten (die von Aethelred generiert wurden)
            # Fallback falls created_at Spalte nicht existiert
            try:
                cursor.execute("""
                    SELECT statement, created_at 
                    FROM facts 
                    ORDER BY created_at DESC 
                    LIMIT ?
                """, (limit,))
            except sqlite3.OperationalError:
                # Fallback ohne created_at
                cursor.execute("""
                    SELECT statement 
                    FROM facts 
                    LIMIT ?
                """, (limit,))
            
            facts = cursor.fetchall()
            conn.close()
            
            print(f"[THESIS] Loaded {len(facts)} recent facts")
            
            # Analysiere Fakten
            for fact_row in facts:
                if len(fact_row) == 2:
                    fact_str, created_at = fact_row
                else:
                    fact_str = fact_row[0]
                    created_at = None
                self.analyze_fact_for_thesis(fact_str)
            
            print(f"[ANALYSIS] Found {len(self.facts_by_predicate)} predicates")
            print(f"[ANALYSIS] Found {len(self.facts_by_entity)} entities")
            
            return True
            
        except Exception as e:
            print(f"[ERROR] DB load failed: {e}")
            return False
    
    def analyze_fact_for_thesis(self, fact: str):
        """Analysiere Fakt für Thesen-Generierung"""
        # Pattern: Predicate(Subject, Object).
        match = re.match(r'^([A-Za-z0-9_]+)\(([^,)]+)(?:,\s*([^)]+))?\)\.$', fact)
        if not match:
            return
            
        predicate = match.group(1)
        subject = match.group(2).strip() if match.group(2) else ""
        obj = match.group(3).strip() if match.group(3) else ""
        
        # Speichere für Thesen-Generierung
        if subject:
            self.facts_by_predicate[predicate].append((subject, obj, fact))
            self.facts_by_entity[subject].append((predicate, obj, fact))
            if obj:
                self.facts_by_entity[obj].append((predicate, subject, fact))
                # Verbindungen für Netzwerk-Analyse
                self.entity_connections[subject].add(obj)
                self.entity_connections[obj].add(subject)
    
    def generate_correlation_theses(self) -> List[Thesis]:
        """Generiere Thesen basierend auf Korrelationen zwischen Fakten"""
        theses = []
        
        # Finde häufige Prädikat-Kombinationen
        predicate_combinations = defaultdict(int)
        
        for entity, connections in self.facts_by_entity.items():
            predicates = [pred for pred, obj, fact in connections]
            # Zähle Kombinationen von Prädikaten für dieselbe Entity
            for i in range(len(predicates)):
                for j in range(i+1, len(predicates)):
                    combo = tuple(sorted([predicates[i], predicates[j]]))
                    predicate_combinations[combo] += 1
        
        # Generiere Thesen für häufige Kombinationen
        for (pred1, pred2), count in predicate_combinations.items():
            if count >= 3:  # Mindestens 3 Beispiele
                # Finde konkrete Beispiele
                examples = []
                for entity, connections in self.facts_by_entity.items():
                    entity_preds = [pred for pred, obj, fact in connections]
                    if pred1 in entity_preds and pred2 in entity_preds:
                        examples.append(entity)
                        if len(examples) >= 5:
                            break
                
                if examples:
                    thesis = Thesis(
                        statement=f"Entities with {pred1} often also have {pred2}",
                        supporting_facts=[f"Found {count} entities with both {pred1} and {pred2}"],
                        confidence=min(count / 10.0, 0.9),
                        category="correlation",
                        created_at=datetime.now().isoformat()
                    )
                    theses.append(thesis)
        
        return theses[:5]  # Max 5 Korrelations-Thesen
    
    def generate_hierarchical_theses(self) -> List[Thesis]:
        """Generiere Thesen basierend auf hierarchischen Beziehungen"""
        theses = []
        
        # IsA Hierarchien
        isa_facts = self.facts_by_predicate.get('IsA', [])
        if len(isa_facts) >= 5:
            # Finde gemeinsame Eigenschaften von Entities gleichen Typs
            type_groups = defaultdict(list)
            for subject, obj, fact in isa_facts:
                if obj:
                    type_groups[obj].append(subject)
            
            for type_name, entities in type_groups.items():
                if len(entities) >= 3:
                    # Finde gemeinsame Prädikate für diese Entities
                    common_predicates = defaultdict(int)
                    for entity in entities:
                        if entity in self.facts_by_entity:
                            for pred, obj, fact in self.facts_by_entity[entity]:
                                common_predicates[pred] += 1
                    
                    # Generiere These für häufige Eigenschaften
                    for pred, count in common_predicates.items():
                        if count >= 2 and count >= len(entities) * 0.6:  # 60% der Entities
                            thesis = Thesis(
                                statement=f"Most {type_name} entities have {pred}",
                                supporting_facts=[f"Found {count} out of {len(entities)} {type_name} entities with {pred}"],
                                confidence=count / len(entities),
                                category="hierarchical",
                                created_at=datetime.now().isoformat()
                            )
                            theses.append(thesis)
                            if len(theses) >= 3:
                                break
        
        return theses
    
    def generate_causal_theses(self) -> List[Thesis]:
        """Generiere Thesen basierend auf möglichen Kausalzusammenhängen"""
        theses = []
        
        # Suche nach kausalen Mustern
        causal_patterns = [
            ('Cause', 'Effect'),
            ('Produces', 'Product'),
            ('Creates', 'Created'),
            ('Generates', 'Generated'),
            ('Results', 'Result')
        ]
        
        for cause_pred, effect_pred in causal_patterns:
            cause_facts = self.facts_by_predicate.get(cause_pred, [])
            effect_facts = self.facts_by_predicate.get(effect_pred, [])
            
            if len(cause_facts) >= 2 and len(effect_facts) >= 2:
                # Finde überlappende Entities
                cause_entities = set(subject for subject, obj, fact in cause_facts)
                effect_entities = set(subject for subject, obj, fact in effect_facts)
                
                overlap = cause_entities.intersection(effect_entities)
                if len(overlap) >= 2:
                    thesis = Thesis(
                        statement=f"Entities that {cause_pred.lower()} often also {effect_pred.lower()}",
                        supporting_facts=[f"Found {len(overlap)} entities with both {cause_pred} and {effect_pred}"],
                        confidence=min(len(overlap) / 5.0, 0.8),
                        category="causal",
                        created_at=datetime.now().isoformat()
                    )
                    theses.append(thesis)
        
        return theses[:3]  # Max 3 Kausal-Thesen
    
    def generate_network_theses(self) -> List[Thesis]:
        """Generiere Thesen basierend auf Netzwerk-Analyse"""
        theses = []
        
        # Finde hoch vernetzte Entities
        highly_connected = []
        for entity, connections in self.entity_connections.items():
            if len(connections) >= 5:
                highly_connected.append((entity, len(connections)))
        
        # Sortiere nach Verbindungen
        highly_connected.sort(key=lambda x: x[1], reverse=True)
        
        for entity, connection_count in highly_connected[:3]:
            # Finde gemeinsame Eigenschaften der verbundenen Entities
            connected_entities = list(self.entity_connections[entity])
            common_predicates = defaultdict(int)
            
            for connected in connected_entities:
                if connected in self.facts_by_entity:
                    for pred, obj, fact in self.facts_by_entity[connected]:
                        common_predicates[pred] += 1
            
            # Generiere These für häufige Eigenschaften
            for pred, count in common_predicates.items():
                if count >= 3:
                    thesis = Thesis(
                        statement=f"Entities connected to {entity} often have {pred}",
                        supporting_facts=[f"Found {count} connected entities with {pred}"],
                        confidence=min(count / len(connected_entities), 0.7),
                        category="network",
                        created_at=datetime.now().isoformat()
                    )
                    theses.append(thesis)
                    break
        
        return theses
    
    def generate_contradiction_theses(self) -> List[Thesis]:
        """Generiere Thesen über mögliche Widersprüche"""
        theses = []
        
        # Suche nach möglichen Widersprüchen
        # Z.B. Entity hat sowohl positive als auch negative Eigenschaften
        opposite_predicates = [
            ('Hot', 'Cold'),
            ('Fast', 'Slow'),
            ('Large', 'Small'),
            ('High', 'Low'),
            ('Strong', 'Weak')
        ]
        
        for pos_pred, neg_pred in opposite_predicates:
            pos_facts = self.facts_by_predicate.get(pos_pred, [])
            neg_facts = self.facts_by_predicate.get(neg_pred, [])
            
            if pos_facts and neg_facts:
                # Finde Entities mit beiden Eigenschaften
                pos_entities = set(subject for subject, obj, fact in pos_facts)
                neg_entities = set(subject for subject, obj, fact in neg_facts)
                
                contradiction_entities = pos_entities.intersection(neg_entities)
                if contradiction_entities:
                    thesis = Thesis(
                        statement=f"Some entities exhibit both {pos_pred.lower()} and {neg_pred.lower()} properties",
                        supporting_facts=[f"Found {len(contradiction_entities)} entities with both properties"],
                        confidence=0.6,  # Moderate confidence für Widersprüche
                        category="contradiction",
                        created_at=datetime.now().isoformat()
                    )
                    theses.append(thesis)
        
        return theses[:2]  # Max 2 Widerspruchs-Thesen
    
    def save_theses_to_db(self, theses: List[Thesis]) -> int:
        """Speichere Thesen in der Datenbank"""
        saved_count = 0
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Erstelle Tabelle für Thesen falls nicht vorhanden
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS theses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    statement TEXT,
                    supporting_facts TEXT,
                    confidence REAL,
                    category TEXT,
                    status TEXT DEFAULT 'pending',
                    created_at TEXT
                )
            """)
            
            # Füge Thesen hinzu
            for thesis in theses:
                try:
                    cursor.execute("""
                        INSERT INTO theses (statement, supporting_facts, confidence, category, status, created_at)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        thesis.statement,
                        '; '.join(thesis.supporting_facts),
                        thesis.confidence,
                        thesis.category,
                        thesis.status,
                        thesis.created_at
                    ))
                    saved_count += 1
                except sqlite3.IntegrityError:
                    continue  # Duplikat
            
            conn.commit()
            conn.close()
            
            print(f"[THESIS] Saved {saved_count} theses to database")
            
        except Exception as e:
            print(f"[ERROR] Failed to save theses: {e}")
        
        return saved_count
    
    def run(self, duration_minutes: float = 2.0):
        """Hauptschleife für Thesen-Generierung"""
        print(f"[START] Thesis Generator - {duration_minutes} minutes")
        print("[INFO] Generating logical theses from Aethelred facts")
        
        start_time = time.time()
        end_time = start_time + (duration_minutes * 60)
        total_theses = 0
        round_num = 0
        
        while time.time() < end_time:
            round_num += 1
            print(f"\n=== Thesis Generation Round {round_num} ===")
            
            # Lade neueste Fakten
            if not self.load_recent_facts(500):
                print("[SKIP] Fact loading failed")
                time.sleep(10)
                continue
            
            # Generiere verschiedene Thesen-Typen
            all_theses = []
            
            # Korrelations-Thesen
            correlation_theses = self.generate_correlation_theses()
            all_theses.extend(correlation_theses)
            print(f"[CORRELATION] Generated {len(correlation_theses)} correlation theses")
            
            # Hierarchische Thesen
            hierarchical_theses = self.generate_hierarchical_theses()
            all_theses.extend(hierarchical_theses)
            print(f"[HIERARCHICAL] Generated {len(hierarchical_theses)} hierarchical theses")
            
            # Kausale Thesen
            causal_theses = self.generate_causal_theses()
            all_theses.extend(causal_theses)
            print(f"[CAUSAL] Generated {len(causal_theses)} causal theses")
            
            # Netzwerk-Thesen
            network_theses = self.generate_network_theses()
            all_theses.extend(network_theses)
            print(f"[NETWORK] Generated {len(network_theses)} network theses")
            
            # Widerspruchs-Thesen
            contradiction_theses = self.generate_contradiction_theses()
            all_theses.extend(contradiction_theses)
            print(f"[CONTRADICTION] Generated {len(contradiction_theses)} contradiction theses")
            
            # Speichere Thesen
            saved_count = self.save_theses_to_db(all_theses)
            total_theses += saved_count
            
            # Zeige Beispiele
            for i, thesis in enumerate(all_theses[:3]):
                print(f"[EXAMPLE {i+1}] {thesis.statement} (confidence: {thesis.confidence:.2f})")
            
            print(f"[STATS] Generated {len(all_theses)} theses, saved {saved_count}, Total: {total_theses}")
            
            # Pause zwischen Runden
            if time.time() < end_time:
                time.sleep(20)
        
        print(f"\n[DONE] Generated {total_theses} theses in {round_num} rounds")
        print("[INFO] Theses are ready for LLM proof validation")

def main():
    parser = argparse.ArgumentParser(description="Thesis Generator Engine")
    parser.add_argument("-d", "--duration", type=float, default=0.1, help="Duration in minutes")
    parser.add_argument("-p", "--port", type=int, default=5002, help="Port (unused)")
    args = parser.parse_args()
    
    generator = ThesisGenerator()
    generator.run(duration_minutes=args.duration)

if __name__ == "__main__":
    main()
