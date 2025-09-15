#!/usr/bin/env python3
"""
Batch Query Optimizer für HAK_GAL_HEXAGONAL
Ersetzt N+1-Abfragen durch effiziente Batch-basierte Datenabrufe
"""

import sqlite3
import time
from typing import List, Dict, Any, Tuple

class BatchQueryOptimizer:
    """Optimiert Datenbankabfragen durch Batch-Processing"""
    
    def __init__(self, db_path: str = 'hexagonal_kb.db'):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row  # Ermöglicht dict-ähnlichen Zugriff
    
    def batch_get_facts_by_predicates(self, predicates: List[str]) -> Dict[str, List[Dict]]:
        """Holt alle Fakten für mehrere Prädikate in einer Abfrage"""
        if not predicates:
            return {}
        
        placeholders = ','.join(['?' for _ in predicates])
        query = f"""
        SELECT predicate, statement, subject, object, confidence, source
        FROM facts 
        WHERE predicate IN ({placeholders})
        ORDER BY predicate, confidence DESC
        """
        
        start_time = time.time()
        cursor = self.conn.cursor()
        cursor.execute(query, predicates)
        results = cursor.fetchall()
        end_time = time.time()
        
        # Gruppiere Ergebnisse nach Prädikat
        grouped_results = {}
        for row in results:
            predicate = row['predicate']
            if predicate not in grouped_results:
                grouped_results[predicate] = []
            grouped_results[predicate].append(dict(row))
        
        print(f'Batch-Abfrage für {len(predicates)} Prädikate: {len(results)} Ergebnisse in {(end_time - start_time)*1000:.2f}ms')
        return grouped_results
    
    def batch_get_facts_by_sources(self, sources: List[str]) -> Dict[str, List[Dict]]:
        """Holt alle Fakten für mehrere Quellen in einer Abfrage"""
        if not sources:
            return {}
        
        placeholders = ','.join(['?' for _ in sources])
        query = f"""
        SELECT source, statement, predicate, subject, object, confidence
        FROM facts 
        WHERE source IN ({placeholders})
        ORDER BY source, confidence DESC
        """
        
        start_time = time.time()
        cursor = self.conn.cursor()
        cursor.execute(query, sources)
        results = cursor.fetchall()
        end_time = time.time()
        
        # Gruppiere Ergebnisse nach Quelle
        grouped_results = {}
        for row in results:
            source = row['source']
            if source not in grouped_results:
                grouped_results[source] = []
            grouped_results[source].append(dict(row))
        
        print(f'Batch-Abfrage für {len(sources)} Quellen: {len(results)} Ergebnisse in {(end_time - start_time)*1000:.2f}ms')
        return grouped_results
    
    def batch_get_facts_extended_by_types(self, fact_types: List[str]) -> Dict[str, List[Dict]]:
        """Holt alle erweiterten Fakten für mehrere Typen in einer Abfrage"""
        if not fact_types:
            return {}
        
        placeholders = ','.join(['?' for _ in fact_types])
        query = f"""
        SELECT fact_type, statement, predicate, domain, complexity, confidence, source, created_at
        FROM facts_extended 
        WHERE fact_type IN ({placeholders})
        ORDER BY fact_type, complexity DESC, confidence DESC
        """
        
        start_time = time.time()
        cursor = self.conn.cursor()
        cursor.execute(query, fact_types)
        results = cursor.fetchall()
        end_time = time.time()
        
        # Gruppiere Ergebnisse nach Typ
        grouped_results = {}
        for row in results:
            fact_type = row['fact_type']
            if fact_type not in grouped_results:
                grouped_results[fact_type] = []
            grouped_results[fact_type].append(dict(row))
        
        print(f'Batch-Abfrage für {len(fact_types)} Fact-Typen: {len(results)} Ergebnisse in {(end_time - start_time)*1000:.2f}ms')
        return grouped_results
    
    def batch_get_tool_performance(self, tool_names: List[str], days_back: int = 7) -> Dict[str, List[Dict]]:
        """Holt Performance-Daten für mehrere Tools in einer Abfrage"""
        if not tool_names:
            return {}
        
        placeholders = ','.join(['?' for _ in tool_names])
        query = f"""
        SELECT tool_name, execution_time, success, confidence_score, timestamp, task_description
        FROM tool_performance 
        WHERE tool_name IN ({placeholders})
        AND timestamp > datetime('now', '-{days_back} days')
        ORDER BY tool_name, timestamp DESC
        """
        
        start_time = time.time()
        cursor = self.conn.cursor()
        cursor.execute(query, tool_names)
        results = cursor.fetchall()
        end_time = time.time()
        
        # Gruppiere Ergebnisse nach Tool
        grouped_results = {}
        for row in results:
            tool_name = row['tool_name']
            if tool_name not in grouped_results:
                grouped_results[tool_name] = []
            grouped_results[tool_name].append(dict(row))
        
        print(f'Batch-Abfrage für {len(tool_names)} Tools: {len(results)} Ergebnisse in {(end_time - start_time)*1000:.2f}ms')
        return grouped_results
    
    def get_most_common_predicates(self, limit: int = 10) -> List[Tuple[str, int]]:
        """Holt die häufigsten Prädikate für Batch-Optimierung"""
        query = """
        SELECT predicate, COUNT(*) as count
        FROM facts 
        WHERE predicate IS NOT NULL
        GROUP BY predicate 
        ORDER BY count DESC 
        LIMIT ?
        """
        
        cursor = self.conn.cursor()
        cursor.execute(query, (limit,))
        return cursor.fetchall()
    
    def get_most_common_sources(self, limit: int = 10) -> List[Tuple[str, int]]:
        """Holt die häufigsten Quellen für Batch-Optimierung"""
        query = """
        SELECT source, COUNT(*) as count
        FROM facts 
        WHERE source IS NOT NULL
        GROUP BY source 
        ORDER BY count DESC 
        LIMIT ?
        """
        
        cursor = self.conn.cursor()
        cursor.execute(query, (limit,))
        return cursor.fetchall()
    
    def close(self):
        """Schließt die Datenbankverbindung"""
        self.conn.close()

