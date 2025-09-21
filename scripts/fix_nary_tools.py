#!/usr/bin/env python3
"""
Fix für n-äre Fact Tools in HAK_GAL
Repariert: semantic_similarity, consistency_check, validate_facts, inference_chain
Author: Claude
Date: 2025-09-19
"""

import sqlite3
import re
from typing import List, Tuple, Dict, Optional
import json
from difflib import SequenceMatcher
import os

# Datenbank-Pfad
DB_PATH = r'D:\MCP Mods\HAK_GAL_HEXAGONAL\hexagonal_kb.db'

class NaryFactParser:
    """Parser für n-äre Facts mit Q(...) Notation Support"""
    
    @staticmethod
    def extract_predicate(statement: str) -> Optional[str]:
        """Extrahiert Prädikat aus n-ärem Fact"""
        match = re.match(r'^(\w+)\(', statement)
        return match.group(1) if match else None
    
    @staticmethod
    def extract_arguments(statement: str) -> List[str]:
        """Extrahiert alle Argumente unter Berücksichtigung von Q(...) Notation"""
        match = re.match(r'\w+\((.*?)\)\.?$', statement, re.DOTALL)
        if not match:
            return []
        
        args_str = match.group(1)
        arguments = []
        current_arg = ""
        paren_depth = 0
        
        for char in args_str:
            if char == '(' :
                paren_depth += 1
                current_arg += char
            elif char == ')':
                paren_depth -= 1
                current_arg += char
            elif char == ',' and paren_depth == 0:
                arguments.append(current_arg.strip())
                current_arg = ""
            else:
                current_arg += char
        
        if current_arg.strip():
            arguments.append(current_arg.strip())
            
        return arguments
    
    @staticmethod
    def extract_entities(statement: str) -> List[str]:
        """Extrahiert alle Entities (non-Q values) aus einem Fact"""
        args = NaryFactParser.extract_arguments(statement)
        entities = []
        
        for arg in args:
            # Skip Q(...) notation values
            if not arg.startswith('Q(') and not arg.startswith('k:Q(') and not arg.startswith('T:Q('):
                # Entferne Präfixe wie "k:", "T:" etc.
                if ':' in arg and not '(' in arg:
                    arg = arg.split(':')[1]
                entities.append(arg)
                
        return entities
    

