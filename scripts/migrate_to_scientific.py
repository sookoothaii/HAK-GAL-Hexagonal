#!/usr/bin/env python3
"""
MIGRATION: Bereinigung und Neustart mit wissenschaftlichen Fakten
"""

import sqlite3
import datetime
import shutil
from pathlib import Path

def migrate_to_scientific_facts():
    """
    Migriert die Datenbank zu wissenschaftlich validierten Fakten
    """
    
    print("MIGRATION ZU WISSENSCHAFTLICHEN FAKTEN")
    print("="*60)
    
    # 1. BACKUP
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"hexagonal_kb_BEFORE_MIGRATION_{timestamp}.db"
    print(f"1. Erstelle Backup: {backup_file}")
    shutil.copy2("hexagonal_kb.db", backup_file)
    
    conn = sqlite3.connect("hexagonal_kb.db")
    cursor = conn.cursor()
    
    # 2. ANALYSIERE AKTUELLEN ZUSTAND
    cursor.execute("SELECT COUNT(*) FROM facts")
    total_before = cursor.fetchone()[0]
    print(f"2. Fakten vor Migration: {total_before:,}")
    
    # 3. RETTE WISSENSCHAFTLICH KORREKTE FAKTEN
    print("\n3. Identifiziere wissenschaftlich korrekte Fakten...")
    
    # Erstelle temporäre Tabelle für gute Fakten
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS facts_validated (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            statement TEXT UNIQUE NOT NULL,
            confidence REAL DEFAULT 1.0,
            validated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            domain TEXT,
            argument_count INTEGER,
            predicate TEXT
        )
    """)
    
    # Rette definitiv korrekte Fakten
    good_patterns = [
        "ConsistsOf(atom, proton, neutron, electron)",
        "HasProperty(H2O, polar)",
        "HasProperty(CO2, nonpolar)",
        "HasProperty(NH3, polar)",
        "HasProperty(CH4, nonpolar)",
        "IsTypeOf(NaCl, compound)",
        "ConsistsOf(H2, hydrogen)",
        "HasProperty(electron, charge)",
        "HasProperty(photon, energy)",
        "IsTypeOf(virus, infectious_agent)",
        "IsTypeOf(blockchain, distributed_ledger_technology)",
        "IsTypeOf(electromagnetism, fundamental_force)",
        "HasPart(cell, membrane)",
        "HasPart(cell, cytoplasm)",
        "HasProperty(quantum_particles, uncertainty_principle)"
    ]
    
    saved = 0
    for pattern in good_patterns:
        cursor.execute("""
            INSERT OR IGNORE INTO facts_validated 
            (statement, confidence, domain, argument_count, predicate)
            SELECT 
                statement,
                1.0,
                CASE
                    WHEN statement LIKE '%atom%' OR statement LIKE '%electron%' THEN 'PHYSICS'
                    WHEN statement LIKE '%H2O%' OR statement LIKE '%CO2%' THEN 'CHEMISTRY'
                    WHEN statement LIKE '%cell%' OR statement LIKE '%virus%' THEN 'BIOLOGY'
                    WHEN statement LIKE '%blockchain%' THEN 'COMPUTER_SCIENCE'
                    ELSE 'GENERAL'
                END,
                LENGTH(statement) - LENGTH(REPLACE(statement, ',', '')) + 1,
                SUBSTR(statement, 1, INSTR(statement, '(') - 1)
            FROM facts
            WHERE statement = ?
        """, (pattern,))
        saved += cursor.rowcount
    
    print(f"   Gerettete validierte Fakten: {saved}")
    
    # 4. LÖSCHE ALLE SCHLECHTEN FAKTEN
    print("\n4. Lösche wissenschaftlich falsche Fakten...")
    
    # Liste der Löschungen mit Begründung
    deletions = [
        ("DELETE FROM facts WHERE statement LIKE '%Einstein%' AND statement NOT LIKE '%WasDevelopedBy%'", 
         "Personen-Physics-Mix"),
        ("DELETE FROM facts WHERE statement LIKE '%Newton%' AND statement NOT LIKE '%WasDevelopedBy%'",
         "Personen-Physics-Mix"),
        ("DELETE FROM facts WHERE statement LIKE '%Bohr%' AND statement NOT LIKE '%WasDevelopedBy%'",
         "Personen-Physics-Mix"),
        ("DELETE FROM facts WHERE statement LIKE 'HasProperty(%, complex%'",
         "Vage HasProperty"),
        ("DELETE FROM facts WHERE statement LIKE 'HasProperty(%, simple%'",
         "Vage HasProperty"),
        ("DELETE FROM facts WHERE statement LIKE 'HasProperty(%, dynamic%'",
         "Vage HasProperty"),
        ("DELETE FROM facts WHERE statement LIKE 'HasProperty(%, static%'",
         "Vage HasProperty"),
        ("DELETE FROM facts WHERE statement LIKE 'Field(%'",
         "Vages Prädikat"),
        ("DELETE FROM facts WHERE statement LIKE 'Wave(%'",
         "Vages Prädikat"),
        ("DELETE FROM facts WHERE statement LIKE 'DNA(%'",
         "DNA ist kein Prädikat"),
        ("DELETE FROM facts WHERE statement LIKE 'Compound(%'",
         "Falsches chemisches Pattern"),
        ("DELETE FROM facts WHERE statement LIKE 'ConsistsOf(CH4, CO2%'",
         "Chemisch falsch"),
        ("DELETE FROM facts WHERE statement LIKE 'ConsistsOf(CH4, H2O%'",
         "Chemisch falsch"),
        ("DELETE FROM facts WHERE statement LIKE 'ConsistsOf(2025_%'",
         "Datum ist keine Substanz"),
        ("DELETE FROM facts WHERE statement LIKE 'DetectedVia%' AND statement NOT IN (SELECT statement FROM facts_validated)",
         "Unvalidierte DetectedVia")
    ]
    
    total_deleted = 0
    for query, reason in deletions:
        cursor.execute(query)
        deleted = cursor.rowcount
        if deleted > 0:
            total_deleted += deleted
            print(f"   - {reason}: {deleted} gelöscht")
    
    # 5. ERSTELLE NEUE HAUPTTABELLE
    print("\n5. Erstelle neue Struktur...")
    
    # Benenne alte Tabelle um
    cursor.execute("ALTER TABLE facts RENAME TO facts_old")
    
    # Erstelle neue facts Tabelle mit besserer Struktur
    cursor.execute("""
        CREATE TABLE facts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            statement TEXT UNIQUE NOT NULL,
            predicate TEXT NOT NULL,
            domain TEXT,
            argument_count INTEGER,
            confidence REAL DEFAULT 1.0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            validated BOOLEAN DEFAULT 0,
            source TEXT DEFAULT 'manual'
        )
    """)
    
    # Kopiere validierte Fakten
    cursor.execute("""
        INSERT INTO facts (statement, predicate, domain, argument_count, confidence, validated)
        SELECT statement, predicate, domain, argument_count, confidence, 1
        FROM facts_validated
    """)
    
    migrated = cursor.rowcount
    
    # 6. AUFRÄUMEN
    print("\n6. Aufräumen...")
    cursor.execute("DROP TABLE IF EXISTS facts_old")
    
    # VACUUM muss außerhalb der Transaktion sein
    conn.commit()
    conn.execute("VACUUM")
    conn.commit()
    
    # 7. FINALE STATISTIK
    cursor.execute("SELECT COUNT(*) FROM facts")
    total_after = cursor.fetchone()[0]
    
    print("\n" + "="*60)
    print("MIGRATION ABGESCHLOSSEN")
    print("-"*40)
    print(f"Vorher:        {total_before:,} Fakten")
    print(f"Gelöscht:      {total_deleted:,} Fakten")
    print(f"Validiert:     {migrated:,} Fakten")
    print(f"Nachher:       {total_after:,} Fakten")
    print(f"Reduktion:     {((total_before-total_after)/total_before*100):.1f}%")
    
    # Zeige Beispiele
    print("\nBEISPIELE VALIDIERTER FAKTEN:")
    cursor.execute("SELECT statement FROM facts WHERE validated=1 LIMIT 10")
    for fact in cursor.fetchall():
        print(f"  ✓ {fact[0]}")
    
    conn.close()
    
    print("\n" + "="*60)
    print("NÄCHSTE SCHRITTE:")
    print("1. Governor mit governor_extended_optimized.conf neustarten")
    print("2. DeepSeek als LLM-Provider konfigurieren")
    print("3. validated_fact_patterns.py in Engine einbinden")
    print("4. Monitoring aktivieren für Qualitätskontrolle")
    
    return total_after

if __name__ == "__main__":
    remaining_facts = migrate_to_scientific_facts()
    
    if remaining_facts < 50:
        print("\n⚠️  WARNUNG: Sehr wenige Fakten übrig!")
        print("    Das ist normal - wir starten mit einer sauberen Basis.")
        print("    Die neue Engine wird wissenschaftlich korrekte Fakten generieren.")
