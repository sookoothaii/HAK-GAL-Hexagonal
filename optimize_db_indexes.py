#!/usr/bin/env python3
"""
SQLite Index Optimization für HAK_GAL_HEXAGONAL
Erstellt optimierte Indizes basierend auf der Performance-Analyse
"""

import sqlite3
import time

def create_optimized_indexes():
    """Erstellt optimierte Indizes für bessere Performance"""
    
    print('=== SQLite Index Optimization ===')
    print()
    
    # Verbindung zur Datenbank
    conn = sqlite3.connect('hexagonal_kb.db')
    cursor = conn.cursor()
    
    # Liste der zu erstellenden Indizes
    indexes_to_create = [
        # Basis-Indizes für häufige Abfragen
        ("idx_facts_source", "CREATE INDEX IF NOT EXISTS idx_facts_source ON facts(source)"),
        ("idx_facts_confidence", "CREATE INDEX IF NOT EXISTS idx_facts_confidence ON facts(confidence)"),
        
        # Zusammengesetzte Indizes für komplexe Abfragen
        ("idx_facts_predicate_source", "CREATE INDEX IF NOT EXISTS idx_facts_predicate_source ON facts(predicate, source)"),
        ("idx_facts_predicate_confidence", "CREATE INDEX IF NOT EXISTS idx_facts_predicate_confidence ON facts(predicate, confidence)"),
        
        # Indizes für facts_extended (wichtigste Tabelle)
        ("idx_facts_ext_source", "CREATE INDEX IF NOT EXISTS idx_facts_ext_source ON facts_extended(source)"),
        ("idx_facts_ext_created_at", "CREATE INDEX IF NOT EXISTS idx_facts_ext_created_at ON facts_extended(created_at)"),
        ("idx_facts_ext_predicate_source", "CREATE INDEX IF NOT EXISTS idx_facts_ext_predicate_source ON facts_extended(predicate, source)"),
        ("idx_facts_ext_type_domain", "CREATE INDEX IF NOT EXISTS idx_facts_ext_type_domain ON facts_extended(fact_type, domain)"),
        
        # Indizes für tool_performance (Monitoring)
        ("idx_tool_perf_tool_name", "CREATE INDEX IF NOT EXISTS idx_tool_perf_tool_name ON tool_performance(tool_name)"),
        ("idx_tool_perf_timestamp", "CREATE INDEX IF NOT EXISTS idx_tool_perf_timestamp ON tool_performance(timestamp)"),
        ("idx_tool_perf_success", "CREATE INDEX IF NOT EXISTS idx_tool_perf_success ON tool_performance(success)"),
        
        # Indizes für fact_relations
        ("idx_fact_relations_type", "CREATE INDEX IF NOT EXISTS idx_fact_relations_type ON fact_relations(relation_type)"),
        ("idx_fact_relations_created_at", "CREATE INDEX IF NOT EXISTS idx_fact_relations_created_at ON fact_relations(created_at)"),
        
        # Indizes für discovered_topics
        ("idx_discovered_topics_type", "CREATE INDEX IF NOT EXISTS idx_discovered_topics_type ON discovered_topics(topic_type)"),
        ("idx_discovered_topics_explored", "CREATE INDEX IF NOT EXISTS idx_discovered_topics_explored ON discovered_topics(explored)"),
    ]
    
    print(f'Erstelle {len(indexes_to_create)} optimierte Indizes...')
    print()
    
    created_count = 0
    skipped_count = 0
    
    for idx_name, idx_sql in indexes_to_create:
        try:
            # Prüfe ob Index bereits existiert
            cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND name=?", (idx_name,))
            if cursor.fetchone():
                print(f'  ⏭️  {idx_name} - bereits vorhanden')
                skipped_count += 1
            else:
                start_time = time.time()
                cursor.execute(idx_sql)
                end_time = time.time()
                print(f'  ✅ {idx_name} - erstellt in {(end_time - start_time)*1000:.2f}ms')
                created_count += 1
        except Exception as e:
            print(f'  ❌ {idx_name} - Fehler: {e}')
    
    # Committe die Änderungen
    conn.commit()
    
    print()
    print(f'Index-Erstellung abgeschlossen:')
    print(f'  - {created_count} neue Indizes erstellt')
    print(f'  - {skipped_count} Indizes bereits vorhanden')
    
    # Analysiere die Datenbank nach der Optimierung
    print()
    print('=== Post-Optimization Analysis ===')
    
    # Teste Performance-Verbesserungen
    print('Performance-Tests nach Index-Optimierung:')
    
    # Test 1: Prädikat-Suche
    start_time = time.time()
    cursor.execute('SELECT COUNT(*) FROM facts WHERE predicate = ?', ('is_a',))
    result = cursor.fetchone()[0]
    end_time = time.time()
    print(f'  - Prädikat-Suche: {result} Ergebnisse in {(end_time - start_time)*1000:.2f}ms')
    
    # Test 2: Quellen-Suche
    start_time = time.time()
    cursor.execute('SELECT COUNT(*) FROM facts WHERE source = ?', ('system',))
    result = cursor.fetchone()[0]
    end_time = time.time()
    print(f'  - Quellen-Suche: {result} Ergebnisse in {(end_time - start_time)*1000:.2f}ms')
    
    # Test 3: Zusammengesetzte Abfrage
    start_time = time.time()
    cursor.execute('SELECT COUNT(*) FROM facts WHERE predicate = ? AND source = ?', ('is_a', 'system'))
    result = cursor.fetchone()[0]
    end_time = time.time()
    print(f'  - Zusammengesetzte Abfrage: {result} Ergebnisse in {(end_time - start_time)*1000:.2f}ms')
    
    # Test 4: facts_extended Abfrage
    start_time = time.time()
    cursor.execute('SELECT COUNT(*) FROM facts_extended WHERE fact_type = ?', ('relation',))
    result = cursor.fetchone()[0]
    end_time = time.time()
    print(f'  - facts_extended Abfrage: {result} Ergebnisse in {(end_time - start_time)*1000:.2f}ms')
    
    # Zeige alle Indizes
    print()
    print('Alle verfügbaren Indizes:')
    cursor.execute("SELECT name FROM sqlite_master WHERE type='index' ORDER BY name")
    indexes = cursor.fetchall()
    for idx in indexes:
        print(f'  - {idx[0]}')
    
    conn.close()
    print()
    print('Optimization complete!')

if __name__ == '__main__':
    create_optimized_indexes()