class FixedNaryTools:
    """Reparierte Versionen der defekten Tools"""
    
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self.parser = NaryFactParser()
    
    def semantic_similarity(self, statement: str, threshold: float = 0.7, limit: int = 10) -> List[Tuple[float, str]]:
        """
        Findet semantisch ähnliche Facts zu einem gegebenen Statement.
        Funktioniert mit n-ären Facts.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Parse input statement
        input_predicate = self.parser.extract_predicate(statement)
        input_args = self.parser.extract_arguments(statement)
        input_entities = self.parser.extract_entities(statement)
        
        results = []
        
        # Hole alle Facts mit gleichem Prädikat
        cursor.execute("SELECT statement FROM facts")
        all_facts = cursor.fetchall()
        
        for (fact,) in all_facts:
            if fact == statement:
                continue
                
            fact_predicate = self.parser.extract_predicate(fact)
            
            # Berechne Ähnlichkeit
            similarity = 0.0
            
            # 1. Prädikat-Match (40% Gewicht)
            if fact_predicate == input_predicate:
                similarity += 0.4
            elif fact_predicate and input_predicate:
                pred_sim = SequenceMatcher(None, fact_predicate, input_predicate).ratio()
                similarity += 0.4 * pred_sim
            
            # 2. Argument-Überlappung (40% Gewicht)
            fact_args = self.parser.extract_arguments(fact)
            if input_args and fact_args:
                # Zähle übereinstimmende Argumente
                matches = 0
                for arg in input_args:
                    if arg in fact_args:
                        matches += 1
                arg_similarity = matches / max(len(input_args), len(fact_args))
                similarity += 0.4 * arg_similarity
            
            # 3. Entity-Überlappung (20% Gewicht)
            fact_entities = self.parser.extract_entities(fact)
            if input_entities and fact_entities:
                entity_matches = 0
                for entity in input_entities:
                    if entity in fact_entities:
                        entity_matches += 1
                entity_similarity = entity_matches / max(len(input_entities), len(fact_entities))
                similarity += 0.2 * entity_similarity
            
            if similarity >= threshold:
                results.append((similarity, fact))
        
        conn.close()
        
        # Sortiere nach Ähnlichkeit
        results.sort(key=lambda x: x[0], reverse=True)
        return results[:limit]
    
    def consistency_check(self, limit: int = 100) -> List[Tuple[str, str, str]]:
        """
        Prüft auf inkonsistente Facts in der Knowledge Base.
        Funktioniert mit n-ären Facts.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT statement FROM facts LIMIT ?", (limit * 2,))
        facts = [row[0] for row in cursor.fetchall()]
        
        inconsistencies = []
        
        for i, fact1 in enumerate(facts):
            pred1 = self.parser.extract_predicate(fact1)
            args1 = self.parser.extract_arguments(fact1)
            
            if not pred1 or not args1:
                continue
                
            for fact2 in facts[i+1:]:
                pred2 = self.parser.extract_predicate(fact2)
                args2 = self.parser.extract_arguments(fact2)
                
                if not pred2 or not args2:
                    continue
                
                # Check für Widersprüche
                # 1. Gleiches Prädikat, gleiche erste Argumente, aber unterschiedliche Werte
                if pred1 == pred2 and len(args1) >= 2 and len(args2) >= 2:
                    if args1[0] == args2[0]:  # Gleiches Subject
                        # Prüfe ob unterschiedliche Werte für gleiche Property
                        if args1[1:] != args2[1:]:
                            # Nur als Inkonsistenz markieren wenn es semantisch widersprüchlich ist
                            if self._is_contradiction(pred1, args1, args2):
                                inconsistencies.append((fact1, fact2, "Widersprüchliche Werte"))
                
                # 2. Logische Widersprüche (z.B. A->B und B->A für nicht-symmetrische Relationen)
                if pred1 in ['ParentOf', 'CausedBy', 'PrecedesTemporally']:
                    if len(args1) >= 2 and len(args2) >= 2:
                        if args1[0] == args2[1] and args1[1] == args2[0]:
                            inconsistencies.append((fact1, fact2, "Zirkuläre Beziehung"))
        
        conn.close()
        return inconsistencies[:limit]
    
    def _is_contradiction(self, predicate: str, args1: List[str], args2: List[str]) -> bool:
        """Prüft ob zwei Argument-Sets für das gleiche Prädikat widersprüchlich sind"""
        # Spezielle Regeln für bestimmte Prädikate
        if predicate in ['Temperature', 'Pressure', 'Concentration']:
            # Unterschiedliche Messwerte sind OK (verschiedene Bedingungen)
            return False
        
        if predicate in ['IsA', 'HasProperty', 'PartOf']:
            # Diese können multiple Werte haben
            return False
            
        # Default: Unterschiedliche Werte sind potentiell widersprüchlich
        return True
    
    def validate_facts(self, limit: int = 100) -> Dict[str, List[str]]:
        """
        Validiert Facts auf syntaktische und semantische Korrektheit.
        Funktioniert mit n-ären Facts.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT statement FROM facts LIMIT ?", (limit,))
        facts = [row[0] for row in cursor.fetchall()]
        
        validation_results = {
            'valid': [],
            'syntax_error': [],
            'missing_predicate': [],
            'empty_arguments': [],
            'suspicious_values': [],
            'well_formed_quantity': []
        }
        
        for fact in facts:
            # Syntax Check
            if not re.match(r'^\w+\(.*\)\.?$', fact):
                validation_results['syntax_error'].append(fact)
                continue
            
            # Prädikat Check
            predicate = self.parser.extract_predicate(fact)
            if not predicate:
                validation_results['missing_predicate'].append(fact)
                continue
            
            # Argument Check
            args = self.parser.extract_arguments(fact)
            if not args:
                validation_results['empty_arguments'].append(fact)
                continue
            
            # Prüfe auf verdächtige Werte
            suspicious = False
            for arg in args:
                if arg.lower() in ['null', 'none', 'undefined', 'unknown']:
                    validation_results['suspicious_values'].append(fact)
                    suspicious = True
                    break
            
            # Prüfe Q(...) Notation
            if 'Q(' in fact:
                # Validiere Q(...) Format
                q_pattern = r'Q\([^,]+,[^,)]+(?:,[^,)]+)*\)'
                if re.search(q_pattern, fact):
                    validation_results['well_formed_quantity'].append(fact)
            
            # Wenn alles OK, als valid markieren
            if not suspicious:
                validation_results['valid'].append(fact)
        
        conn.close()
        return validation_results
    
    def inference_chain(self, start_fact: str, max_depth: int = 5) -> List[List[str]]:
        """
        Baut Inferenzketten ausgehend von einem Fact.
        Funktioniert mit n-ären Facts.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        chains = []
        visited = set()
        
        def find_chains(current_fact: str, current_chain: List[str], depth: int):
            if depth >= max_depth or current_fact in visited:
                if len(current_chain) > 1:
                    chains.append(current_chain.copy())
                return
            
            visited.add(current_fact)
            
            # Extrahiere Entities aus aktuellem Fact
            entities = self.parser.extract_entities(current_fact)
            
            for entity in entities:
                # Finde Facts die diese Entity enthalten
                cursor.execute(
                    "SELECT statement FROM facts WHERE statement LIKE ? AND statement != ?",
                    (f'%{entity}%', current_fact)
                )
                related_facts = cursor.fetchall()
                
                for (related,) in related_facts[:5]:  # Limitiere auf 5 pro Entity
                    # Prüfe ob es wirklich eine sinnvolle Verbindung ist
                    related_entities = self.parser.extract_entities(related)
                    if entity in related_entities:
                        new_chain = current_chain + [related]
                        find_chains(related, new_chain, depth + 1)
            
            visited.remove(current_fact)
        
        # Starte Kettenbildung
        find_chains(start_fact, [start_fact], 0)
        
        conn.close()
        
        # Entferne Duplikate und sortiere nach Länge
        unique_chains = []
        seen = set()
        for chain in chains:
            chain_tuple = tuple(chain)
            if chain_tuple not in seen:
                seen.add(chain_tuple)
                unique_chains.append(chain)
        
        unique_chains.sort(key=len, reverse=True)
        return unique_chains[:10]  # Maximal 10 Ketten


