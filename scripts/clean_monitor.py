#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
HAK-GAL Clean Facts Monitor
===========================
Zeigt nur echte, verifizierte Metriken direkt aus der Datenbank
Keine Heuristiken, keine Vermutungen - nur Fakten!
"""

import sqlite3
import time
import sys
import os
from datetime import datetime
from collections import defaultdict
from typing import List, Dict, Tuple

class CleanFactsMonitor:
    """Sauberer Monitor mit direkten DB-Metriken"""
    
    def __init__(self, db_path: str = None, interval: int = 2):
        self.db_path = db_path or r"D:\MCP Mods\HAK_GAL_HEXAGONAL\hexagonal_kb.db"
        self.interval = interval
        
        # Session tracking
        self.start_time = time.time()
        self.start_count = 0
        self.last_count = 0
        self.session_facts = []
        self.first_run = True
        
    def clear_screen(self):
        """Bildschirm löschen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def get_facts_count(self) -> int:
        """Hole exakte Anzahl der Fakten aus DB"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM facts")
            count = cursor.fetchone()[0]
            conn.close()
            return count
        except:
            return 0
    
    def get_recent_facts(self, limit: int = 5) -> List[str]:
        """Hole die neuesten Fakten"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT statement 
                FROM facts 
                ORDER BY rowid DESC 
                LIMIT ?
            """, (limit,))
            facts = [row[0] for row in cursor.fetchall()]
            conn.close()
            return facts
        except:
            return []
    
    def get_top_predicates(self, limit: int = 10) -> List[Tuple[str, int]]:
        """Hole die häufigsten Prädikate"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    SUBSTR(statement, 1, INSTR(statement, '(') - 1) as predicate,
                    COUNT(*) as count
                FROM facts
                WHERE INSTR(statement, '(') > 0
                GROUP BY predicate
                ORDER BY count DESC
                LIMIT ?
            """, (limit,))
            predicates = cursor.fetchall()
            conn.close()
            return predicates
        except:
            return []
    
    def get_growth_stats(self) -> Dict:
        """Berechne Wachstums-Statistiken"""
        runtime = time.time() - self.start_time
        total_added = self.last_count - self.start_count
        
        # Wachstumsraten
        facts_per_minute = (total_added / (runtime / 60)) if runtime > 0 else 0
        facts_per_hour = facts_per_minute * 60
        
        # Zeit bis Ziel
        current = self.last_count
        time_to_10k = ((10000 - current) / facts_per_minute) if facts_per_minute > 0 else float('inf')
        time_to_25k = ((25000 - current) / facts_per_minute) if facts_per_minute > 0 else float('inf')
        
        return {
            'runtime': runtime,
            'total_added': total_added,
            'per_minute': facts_per_minute,
            'per_hour': facts_per_hour,
            'time_to_10k': time_to_10k,
            'time_to_25k': time_to_25k
        }
    
    def format_time(self, seconds: float) -> str:
        """Formatiere Zeit in lesbares Format"""
        if seconds == float('inf'):
            return "∞"
        
        if seconds < 60:
            return f"{int(seconds)}s"
        elif seconds < 3600:
            return f"{int(seconds/60)}m"
        elif seconds < 86400:
            hours = int(seconds / 3600)
            minutes = int((seconds % 3600) / 60)
            return f"{hours}h {minutes}m"
        else:
            days = int(seconds / 86400)
            hours = int((seconds % 86400) / 3600)
            return f"{days}d {hours}h"
    
    def print_header(self):
        """Drucke Header"""
        print("=" * 80)
        print("HAK-GAL FACTS MONITOR - CLEAN VERSION".center(80))
        print("=" * 80)
    
    def print_main_stats(self, current_count: int, diff: int):
        """Drucke Haupt-Statistiken"""
        print(f"\n📊 KNOWLEDGE BASE")
        print(f"   Total Facts: {current_count:,}")
        
        if diff > 0:
            print(f"   ✅ New: +{diff} facts")
        elif diff < 0:
            print(f"   ⚠️  Removed: {abs(diff)} facts")
        else:
            print(f"   💤 No changes")
    
    def print_growth_stats(self, stats: Dict):
        """Drucke Wachstums-Statistiken"""
        print(f"\n📈 GROWTH METRICS")
        print(f"   Session Duration: {self.format_time(stats['runtime'])}")
        print(f"   Session Added: +{stats['total_added']:,} facts")
        
        if stats['per_minute'] > 0:
            print(f"   Growth Rate: {stats['per_minute']:.1f} facts/min")
            print(f"   Projected/Hour: {stats['per_hour']:.0f} facts")
            print(f"   Time to 10,000: {self.format_time(stats['time_to_10k'] * 60)}")
            print(f"   Time to 25,000: {self.format_time(stats['time_to_25k'] * 60)}")
    
    def print_predicates(self, predicates: List[Tuple[str, int]]):
        """Drucke Top-Prädikate"""
        if predicates:
            print(f"\n🏆 TOP PREDICATES")
            for i, (pred, count) in enumerate(predicates[:5], 1):
                bar_length = int(count / predicates[0][1] * 30)  # Relative Bar
                bar = "█" * bar_length
                print(f"   {i}. {pred:20} {count:4} {bar}")
    
    def print_recent_facts(self, facts: List[str]):
        """Drucke neueste Fakten"""
        if facts:
            print(f"\n📝 LATEST FACTS")
            for fact in facts[:3]:
                if len(fact) > 70:
                    fact = fact[:67] + "..."
                print(f"   • {fact}")
    
    def print_footer(self):
        """Drucke Footer"""
        print("\n" + "─" * 80)
        print(f"Update interval: {self.interval}s | Press Ctrl+C to stop")
    
    def run(self):
        """Hauptschleife"""
        try:
            # Initial check
            initial_count = self.get_facts_count()
            if initial_count == 0:
                print("❌ Cannot connect to database!")
                return
            
            self.start_count = initial_count
            self.last_count = initial_count
            
            print(f"✅ Connected to database")
            print(f"📊 Starting with {initial_count:,} facts")
            print(f"🔄 Updates every {self.interval} seconds")
            time.sleep(2)
            
            while True:
                # Clear screen
                self.clear_screen()
                
                # Get current data
                current_count = self.get_facts_count()
                diff = current_count - self.last_count
                
                # Track new facts
                if diff > 0:
                    new_facts = self.get_recent_facts(diff)
                    self.session_facts.extend(new_facts)
                
                # Print everything
                self.print_header()
                self.print_main_stats(current_count, diff)
                
                # Growth stats
                stats = self.get_growth_stats()
                self.print_growth_stats(stats)
                
                # Top predicates
                predicates = self.get_top_predicates()
                self.print_predicates(predicates)
                
                # Recent facts
                recent = self.get_recent_facts()
                self.print_recent_facts(recent)
                
                self.print_footer()
                
                # Update for next iteration
                self.last_count = current_count
                
                # Wait
                time.sleep(self.interval)
                
        except KeyboardInterrupt:
            print("\n\n✋ Monitor stopped")
            print(f"📊 Final count: {self.last_count:,} facts")
            print(f"✅ Session added: +{self.last_count - self.start_count:,} facts")
            
        except Exception as e:
            print(f"\n❌ Error: {e}")

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Clean Facts Monitor')
    parser.add_argument('--interval', type=int, default=2, 
                       help='Update interval in seconds (default: 2)')
    parser.add_argument('--db', type=str, 
                       help='Database path')
    
    args = parser.parse_args()
    
    monitor = CleanFactsMonitor(
        db_path=args.db,
        interval=args.interval
    )
    monitor.run()

if __name__ == "__main__":
    main()
