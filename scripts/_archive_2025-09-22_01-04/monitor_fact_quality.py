#!/usr/bin/env python
"""
Real-time Fact Quality Monitor
===============================
Überwacht die Qualität neuer Facts in Echtzeit
"""

import sqlite3
import time
from pathlib import Path
from datetime import datetime
import os

def monitor_fact_quality():
    """Monitor fact quality in real-time"""
    
    db_path = Path("hexagonal_kb.db")
    
    if not db_path.exists():
        print("❌ Database not found!")
        return
    
    print("="*70)
    print("📊 REAL-TIME FACT QUALITY MONITOR")
    print("="*70)
    print("Press Ctrl+C to stop monitoring\n")
    
    last_id = 0
    bad_patterns = ['Update', 'X1', 'X2', 'X3', 'FactQuery', 'Test', 'Debug']
    good_patterns = ['IsA', 'HasProperty', 'Causes', 'RelatedTo', 'Contains', 
                    'PartOf', 'UsedFor', 'LocatedIn', 'CreatedBy', 'Requires']
    
    good_count = 0
    bad_count = 0
    total_new = 0
    
    try:
        while True:
            with sqlite3.connect(str(db_path)) as conn:
                # Get new facts since last check
                cursor = conn.execute("""
                    SELECT id, statement, confidence, source 
                    FROM facts 
                    WHERE id > ?
                    ORDER BY id
                """, (last_id,))
                
                new_facts = cursor.fetchall()
                
                if new_facts:
                    os.system('cls' if os.name == 'nt' else 'clear')
                    print("="*70)
                    print(f"📊 FACT QUALITY MONITOR - {datetime.now().strftime('%H:%M:%S')}")
                    print("="*70)
                    
                    for fact_id, statement, confidence, source in new_facts:
                        last_id = fact_id
                        total_new += 1
                        
                        # Analyze quality
                        is_bad = any(bad in statement for bad in bad_patterns)
                        is_good = any(good in statement for good in good_patterns)
                        
                        if is_bad:
                            bad_count += 1
                            quality = "❌ BAD"
                            color = "\033[91m"  # Red
                        elif is_good:
                            good_count += 1
                            quality = "✅ GOOD"
                            color = "\033[92m"  # Green
                        else:
                            quality = "⚠️ NEUTRAL"
                            color = "\033[93m"  # Yellow
                        
                        # Print fact with quality indicator
                        print(f"{color}[{fact_id}] {quality}: {statement[:80]}\033[0m")
                        if confidence:
                            print(f"    Confidence: {confidence:.2f}")
                    
                    # Statistics
                    print("\n" + "-"*70)
                    print("📈 SESSION STATISTICS:")
                    print(f"  Total New Facts: {total_new}")
                    print(f"  ✅ Good Quality: {good_count} ({(good_count/total_new*100):.1f}%)")
                    print(f"  ❌ Bad Quality: {bad_count} ({(bad_count/total_new*100):.1f}%)")
                    print(f"  ⚠️ Neutral: {total_new - good_count - bad_count}")
                    
                    quality_score = (good_count / total_new * 100) if total_new > 0 else 0
                    
                    print(f"\n  📊 QUALITY SCORE: {quality_score:.1f}%")
                    
                    if quality_score < 50:
                        print("\n  🚨 WARNING: Quality too low! Consider stopping governor!")
                    elif quality_score < 70:
                        print("\n  ⚠️ Quality could be better. Check engine configuration.")
                    else:
                        print("\n  ✅ Good quality! Keep going!")
                    
                    # Get current fact count
                    cursor = conn.execute("SELECT COUNT(*) FROM facts")
                    total_facts = cursor.fetchone()[0]
                    print(f"\n  📦 Total Facts in DB: {total_facts:,}")
                    
                    # Learning rate
                    if total_new > 0:
                        print(f"  ⚡ Current Rate: ~{total_new} facts in last check")
            
            # Wait 10 seconds before next check
            time.sleep(10)
            
    except KeyboardInterrupt:
        print("\n\n" + "="*70)
        print("MONITORING STOPPED")
        print("="*70)
        print(f"Final Statistics:")
        print(f"  Total Monitored: {total_new}")
        print(f"  Good Quality: {good_count} ({(good_count/total_new*100):.1f}%)" if total_new > 0 else "")
        print(f"  Bad Quality: {bad_count} ({(bad_count/total_new*100):.1f}%)" if total_new > 0 else "")

if __name__ == "__main__":
    monitor_fact_quality()