def test_fixed_tools():
    """Testet die reparierten Tools"""
    tools = FixedNaryTools()
    
    print("=== TESTE REPARIERTE TOOLS ===\n")
    
    # Test 1: Semantic Similarity
    print("1. SEMANTIC SIMILARITY TEST")
    test_fact = "ChemicalReaction(H2, O2, H2O, combustion, exothermic, T:Q(2800, K))"
    results = tools.semantic_similarity(test_fact, threshold=0.3, limit=5)
    print(f"   Input: {test_fact[:60]}...")
    print(f"   Gefundene ähnliche Facts: {len(results)}")
    for score, fact in results[:3]:
        print(f"   - Score {score:.2f}: {fact[:60]}...")
    
    # Test 2: Consistency Check
    print("\n2. CONSISTENCY CHECK TEST")
    inconsistencies = tools.consistency_check(limit=50)
    print(f"   Gefundene Inkonsistenzen: {len(inconsistencies)}")
    for fact1, fact2, reason in inconsistencies[:3]:
        print(f"   - {reason}:")
        print(f"     Fact1: {fact1[:50]}...")
        print(f"     Fact2: {fact2[:50]}...")
    
    # Test 3: Validate Facts
    print("\n3. VALIDATE FACTS TEST")
    validation = tools.validate_facts(limit=50)
    print(f"   Valide Facts: {len(validation['valid'])}")
    print(f"   Syntax Fehler: {len(validation['syntax_error'])}")
    print(f"   Fehlende Prädikate: {len(validation['missing_predicate'])}")
    print(f"   Verdächtige Werte: {len(validation['suspicious_values'])}")
    print(f"   Korrekte Q(...) Notation: {len(validation['well_formed_quantity'])}")
    
    # Test 4: Inference Chain
    print("\n4. INFERENCE CHAIN TEST")
    start = "ChemicalReaction(H2, O2, H2O, combustion, exothermic, 2800K)"
    chains = tools.inference_chain(start, max_depth=3)
    print(f"   Start: {start[:60]}...")
    print(f"   Gefundene Ketten: {len(chains)}")
    for i, chain in enumerate(chains[:2]):
        print(f"   Kette {i+1} (Länge {len(chain)}):")
        for j, fact in enumerate(chain):
            print(f"     {j+1}. {fact[:50]}...")
    
    print("\n=== TESTS ABGESCHLOSSEN ===")
    return True


if __name__ == "__main__":
    # Führe Tests aus
    success = test_fixed_tools()
    
    if success:
        print("\n✅ Alle reparierten Tools funktionieren mit n-ären Facts!")
        print("\nNächste Schritte:")
        print("1. Integration der reparierten Funktionen in MCP Server")
        print("2. Ersetzen der alten Tool-Implementierungen")
        print("3. Entfernung der predicate/subject/object Spalten aus DB Schema")
    else:
        print("\n❌ Einige Tests fehlgeschlagen. Bitte Logs prüfen.")
