#!/usr/bin/env python3
"""
Advanced Facts Repair Script für HAK-GAL Knowledge Base
========================================================
Repariert die 118 problematischen Facts mit strukturellen Fehlern
"""

import sqlite3
import json
import re
from pathlib import Path
from datetime import datetime
import argparse

class FactsRepair:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.backup_path = f"{db_path}.repair_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.repairs = []
        
    def analyze_pattern(self, fact: str) -> tuple:
        """Analysiere das Muster des fehlerhaften Facts"""
        # Pattern 1: HasProperty(PasswordStorage(, HedWith).
        # Should be: HasProperty(PasswordStorage, HedWith).
        pattern1 = r'HasProperty\(([^(]+)\(\s*,\s*([^)]+)\)\)'
        
        # Pattern 2: HasProperty(Storage(, HedWith).).
        # Should be: HasProperty(Storage, HedWith).
        pattern2 = r'HasProperty\(([^(]+)\(\s*,\s*([^)]+)\)\.\)\.'
        
        # Pattern 3: ConsistsOf(..., OneOriginal(parental)Strand)
        # Should be: ConsistsOf(..., OneOriginalParentalStrand)
        pattern3 = r'([A-Za-z]+)\(([^)]*)\(([^)]+)\)([^)]*)\)'
        
        # Pattern 4: NetworkProtocol(TCP/IP, ...)
        # Should be: NetworkProtocol(TCP_IP, ...)
        
        if '(,' in fact:
            # This is the most common problem
            return ('double_open_paren', fact)
        elif fact.endswith('.).'):
            return ('extra_closing', fact)
        elif '/' in fact:
            return ('slash_in_name', fact)
        else:
            return ('unknown', fact)
            
    def repair_fact(self, fact: str) -> str:
        """Repariere einen fehlerhaften Fact"""
        pattern_type, _ = self.analyze_pattern(fact)
        
        if pattern_type == 'double_open_paren':
            # Fix: HasProperty(PasswordStorage(, HedWith)
            # Pattern: Something(, Something)
            # Convert to: Something, Something
            
            # Remove the problematic double opening parenthesis
            if 'HasProperty(' in fact:
                # Extract the parts
                match = re.search(r'HasProperty\(([^(]+)\(\s*,\s*([^)]+)\)', fact)
                if match:
                    arg1 = match.group(1).strip()
                    arg2 = match.group(2).strip()
                    # Remove trailing dots and parentheses
                    arg2 = arg2.rstrip(').').rstrip('.')
                    return f"HasProperty({arg1}, {arg2})."
                    
            # Generic fix for other predicates
            match = re.search(r'([A-Za-z]+)\(([^(]+)\(\s*,\s*([^)]+)\)', fact)
            if match:
                predicate = match.group(1)
                arg1 = match.group(2).strip()
                arg2 = match.group(3).strip()
                arg2 = arg2.rstrip(').').rstrip('.')
                return f"{predicate}({arg1}, {arg2})."
                
        elif pattern_type == 'extra_closing':
            # Remove extra ).
            fact = fact.replace('.).', ').')
            return fact
            
        elif pattern_type == 'slash_in_name':
            # Replace slashes with underscores
            fact = fact.replace('/', '_')
            return fact
            
        # If we can't repair it, return original
        return fact
        
    def repair_database(self, dry_run: bool = False):
        """Repariere die problematischen Facts in der Datenbank"""
        
        # Backup first
        if not dry_run:
            print(f"[BACKUP] Creating backup: {self.backup_path}")
            import shutil
            shutil.copy2(self.db_path, self.backup_path)
            print(f"[OK] Backup created")
            
        # Load problematic facts
        problem_file = "problematic_facts_20250812_051823.json"
        if not Path(problem_file).exists():
            print(f"[ERROR] Problematic facts file not found: {problem_file}")
            return
            
        with open(problem_file, 'r', encoding='utf-8') as f:
            problematic_facts = json.load(f)
            
        print(f"\n[INFO] Processing {len(problematic_facts)} problematic facts...")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        repaired = 0
        failed = 0
        
        for fact_info in problematic_facts:
            fact_id = fact_info['id']
            original = fact_info['original']
            
            # Attempt repair
            repaired_fact = self.repair_fact(original)
            
            if repaired_fact != original:
                print(f"\n[REPAIR] Fact ID {fact_id}:")
                print(f"  Original: {original[:80]}...")
                print(f"  Repaired: {repaired_fact[:80]}...")
                
                if not dry_run:
                    try:
                        # Update in database
                        cursor.execute(
                            "UPDATE facts SET statement = ? WHERE rowid = ?",
                            (repaired_fact, fact_id)
                        )
                        repaired += 1
                        self.repairs.append({
                            'id': fact_id,
                            'original': original,
                            'repaired': repaired_fact
                        })
                    except Exception as e:
                        print(f"  [ERROR] Failed to update: {e}")
                        failed += 1
                else:
                    repaired += 1
                    self.repairs.append({
                        'id': fact_id,
                        'original': original,
                        'repaired': repaired_fact
                    })
            else:
                print(f"[SKIP] Could not repair fact ID {fact_id}")
                failed += 1
                
        if not dry_run:
            conn.commit()
            print(f"\n[OK] Database updated successfully")
        else:
            print(f"\n[DRY RUN] No changes made to database")
            
        conn.close()
        
        # Save repair log
        log_file = f"repair_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(self.repairs, f, indent=2, ensure_ascii=False)
        print(f"[SAVED] Repair log saved to: {log_file}")
        
        # Summary
        print(f"\n[SUMMARY]")
        print(f"  Total problematic facts: {len(problematic_facts)}")
        print(f"  Successfully repaired: {repaired}")
        print(f"  Failed to repair: {failed}")
        
        return repaired, failed

def main():
    parser = argparse.ArgumentParser(description='Repair problematic facts in HAK-GAL database')
    parser.add_argument('--db', type=str, 
                       default='../HAK_GAL_SUITE/k_assistant.db',
                       help='Path to database')
    parser.add_argument('--dry-run', action='store_true',
                       help='Simulate repairs without changing database')
    
    args = parser.parse_args()
    
    # Find database
    db_path = Path(args.db)
    if not db_path.exists():
        # Try alternative path
        alt_path = Path('..') / 'HAK_GAL_SUITE' / 'k_assistant.db'
        if alt_path.exists():
            db_path = alt_path
        else:
            print(f"[ERROR] Database not found: {args.db}")
            return 1
            
    print(f"[DB] Using database: {db_path}")
    print("=" * 60)
    print("HAK-GAL FACTS REPAIR TOOL")
    print("=" * 60)
    
    repairer = FactsRepair(str(db_path))
    repaired, failed = repairer.repair_database(dry_run=args.dry_run)
    
    if repaired > 0:
        print(f"\n[SUCCESS] Repair process completed!")
        if args.dry_run:
            print("Run without --dry-run to apply repairs")
    else:
        print(f"\n[WARNING] No facts could be repaired automatically")
        print("Manual intervention may be required")
        
    return 0 if repaired > 0 else 1

if __name__ == "__main__":
    import sys
    sys.exit(main())