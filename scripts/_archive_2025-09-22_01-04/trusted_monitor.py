#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
HAK-GAL Trusted Monitor
=======================
Nur verifizierte Metriken direkt aus der SQLite-Datenbank
Keine Schätzungen, keine Heuristiken - nur Fakten!
"""

import sqlite3
import time
import sys
import os
from datetime import datetime, timedelta
from pathlib import Path

class TrustedMonitor:
    """Monitor mit 100% vertrauenswürdigen Metriken"""
    
    def __init__(self, interval: int = 2):
        self.db_path = Path(r"D:\MCP Mods\HAK_GAL_HEXAGONAL\hexagonal_kb.db")
        self.interval = interval
        
        # Session tracking
        self.start_time = datetime.now()
        self.start_count = None
        self.last_count = None
        self.max_count = 0
        self.checks = 0
        
    def get_db_stats(self):
        """Hole alle Statistiken in einer DB-Verbindung"""
        stats = {}
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 1. Fakten-Anzahl
            cursor.execute("SELECT COUNT(*) FROM facts")
            stats['total'] = cursor.fetchone()[0]
            
            # 2. Neueste 5 Fakten
            cursor.execute("""
                SELECT statement 
                FROM facts 
                ORDER BY rowid DESC 
                LIMIT 5
            """)
            stats['recent'] = [row[0] for row in cursor.fetchall()]
            
            # 3. Top 10 Prädikate mit Counts
            cursor.execute("""
                SELECT 
                    SUBSTR(statement, 1, INSTR(statement, '(') - 1) as pred,
                    COUNT(*) as cnt
                FROM facts
                WHERE INSTR(statement, '(') > 0
                GROUP BY pred
                ORDER BY cnt DESC
                LIMIT 10
            """)
            stats['predicates'] = cursor.fetchall()
            
            # 4. Datenbank-Größe
            cursor.execute("SELECT page_count * page_size FROM pragma_page_count(), pragma_page_size()")
            stats['db_size'] = cursor.fetchone()[0]
            
            conn.close()
            return stats
            
        except Exception as e:
            return {'error': str(e)}
    
    def format_size(self, bytes):
        """Formatiere Bytes in KB/MB"""
        if bytes < 1024:
            return f"{bytes} B"
        elif bytes < 1024 * 1024:
            return f"{bytes/1024:.1f} KB"
        else:
            return f"{bytes/(1024*1024):.2f} MB"
    
    def clear(self):
        """Clear screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def run(self):
        """Hauptschleife"""
        print("🚀 HAK-GAL Trusted Monitor starting...")
        print(f"📊 Database: {self.db_path.name}")
        
        # Initial check
        stats = self.get_db_stats()
        if 'error' in stats:
            print(f"❌ Database error: {stats['error']}")
            return
            
        self.start_count = stats['total']
        self.last_count = stats['total']
        self.max_count = stats['total']
        
        print(f"✅ Connected! Found {stats['total']:,} facts")
        time.sleep(2)
        
        try:
            while True:
                self.clear()
                self.checks += 1
                
                # Get fresh stats
                stats = self.get_db_stats()
                
                if 'error' in stats:
                    print(f"❌ DB Error: {stats['error']}")
                    time.sleep(self.interval)
                    continue
                
                current = stats['total']
                diff = current - self.last_count
                session_diff = current - self.start_count
                runtime = datetime.now() - self.start_time
                
                # Update max
                if current > self.max_count:
                    self.max_count = current
                
                # Header
                print("=" * 70)
                print("HAK-GAL KNOWLEDGE BASE MONITOR".center(70))
                print("=" * 70)
                
                # Main stats
                print(f"\n📊 DATABASE STATUS")
                print(f"   Facts Count:  {current:,}")
                print(f"   DB Size:      {self.format_size(stats['db_size'])}")
                print(f"   Last Check:   {datetime.now().strftime('%H:%M:%S')}")
                
                # Changes
                if diff != 0:
                    if diff > 0:
                        print(f"\n   🆕 CHANGE: +{diff} new facts!")
                    else:
                        print(f"\n   ⚠️ CHANGE: -{abs(diff)} facts removed")
                
                # Session stats
                print(f"\n📈 SESSION STATISTICS")
                print(f"   Running for:  {str(runtime).split('.')[0]}")
                print(f"   Started with: {self.start_count:,} facts")
                print(f"   Added total:  +{session_diff:,} facts")
                print(f"   Max reached:  {self.max_count:,} facts")
                print(f"   DB checks:    {self.checks}")
                
                # Growth rate
                if runtime.total_seconds() > 60:
                    rate = session_diff / (runtime.total_seconds() / 60)
                    print(f"   Growth rate:  {rate:.1f} facts/minute")
                    
                    if rate > 0:
                        to_10k = (10000 - current) / rate
                        if to_10k > 0:
                            print(f"   ETA to 10k:   {int(to_10k)} minutes")
                
                # Top predicates
                if stats['predicates']:
                    print(f"\n🏆 TOP PREDICATES")
                    for i, (pred, cnt) in enumerate(stats['predicates'][:5], 1):
                        bar_size = int(cnt / stats['predicates'][0][1] * 20)
                        bar = "▓" * bar_size + "░" * (20 - bar_size)
                        print(f"   {i}. {pred:20} {cnt:4}  {bar}")
                
                # Recent facts
                if stats['recent']:
                    print(f"\n📝 NEWEST FACTS")
                    for fact in stats['recent'][:3]:
                        display = fact if len(fact) <= 60 else fact[:57] + "..."
                        print(f"   → {display}")
                
                # Footer
                print("\n" + "─" * 70)
                print(f"Refresh: {self.interval}s | Press Ctrl+C to stop")
                
                # Update last count
                self.last_count = current
                
                # Wait
                time.sleep(self.interval)
                
        except KeyboardInterrupt:
            runtime = datetime.now() - self.start_time
            print("\n\n" + "=" * 70)
            print("SESSION SUMMARY".center(70))
            print("=" * 70)
            print(f"Duration:     {str(runtime).split('.')[0]}")
            print(f"Start count:  {self.start_count:,}")
            print(f"Final count:  {self.last_count:,}")
            print(f"Total added:  +{self.last_count - self.start_count:,}")
            print(f"Max reached:  {self.max_count:,}")
            print(f"DB checks:    {self.checks}")
            
            if runtime.total_seconds() > 0:
                rate = (self.last_count - self.start_count) / (runtime.total_seconds() / 60)
                print(f"Avg rate:     {rate:.2f} facts/minute")
            
            print("\n✅ Monitor stopped successfully")

def main():
    import argparse
    parser = argparse.ArgumentParser(description='HAK-GAL Trusted Monitor')
    parser.add_argument('--interval', '-i', type=int, default=2,
                       help='Update interval in seconds (default: 2)')
    args = parser.parse_args()
    
    if args.interval < 1:
        print("❌ Interval must be at least 1 second")
        return
        
    monitor = TrustedMonitor(interval=args.interval)
    monitor.run()

if __name__ == "__main__":
    main()
