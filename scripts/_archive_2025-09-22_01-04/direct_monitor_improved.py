#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
HAK-GAL Facts Monitor (Improved) - Überwacht das Wachstum der Knowledge Base
Übersichtliche, erweiterte Version mit besserer Struktur
"""

import sqlite3
import time
import sys
import os
from datetime import datetime, timedelta
from typing import List, Tuple, Dict, Optional
from dataclasses import dataclass
from collections import defaultdict

@dataclass
class FactStatistics:
    """Datenklasse für Fakten-Statistiken"""
    total_count: int
    recent_facts: List[str]
    predicates: Dict[str, int]
    growth_rate: float
    session_added: int
    session_removed: int
    last_update: datetime

class EnhancedFactsMonitor:
    """Verbesserter Knowledge Base Monitor mit erweiterter Funktionalität"""
    
    def __init__(self, db_path: Optional[str] = None, update_interval: int = 5):
        """
        Initialisierung des Monitors
        
        Args:
            db_path: Pfad zur Datenbank (None = Standard-Pfad)
            update_interval: Update-Intervall in Sekunden
        """
        self.db_path = db_path or r"D:\MCP Mods\HAK_GAL_HEXAGONAL\hexagonal_kb.db"
        self.update_interval = update_interval
        
        # Statistik-Tracking
        self.last_count = 0
        self.start_count = 0
        self.start_time = time.time()
        self.session_added = 0
        self.session_removed = 0
        self.hourly_counts = []  # Für stündliche Wachstumsrate
        self.last_hour_check = datetime.now()
        
        # Cache
        self.recent_facts_cache = []
        self.predicate_cache = {}
        
        # Display-Kontrolle
        self.first_run = True
        self.screen_lines = 25  # Anzahl der genutzten Zeilen
        
        # Farben (ANSI codes)
        self.colors = {
            'header': '\033[36m',    # Cyan
            'success': '\033[32m',   # Grün
            'warning': '\033[33m',   # Gelb
            'error': '\033[31m',     # Rot
            'info': '\033[94m',      # Blau
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
        """Hole umfassende Datenbank-Statistiken"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Gesamtzahl der Fakten
            cursor.execute("SELECT COUNT(*) FROM facts")
            total_count = cursor.fetchone()[0]
            
            # Neueste Fakten (nur bei Änderung)
            recent_facts = []
            if total_count != self.last_count:
                cursor.execute("""
                    SELECT statement, timestamp
                    FROM facts 
                    ORDER BY rowid DESC 
                    LIMIT 10
                """)
                recent_facts = [row[0] for row in cursor.fetchall()]
            else:
                recent_facts = self.recent_facts_cache
            
            # Top-Prädikate (alle 10 Updates aktualisieren)
            predicates = {}
            if total_count % 10 == 0 or not self.predicate_cache:
                cursor.execute("""
                    SELECT 
                        CASE 
                            WHEN INSTR(statement, '(') > 0 
                            THEN SUBSTR(statement, 1, INSTR(statement, '(') - 1)
                            ELSE 'Unknown'
                        END as predicate,
                        COUNT(*) as count
                    FROM facts
                    GROUP BY predicate
                    ORDER BY count DESC
                    LIMIT 5
                """)
                predicates = dict(cursor.fetchall())
                self.predicate_cache = predicates
            else:
                predicates = self.predicate_cache
            
            conn.close()
            
            # Berechne Session-Statistiken
            diff = total_count - self.last_count
            if diff > 0:
                self.session_added += diff
            elif diff < 0:
                self.session_removed += abs(diff)
            
            # Berechne Wachstumsrate (Facts pro Minute)
            runtime = time.time() - self.start_time
            growth_rate = (total_count - self.start_count) / (runtime / 60) if runtime > 60 else 0
            
            # Speichere für nächsten Durchlauf
            self.recent_facts_cache = recent_facts
            
            return FactStatistics(
                total_count=total_count,
                recent_facts=recent_facts,
                predicates=predicates,
                growth_rate=growth_rate,
                session_added=self.session_added,
                session_removed=self.session_removed,
                last_update=datetime.now()
            )
            
        except Exception as e:
            return FactStatistics(
                total_count=self.last_count,
                recent_facts=self.recent_facts_cache,
                predicates=self.predicate_cache,
                growth_rate=0,
                session_added=self.session_added,
                session_removed=self.session_removed,
                last_update=datetime.now()
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
        self.write_line(2, " HAK-GAL KNOWLEDGE BASE MONITOR - Enhanced Edition ".center(80), 'header')
        self.write_line(3, "="*80, 'header')
    
    def draw_statistics(self, stats: FactStatistics, runtime: float):
        """Zeichne Statistik-Bereich"""
        # Basis-Informationen
        self.write_line(5, f"📊 DATABASE STATUS", 'info')
        self.write_line(6, f"   Path: {self.db_path}")
        self.write_line(7, f"   Total Facts: {stats.total_count:,}")
        self.write_line(8, f"   Last Update: {stats.last_update.strftime('%H:%M:%S')}")
        
        # Session-Statistiken
        self.write_line(10, f"📈 SESSION STATISTICS", 'info')
        self.write_line(11, f"   Runtime: {self.format_duration(runtime)}")
        self.write_line(12, f"   Facts Added: +{stats.session_added}", 'success')
        self.write_line(13, f"   Facts Removed: -{stats.session_removed}", 'warning')
        
        net_change = stats.session_added - stats.session_removed
        color = 'success' if net_change > 0 else 'warning' if net_change < 0 else 'info'
        self.write_line(14, f"   Net Change: {'+' if net_change >= 0 else ''}{net_change}", color)
        
        if runtime > 60:
            self.write_line(15, f"   Growth Rate: {stats.growth_rate:.2f} facts/minute")
    
    def draw_predicates(self, stats: FactStatistics):
        """Zeichne Top-Prädikate"""
        self.write_line(17, f"🔤 TOP PREDICATES", 'info')
        row = 18
        for predicate, count in list(stats.predicates.items())[:3]:
            self.write_line(row, f"   {predicate}: {count} facts")
            row += 1
    
    def draw_recent_facts(self, stats: FactStatistics):
        """Zeichne neueste Fakten"""
        if stats.recent_facts:
            self.write_line(22, f"📝 RECENT FACTS", 'info')
            row = 23
            for fact in stats.recent_facts[:3]:
                # Kürze lange Fakten
                display_fact = fact if len(fact) <= 70 else fact[:67] + "..."
                self.write_line(row, f"   • {display_fact}")
                row += 1
    
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
        
        self.write_line(27, "─"*80)
        self.write_line(28, f" {status} | Refresh: {self.update_interval}s | Press Ctrl+C to exit ".center(80), color)
        self.write_line(29, "─"*80)
    
    def initialize_display(self):
        """Initialisiere das Display beim ersten Durchlauf"""
        self.clear_screen()
        self.draw_header()
        # Reserviere Platz für alle Zeilen
        for i in range(4, 30):
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
        self.move_cursor(30)
    
    def run(self):
        """Hauptschleife des Monitors"""
        try:
            print("Starting Enhanced HAK-GAL Facts Monitor...")
            print(f"Connecting to database: {self.db_path}")
            
            # Test-Verbindung
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM facts")
            initial_count = cursor.fetchone()[0]
            conn.close()
            
            print(f"✅ Connected! Found {initial_count:,} facts")
            time.sleep(2)
            
            # Hauptschleife
            while True:
                self.display_update()
                time.sleep(self.update_interval)
                
        except KeyboardInterrupt:
            self.write_line(31, "\n✋ Monitor stopped by user.", 'warning')
            sys.exit(0)
        except sqlite3.Error as e:
            self.write_line(31, f"\n❌ Database Error: {e}", 'error')
            sys.exit(1)
        except Exception as e:
            self.write_line(31, f"\n❌ Unexpected Error: {e}", 'error')
            sys.exit(1)

def main():
    """Hauptfunktion mit Kommandozeilen-Argumenten"""
    import argparse
    
    parser = argparse.ArgumentParser(description='HAK-GAL Knowledge Base Monitor')
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
