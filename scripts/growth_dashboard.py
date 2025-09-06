#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
HAK-GAL Growth Dashboard - Zeigt Monitor + Experiment-Status kombiniert
"""

import sqlite3
import requests
import time
import sys
import os
import json
import threading
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, field

@dataclass
class ExperimentStatus:
    """Status des laufenden Experiments"""
    running: bool = False
    current_cycle: int = 0
    total_cycles: int = 0
    topic: str = ""
    facts_added: int = 0
    facts_rejected: int = 0
    last_fact: str = ""
    start_time: Optional[datetime] = None

@dataclass 
class MonitorData:
    """Monitor-Daten"""
    total_facts: int = 0
    recent_facts: List[str] = field(default_factory=list)
    growth_rate: float = 0.0
    session_added: int = 0

class GrowthDashboard:
    """Kombiniertes Dashboard für Monitor + Experiments"""
    
    def __init__(self):
        self.db_path = r"D:\MCP Mods\HAK_GAL_HEXAGONAL\hexagonal_kb.db"
        self.api_base = "http://localhost:5002/api"
        
        # Status
        self.monitor_data = MonitorData()
        self.experiment_status = ExperimentStatus()
        self.last_fact_count = 0
        self.start_time = time.time()
        self.start_count = 0
        
        # Display
        self.colors = {
            'header': '\033[36m',    # Cyan
            'success': '\033[32m',   # Grün  
            'warning': '\033[33m',   # Gelb
            'error': '\033[31m',     # Rot
            'info': '\033[94m',      # Blau
            'reset': '\033[0m'       # Reset
        }
    
    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def write_line(self, row: int, text: str, color: str = None):
        """Schreibe Text in bestimmte Zeile"""
        sys.stdout.write(f"\033[{row};0H\033[K")  # Position + Clear
        if color and color in self.colors:
            text = f"{self.colors[color]}{text}{self.colors['reset']}"
        sys.stdout.write(text)
        sys.stdout.flush()
    
    def check_api_status(self) -> bool:
        """Prüfe ob API läuft"""
        try:
            response = requests.get(f"{self.api_base}/system/status", timeout=1)
            return response.status_code == 200
        except:
            return False
    
    def check_experiment_running(self) -> bool:
        """Prüfe ob ein Experiment läuft (heuristisch)"""
        # Checke ob in den letzten 10 Sekunden neue Fakten mit source "cycle_" oder "seed_" hinzugefügt wurden
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Prüfe die letzten 10 Fakten
            cursor.execute("""
                SELECT statement, context 
                FROM facts 
                ORDER BY rowid DESC 
                LIMIT 10
            """)
            recent = cursor.fetchall()
            conn.close()
            
            for fact, context in recent:
                if context and ('cycle_' in context or 'seed_experiment' in context):
                    return True
            return False
        except:
            return False
    
    def update_monitor_data(self):
        """Update Monitor-Daten aus DB"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Fakten zählen
            cursor.execute("SELECT COUNT(*) FROM facts")
            total = cursor.fetchone()[0]
            
            # Neueste Fakten
            cursor.execute("SELECT statement FROM facts ORDER BY rowid DESC LIMIT 5")
            recent = [row[0][:60] + "..." if len(row[0]) > 60 else row[0] 
                     for row in cursor.fetchall()]
            
            conn.close()
            
            # Update Monitor-Daten
            if self.start_count == 0:
                self.start_count = total
                self.last_fact_count = total
            
            diff = total - self.last_fact_count
            if diff > 0:
                self.monitor_data.session_added += diff
            
            runtime = time.time() - self.start_time
            growth_rate = (total - self.start_count) / (runtime / 60) if runtime > 60 else 0
            
            self.monitor_data.total_facts = total
            self.monitor_data.recent_facts = recent
            self.monitor_data.growth_rate = growth_rate
            self.last_fact_count = total
            
        except Exception as e:
            print(f"DB Error: {e}")
    
    def draw_header(self):
        """Header zeichnen"""
        self.write_line(1, "="*80, 'header')
        self.write_line(2, " HAK-GAL GROWTH DASHBOARD - Monitor + Experiments ".center(80), 'header')
        self.write_line(3, "="*80, 'header')
    
    def draw_monitor_section(self):
        """Monitor-Bereich"""
        self.write_line(5, "📊 KNOWLEDGE BASE STATUS", 'info')
        self.write_line(6, f"   Total Facts: {self.monitor_data.total_facts:,}")
        self.write_line(7, f"   Session Added: +{self.monitor_data.session_added}", 'success')
        
        if self.monitor_data.growth_rate > 0:
            self.write_line(8, f"   Growth Rate: {self.monitor_data.growth_rate:.1f} facts/min")
        
        # Recent Facts
        self.write_line(10, "📝 RECENT ADDITIONS", 'info')
        for i, fact in enumerate(self.monitor_data.recent_facts[:3], start=11):
            self.write_line(i, f"   • {fact}")
    
    def draw_experiment_section(self):
        """Experiment-Status Bereich"""
        self.write_line(15, "🧪 EXPERIMENT STATUS", 'info')
        
        # Check API
        api_running = self.check_api_status()
        api_status = "✅ Online" if api_running else "❌ Offline"
        api_color = 'success' if api_running else 'error'
        self.write_line(16, f"   API Server: {api_status}", api_color)
        
        # Check Experiment
        exp_running = self.check_experiment_running()
        if exp_running:
            self.write_line(17, "   Experiment: 🔄 RUNNING", 'warning')
            self.write_line(18, "   (Growth experiment detected from context)")
        else:
            self.write_line(17, "   Experiment: 💤 Not running", 'info')
            self.write_line(18, "   Run: python focused_growth_experiment.py")
    
    def draw_commands_section(self):
        """Befehle-Bereich"""
        self.write_line(20, "⌨️  COMMANDS", 'info')
        self.write_line(21, "   Terminal 1: python direct_monitor.py")
        self.write_line(22, "   Terminal 2: python focused_growth_experiment.py")
        self.write_line(23, "   Terminal 3: python growth_dashboard.py (this)")
    
    def draw_status_bar(self):
        """Status-Bar"""
        runtime = int(time.time() - self.start_time)
        runtime_str = f"{runtime//60}m {runtime%60}s"
        
        self.write_line(25, "─"*80)
        status = f"Runtime: {runtime_str} | Refresh: 3s | Press Ctrl+C to exit"
        self.write_line(26, status.center(80), 'info')
        self.write_line(27, "─"*80)
    
    def display_update(self):
        """Update gesamtes Display"""
        self.update_monitor_data()
        
        # Zeichne alle Bereiche
        self.draw_monitor_section()
        self.draw_experiment_section()
        self.draw_commands_section()
        self.draw_status_bar()
        
        # Cursor ans Ende
        sys.stdout.write("\033[28;0H")
    
    def run(self):
        """Hauptschleife"""
        try:
            print("Starting HAK-GAL Growth Dashboard...")
            print("Checking database connection...")
            
            # Test DB
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM facts")
            count = cursor.fetchone()[0]
            conn.close()
            
            print(f"✅ Connected! {count:,} facts found")
            time.sleep(1)
            
            # Initialisiere Display
            self.clear_screen()
            self.draw_header()
            
            # Hauptschleife
            while True:
                self.display_update()
                time.sleep(3)
                
        except KeyboardInterrupt:
            print("\n\n✋ Dashboard stopped.")
            sys.exit(0)
        except Exception as e:
            print(f"\n❌ Error: {e}")
            sys.exit(1)

def main():
    dashboard = GrowthDashboard()
    dashboard.run()

if __name__ == "__main__":
    main()
