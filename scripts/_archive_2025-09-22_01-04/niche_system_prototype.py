"""
HAK/GAL Nischen-System - Prototyp Implementation V2
Basierend auf Multi-Agent Konsens (DeepSeek + Claude + Gemini)
Mit GPT5 Quick-Fixes implementiert
"""

import sqlite3
import json
import time
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class Niche:
    """Repräsentiert eine spezialisierte Wissensdomäne"""
    name: str
    keywords: List[str]
    parent: Optional[str] = None
    threshold: float = 0.5  # GPT5 Fix: Default auf 0.5 gesenkt
    created_at: str = None
    last_updated: str = None
    
class NicheManager:
    """Verwaltet alle Nischen und deren Datenbanken"""
    
    def __init__(self, main_db_path: str = "hexagonal_kb.db", batch_size: int = 100):
        self.main_db_path = main_db_path
        self.niches_dir = Path("niches")
        self.niches_dir.mkdir(exist_ok=True)
        self.niches = {}
        self.batch_size = batch_size  # GPT5 Fix: Konfigurierbare Batch-Größe
        self.load_niches_config()
    
    def load_niches_config(self):
        """Lädt Nischen-Konfiguration aus JSON"""
        config_path = self.niches_dir / "niches_config.json"
        if config_path.exists():
            with open(config_path, 'r') as f:
                config = json.load(f)
                for name, data in config.items():
                    self.niches[name] = Niche(**data)
    
    def save_niches_config(self):
        """Speichert aktuelle Nischen-Konfiguration"""
        config = {}
        for name, niche in self.niches.items():
            config[name] = {
                'name': niche.name,
                'keywords': niche.keywords,
                'parent': niche.parent,
                'threshold': niche.threshold,
                'created_at': niche.created_at,
                'last_updated': niche.last_updated
            }
        
        config_path = self.niches_dir / "niches_config.json"
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
    
    def _setup_niche_db(self, conn: sqlite3.Connection):
        """GPT5 Fix: WAL-Mode und Optimierungen für Nischen-DB"""
        cursor = conn.cursor()
        
        # Performance-Optimierungen
        cursor.execute('PRAGMA journal_mode=WAL')
        cursor.execute('PRAGMA synchronous=FULL')
        cursor.execute('PRAGMA wal_autocheckpoint=1000')
        
        # Schema mit UNIQUE constraint
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS facts (
                id INTEGER PRIMARY KEY,
                fact_text TEXT NOT NULL UNIQUE,  -- GPT5 Fix: UNIQUE hinzugefügt
                relevance_score REAL,
                source_fact_id INTEGER,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # GPT5 Fix: Index für Performance
        cursor.execute('''
            CREATE UNIQUE INDEX IF NOT EXISTS idx_facts_text 
            ON facts(fact_text)
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS niche_metadata (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        ''')
        
        # GPT5 Fix: Stats-Tabelle für Telemetry
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS import_stats (
                import_id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                facts_imported INTEGER,
                duration_seconds REAL,
                keywords_used TEXT
            )
        ''')
        
        conn.commit()
    
    def create_niche(self, name: str, keywords: List[str], 
                     parent: Optional[str] = None, threshold: Optional[float] = None) -> Niche:
        """Erstellt eine neue Nische mit eigener Datenbank"""
        
        # GPT5 Fix: Dynamischer Threshold
        if threshold is None:
            threshold = min(0.5, 1.0 / max(len(keywords), 1))
        
        # Nischen-Objekt erstellen
        niche = Niche(
            name=name,
            keywords=keywords,
            parent=parent,
            threshold=threshold,
            created_at=datetime.now().isoformat(),
            last_updated=datetime.now().isoformat()
        )
        
        # Nischen-Datenbank erstellen
        niche_db_path = self.niches_dir / f"{name}.db"
        conn = sqlite3.connect(niche_db_path)
        
        # Setup mit Optimierungen
        self._setup_niche_db(conn)
        
        cursor = conn.cursor()
        
        # Metadata speichern (mit REPLACE statt INSERT)
        cursor.execute('REPLACE INTO niche_metadata VALUES (?, ?)', 
                      ('keywords', json.dumps(keywords)))
        cursor.execute('REPLACE INTO niche_metadata VALUES (?, ?)', 
                      ('threshold', str(threshold)))
        
        conn.commit()
        conn.close()
        
        # In Registry speichern
        self.niches[name] = niche
        self.save_niches_config()
        
        # Initial mit Fakten befüllen
        count = self.populate_niche(name)
        
        return niche
    
    def populate_niche(self, niche_name: str):
        """Befüllt Nische mit relevanten Fakten aus Master-DB"""
        if niche_name not in self.niches:
            raise ValueError(f"Nische '{niche_name}' existiert nicht")
        
        start_time = time.time()
        niche = self.niches[niche_name]
        niche_db_path = self.niches_dir / f"{niche_name}.db"
        
        # Verbindungen öffnen
        main_conn = sqlite3.connect(self.main_db_path)
        niche_conn = sqlite3.connect(niche_db_path)
        
        # WAL-Mode auch für Hauptverbindung
        main_conn.execute('PRAGMA journal_mode=WAL')
        
        main_cursor = main_conn.cursor()
        niche_cursor = niche_conn.cursor()
        
        facts_imported = 0
        
        # GPT5 Fix: Korrektes SQL ohne nicht-existente Spalten
        for keyword in niche.keywords:
            query = '''
                SELECT statement 
                FROM facts 
                WHERE LOWER(statement) LIKE LOWER(?)
                LIMIT ?
            '''
            main_cursor.execute(query, (f'%{keyword}%', self.batch_size))
            
            for (fact_text,) in main_cursor.fetchall():
                # GPT5 Fix: Verbesserte Relevanzberechnung
                relevance = self._calculate_relevance_improved(fact_text, niche.keywords)
                
                if relevance >= niche.threshold:
                    try:
                        niche_cursor.execute('''
                            INSERT INTO facts 
                            (fact_text, relevance_score, source_fact_id) 
                            VALUES (?, ?, ?)
                        ''', (fact_text, relevance, 0))
                        facts_imported += 1
                    except sqlite3.IntegrityError:
                        # Duplikat, ignorieren (wegen UNIQUE constraint)
                        pass
        
        # GPT5 Fix: Telemetry speichern
        duration = time.time() - start_time
        niche_cursor.execute('''
            INSERT INTO import_stats (facts_imported, duration_seconds, keywords_used)
            VALUES (?, ?, ?)
        ''', (facts_imported, duration, json.dumps(niche.keywords)))
        
        niche_conn.commit()
        
        # Update timestamp
        niche.last_updated = datetime.now().isoformat()
        self.save_niches_config()
        
        main_conn.close()
        niche_conn.close()
        
        print(f"Nische '{niche_name}' befüllt mit {facts_imported} Fakten in {duration:.2f}s")
        return facts_imported
    
    def _calculate_relevance(self, text: str, keywords: List[str]) -> float:
        """Original einfache Relevanzberechnung"""
        text_lower = text.lower()
        matches = sum(1 for kw in keywords if kw.lower() in text_lower)
        return min(1.0, matches / len(keywords))
    
    def _calculate_relevance_improved(self, text: str, keywords: List[str]) -> float:
        """GPT5 Fix: Verbesserte Relevanzberechnung mit Token-Normalisierung"""
        import re
        
        # Text in Tokens zerlegen
        text_tokens = set(re.findall(r'\w+', text.lower()))
        keyword_tokens = set()
        for kw in keywords:
            keyword_tokens.update(re.findall(r'\w+', kw.lower()))
        
        # Schnittmenge berechnen
        if not keyword_tokens:
            return 0.0
        
        intersection = text_tokens & keyword_tokens
        return len(intersection) / len(keyword_tokens)
    
    def query_niche(self, niche_name: str, query: str, limit: int = 10) -> List[Dict]:
        """Fragt eine spezifische Nische ab"""
        if niche_name not in self.niches:
            raise ValueError(f"Nische '{niche_name}' existiert nicht")
        
        niche_db_path = self.niches_dir / f"{niche_name}.db"
        conn = sqlite3.connect(niche_db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT fact_text, relevance_score 
            FROM facts 
            WHERE LOWER(fact_text) LIKE LOWER(?)
            ORDER BY relevance_score DESC
            LIMIT ?
        ''', (f'%{query}%', limit))
        
        results = [
            {'fact': row[0], 'relevance': row[1]}
            for row in cursor.fetchall()
        ]
        
        conn.close()
        return results
    
    def get_niche_stats(self) -> Dict:
        """Gibt erweiterte Statistiken über alle Nischen zurück"""
        stats = {}
        
        for name, niche in self.niches.items():
            niche_db_path = self.niches_dir / f"{name}.db"
            if niche_db_path.exists():
                conn = sqlite3.connect(niche_db_path)
                cursor = conn.cursor()
                
                # Fakten zählen
                cursor.execute('SELECT COUNT(*) FROM facts')
                count = cursor.fetchone()[0]
                
                # GPT5 Fix: Import-Stats abrufen (mit Fallback)
                try:
                    cursor.execute('''
                        SELECT SUM(facts_imported), AVG(duration_seconds), COUNT(*)
                        FROM import_stats
                    ''')
                    import_data = cursor.fetchone()
                except sqlite3.OperationalError:
                    # Tabelle existiert nicht (alte Nische)
                    import_data = (None, None, None)
                
                conn.close()
                
                stats[name] = {
                    'fact_count': count,
                    'keywords': niche.keywords,
                    'threshold': niche.threshold,
                    'last_updated': niche.last_updated,
                    'total_imports': import_data[0] or count,
                    'avg_import_time': round(import_data[1] or 0, 2) if import_data[1] else 0,
                    'import_runs': import_data[2] or 1
                }
        
        return stats

# === Demo / Test ===
if __name__ == "__main__":
    print("=== HAK/GAL NISCHEN-SYSTEM V2 (mit GPT5 Fixes) ===\n")
    
    # Manager initialisieren
    nm = NicheManager(
        main_db_path="D:\\MCP Mods\\HAK_GAL_HEXAGONAL\\hexagonal_kb.db",
        batch_size=150  # Größere Batches
    )
    
    # Test-Nische mit automatischem Threshold
    print("Erstelle Test-Nische mit GPT5-Optimierungen...")
    test_niche = nm.create_niche(
        name="optimized_test",
        keywords=["HAK_GAL", "System", "Contains"]
        # Threshold wird automatisch berechnet
    )
    
    print(f"  Threshold automatisch gesetzt: {test_niche.threshold}")
    
    # Stats anzeigen
    stats = nm.get_niche_stats()
    for niche, data in stats.items():
        print(f"\n{niche}:")
        print(f"  - {data['fact_count']} Fakten")
        print(f"  - {data['import_runs']} Import-Läufe")
        print(f"  - Ø {data['avg_import_time']}s pro Import")
    
    print("\n✅ GPT5 Quick-Fixes implementiert!")

