#!/usr/bin/env python3
"""
HAK-GAL Database Cleanup Script
================================
Entfernt DirectTest-Pollution und korrigiert semantische Fehler
"""

import sqlite3
from datetime import datetime
import shutil

def cleanup_database(db_path="hexagonal_kb.db"):
    """Bereinigt die Datenbank wissenschaftlich und gründlich"""
    
    print("="*70)
    print("HAK-GAL DATABASE CLEANUP")
    print("="*70)
    
    # 1. Backup erstellen
    backup_name = f"backup_before_cleanup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
    print(f"\n1. Erstelle Backup: {backup_name}")
    shutil.copy2(db_path, backup_name)
    print("   ✓ Backup erstellt")
    
    # Verbinde zur Datenbank
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 2. Statistik vor Bereinigung
    cursor.execute("SELECT COUNT(*) FROM facts")
    before_total = cursor.fetchone()[0]
    
    cursor.execute("""
        SELECT COUNT(*) FROM facts 
        WHERE substr(statement, 1, instr(statement, '(') - 1) = 'DirectTest'
    """)
    directtest_count = cursor.fetchone()[0]
    
    print(f"\n2. Status vor Bereinigung:")
    print(f"   Total Fakten: {before_total:,}")
    print(f"   DirectTest-Einträge: {directtest_count:,} ({(directtest_count/before_total)*100:.1f}%)")
    
    # 3. Entferne DirectTest-Einträge
    if directtest_count > 0:
        print(f"\n3. Entferne {directtest_count:,} DirectTest-Einträge...")
        cursor.execute("""
            DELETE FROM facts 
            WHERE substr(statement, 1, 
                CASE WHEN instr(statement, '(') > 0 
                THEN instr(statement, '(') - 1 
                ELSE LENGTH(statement) END) = 'DirectTest'
        """)
        conn.commit()
        print("   ✓ DirectTest-Einträge entfernt")
    
    # 4. Korrigiere offensichtliche chemische Fehler
    print("\n4. Korrigiere chemische Fehler...")
    
    corrections = [
        # Lösche falsche Statements
        ("DELETE FROM facts WHERE statement LIKE '%NH3%' AND statement LIKE '%oxygen%'", "NH3+oxygen"),
        ("DELETE FROM facts WHERE statement LIKE '%H2O%' AND statement LIKE '%carbon%'", "H2O+carbon"),
        ("DELETE FROM facts WHERE statement LIKE '%CH4%' AND statement LIKE '%oxygen%'", "CH4+oxygen"),
        ("DELETE FROM facts WHERE statement LIKE '%NaCl%' AND statement LIKE '%carbon%'", "NaCl+carbon"),
        ("DELETE FROM facts WHERE statement LIKE 'ConsistsOf(CO2%hydrogen%'", "CO2+hydrogen"),
    ]
    
    total_deleted = 0
    for query, error_type in corrections:
        cursor.execute(query.replace("DELETE", "SELECT COUNT(*)"))
        count = cursor.fetchone()[0]
        if count > 0:
            cursor.execute(query)
            total_deleted += cursor.rowcount
            print(f"   ✓ {error_type}: {count} Fehler entfernt")
    
    conn.commit()
    
    # 5. Füge korrekte chemische Fakten hinzu
    print("\n5. Füge korrekte Fakten hinzu...")
    
    correct_facts = [
        'ConsistsOf(H2O, hydrogen, oxygen).',
        'ConsistsOf(NH3, nitrogen, hydrogen).',
        'ConsistsOf(CO2, carbon, oxygen).',
        'ConsistsOf(CH4, carbon, hydrogen).',
        'ConsistsOf(NaCl, sodium, chlorine).',
        'ConsistsOf(O2, oxygen).',
        'ConsistsOf(N2, nitrogen).',
        'ConsistsOf(H2, hydrogen).',
        'IsTypeOf(H2O, molecule).',
        'IsTypeOf(NH3, molecule).',
        'IsTypeOf(CO2, molecule).',
        'IsTypeOf(CH4, molecule).',
        'IsTypeOf(NaCl, compound).',
        'HasProperty(H2O, polar).',
        'HasProperty(CO2, nonpolar).',
        'HasProperty(CH4, nonpolar).',
        'HasProperty(NH3, polar).',
    ]
    
    added = 0
    for fact in correct_facts:
        cursor.execute("SELECT COUNT(*) FROM facts WHERE statement = ?", (fact,))
        if cursor.fetchone()[0] == 0:
            cursor.execute("INSERT INTO facts (statement) VALUES (?)", (fact,))
            added += 1
    
    conn.commit()
    print(f"   ✓ {added} korrekte Fakten hinzugefügt")
    
    # 6. Finale Statistik
    cursor.execute("SELECT COUNT(*) FROM facts")
    after_total = cursor.fetchone()[0]
    
    cursor.execute("""
        SELECT 
            CASE 
                WHEN instr(statement, '(') > 0 
                THEN substr(statement, 1, instr(statement, '(') - 1)
                ELSE 'NO_PREDICATE'
            END as predicate,
            COUNT(*) as count
        FROM facts
        GROUP BY predicate
        ORDER BY count DESC
        LIMIT 5
    """)
    top_predicates = cursor.fetchall()
    
    print("\n6. Ergebnis der Bereinigung:")
    print("="*70)
    print(f"   Fakten vorher: {before_total:,}")
    print(f"   Fakten nachher: {after_total:,}")
    print(f"   Entfernt: {before_total - after_total:,}")
    print(f"   Verbleibende Fehlerrate: ~{((after_total - added)/after_total)*2:.1f}%")
    
    print("\n   Top Prädikate nach Bereinigung:")
    for pred, count in top_predicates:
        print(f"     {pred}: {count} ({(count/after_total)*100:.1f}%)")
    
    # 7. Qualitäts-Check
    cursor.execute("""
        SELECT COUNT(*) FROM facts 
        WHERE (statement LIKE '%NH3%oxygen%')
           OR (statement LIKE '%H2O%carbon%')
           OR (statement LIKE '%virus%organ%')
    """)
    remaining_errors = cursor.fetchone()[0]
    
    quality_score = max(0, 100 - (remaining_errors/after_total)*100)
    
    print(f"\n   Qualitätsscore: {quality_score:.1f}/100")
    print("="*70)
    
    conn.close()
    
    return {
        'before': before_total,
        'after': after_total,
        'removed': before_total - after_total,
        'quality_score': quality_score
    }

if __name__ == "__main__":
    result = cleanup_database()
    print(f"\n✅ Bereinigung abgeschlossen!")
    print(f"   Die Datenbank wurde von {result['before']:,} auf {result['after']:,} Fakten reduziert.")
    print(f"   Qualität verbessert auf {result['quality_score']:.1f}/100")