def performance_comparison():
    """Vergleicht N+1-Abfragen vs. Batch-Abfragen"""
    
    print('=== Performance Comparison: N+1 vs Batch Queries ===')
    print()
    
    optimizer = BatchQueryOptimizer()
    
    # Hole häufigste Prädikate und Quellen
    common_predicates = [p[0] for p in optimizer.get_most_common_predicates(5)]
    common_sources = [s[0] for s in optimizer.get_most_common_sources(5)]
    
    print(f'Häufigste Prädikate: {common_predicates}')
    print(f'Häufigste Quellen: {common_sources}')
    print()
    
    # Test 1: N+1-Abfragen für Prädikate
    print('1. N+1-Abfragen für Prädikate:')
    n1_start = time.time()
    n1_results = {}
    for predicate in common_predicates:
        cursor = optimizer.conn.cursor()
        cursor.execute('SELECT * FROM facts WHERE predicate = ?', (predicate,))
        n1_results[predicate] = cursor.fetchall()
    n1_end = time.time()
    n1_time = (n1_end - n1_start) * 1000
    print(f'   Zeit: {n1_time:.2f}ms für {len(common_predicates)} Abfragen')
    
    # Test 2: Batch-Abfrage für Prädikate
    print('2. Batch-Abfrage für Prädikate:')
    batch_results = optimizer.batch_get_facts_by_predicates(common_predicates)
    
    # Test 3: N+1-Abfragen für Quellen
    print('3. N+1-Abfragen für Quellen:')
    n1_start = time.time()
    n1_source_results = {}
    for source in common_sources:
        cursor = optimizer.conn.cursor()
        cursor.execute('SELECT * FROM facts WHERE source = ?', (source,))
        n1_source_results[source] = cursor.fetchall()
    n1_end = time.time()
    n1_source_time = (n1_end - n1_start) * 1000
    print(f'   Zeit: {n1_source_time:.2f}ms für {len(common_sources)} Abfragen')
    
    # Test 4: Batch-Abfrage für Quellen
    print('4. Batch-Abfrage für Quellen:')
    batch_source_results = optimizer.batch_get_facts_by_sources(common_sources)
    
    # Berechne Performance-Verbesserung
    print()
    print('=== Performance-Verbesserung ===')
    print(f'Prädikat-Abfragen: {n1_time:.2f}ms → Batch (siehe oben)')
    print(f'Quellen-Abfragen: {n1_source_time:.2f}ms → Batch (siehe oben)')
    
    optimizer.close()

if __name__ == '__main__':
    performance_comparison()




