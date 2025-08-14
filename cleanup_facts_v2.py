#!/usr/bin/env python3
"""
Facts Cleanup Script V2 für HAK-GAL Knowledge Base
==================================================
Angepasst für tatsächliche DB-Struktur:
- Tabelle: facts
- Spalten: statement, context, fact_metadata
"""

import sqlite3
import re
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import List, Tuple, Dict, Any

class FactsCleanerV2:
    """Bereinigt problematische Facts in der Knowledge Base"""
    
    def __init__(self, db_path: str = "k_assistant.db"):
        self.db_path = db_path
        self.backup_path = f"{db_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.stats = {
            'total': 0,
            'encoding_fixed': 0,
            'structure_fixed': 0,
            'unchanged': 0,
            'problematic': []
        }
        
        # Encoding-Ersetzungen
        self.encoding_replacements = {
            '²': '2',          # Superscript 2
            '³': '3',          # Superscript 3
            '°': 'deg',        # Degree symbol
            '—': '-',          # Em-dash zu Hyphen
            '–': '-',          # En-dash zu Hyphen
            ''': "'",          # Smart quote
            ''': "'",          # Smart quote
            '"': '"',          # Smart quote
            '"': '"',          # Smart quote
            'â€™': "'",        # Broken UTF-8
            'â€"': '-',        # Broken UTF-8
            'â€œ': '"',        # Broken UTF-8
            'â€': '"',         # Broken UTF-8
            '…': '...',        # Ellipsis
            '×': 'x',          # Multiplication sign
            '÷': '/',          # Division sign
            '±': '+/-',        # Plus-minus
            '≈': '~',          # Approximately
            '≠': '!=',         # Not equal
            '≤': '<=',         # Less or equal
            '≥': '>=',         # Greater or equal
            '∞': 'infinity',   # Infinity
            'µ': 'micro',      # Micro sign
            '€': 'EUR',        # Euro
            '£': 'GBP',        # Pound
            '¥': 'JPY',        # Yen
        }
        
    def backup_database(self):
        """Erstellt Backup der Datenbank"""
        print(f"[BACKUP] Creating backup: {self.backup_path}")
        try:
            import shutil
            shutil.copy2(self.db_path, self.backup_path)
            print(f"[OK] Backup created successfully")
            return True
        except Exception as e:
            print(f"[ERROR] Backup failed: {e}")
            return False
    
    def fix_encoding(self, text: str) -> str:
        """Behebt Encoding-Probleme"""
        original = text
        
        # Ersetze problematische Zeichen
        for old, new in self.encoding_replacements.items():
            if old in text:
                text = text.replace(old, new)
        
        # ASCII-Check: Zeige welche non-ASCII Zeichen noch da sind
        non_ascii = [c for c in text if ord(c) > 127]
        if non_ascii:
            # Ersetze verbleibende non-ASCII durch ?
            text = ''.join(char if ord(char) < 128 else '?' for char in text)
        
        if text != original:
            self.stats['encoding_fixed'] += 1
            
        return text
    
    def balance_parentheses(self, text: str) -> str:
        """Balanciert Klammern in einem Text"""
        open_count = text.count('(')
        close_count = text.count(')')
        
        if open_count > close_count:
            # Füge fehlende schließende Klammern hinzu
            text = text + ')' * (open_count - close_count)
        elif close_count > open_count:
            # Entferne überschüssige schließende Klammern
            for _ in range(close_count - open_count):
                idx = text.rfind(')')
                if idx != -1:
                    text = text[:idx] + text[idx+1:]
        
        return text
    
    def fix_structure(self, fact: str) -> str:
        """Behebt strukturelle Probleme in Facts"""
        original = fact
        
        # Entferne mehrfache Spaces
        fact = re.sub(r'\s+', ' ', fact)
        
        # Fix für Predicates mit Slash (z.B. TCP/IP -> TCP_IP)
        # Pattern: Predicate(Args).
        match = re.match(r'^([A-Za-z]+(?:/[A-Za-z]+)*)\((.*)\)\.$', fact)
        if match:
            predicate = match.group(1).replace('/', '_')
            args = match.group(2)
            fact = f"{predicate}({args})."
        
        # Balanciere Klammern
        fact = self.balance_parentheses(fact)
        
        # Stelle sicher dass Fact mit ). endet
        if not fact.endswith(').'):
            if fact.endswith(')'):
                fact = fact + '.'
            elif fact.endswith('.'):
                # Prüfe ob ) vor . fehlt
                if '(' in fact and ')' not in fact[-3:]:
                    fact = fact[:-1] + ').'
        
        if fact != original:
            self.stats['structure_fixed'] += 1
            
        return fact
    
    def validate_fact(self, fact: str) -> Tuple[bool, str]:
        """Validiert ein Fact"""
        # Basis-Pattern für Facts: Predicate(Args).
        pattern = r'^[A-Za-z_][A-Za-z0-9_]*\([^)]*\)\.$'
        
        if not re.match(pattern, fact):
            return False, "Invalid fact structure"
        
        # Prüfe balancierte Klammern
        if fact.count('(') != fact.count(')'):
            return False, "Unbalanced parentheses"
        
        # Prüfe auf problematische Zeichen
        if any(ord(c) > 127 for c in fact):
            return False, "Contains non-ASCII characters"
        
        return True, "OK"
    
    def clean_facts(self, dry_run: bool = False):
        """Hauptfunktion zum Bereinigen der Facts"""
        
        if not dry_run and not self.backup_database():
            print("[ABORT] Could not create backup")
            return
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Hole alle Facts mit rowid als ID
        cursor.execute("SELECT rowid, statement, context, fact_metadata FROM facts")
        facts = cursor.fetchall()
        self.stats['total'] = len(facts)
        
        print(f"\n[INFO] Processing {len(facts)} facts...")
        
        updates = []
        
        for row_id, statement, context, metadata in facts:
            original_statement = statement
            
            # Phase 1: Encoding-Fixes
            statement = self.fix_encoding(statement)
            
            # Phase 2: Struktur-Fixes (wenn es wie ein Fact aussieht)
            if re.match(r'^[A-Za-z]+\(.*\)\.$', statement):
                statement = self.fix_structure(statement)
            
            # Phase 3: Validierung (nur für strukturierte Facts)
            if re.match(r'^[A-Za-z]+\(.*\)\.$', statement):
                is_valid, error_msg = self.validate_fact(statement)
                
                if not is_valid:
                    self.stats['problematic'].append({
                        'id': row_id,
                        'original': original_statement,
                        'cleaned': statement,
                        'error': error_msg
                    })
                    continue
            
            # Update wenn geändert
            if statement != original_statement:
                # Context und Metadata auch bereinigen
                clean_context = self.fix_encoding(context) if context else context
                clean_metadata = self.fix_encoding(metadata) if metadata else metadata
                
                updates.append((statement, clean_context, clean_metadata, row_id))
            else:
                self.stats['unchanged'] += 1
        
        # Zeige Statistiken
        print(f"\n[STATS] Cleanup Statistics:")
        print(f"  Total facts: {self.stats['total']}")
        print(f"  Encoding fixed: {self.stats['encoding_fixed']}")
        print(f"  Structure fixed: {self.stats['structure_fixed']}")
        print(f"  Unchanged: {self.stats['unchanged']}")
        print(f"  Problematic: {len(self.stats['problematic'])}")
        
        if self.stats['problematic']:
            print(f"\n[WARNING] {len(self.stats['problematic'])} facts could not be fixed:")
            for p in self.stats['problematic'][:5]:  # Zeige erste 5
                print(f"  ID {p['id']}: {p['error']}")
                print(f"    Original: {p['original'][:60]}...")
            
            if len(self.stats['problematic']) > 5:
                print(f"  ... and {len(self.stats['problematic']) - 5} more")
        
        if dry_run:
            print(f"\n[DRY RUN] No changes made")
            print(f"Would update {len(updates)} facts")
        else:
            if updates:
                print(f"\n[UPDATE] Applying {len(updates)} updates...")
                cursor.executemany(
                    "UPDATE facts SET statement=?, context=?, fact_metadata=? WHERE rowid=?",
                    updates
                )
                conn.commit()
                print(f"[OK] Updates applied successfully")
            else:
                print(f"\n[OK] No updates needed")
        
        # Speichere problematische Facts für manuelle Review
        if self.stats['problematic']:
            problem_file = f"problematic_facts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(problem_file, 'w', encoding='utf-8') as f:
                json.dump(self.stats['problematic'], f, indent=2, ensure_ascii=False)
            print(f"\n[SAVED] Problematic facts saved to: {problem_file}")
        
        conn.close()
        
        return self.stats

