#!/usr/bin/env python3
"""
HAK/GAL Nischen-Import Script
Importiert Fakten aus der Haupt-DB in die Nischen-DBs
mit Relevanz-Score-Berechnung basierend auf Keywords
"""

import json
import sqlite3
from pathlib import Path
from datetime import datetime
import time
import sys

class NicheImporter:
    def __init__(self, main_db_path="D:/MCP Mods/HAK_GAL_HEXAGONAL/hexagonal_kb.db",
                 niches_dir="D:/MCP Mods/HAK_GAL_HEXAGONAL/niches"):
        self.main_db = Path(main_db_path)
        self.niches_dir = Path(niches_dir)
        self.config_path = self.niches_dir / "niches_config.json"
        
        # Stelle sicher, dass niches_dir existiert
        self.niches_dir.mkdir(exist_ok=True)
        
        # Lade Konfiguration
        with open(self.config_path, 'r') as f:
            self.config = json.load(f)
        
        print(f"[INFO] Geladen: {len(self.config)} Nischen aus {self.config_path}")
        print(f"[INFO] Haupt-DB: {self.main_db}")
    
    def calculate_relevance(self, fact_text, keywords, threshold=0.5):
        """
        Berechnet Relevanz-Score basierend auf Keyword-Matching
        Token-basiertes Scoring: Anzahl gefundener Keywords / Anzahl Keywords
        """
        fact_lower = fact_text.lower()
        matches = 0
        
        for keyword in keywords:
            if keyword.lower() in fact_lower:
                matches += 1
        
        if len(keywords) > 0:
            score = matches / len(keywords)
        else:
            score = 0.0
        
        return score
    
    def create_niche_db(self, niche_name):
        """
        Erstellt eine neue Nischen-DB mit optimierter Struktur
        """
        niche_db_path = self.niches_dir / f"{niche_name}.db"
        
        conn = sqlite3.connect(niche_db_path)
        cursor = conn.cursor()
        
        # Erstelle Facts-Tabelle mit Relevanz-Score
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS facts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fact_text TEXT NOT NULL UNIQUE,
                relevance_score REAL NOT NULL,
                imported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Erstelle Index für Performance
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_relevance 
            ON facts(relevance_score DESC)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_fact_text 
            ON facts(fact_text)
        ''')
        
        # Import-Statistik Tabelle
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS import_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                facts_imported INTEGER,
                duration_seconds REAL,
                source TEXT
            )
        ''')
        
        # Aktiviere WAL-Mode für bessere Performance
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.execute("PRAGMA wal_autocheckpoint=1000")
        
        conn.commit()
        conn.close()
        
        print(f"  [OK] Nischen-DB erstellt: {niche_db_path}")
        return niche_db_path
    
    def import_facts_to_niche(self, niche_name, niche_config):
        """
        Importiert relevante Fakten aus Haupt-DB in Nischen-DB
        """
        print(f"\n[IMPORT] Nische: {niche_name}")
        print(f"  Keywords: {', '.join(niche_config['keywords'])}")
        print(f"  Threshold: {niche_config['threshold']}")
        
        # Erstelle Nischen-DB
        niche_db_path = self.create_niche_db(niche_name)
        
        # Hole Fakten aus Haupt-DB
        main_conn = sqlite3.connect(self.main_db)
        cursor = main_conn.execute("SELECT statement FROM facts")
        all_facts = cursor.fetchall()
        main_conn.close()
        
        print(f"  [INFO] {len(all_facts)} Fakten aus Haupt-DB geladen")
        
        # Importiere relevante Fakten
        niche_conn = sqlite3.connect(niche_db_path)
        niche_cursor = niche_conn.cursor()
        
        imported = 0
        skipped = 0
        start_time = time.time()
        
        # Batch-Import für Performance
        batch_data = []
        
        for (fact,) in all_facts:
            # Berechne Relevanz
            relevance = self.calculate_relevance(
                fact, 
                niche_config['keywords'],
                niche_config['threshold']
            )
            
            # Importiere nur wenn über Threshold
            if relevance >= niche_config['threshold']:
                batch_data.append((fact, relevance))
                imported += 1
            else:
                skipped += 1
            
            # Batch-Insert alle 1000 Fakten
            if len(batch_data) >= 1000:
                try:
                    niche_cursor.executemany(
                        "INSERT OR IGNORE INTO facts (fact_text, relevance_score) VALUES (?, ?)",
                        batch_data
                    )
                    niche_conn.commit()
                    batch_data = []
                except Exception as e:
                    print(f"  [WARN] Batch-Insert Fehler: {e}")
        
        # Letzte Batch
        if batch_data:
            try:
                niche_cursor.executemany(
                    "INSERT OR IGNORE INTO facts (fact_text, relevance_score) VALUES (?, ?)",
                    batch_data
                )
                niche_conn.commit()
            except Exception as e:
                print(f"  [WARN] Final Batch-Insert Fehler: {e}")
        
        duration = time.time() - start_time
        
        # Speichere Import-Statistik
        niche_cursor.execute(
            "INSERT INTO import_stats (facts_imported, duration_seconds, source) VALUES (?, ?, ?)",
            (imported, duration, str(self.main_db))
        )
        niche_conn.commit()
        
        # Zeige Statistik
        niche_cursor.execute("SELECT COUNT(*) FROM facts")
        total_in_db = niche_cursor.fetchone()[0]
        
        niche_cursor.execute("SELECT MIN(relevance_score), MAX(relevance_score), AVG(relevance_score) FROM facts")
        min_rel, max_rel, avg_rel = niche_cursor.fetchone()
        
        niche_conn.close()
        
        # Update Config mit Zeitstempel
        self.config[niche_name]['last_updated'] = datetime.now().isoformat()
        
        print(f"  [DONE] Importiert: {imported} | Übersprungen: {skipped}")
        print(f"  [STATS] Total in DB: {total_in_db}")
        if total_in_db > 0:
            print(f"  [RELEVANCE] Min: {min_rel:.3f} | Max: {max_rel:.3f} | Avg: {avg_rel:.3f}")
        print(f"  [TIME] {duration:.3f}s")
        
        return imported
    
    def run_import(self):
        """
        Führt den Import für alle konfigurierten Nischen durch
        """
        print("\n" + "="*60)
        print("HAK/GAL NISCHEN-IMPORT")
        print("="*60)
        
        total_imported = 0
        start_time = time.time()
        
        # Importiere für jede Nische
        for niche_name, niche_config in self.config.items():
            imported = self.import_facts_to_niche(niche_name, niche_config)
            total_imported += imported
        
        # Speichere aktualisierte Config
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=2)
        
        total_duration = time.time() - start_time
        
        print("\n" + "="*60)
        print("IMPORT ABGESCHLOSSEN")
        print("="*60)
        print(f"✅ Nischen verarbeitet: {len(self.config)}")
        print(f"✅ Fakten importiert: {total_imported}")
        print(f"✅ Gesamtzeit: {total_duration:.2f}s")
        print(f"✅ Config aktualisiert: {self.config_path}")
    
    def show_statistics(self):
        """
        Zeigt detaillierte Statistiken aller Nischen
        """
        print("\n" + "="*60)
        print("NISCHEN-STATISTIKEN")
        print("="*60)
        
        total_facts = 0
        
        for niche_name in self.config.keys():
            niche_db_path = self.niches_dir / f"{niche_name}.db"
            
            if not niche_db_path.exists():
                print(f"\n[{niche_name}] - Keine DB gefunden")
                continue
            
            conn = sqlite3.connect(niche_db_path)
            cursor = conn.cursor()
            
            # Basis-Stats
            cursor.execute("SELECT COUNT(*) FROM facts")
            count = cursor.fetchone()[0]
            
            cursor.execute("SELECT MIN(relevance_score), MAX(relevance_score), AVG(relevance_score) FROM facts")
            min_rel, max_rel, avg_rel = cursor.fetchone() or (0, 0, 0)
            
            # Top-Fakten
            cursor.execute("SELECT fact_text, relevance_score FROM facts ORDER BY relevance_score DESC LIMIT 3")
            top_facts = cursor.fetchall()
            
            conn.close()
            
            total_facts += count
            
            print(f"\n[{niche_name}]")
            print(f"  Fakten: {count}")
            if count > 0:
                print(f"  Relevanz: Min={min_rel:.3f}, Max={max_rel:.3f}, Avg={avg_rel:.3f}")
                print(f"  Top-Fakten:")
                for i, (fact, score) in enumerate(top_facts, 1):
                    fact_preview = fact[:60] + "..." if len(fact) > 60 else fact
                    print(f"    {i}. [{score:.3f}] {fact_preview}")
        
        print(f"\n{'='*60}")
        print(f"GESAMT: {total_facts} Fakten in allen Nischen")


if __name__ == "__main__":
    # Parse Arguments
    if len(sys.argv) > 1 and sys.argv[1] == "--stats":
        # Nur Statistiken anzeigen
        importer = NicheImporter()
        importer.show_statistics()
    else:
        # Führe Import durch
        importer = NicheImporter()
        importer.run_import()
        importer.show_statistics()
