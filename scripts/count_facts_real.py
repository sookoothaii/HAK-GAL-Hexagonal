import sqlite3
from pathlib import Path

# Direkte Verbindung zur SQLite DB
db_path = Path("D:/MCP Mods/HAK_GAL_HEXAGONAL/hexagonal_kb.db")

if db_path.exists():
    conn = sqlite3.connect(str(db_path))
    
    # Gesamtanzahl der Fakten
    cursor = conn.execute("SELECT COUNT(*) FROM facts")
    total_count = cursor.fetchone()[0]
    print(f"GESAMTANZAHL FAKTEN: {total_count:,}")
    print("="*60)
    
    # Top 20 Prädikate mit Anzahl
    cursor = conn.execute("""
        SELECT 
            CASE 
                WHEN instr(statement, '(') > 0 
                THEN substr(statement, 1, instr(statement, '(') - 1)
                ELSE 'Invalid'
            END as predicate,
            COUNT(*) as cnt
        FROM facts 
        GROUP BY predicate
        ORDER BY cnt DESC
        LIMIT 20
    """)
    
    print("\nTop 20 Prädikate:")
    print("-"*40)
    total_in_top20 = 0
    for pred, cnt in cursor:
        total_in_top20 += cnt
        print(f"{pred:30} {cnt:8,} Fakten")
    
    print("-"*40)
    print(f"Summe Top 20:                 {total_in_top20:8,} Fakten")
    print(f"Andere Prädikate:             {total_count - total_in_top20:8,} Fakten")
    
    # Anzahl unterschiedlicher Prädikate
    cursor = conn.execute("""
        SELECT COUNT(DISTINCT 
            CASE 
                WHEN instr(statement, '(') > 0 
                THEN substr(statement, 1, instr(statement, '(') - 1)
                ELSE 'Invalid'
            END
        ) FROM facts
    """)
    unique_predicates = cursor.fetchone()[0]
    print(f"\nAnzahl unterschiedlicher Prädikate: {unique_predicates}")
    
    conn.close()
else:
    print("Datenbank nicht gefunden!")
