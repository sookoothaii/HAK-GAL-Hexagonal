#!/usr/bin/env python3
"""
SQLite Performance Analysis für HAK_GAL_HEXAGONAL
Analysiert die aktuelle Datenbankstruktur und identifiziert Optimierungsmöglichkeiten
"""

import sqlite3
import time
from collections import Counter

def analyze_database():
    """Analysiert die SQLite-Datenbank und identifiziert Performance-Bottlenecks"""
    
    print('=== SQLite Performance Analysis ===')
    print()
    
    # Verbindung zur Datenbank
    conn = sqlite3.connect('hexagonal_kb.db')
    cursor = conn.cursor()
    
    # 1. Tabellenstruktur analysieren
    print('1. Tabellenstruktur:')
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    for table in tables:
        print(f'  - {table[0]}')
        cursor.execute(f'PRAGMA table_info({table[0]})')
        columns = cursor.fetchall()
        for col in columns:
            print(f'    * {col[1]} ({col[2]})')
    
    print()
    
    # 2. Aktuelle Indizes analysieren
    print('2. Aktuelle Indizes:')
    cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='index'")
    indexes = cursor.fetchall()
    for idx in indexes:
        print(f'  - {idx[0]}: {idx[1]}')
    
    print()
    
    # 3. Datenbankgröße und Statistiken
    print('3. Datenbankstatistiken:')
    cursor.execute('SELECT COUNT(*) FROM facts')
    fact_count = cursor.fetchone()[0]
    print(f'  - Fakten: {fact_count:,}')
    
    # Prüfe ob audit_log Tabelle existiert
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='audit_log'")
    if cursor.fetchone():
        cursor.execute('SELECT COUNT(*) FROM audit_log')
        audit_count = cursor.fetchone()[0]
        print(f'  - Audit-Einträge: {audit_count:,}')
    else:
        print('  - Audit-Einträge: Tabelle nicht vorhanden')
    
    # 4. Häufige Abfragefelder identifizieren
    print()
    print('4. Häufige Abfragefelder (Sample):')
    cursor.execute('SELECT DISTINCT predicate FROM facts LIMIT 10')
    predicates = cursor.fetchall()
    print('  - Prädikate:', [p[0] for p in predicates])
    
    cursor.execute('SELECT DISTINCT source FROM facts LIMIT 10')
    sources = cursor.fetchall()
    print('  - Quellen:', [s[0] for s in sources])
    
    # 5. Performance-Test: Häufige Abfragen
    print()
    print('5. Performance-Test häufiger Abfragen:')
    
    # Test 1: Suche nach Prädikat
    start_time = time.time()
    cursor.execute('SELECT COUNT(*) FROM facts WHERE predicate = ?', ('is_a',))
    result = cursor.fetchone()[0]
    end_time = time.time()
    print(f'  - Prädikat-Suche: {result} Ergebnisse in {(end_time - start_time)*1000:.2f}ms')
    
    # Test 2: Suche nach Quelle
    start_time = time.time()
    cursor.execute('SELECT COUNT(*) FROM facts WHERE source = ?', ('manual',))
    result = cursor.fetchone()[0]
    end_time = time.time()
    print(f'  - Quellen-Suche: {result} Ergebnisse in {(end_time - start_time)*1000:.2f}ms')
    
    # Test 3: Zeitbasierte Abfrage (nur wenn Spalte existiert)
    cursor.execute("PRAGMA table_info(facts)")
    columns = [col[1] for col in cursor.fetchall()]
    if 'created_at' in columns:
        start_time = time.time()
        cursor.execute('SELECT COUNT(*) FROM facts WHERE created_at > datetime("now", "-7 days")')
        result = cursor.fetchone()[0]
        end_time = time.time()
        print(f'  - Zeitbasierte Suche: {result} Ergebnisse in {(end_time - start_time)*1000:.2f}ms')
    else:
        print('  - Zeitbasierte Suche: created_at Spalte nicht vorhanden')
    
    # 6. Empfohlene Indizes
    print()
    print('6. Empfohlene Indizes für Performance-Optimierung:')
    print('  - CREATE INDEX idx_facts_predicate ON facts(predicate);')
    print('  - CREATE INDEX idx_facts_source ON facts(source);')
    print('  - CREATE INDEX idx_facts_created_at ON facts(created_at);')
    print('  - CREATE INDEX idx_facts_predicate_source ON facts(predicate, source);')
    print('  - CREATE INDEX idx_audit_log_timestamp ON audit_log(timestamp);')
    
    conn.close()
    print()
    print('Analysis complete!')

if __name__ == '__main__':
    analyze_database()
