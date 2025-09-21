"""
HAK-GAL DirectTest Cleanup Tool
================================
Entfernt die übermäßigen DirectTest-Einträge aus der Datenbank
"""

import sqlite3
from datetime import datetime

def cleanup_direct_tests(keep_samples=100):
    """
    Entfernt DirectTest-Einträge und behält nur eine kleine Stichprobe
    
    Args:
        keep_samples: Anzahl der DirectTest-Einträge die behalten werden sollen
    """
    db_path = r"D:\MCP Mods\HAK_GAL_HEXAGONAL\hexagonal_kb.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("=" * 60)
    print("   DIRECTTEST CLEANUP TOOL")
    print("=" * 60)
    
    # Zähle DirectTest-Einträge
    cursor.execute("SELECT COUNT(*) FROM facts WHERE statement LIKE 'DirectTest%'")
    direct_test_count = cursor.fetchone()[0]
    
    print(f"\n📊 Gefundene DirectTest-Einträge: {direct_test_count:,}")
    
    if direct_test_count <= keep_samples:
        print(f"✅ Keine Bereinigung nötig (nur {direct_test_count} Einträge)")
        return
    
    # Backup erstellen
    print("\n📦 Erstelle Backup...")
    backup_name = f"hexagonal_kb_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
    cursor.execute(f"VACUUM INTO '{backup_name}'")
    print(f"✅ Backup erstellt: {backup_name}")
    
    # Lösche DirectTest-Einträge (behalte nur die ersten keep_samples)
    print(f"\n🗑️ Lösche {direct_test_count - keep_samples:,} DirectTest-Einträge...")
    
    # Hole die ersten keep_samples DirectTest statements
    cursor.execute(f"""
        SELECT statement FROM facts 
        WHERE statement LIKE 'DirectTest%' 
        LIMIT {keep_samples}
    """)
    keep_statements = [row[0] for row in cursor.fetchall()]
    
    # Lösche alle anderen DirectTest-Einträge
    if keep_statements:
        placeholders = ','.join(['?' for _ in keep_statements])
        cursor.execute(f"""
            DELETE FROM facts 
            WHERE statement LIKE 'DirectTest%' 
            AND statement NOT IN ({placeholders})
        """, keep_statements)
    else:
        cursor.execute("DELETE FROM facts WHERE statement LIKE 'DirectTest%'")
    
    deleted = cursor.rowcount
    conn.commit()
    
    print(f"✅ {deleted:,} DirectTest-Einträge gelöscht")
    
    # Neue Statistik
    cursor.execute("SELECT COUNT(*) FROM facts")
    new_total = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM facts WHERE statement LIKE 'DirectTest%'")
    new_direct_test = cursor.fetchone()[0]
    
    print("\n📊 NEUE STATISTIK:")
    print(f"  Total Fakten: {new_total:,}")
    print(f"  DirectTest: {new_direct_test:,} ({(new_direct_test/new_total)*100:.1f}%)")
    
    # Vacuum zur Optimierung
    print("\n🔧 Optimiere Datenbank...")
    cursor.execute("VACUUM")
    
    conn.close()
    print("\n✅ Bereinigung abgeschlossen!")
    
    return {
        'deleted': deleted,
        'new_total': new_total,
        'backup': backup_name
    }

if __name__ == "__main__":
    # Führe Cleanup aus - behalte nur 100 DirectTest-Samples
    result = cleanup_direct_tests(keep_samples=100)
    
    if result:
        print("\n" + "=" * 60)
        print("💡 NÄCHSTE SCHRITTE:")
        print("1. Stoppe den DirectTest-Generator falls er noch läuft")
        print("2. Implementiere bessere Fact-Generatoren")
        print("3. Führe kb_quality_analyzer.py erneut aus")
