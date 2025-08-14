#!/usr/bin/env python3
"""
Facts Cleanup Script für HAK-GAL Knowledge Base
===============================================
Behebt Encoding- und Struktur-Probleme in Facts

Identifizierte Probleme:
- 217 Facts (17.6%) mit Pattern-Fehlern
- 62 Facts (5%) mit Encoding-Problemen
"""

import sqlite3
import re
import sys
from pathlib import Path
from datetime import datetime
import json
from typing import List, Tuple, Dict, Any

class FactsCleaner:
    """Bereinigt problematische Facts in der Knowledge Base"""
    
    def __init__(self, db_path: str = "k_assistant.db"):
        self.db_path = db_path
        self.backup_path = f"{db_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.stats = {
            'total': 0,
            'encoding_fixed': 0,
            'structure_fixed': 0,
            'unchanged': 0,
            'errors': []
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
            '©': '(c)',        # Copyright
            '®': '(R)',        # Registered
            '™': '(TM)',       # Trademark
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
    
    def fix_encoding(self, fact: str) -> str:
        """Behebt Encoding-Probleme"""
        original = fact
        
        # Ersetze problematische Zeichen
        for old, new in self.encoding_replacements.items():
            if old in fact:
                fact = fact.replace(old, new)
        
        # Entferne non-ASCII Zeichen die nicht ersetzt wurden
        fact = ''.join(char if ord(char) < 128 else '?' for char in fact)
        
        if fact != original:
            self.stats['encoding_fixed'] += 1
            
        return fact
    
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
                # Finde letzte ) und entferne sie
                idx = text.rfind(')')
                if idx != -1:
                    text = text[:idx] + text[idx+1:]
        
        return text
    
    def fix_structure(self, fact: str) -> str:
        """Behebt strukturelle Probleme"""
        original = fact
        
        # Entferne mehrfache Spaces
        fact = re.sub(r'\s+', ' ', fact)
        
        # Fix für Predicates mit Slash (z.B. TCP/IP -> TCP_IP)
        # Nur in Predicate-Namen, nicht in Argumenten
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
                # Füge fehlende ) vor dem Punkt ein
                fact = fact[:-1] + ').'
        
        # Fix für verschachtelte Klammern in Argumenten
        # Z.B. OneOriginal(parental)Strand -> OneOriginal_parental_Strand
        def fix_nested(match):
            content = match.group(1)
            # Ersetze innere Klammern durch Underscores
            content = re.sub(r'\(([^)]*)\)', r'_\1_', content)
            return f"({content})"
        
        fact = re.sub(r'\(([^)]*\([^)]*\)[^)]*)\)', fix_nested, fact)
        
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
        
        # Hole alle Facts (rowid als id)
        cursor.execute("SELECT rowid, subject, predicate, object FROM facts")
        facts = cursor.fetchall()
        self.stats['total'] = len(facts)
        
        print(f"\n[INFO] Processing {len(facts)} facts...")
        
        updates = []
        problematic = []
        
        for fact_id, subject, predicate, obj in facts:
            # Konstruiere Fact-String
            fact_str = f"{predicate}({subject}, {obj})."
            original = fact_str
            
            # Phase 1: Encoding-Fixes
            fact_str = self.fix_encoding(fact_str)
            
            # Phase 2: Struktur-Fixes
            fact_str = self.fix_structure(fact_str)
            
            # Phase 3: Validierung
            is_valid, error_msg = self.validate_fact(fact_str)
            
            if not is_valid:
                problematic.append({
                    'id': fact_id,
                    'original': original,
                    'cleaned': fact_str,
                    'error': error_msg
                })
                continue
            
            if fact_str != original:
                # Parse zurück in Komponenten
                match = re.match(r'^([A-Za-z_][A-Za-z0-9_]*)\(([^,]+),\s*(.+)\)\.$', fact_str)
                if match:
                    new_predicate = match.group(1)
                    new_subject = match.group(2).strip()
                    new_object = match.group(3).strip()
                    
                    updates.append((new_subject, new_predicate, new_object, fact_id))
                else:
                    problematic.append({
                        'id': fact_id,
                        'original': original,
                        'cleaned': fact_str,
                        'error': 'Could not parse cleaned fact'
                    })
            else:
                self.stats['unchanged'] += 1
        
        # Zeige Statistiken
        print(f"\n[STATS] Cleanup Statistics:")
        print(f"  Total facts: {self.stats['total']}")
        print(f"  Encoding fixed: {self.stats['encoding_fixed']}")
        print(f"  Structure fixed: {self.stats['structure_fixed']}")
        print(f"  Unchanged: {self.stats['unchanged']}")
        print(f"  Problematic: {len(problematic)}")
        
        if problematic:
            print(f"\n[WARNING] {len(problematic)} facts could not be fixed:")
            for p in problematic[:10]:  # Zeige erste 10
                print(f"  ID {p['id']}: {p['error']}")
                print(f"    Original: {p['original'][:50]}...")
                print(f"    Cleaned: {p['cleaned'][:50]}...")
            
            if len(problematic) > 10:
                print(f"  ... and {len(problematic) - 10} more")
        
        if dry_run:
            print(f"\n[DRY RUN] No changes made")
            print(f"Would update {len(updates)} facts")
        else:
            if updates:
                print(f"\n[UPDATE] Applying {len(updates)} updates...")
                cursor.executemany(
                    "UPDATE facts SET subject=?, predicate=?, object=? WHERE rowid=?",
                    updates
                )
                conn.commit()
                print(f"[OK] Updates applied successfully")
            else:
                print(f"\n[OK] No updates needed")
        
        # Speichere problematische Facts für manuelle Review
        if problematic:
            problem_file = f"problematic_facts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(problem_file, 'w', encoding='utf-8') as f:
                json.dump(problematic, f, indent=2, ensure_ascii=False)
            print(f"\n[SAVED] Problematic facts saved to: {problem_file}")
        
        conn.close()
        
        return self.stats

def main():
    """Hauptfunktion"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Clean HAK-GAL Facts Database')
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
    
    cleaner = FactsCleaner(str(db_path))
    
    if args.encoding_only:
        print("[MODE] Fixing encoding issues only")
        # Modifiziere fix_structure um nichts zu tun
        cleaner.fix_structure = lambda x: x
    elif args.structure_only:
        print("[MODE] Fixing structure issues only")
        # Modifiziere fix_encoding um nichts zu tun
        cleaner.fix_encoding = lambda x: x
    
    stats = cleaner.clean_facts(dry_run=args.dry_run)
    
    print("\n[DONE] Cleanup complete!")
    
    return 0 if stats else 1

if __name__ == '__main__':
    sys.exit(main())