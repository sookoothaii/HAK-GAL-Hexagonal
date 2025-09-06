#!/usr/bin/env python
"""
Real-time Fact Quality Monitor - FIXED VERSION
===============================================
Verwendet ROWID für SQLite ohne explizite ID-Spalte
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
    
    # Get starting point
    with sqlite3.connect(str(db_path)) as conn:
        cursor = conn.execute("SELECT MAX(rowid) FROM facts")
        last_rowid = cursor.fetchone()[0] or 0
    
    bad_patterns = ['Update', 'X1', 'X2', 'X3', 'FactQuery', 'UpdateStatement', 
                   'Test', 'Debug', 'newPred', 'newArg', 'dummy', 'temp']
    good_patterns = ['IsA', 'HasProperty', 'Causes', 'RelatedTo', 'Contains', 
                    'PartOf', 'UsedFor', 'LocatedIn', 'CreatedBy', 'Requires',
                    'Influences', 'Produces', 'DependsOn', 'Enables']
    
    good_count = 0
    bad_count = 0
    total_new = 0
    
    try:
        while True:
            with sqlite3.connect(str(db_path)) as conn:
                # Get new facts since last check
                cursor = conn.execute("""
                    SELECT rowid, statement, confidence, source 
                    FROM facts 
                    WHERE rowid > ?
                    ORDER BY rowid
                """, (last_rowid,))
                
                new_facts = cursor.fetchall()
                
                if new_facts:
                    os.system('cls' if os.name == 'nt' else 'clear')
                    print("="*70)
                    print(f"📊 FACT QUALITY MONITOR - {datetime.now().strftime('%H:%M:%S')}")
                    print("="*70)
                    
                    for rowid, statement, confidence, source in new_facts:
                        last_rowid = rowid
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
                        print(f"{color}[{rowid}] {quality}: {statement[:80]}\033[0m")
                        if confidence and confidence != 1.0:
                            print(f"    Confidence: {confidence:.2f}")
                        if source and source != 'unknown':
                            print(f"    Source: {source}")
                    
                    # Statistics
                    print("\n" + "-"*70)
                    print("📈 SESSION STATISTICS:")
                    print(f"  Total New Facts: {total_new}")
                    
                    if total_new > 0:
                        print(f"  ✅ Good Quality: {good_count} ({(good_count/total_new*100):.1f}%)")
                        print(f"  ❌ Bad Quality: {bad_count} ({(bad_count/total_new*100):.1f}%)")
                        print(f"  ⚠️ Neutral: {total_new - good_count - bad_count}")
                        
                        quality_score = (good_count / total_new * 100)
                        
                        print(f"\n  📊 QUALITY SCORE: {quality_score:.1f}%")
                        
                        if quality_score < 30:
                            print("\n  🚨 CRITICAL: Quality too low! STOP GOVERNOR NOW!")
                            print("     Run: python emergency_cleanup_facts_fixed.py")
                        elif quality_score < 50:
                            print("\n  ⚠️ WARNING: Poor quality. Consider stopping.")
                        elif quality_score < 70:
                            print("\n  ⚠️ Quality could be better. Check configuration.")
                        else:
                            print("\n  ✅ Good quality! Keep going!")
                    
                    # Get current fact count
                    cursor = conn.execute("SELECT COUNT(*) FROM facts")
                    total_facts = cursor.fetchone()[0]
                    print(f"\n  📦 Total Facts in DB: {total_facts:,}")
                    
                    # Calculate rate
                    print(f"  ⚡ New facts in this batch: {len(new_facts)}")
                    
                    # Show bad patterns if any
                    if bad_count > good_count:
                        print("\n  🚨 BAD PATTERNS DOMINATING:")
                        bad_in_batch = [f for _, f, _, _ in new_facts if any(b in f for b in bad_patterns)]
                        for bad_pred in set([f.split('(')[0] for f in bad_in_batch if '(' in f]):
                            count = sum(1 for f in bad_in_batch if f.startswith(bad_pred))
                            print(f"     - {bad_pred}: {count} occurrences")
            
            # Wait before next check
            time.sleep(5)  # Check every 5 seconds
            
    except KeyboardInterrupt:
        print("\n\n" + "="*70)
        print("MONITORING STOPPED")
        print("="*70)
        print(f"Final Statistics:")
        print(f"  Total Monitored: {total_new}")
        if total_new > 0:
            print(f"  Good Quality: {good_count} ({(good_count/total_new*100):.1f}%)")
            print(f"  Bad Quality: {bad_count} ({(bad_count/total_new*100):.1f}%)")
            
            if bad_count > good_count:
                print("\n🚨 RECOMMENDATION: Clean up bad facts!")
                print("   Run: python emergency_cleanup_facts_fixed.py")
            elif good_count / total_new < 0.7:
                print("\n⚠️ RECOMMENDATION: Optimize engines")
                print("   Run: python optimize_learning_engines.py")

if __name__ == "__main__":
    monitor_fact_quality()
