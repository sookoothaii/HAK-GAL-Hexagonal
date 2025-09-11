"""
SQLite Performance Patch für hexagonal_api_enhanced_clean.py
Fügen Sie diese Zeilen in die SQLiteFactRepository __init__ Methode ein
"""

# Diese Zeilen müssen in src_hexagonal/adapters/sqlite_adapter.py
# in der __init__ Methode der SQLiteFactRepository Klasse eingefügt werden:

def apply_optimizations(conn):
    """Apply performance optimizations to SQLite connection"""
    cursor = conn.cursor()
    
    # Performance optimizations
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA synchronous=NORMAL")  # Faster but still safe
    cursor.execute("PRAGMA cache_size=10000")     # 10MB cache
    cursor.execute("PRAGMA temp_store=MEMORY")    # Use memory for temp tables
    cursor.execute("PRAGMA mmap_size=268435456")  # 256MB memory-mapped I/O
    
    conn.commit()
    
# Dann in jeder Methode die eine Connection öffnet:
# conn = sqlite3.connect(self.db_path)
# apply_optimizations(conn)  # <-- Diese Zeile hinzufügen

print("""
ANLEITUNG:
==========
1. Öffnen Sie: src_hexagonal/adapters/sqlite_adapter.py
2. Suchen Sie nach: class SQLiteFactRepository
3. Fügen Sie die apply_optimizations Funktion hinzu
4. Rufen Sie sie nach jedem sqlite3.connect() auf
5. Starten Sie die API neu

Dann werden die Optimierungen bei JEDER Connection angewendet!
""")
