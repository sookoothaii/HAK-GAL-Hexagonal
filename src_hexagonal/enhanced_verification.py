"""
Erweiterte Verify-Feature Implementierung
Nach HAK-GAL Verfassung Artikel 6: Empirische Validierung
"""

def create_enhanced_verified_queries_table(conn):
    """
    Erweiterte Tabelle für verifizierte Queries mit mehr Kontext
    """
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS verified_queries (
            query TEXT PRIMARY KEY,
            confidence REAL NOT NULL,
            trust_components TEXT NOT NULL,  -- JSON string
            verified_by TEXT,
            verified_at TEXT NOT NULL,
            explanation TEXT,
            metadata TEXT  -- JSON string for additional context
        )
    """)
    
    # Index für schnellere Zeitbasierte Queries
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_verified_at 
        ON verified_queries(verified_at)
    """)
    
    conn.commit()
    

def save_verification(conn, query, confidence, trust_components, user_id=None, explanation=None):
    """
    Speichert eine verifizierte Query mit vollständigem Kontext
    """
    import json
    from datetime import datetime, timezone
    
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO verified_queries 
        (query, confidence, trust_components, verified_by, verified_at, explanation, metadata)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        query,
        confidence,
        json.dumps(trust_components),
        user_id or 'anonymous',
        datetime.now(timezone.utc).isoformat(),
        explanation,
        json.dumps({"version": "1.0", "source": "manual_verification"})
    ))
    
    conn.commit()
    return cursor.rowcount > 0


def get_verification(conn, query):
    """
    Holt die Verifikationsdaten für eine Query
    """
    import json
    
    cursor = conn.cursor()
    cursor.execute("""
        SELECT confidence, trust_components, verified_by, verified_at, explanation, metadata
        FROM verified_queries 
        WHERE query = ?
        LIMIT 1
    """, (query,))
    
    row = cursor.fetchone()
    if row:
        return {
            'confidence': row[0],
            'trust_components': json.loads(row[1]),
            'verified_by': row[2],
            'verified_at': row[3],
            'explanation': row[4],
            'metadata': json.loads(row[5]) if row[5] else {}
        }
    return None


def cleanup_old_verifications(conn, days=30):
    """
    Entfernt Verifikationen älter als X Tage
    """
    from datetime import datetime, timedelta, timezone
    
    cutoff_date = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
    
    cursor = conn.cursor()
    cursor.execute("""
        DELETE FROM verified_queries 
        WHERE verified_at < ?
    """, (cutoff_date,))
    
    conn.commit()
    return cursor.rowcount
