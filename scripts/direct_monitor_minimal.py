#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
HAK-GAL Facts Monitor (Minimal) - Kompakte Version für schnelle Überwachung
"""

import sqlite3
import time
from datetime import datetime

DB_PATH = r"D:\MCP Mods\HAK_GAL_HEXAGONAL\hexagonal_kb.db"

def monitor():
    """Minimaler Monitor mit essentiellen Informationen"""
    
    def get_count():
        """Hole aktuelle Anzahl der Fakten"""
        try:
            with sqlite3.connect(DB_PATH) as conn:
                return conn.execute("SELECT COUNT(*) FROM facts").fetchone()[0]
        except:
            return -1
    
    def get_recent():
        """Hole die 3 neuesten Fakten"""
        try:
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.execute("SELECT statement FROM facts ORDER BY rowid DESC LIMIT 3")
                return [row[0][:80] for row in cursor.fetchall()]
        except:
            return []
    
    # Initialisierung
    print("\033[2J\033[H")  # Clear screen
    print("="*60)
    print("HAK-GAL MONITOR (Minimal)")
    print("="*60)
    
    start_count = get_count()
    start_time = time.time()
    last_count = start_count
    
    if start_count == -1:
        print("❌ Cannot connect to database!")
        return
    
    print(f"Start: {start_count:,} facts")
    print("-"*60)
    
    try:
        while True:
            current = get_count()
            runtime = int(time.time() - start_time)
            diff = current - last_count
            total_diff = current - start_count
            
            # Status-Zeile (überschreibt sich selbst)
            status = f"\r[{datetime.now().strftime('%H:%M:%S')}] "
            status += f"Facts: {current:,} | "
            status += f"Session: {'+' if total_diff >= 0 else ''}{total_diff} | "
            status += f"Runtime: {runtime//60}m {runtime%60}s"
            
            if diff != 0:
                status += f" | {'✅ NEW' if diff > 0 else '⚠️ REMOVED'}: {abs(diff)}"
                print(status + " "*20)  # Zeile überschreiben mit Padding
                
                # Bei Änderung: Zeige neueste Fakten
                if diff > 0:
                    recent = get_recent()
                    for fact in recent[:2]:
                        print(f"  → {fact}")
                    print("-"*60)
            else:
                print(status, end="", flush=True)
            
            last_count = current
            time.sleep(5)
            
    except KeyboardInterrupt:
        print(f"\n\nFinal: {current:,} facts (Net: {'+' if total_diff >= 0 else ''}{total_diff})")
        print("Monitor stopped.")

if __name__ == "__main__":
    monitor()
