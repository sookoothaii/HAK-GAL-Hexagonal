#!/usr/bin/env python3
"""
BEREINIGUNG DER KNOWLEDGE BASE
Entfernt wissenschaftlich wertlose/vage Fakten
"""

import sqlite3
import datetime
import shutil
from pathlib import Path

def cleanup_database():
    # 1. BACKUP ERSTELLEN
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"hexagonal_kb_BEFORE_CLEANUP_{timestamp}.db"
    
    print("BEREINIGUNG DER KNOWLEDGE BASE")
    print("="*60)
    print(f"1. Erstelle Backup: {backup_file}")
    shutil.copy2("hexagonal_kb.db", backup_file)
    
    conn = sqlite3.connect("hexagonal_kb.db")
    cursor = conn.cursor()
    
    # 2. ZÄHLE VORHER
    cursor.execute("SELECT COUNT(*) FROM facts")
    count_before = cursor.fetchone()[0]
    print(f"2. Fakten vorher: {count_before:,}")
    
    # 3. LÖSCHE VAGE HASPROPERTY-FAKTEN
    vague_properties = [
        'complex', 'simple', 'dynamic', 'static', 'variable',
        'optimal', 'critical', 'essential', 'fundamental', 'reactive',
        'stable', 'active', 'passive', 'flexible', 'robust',
        'efficient', 'effective', 'important', 'significant', 'primary',
        'secondary', 'basic', 'advanced', 'modern', 'traditional',
        'standard', 'custom', 'generic', 'specific', 'general'
    ]
    
    print("\n3. LÖSCHE VAGE HASPROPERTY-FAKTEN:")
    print("-"*40)
    
    deleted_vague = 0
    for prop in vague_properties:
        cursor.execute("""
            DELETE FROM facts 
            WHERE statement LIKE ? 
            OR statement LIKE ?
        """, (f'HasProperty(%, {prop}).', f'HasProperty(%, {prop})'))
        
        count = cursor.rowcount
        if count > 0:
            deleted_vague += count
            print(f"   - Gelöscht: {count:4} x HasProperty(..., {prop})")
    
    # 4. LÖSCHE UNSINNIGE CONSISTSOF
    print("\n4. LÖSCHE UNSINNIGE CONSISTSOF-FAKTEN:")
    print("-"*40)
    
    # ConsistsOf mit Datumsangaben
    cursor.execute("""
        DELETE FROM facts 
        WHERE statement LIKE 'ConsistsOf(2025_%'
        OR statement LIKE 'ConsistsOf(2024_%'
        OR statement LIKE 'ConsistsOf(%User, %'
    """)
    deleted_dates = cursor.rowcount
    print(f"   - Gelöscht: {deleted_dates} ConsistsOf mit Datum/User")
    
    # ConsistsOf mit unsinnigen AI-Kombinationen
    cursor.execute("""
        DELETE FROM facts 
        WHERE statement LIKE 'ConsistsOf(AI, API%'
        OR statement LIKE 'ConsistsOf(API, AI%'
    """)
    deleted_ai = cursor.rowcount
    print(f"   - Gelöscht: {deleted_ai} unsinnige AI/API ConsistsOf")
    
    # 5. LÖSCHE FAKTEN MIT >4 ARGUMENTEN (außer sinnvolle)
    print("\n5. LÖSCHE FAKTEN MIT ZU VIELEN ARGUMENTEN:")
    print("-"*40)
    
    cursor.execute("""
        DELETE FROM facts 
        WHERE (LENGTH(statement) - LENGTH(REPLACE(statement, ',', ''))) > 3
        AND statement NOT LIKE 'ConsistsOf(atom, proton, neutron, electron%'
        AND statement NOT LIKE 'ConsistsOf(% hydrogen, carbon, oxygen%'
    """)
    deleted_long = cursor.rowcount
    print(f"   - Gelöscht: {deleted_long} Fakten mit >4 Argumenten")
    
    # 6. LÖSCHE DUPLIKATE (gleiche Statements)
    print("\n6. LÖSCHE DUPLIKATE:")
    print("-"*40)
    
    cursor.execute("""
        DELETE FROM facts 
        WHERE rowid NOT IN (
            SELECT MIN(rowid) 
            FROM facts 
            GROUP BY statement
        )
    """)
    deleted_dupes = cursor.rowcount
    print(f"   - Gelöscht: {deleted_dupes} Duplikate")
    
    # 7. COMMIT UND STATISTIK
    conn.commit()
    
    cursor.execute("SELECT COUNT(*) FROM facts")
    count_after = cursor.fetchone()[0]
    
    total_deleted = count_before - count_after
    
    print("\n" + "="*60)
    print("ERGEBNIS:")
    print("-"*40)
    print(f"Vorher:           {count_before:,} Fakten")
    print(f"Gelöscht gesamt:  {total_deleted:,} Fakten")
    print(f"  - Vage Props:   {deleted_vague:,}")
    print(f"  - Unsinnige:    {deleted_dates + deleted_ai:,}")
    print(f"  - Zu lang:      {deleted_long:,}")
    print(f"  - Duplikate:    {deleted_dupes:,}")
    print(f"Nachher:          {count_after:,} Fakten")
    print(f"Reduzierung:      {(total_deleted/count_before*100):.1f}%")
    
    # 8. VAKUUM (Datenbank optimieren)
    print("\n7. Optimiere Datenbank...")
    cursor.execute("VACUUM")
    
    # 9. QUALITÄTSPRÜFUNG
    print("\n" + "="*60)
    print("QUALITÄTSPRÜFUNG NACH BEREINIGUNG:")
    print("-"*40)
    
    cursor.execute("""
        SELECT 
            CASE 
                WHEN statement LIKE 'HasProperty(%' THEN 'HasProperty'
                WHEN statement LIKE 'ConsistsOf(%' THEN 'ConsistsOf'
                WHEN statement LIKE 'IsTypeOf(%' THEN 'IsTypeOf'
                WHEN statement LIKE 'HasPart(%' THEN 'HasPart'
                ELSE 'Other'
            END as pred,
            COUNT(*) as cnt
        FROM facts
        GROUP BY pred
        ORDER BY cnt DESC
    """)
    
    for pred, cnt in cursor.fetchall()[:5]:
        pct = cnt/count_after*100
        print(f"{pred:15} {cnt:6,} ({pct:5.1f}%)")
    
    # 10. BEISPIELE GUTER FAKTEN
    print("\n" + "="*60)
    print("BEISPIELE VERBLEIBENDER FAKTEN:")
    print("-"*40)
    
    cursor.execute("""
        SELECT statement FROM facts 
        WHERE statement LIKE 'ConsistsOf(atom%'
        OR statement LIKE 'IsTypeOf(%, compound)'
        OR statement LIKE 'HasProperty(H2O%'
        LIMIT 10
    """)
    
    for fact in cursor.fetchall():
        print(f"  ✓ {fact[0]}")
    
    conn.close()
    
    print("\n" + "="*60)
    print("✅ BEREINIGUNG ABGESCHLOSSEN!")
    print(f"Backup gespeichert als: {backup_file}")
    print(f"Datenbank reduziert auf {count_after:,} wissenschaftliche Fakten")
    
    return count_after

if __name__ == "__main__":
    remaining = cleanup_database()
    
    if remaining < 5000:
        print("\n⚠️  WARNUNG: Nur noch sehr wenige Fakten übrig!")
        print("    Eventuell war die Bereinigung zu aggressiv.")
        print("    Backup kann wiederhergestellt werden.")