def main():
    """Hauptfunktion"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Clean HAK-GAL Facts Database V2')
    parser.add_argument('--db', default='k_assistant.db', help='Database path')
    parser.add_argument('--dry-run', action='store_true', help='Preview changes without applying')
    parser.add_argument('--encoding-only', action='store_true', help='Only fix encoding issues')
    parser.add_argument('--structure-only', action='store_true', help='Only fix structure issues')
    
    args = parser.parse_args()
    
    # Prüfe ob DB existiert
    db_path = Path(args.db)
    if not db_path.exists():
        # Versuche in HAK_GAL_SUITE zu finden
        alt_path = Path(__file__).parent.parent / 'HAK_GAL_SUITE' / args.db
        if alt_path.exists():
            db_path = alt_path
        else:
            print(f"[ERROR] Database not found: {args.db}")
            sys.exit(1)
    
    print(f"[DB] Using database: {db_path}")
    
    cleaner = FactsCleanerV2(str(db_path))
    
    if args.encoding_only:
        print("[MODE] Fixing encoding issues only")
        cleaner.fix_structure = lambda x: x
    elif args.structure_only:
        print("[MODE] Fixing structure issues only")
        cleaner.fix_encoding = lambda x: x
    
    stats = cleaner.clean_facts(dry_run=args.dry_run)
    
    print("\n[DONE] Cleanup complete!")
    
    return 0 if stats else 1

if __name__ == '__main__':
    sys.exit(main())