#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
HAK-GAL Facts Monitor with LLM Source Detection
Zeigt an, ob Fakten von lokalen (Ollama) oder Cloud-LLMs generiert wurden
"""

import sqlite3
import time
import sys
import os
import json
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from collections import defaultdict

@dataclass
class FactStatistics:
    """Datenklasse für Fakten-Statistiken"""
    total_count: int
    recent_facts: List[Tuple[str, str]]  # (statement, source)
    predicates: Dict[str, int]
    growth_rate: float
    session_added: int
    session_removed: int
    last_update: datetime
    llm_stats: Dict[str, int]  # Statistik nach LLM-Quelle

class SourceDetector:
    """Erkennt die Quelle von Fakten (Ollama, Gemini, etc.)"""
    
    def __init__(self):
        self.api_base = "http://localhost:5002/api"
        self.fact_timestamps = {}  # Track when facts were added
        self.llm_activity = []  # Track LLM API calls
        
    def check_ollama_running(self) -> bool:
        """Prüfe ob Ollama läuft"""
        try:
            resp = requests.get("http://localhost:11434/api/tags", timeout=1)
            return resp.status_code == 200
        except:
            return False
    
    def check_api_logs(self) -> Optional[str]:
        """Versuche aus API-Logs die letzte LLM-Quelle zu ermitteln"""
        try:
            # Check the API status endpoint for LLM info
            resp = requests.get(f"{self.api_base}/status", timeout=2)
            if resp.status_code == 200:
                data = resp.json()
                # Look for LLM provider info in status
                if 'last_llm_provider' in data:
                    return data['last_llm_provider']
        except:
            pass
        return None
    
    def detect_source_heuristic(self, fact: str, timestamp: Optional[str] = None) -> str:
        """
        Heuristisch die Quelle eines Fakts bestimmen
        Basiert auf Timing, Patterns und System-Status
        """
        
        # Pattern-basierte Erkennung
        if any(term in fact.lower() for term in ['qwen', 'ollama', 'local']):
            return "Ollama (Pattern)"
        
        if any(term in fact.lower() for term in ['gemini', 'google', 'bard']):
            return "Gemini (Pattern)"
        
        # Check if Ollama is running
        ollama_running = self.check_ollama_running()
        
        # Timing-basierte Erkennung (wenn gerade Facts hinzugefügt wurden)
        current_time = time.time()
        if timestamp:
            # Wenn der Fakt sehr neu ist (< 30 Sekunden)
            try:
                fact_time = datetime.fromisoformat(timestamp).timestamp()
                if current_time - fact_time < 30:
                    # Check welcher LLM gerade aktiv war
                    if ollama_running:
                        return "Ollama (Active)"
                    else:
                        return "Cloud (Recent)"
            except:
                pass
        
        # Default basierend auf System-Status
        if ollama_running:
            return "Ollama (Default)"
        else:
            return "Cloud (Default)"
    
    def analyze_batch(self, facts: List[str]) -> Dict[str, int]:
        """Analysiere eine Gruppe von Fakten"""
        sources = defaultdict(int)
        for fact in facts:
            source = self.detect_source_heuristic(fact)
            base_source = source.split(' ')[0]  # Nur "Ollama" oder "Cloud"
            sources[base_source] += 1
        return dict(sources)

class EnhancedFactsMonitor:
    """Knowledge Base Monitor mit LLM-Source Detection"""
    
    def __init__(self, db_path: Optional[str] = None, update_interval: int = 5):
        self.db_path = db_path or r"D:\MCP Mods\HAK_GAL_HEXAGONAL\hexagonal_kb.db"
        self.update_interval = update_interval
        self.source_detector = SourceDetector()
        
        # Statistik-Tracking
        self.last_count = 0
        self.start_count = 0
        self.start_time = time.time()
        self.session_added = 0
        self.session_removed = 0
        self.llm_stats = defaultdict(int)  # Track facts by LLM source
        
        # Cache
        self.recent_facts_cache = []
        self.predicate_cache = {}
        
        # Display-Kontrolle
        self.first_run = True
        
        # Farben (ANSI codes)
        self.colors = {
            'header': '\033[36m',    # Cyan
            'success': '\033[32m',   # Grün
            'warning': '\033[33m',   # Gelb
            'error': '\033[31m',     # Rot
            'info': '\033[94m',      # Blau
            'ollama': '\033[35m',    # Magenta
            'cloud': '\033[96m',     # Light Cyan
            'reset': '\033[0m'       # Reset
        }
    
    def clear_screen(self):
        """Bildschirm löschen (OS-unabhängig)"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def move_cursor(self, row: int, col: int = 0):
        """Cursor an Position bewegen"""
        sys.stdout.write(f"\033[{row};{col}H")
    
    def clear_line(self, row: int):
        """Zeile löschen"""
        self.move_cursor(row)
        sys.stdout.write("\033[K")
    
    def write_line(self, row: int, text: str, color: str = None):
        """Schreibe Text in bestimmte Zeile mit optionaler Farbe"""
        self.clear_line(row)
        if color and color in self.colors:
            text = f"{self.colors[color]}{text}{self.colors['reset']}"
        sys.stdout.write(text)
        sys.stdout.flush()
    
    def get_database_stats(self) -> FactStatistics:
        """Hole umfassende Datenbank-Statistiken mit Source Detection"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Gesamtzahl der Fakten
            cursor.execute("SELECT COUNT(*) FROM facts")
            total_count = cursor.fetchone()[0]
            
            # Neueste Fakten mit Source Detection
            recent_facts_with_source = []
            if total_count != self.last_count:
                cursor.execute("""
                    SELECT statement
                    FROM facts 
                    ORDER BY rowid DESC 
                    LIMIT 10
                """)
                recent_raw = cursor.fetchall()
                
                for (stmt,) in recent_raw:
                    source = self.source_detector.detect_source_heuristic(stmt)
                    recent_facts_with_source.append((stmt, source))
                    
                    # Update LLM stats für neue Fakten
                    if total_count > self.last_count:
                        base_source = source.split(' ')[0]
                        self.llm_stats[base_source] += 1
            else:
                recent_facts_with_source = self.recent_facts_cache
            
            # Top-Prädikate
            predicates = {}
            if total_count % 10 == 0 or not self.predicate_cache:
                cursor.execute("""
                    SELECT 
                        CASE 
                            WHEN INSTR(statement, '(') > 0 
                            THEN SUBSTR(statement, 1, INSTR(statement, '(') - 1)
                            ELSE 'Unknown'
                        END as pred,
                        COUNT(*) as count
                    FROM facts
                    WHERE pred IS NOT NULL AND pred != ''
                    GROUP BY pred
                    ORDER BY count DESC
                    LIMIT 5
                """)
                predicates = dict(cursor.fetchall())
                self.predicate_cache = predicates
            else:
                predicates = self.predicate_cache
            
            conn.close()
            
            # Session-Statistiken
            diff = total_count - self.last_count
            if diff > 0:
                self.session_added += diff
            elif diff < 0:
                self.session_removed += abs(diff)
            
            # Wachstumsrate
            runtime = time.time() - self.start_time
            growth_rate = (total_count - self.start_count) / (runtime / 60) if runtime > 60 else 0
            
            # Cache update
            self.recent_facts_cache = recent_facts_with_source
            
            return FactStatistics(
                total_count=total_count,
                recent_facts=recent_facts_with_source,
                predicates=predicates,
                growth_rate=growth_rate,
                session_added=self.session_added,
                session_removed=self.session_removed,
                last_update=datetime.now(),
                llm_stats=dict(self.llm_stats)
            )
            
        except Exception as e:
            print(f"\nDEBUG: Database error: {e}")
            return FactStatistics(
                total_count=self.last_count,
                recent_facts=self.recent_facts_cache,
                predicates=self.predicate_cache,
                growth_rate=0,
                session_added=self.session_added,
                session_removed=self.session_removed,
                last_update=datetime.now(),
                llm_stats=dict(self.llm_stats)
            )
    
    def format_duration(self, seconds: float) -> str:
        """Formatiere Laufzeit in lesbares Format"""
        if seconds < 60:
            return f"{int(seconds)}s"
        elif seconds < 3600:
            return f"{int(seconds/60)}m {int(seconds%60)}s"
        else:
            hours = int(seconds / 3600)
            minutes = int((seconds % 3600) / 60)
            return f"{hours}h {minutes}m"
    
    def draw_header(self):
        """Zeichne den Header-Bereich"""
        self.write_line(1, "="*80, 'header')
        self.write_line(2, " HAK-GAL KB MONITOR with LLM Source Detection ".center(80), 'header')
        self.write_line(3, "="*80, 'header')
    
    def draw_statistics(self, stats: FactStatistics, runtime: float):
        """Zeichne Statistik-Bereich"""
        # Basis-Informationen
        self.write_line(5, f"📊 DATABASE STATUS", 'info')
        self.write_line(6, f"   Total Facts: {stats.total_count:,}")
        self.write_line(7, f"   Last Update: {stats.last_update.strftime('%H:%M:%S')}")
        
        # LLM Source Status
        ollama_running = self.source_detector.check_ollama_running()
        ollama_status = "✅ Running" if ollama_running else "❌ Stopped"
        ollama_color = 'ollama' if ollama_running else 'error'
        
        self.write_line(9, f"🤖 LLM STATUS", 'info')
        self.write_line(10, f"   Ollama: {ollama_status}", ollama_color)
        self.write_line(11, f"   Cloud APIs: ✅ Available", 'cloud')
        
        # Session-Statistiken mit LLM-Breakdown
        self.write_line(13, f"📈 SESSION STATISTICS", 'info')
        self.write_line(14, f"   Runtime: {self.format_duration(runtime)}")
        self.write_line(15, f"   Facts Added: +{stats.session_added}", 'success')
        
        # LLM Source Breakdown
        if stats.llm_stats:
            self.write_line(16, f"   Sources:")
            row = 17
            for source, count in stats.llm_stats.items():
                color = 'ollama' if source == 'Ollama' else 'cloud'
                percentage = (count / stats.session_added * 100) if stats.session_added > 0 else 0
                self.write_line(row, f"      {source}: {count} ({percentage:.0f}%)", color)
                row += 1
        
        if runtime > 60:
            self.write_line(19, f"   Growth Rate: {stats.growth_rate:.2f} facts/minute")
    
    def draw_predicates(self, stats: FactStatistics):
        """Zeichne Top-Prädikate"""
        self.write_line(21, f"🔤 TOP PREDICATES", 'info')
        row = 22
        if stats.predicates:
            for predicate, count in list(stats.predicates.items())[:3]:
                display_pred = predicate if len(predicate) <= 30 else predicate[:27] + "..."
                self.write_line(row, f"   {display_pred}: {count} facts")
                row += 1
    
    def draw_recent_facts(self, stats: FactStatistics):
        """Zeichne neueste Fakten mit Source"""
        if stats.recent_facts:
            self.write_line(26, f"📝 RECENT FACTS (with source)", 'info')
            row = 27
            for fact, source in stats.recent_facts[:3]:
                # Bestimme Farbe basierend auf Quelle
                if 'Ollama' in source:
                    color = 'ollama'
                    icon = '🖥️'
                elif 'Cloud' in source or 'Gemini' in source:
                    color = 'cloud'
                    icon = '☁️'
                else:
                    color = None
                    icon = '❓'
                
                # Kürze langen Fakt
                display_fact = fact if len(fact) <= 50 else fact[:47] + "..."
                self.write_line(row, f"   {icon} {display_fact}", color)
                self.write_line(row + 1, f"      Source: {source}")
                row += 2
    
    def draw_status_bar(self, diff: int):
        """Zeichne Status-Bar am unteren Rand"""
        if diff > 0:
            status = f"✅ {diff} new facts added!"
            color = 'success'
        elif diff < 0:
            status = f"⚠️ {abs(diff)} facts removed!"
            color = 'warning'
        else:
            status = "💤 Waiting for changes..."
            color = 'info'
        
        self.write_line(33, "─"*80)
        self.write_line(34, f" {status} | Refresh: {self.update_interval}s | Press Ctrl+C to exit ".center(80), color)
        self.write_line(35, "─"*80)
    
    def initialize_display(self):
        """Initialisiere das Display beim ersten Durchlauf"""
        self.clear_screen()
        self.draw_header()
        # Reserviere Platz für alle Zeilen
        for i in range(4, 36):
            self.write_line(i, "")
    
    def display_update(self):
        """Hauptanzeigeroutine"""
        stats = self.get_database_stats()
        runtime = time.time() - self.start_time
        
        if self.first_run:
            self.start_count = stats.total_count
            self.last_count = stats.total_count
            self.initialize_display()
            self.first_run = False
        
        # Berechne Änderungen
        diff = stats.total_count - self.last_count
        
        # Update Display-Bereiche
        self.draw_statistics(stats, runtime)
        self.draw_predicates(stats)
        self.draw_recent_facts(stats)
        self.draw_status_bar(diff)
        
        # Speichere für nächsten Durchlauf
        self.last_count = stats.total_count
        
        # Cursor ans Ende
        self.move_cursor(36)
    
    def run(self):
        """Hauptschleife des Monitors"""
        try:
            print("Starting HAK-GAL Facts Monitor with LLM Source Detection...")
            print(f"Connecting to database: {self.db_path}")
            
            # Test-Verbindung
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM facts")
            initial_count = cursor.fetchone()[0]
            conn.close()
            
            print(f"✅ Connected! Found {initial_count:,} facts")
            
            # Check Ollama status
            if self.source_detector.check_ollama_running():
                print("🖥️ Ollama is running (local inference active)")
            else:
                print("☁️ Ollama not running (using cloud APIs)")
            
            time.sleep(2)
            
            # Hauptschleife
            while True:
                self.display_update()
                time.sleep(self.update_interval)
                
        except KeyboardInterrupt:
            self.write_line(37, "\n✋ Monitor stopped by user.", 'warning')
            sys.exit(0)
        except sqlite3.Error as e:
            print(f"\n❌ Database Error: {e}")
            sys.exit(1)
        except Exception as e:
            print(f"\n❌ Unexpected Error: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

def main():
    """Hauptfunktion"""
    import argparse
    
    parser = argparse.ArgumentParser(description='HAK-GAL KB Monitor with LLM Source Detection')
    parser.add_argument('--db', type=str, help='Pfad zur Datenbank')
    parser.add_argument('--interval', type=int, default=5, help='Update-Intervall in Sekunden')
    
    args = parser.parse_args()
    
    monitor = EnhancedFactsMonitor(
        db_path=args.db,
        update_interval=args.interval
    )
    monitor.run()

if __name__ == "__main__":
    main()
