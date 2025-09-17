#!/usr/bin/env python3
"""
Cleanup duplicate facts with reordered arguments
"""
import sqlite3
from pathlib import Path
import json
import hashlib
import argparse
from datetime import datetime

def normalize_fact(statement):
    """Normalize fact by sorting arguments within parentheses"""
    if '(' in statement and ')' in statement:
        prefix = statement[:statement.index('(')]
        args_str = statement[statement.index('(')+1:statement.rindex(')')]
        suffix = statement[statement.rindex(')'):]
        
        # Split arguments and sort them
        args = [arg.strip() for arg in args_str.split(',')]
        args_sorted = sorted(args)
        
        # Reconstruct normalized statement
        return f"{prefix}({', '.join(args_sorted)}){suffix}"
    return statement

def main():
    parser = argparse.ArgumentParser(description='Cleanup duplicate facts')
    parser.add_argument('--apply', action='store_true', help='Actually remove duplicates')
    parser.add_argument('--backup', action='store_true', default=True, help='Create backup before cleanup')
    args = parser.parse_args()
    
    db_path = Path(r"D:\MCP Mods\HAK_GAL_HEXAGONAL\hexagonal_kb.db")
    
    print("="*60)
    print("DUPLICATE CLEANUP " + ("EXECUTION" if args.apply else "ANALYSIS"))
    print("="*60)
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    # Get all facts
    cursor.execute("SELECT statement FROM facts")
    all_facts = cursor.fetchall()
    
    print(f"Total facts: {len(all_facts):,}")
    
    # Find duplicates
    normalized_map = {}
    duplicates = []
    
    for (statement,) in all_facts:
        normalized = normalize_fact(statement)
        if normalized in normalized_map:
            duplicates.append((normalized_map[normalized], statement))
        else:
            normalized_map[normalized] = statement
    
    print(f"Unique normalized facts: {len(normalized_map):,}")
    print(f"Duplicates found: {len(duplicates):,}")
    
    if duplicates:
        print("\nExample duplicates:")
        for original, duplicate in duplicates[:10]:
            print(f"  {original}")
            print(f"  = {duplicate}")
            print()
    
    # Calculate space savings
    if duplicates:
        reduction_pct = (len(duplicates) / len(all_facts)) * 100
        print(f"Potential reduction: {reduction_pct:.1f}%")
        print(f"Facts after cleanup: {len(normalized_map):,}")
    
    # Apply cleanup if requested
    if args.apply and duplicates:
        print("\n" + "="*60)
        print("APPLYING CLEANUP")
        print("="*60)
        
        # Create backup first
        if args.backup:
            backup_path = db_path.with_suffix('.db.backup_' + datetime.now().strftime('%Y%m%d_%H%M%S'))
            print(f"Creating backup: {backup_path.name}")
            import shutil
            shutil.copy2(db_path, backup_path)
            print("✅ Backup created")
        
        # Delete duplicates
        print(f"\nDeleting {len(duplicates):,} duplicate facts...")
        
        deleted_count = 0
        for original, duplicate in duplicates:
            try:
                cursor.execute("DELETE FROM facts WHERE statement = ? AND statement != ?", 
                              (duplicate, original))
                deleted_count += cursor.rowcount
                
                # Progress indicator every 100 deletions
                if deleted_count % 100 == 0:
                    print(f"  Deleted: {deleted_count:,} facts...")
                    
            except Exception as e:
                print(f"Error deleting '{duplicate}': {e}")
        
        # Commit changes
        conn.commit()
        
        # Verify new count
        cursor.execute("SELECT COUNT(*) FROM facts")
        new_count = cursor.fetchone()[0]
        
        print(f"\n✅ Cleanup complete!")
        print(f"  Deleted: {deleted_count:,} duplicates")
        print(f"  New total: {new_count:,} facts")
        print(f"  Reduction: {((len(all_facts) - new_count) / len(all_facts)) * 100:.1f}%")
        
        # Run VACUUM to reclaim space
        print("\nOptimizing database...")
        cursor.execute("VACUUM")
        print("✅ Database optimized")
    
    elif args.apply:
        print("\n✅ No duplicates to remove!")
    else:
        print("\n💡 Run with --apply to remove duplicates")
    
    conn.close()
    
    # Save report
    report = {
        'timestamp': datetime.now().isoformat(),
        'mode': 'applied' if args.apply else 'analysis',
        'total_facts': len(all_facts),
        'unique_facts': len(normalized_map),
        'duplicates': len(duplicates),
        'reduction_percent': (len(duplicates) / len(all_facts)) * 100 if duplicates else 0,
        'examples': [(orig, dup) for orig, dup in duplicates[:20]]
    }
    
    report_path = Path("cleanup_report.json")
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\nReport saved to: {report_path}")
    print("="*60)

if __name__ == "__main__":
    main()
