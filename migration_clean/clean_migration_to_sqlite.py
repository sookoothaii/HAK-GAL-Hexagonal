#!/usr/bin/env python3
"""
HAK-GAL Clean Migration to SQLite
==================================
Complete data migration with strict validation and cleaning.
Quality over quantity approach.
"""

import json
import sqlite3
import re
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple, Set
import hashlib
from collections import Counter

class CleanMigrationToSQLite:
    """
    Migrate and clean HAK-GAL knowledge base to SQLite with strict validation.
    """
    
    def __init__(self):
        self.jsonl_path = Path("D:/MCP Mods/HAK_GAL_HEXAGONAL/data/k_assistant.kb.jsonl")
        self.sqlite_path = Path("D:/MCP Mods/HAK_GAL_SUITE/k_assistant.db")
        self.backup_path = Path(f"D:/MCP Mods/HAK_GAL_SUITE/k_assistant_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db")
        
        # Statistics
        self.stats = {
            'jsonl_total': 0,
            'jsonl_valid': 0,
            'jsonl_invalid': 0,
            'duplicates_removed': 0,
            'syntax_errors': 0,
            'migrated': 0,
            'rejected': 0
        }
        
        # Valid facts storage
        self.valid_facts = []
        self.seen_hashes = set()
        self.rejected_facts = []
        
    def validate_statement_syntax(self, statement: str) -> Tuple[bool, str, List[str]]:
        """
        Strict validation of statement syntax.
        Returns: (is_valid, predicate, arguments)
        """
        if not statement:
            return False, "", []
            
        # Clean up statement
        statement = statement.strip()
        
        # Ensure it ends with a period
        if not statement.endswith('.'):
            statement += '.'
            
        # Pattern: Predicate(Arg1, Arg2, ...).
        pattern = r'^([A-Za-z][A-Za-z0-9_]*)\(([^)]+)\)\.$'
        match = re.match(pattern, statement)
        
        if not match:
            return False, "", []
            
        predicate = match.group(1)
        args_str = match.group(2)
        
        # Parse arguments
        args = [arg.strip() for arg in args_str.split(',')]
        
        # Validate arguments
        if len(args) < 1:
            return False, predicate, []
            
        # Check for empty arguments
        if any(not arg for arg in args):
            return False, predicate, args
            
        return True, predicate, args
        
    def normalize_statement(self, statement: str) -> str:
        """
        Normalize statement for consistency.
        """
        statement = statement.strip()
        
        # Ensure ending with period
        if not statement.endswith('.'):
            statement += '.'
            
        # Normalize spacing around parentheses and commas
        statement = re.sub(r'\s*\(\s*', '(', statement)
        statement = re.sub(r'\s*\)\s*', ')', statement)
        statement = re.sub(r'\s*,\s*', ', ', statement)
        
        return statement
        
    def get_statement_hash(self, statement: str) -> str:
        """
        Generate hash for duplicate detection.
        """
        normalized = self.normalize_statement(statement)
        return hashlib.sha256(normalized.encode('utf-8')).hexdigest()
        
    def analyze_jsonl(self):
        """
        Analyze and validate all facts from JSONL.
        """
        print("=" * 60)
        print("PHASE 1: Analyzing JSONL Knowledge Base")
        print("=" * 60)
        
        if not self.jsonl_path.exists():
            print(f"❌ JSONL file not found: {self.jsonl_path}")
            return False
            
        with open(self.jsonl_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                self.stats['jsonl_total'] += 1
                
                if not line.strip():
                    continue
                    
                try:
                    # Parse JSON
                    obj = json.loads(line)
                    statement = obj.get('statement', '')
                    
                    if not statement:
                        self.stats['jsonl_invalid'] += 1
                        self.rejected_facts.append({
                            'line': line_num,
                            'reason': 'No statement field',
                            'data': line[:100]
                        })
                        continue
                        
                    # Validate syntax
                    is_valid, predicate, args = self.validate_statement_syntax(statement)
                    
                    if not is_valid:
                        self.stats['syntax_errors'] += 1
                        self.rejected_facts.append({
                            'line': line_num,
                            'reason': 'Invalid syntax',
                            'statement': statement
                        })
                        continue
                        
                    # Normalize statement
                    normalized = self.normalize_statement(statement)
                    
                    # Check for duplicates
                    stmt_hash = self.get_statement_hash(normalized)
                    if stmt_hash in self.seen_hashes:
                        self.stats['duplicates_removed'] += 1
                        continue
                        
                    self.seen_hashes.add(stmt_hash)
                    
                    # Store valid fact
                    self.valid_facts.append({
                        'statement': normalized,
                        'predicate': predicate,
                        'args': args,
                        'confidence': obj.get('confidence', 1.0),
                        'source': obj.get('source', 'jsonl_migration'),
                        'original_line': line_num
                    })
                    
                    self.stats['jsonl_valid'] += 1
                    
                except json.JSONDecodeError as e:
                    self.stats['jsonl_invalid'] += 1
                    self.rejected_facts.append({
                        'line': line_num,
                        'reason': f'JSON decode error: {e}',
                        'data': line[:100]
                    })
                except Exception as e:
                    self.stats['jsonl_invalid'] += 1
                    self.rejected_facts.append({
                        'line': line_num,
                        'reason': f'Unexpected error: {e}',
                        'data': line[:100]
                    })
                    
        print(f"\n✅ Analysis complete:")
        print(f"   Total lines: {self.stats['jsonl_total']}")
        print(f"   Valid facts: {self.stats['jsonl_valid']}")
        print(f"   Invalid/rejected: {self.stats['jsonl_invalid']}")
        print(f"   Duplicates removed: {self.stats['duplicates_removed']}")
        print(f"   Syntax errors: {self.stats['syntax_errors']}")
        
        return True
        
    def analyze_predicate_distribution(self):
        """
        Analyze predicate distribution for quality assessment.
        """
        print("\n" + "=" * 60)
        print("PHASE 2: Predicate Distribution Analysis")
        print("=" * 60)
        
        predicate_counts = Counter()
        arg_counts = Counter()
        
        for fact in self.valid_facts:
            predicate_counts[fact['predicate']] += 1
            arg_counts[len(fact['args'])] += 1
            
        print("\nTop 20 Predicates:")
        for pred, count in predicate_counts.most_common(20):
            percentage = (count / len(self.valid_facts)) * 100
            print(f"   {pred}: {count} ({percentage:.1f}%)")
            
        print(f"\nArgument Count Distribution:")
        for arg_count, freq in sorted(arg_counts.items()):
            print(f"   {arg_count} args: {freq} facts")
            
        # Language detection
        english_predicates = [p for p in predicate_counts if not any(
            p.startswith(prefix) for prefix in ['Hat', 'Ist', 'Verursacht', 'Besteht', 'Wird']
        )]
        german_predicates = [p for p in predicate_counts if any(
            p.startswith(prefix) for prefix in ['Hat', 'Ist', 'Verursacht', 'Besteht', 'Wird']
        )]
        
        english_count = sum(predicate_counts[p] for p in english_predicates)
        german_count = sum(predicate_counts[p] for p in german_predicates)
        
        print(f"\nLanguage Distribution:")
        print(f"   English predicates: {english_count} ({(english_count/len(self.valid_facts))*100:.1f}%)")
        print(f"   German predicates: {german_count} ({(german_count/len(self.valid_facts))*100:.1f}%)")
        
    def backup_existing_db(self):
        """
        Backup existing SQLite database.
        """
        if self.sqlite_path.exists():
            print(f"\n📦 Backing up existing database to: {self.backup_path}")
            import shutil
            shutil.copy2(self.sqlite_path, self.backup_path)
            print(f"   ✅ Backup created")
            return True
        return False
        
    def migrate_to_sqlite(self):
        """
        Migrate validated facts to SQLite.
        """
        print("\n" + "=" * 60)
        print("PHASE 3: SQLite Migration")
        print("=" * 60)
        
        # Backup existing database
        self.backup_existing_db()
        
        # Connect to SQLite
        conn = sqlite3.connect(self.sqlite_path)
        cursor = conn.cursor()
        
        try:
            # Drop and recreate facts table for clean migration
            print("\n🔧 Recreating facts table...")
            cursor.execute("DROP TABLE IF EXISTS facts")
            cursor.execute("""
                CREATE TABLE facts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    statement TEXT NOT NULL UNIQUE,
                    predicate TEXT NOT NULL,
                    arguments TEXT NOT NULL,
                    arg_count INTEGER NOT NULL,
                    confidence REAL DEFAULT 1.0,
                    source TEXT DEFAULT 'migration',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    hash TEXT UNIQUE
                )
            """)
            
            # Create indexes for performance
            cursor.execute("CREATE INDEX idx_predicate ON facts(predicate)")
            cursor.execute("CREATE INDEX idx_arg_count ON facts(arg_count)")
            cursor.execute("CREATE INDEX idx_confidence ON facts(confidence)")
            cursor.execute("CREATE INDEX idx_created_at ON facts(created_at)")
            
            print("   ✅ Table structure created")
            
            # Insert valid facts
            print(f"\n📝 Inserting {len(self.valid_facts)} valid facts...")
            
            for i, fact in enumerate(self.valid_facts, 1):
                try:
                    stmt_hash = self.get_statement_hash(fact['statement'])
                    cursor.execute("""
                        INSERT INTO facts (statement, predicate, arguments, arg_count, confidence, source, hash)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        fact['statement'],
                        fact['predicate'],
                        json.dumps(fact['args']),
                        len(fact['args']),
                        fact['confidence'],
                        fact['source'],
                        stmt_hash
                    ))
                    self.stats['migrated'] += 1
                    
                    if i % 500 == 0:
                        print(f"   Progress: {i}/{len(self.valid_facts)} ({(i/len(self.valid_facts))*100:.1f}%)")
                        
                except sqlite3.IntegrityError as e:
                    # Duplicate - should not happen after our deduplication
                    self.stats['rejected'] += 1
                except Exception as e:
                    print(f"   ⚠️ Error inserting fact {i}: {e}")
                    self.stats['rejected'] += 1
                    
            # Commit all changes
            conn.commit()
            
            # Verify migration
            cursor.execute("SELECT COUNT(*) FROM facts")
            final_count = cursor.fetchone()[0]
            
            print(f"\n✅ Migration complete:")
            print(f"   Facts migrated: {self.stats['migrated']}")
            print(f"   Facts rejected during insert: {self.stats['rejected']}")
            print(f"   Final database count: {final_count}")
            
            # Analyze final database
            cursor.execute("SELECT predicate, COUNT(*) as cnt FROM facts GROUP BY predicate ORDER BY cnt DESC LIMIT 10")
            top_predicates = cursor.fetchall()
            
            print(f"\nTop 10 predicates in final database:")
            for pred, count in top_predicates:
                print(f"   {pred}: {count}")
                
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()
            
        return True
        
    def save_reports(self):
        """
        Save detailed reports of the migration.
        """
        print("\n" + "=" * 60)
        print("PHASE 4: Generating Reports")
        print("=" * 60)
        
        report_dir = Path("D:/MCP Mods/HAK_GAL_HEXAGONAL/migration_clean/reports")
        report_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Migration summary
        summary_path = report_dir / f"migration_summary_{timestamp}.json"
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump({
                'timestamp': timestamp,
                'statistics': self.stats,
                'source': str(self.jsonl_path),
                'target': str(self.sqlite_path),
                'backup': str(self.backup_path) if self.backup_path.exists() else None
            }, f, indent=2)
        print(f"   ✅ Summary saved: {summary_path}")
        
        # Rejected facts report
        if self.rejected_facts:
            rejected_path = report_dir / f"rejected_facts_{timestamp}.json"
            with open(rejected_path, 'w', encoding='utf-8') as f:
                json.dump(self.rejected_facts[:100], f, indent=2)  # First 100 rejections
            print(f"   ✅ Rejection report saved: {rejected_path}")
            
        # Valid facts sample
        sample_path = report_dir / f"valid_sample_{timestamp}.json"
        with open(sample_path, 'w', encoding='utf-8') as f:
            json.dump(self.valid_facts[:100], f, indent=2)  # First 100 valid facts
        print(f"   ✅ Valid sample saved: {sample_path}")
        
        print(f"\nAll reports saved in: {report_dir}")
        
    def run(self):
        """
        Execute complete migration pipeline.
        """
        print("=" * 60)
        print("HAK-GAL CLEAN MIGRATION TO SQLITE")
        print("=" * 60)
        print(f"Source: {self.jsonl_path}")
        print(f"Target: {self.sqlite_path}")
        print("=" * 60)
        
        # Phase 1: Analyze JSONL
        if not self.analyze_jsonl():
            print("❌ Analysis failed")
            return False
            
        # Phase 2: Analyze distribution
        self.analyze_predicate_distribution()
        
        # User confirmation
        print("\n" + "=" * 60)
        print("READY TO MIGRATE")
        print("=" * 60)
        print(f"Will migrate {len(self.valid_facts)} validated facts to SQLite")
        print(f"Will reject {self.stats['jsonl_invalid']} invalid facts")
        print(f"Removed {self.stats['duplicates_removed']} duplicates")
        
        # Phase 3: Migrate
        if not self.migrate_to_sqlite():
            print("❌ Migration failed")
            return False
            
        # Phase 4: Reports
        self.save_reports()
        
        print("\n" + "=" * 60)
        print("✅ MIGRATION COMPLETED SUCCESSFULLY")
        print("=" * 60)
        print(f"Database: {self.sqlite_path}")
        print(f"Total facts: {self.stats['migrated']}")
        print(f"Quality score: {(self.stats['migrated']/self.stats['jsonl_total'])*100:.1f}% retained after validation")
        print("=" * 60)
        
        return True

if __name__ == "__main__":
    migrator = CleanMigrationToSQLite()
    success = migrator.run()
    
    if success:
        print("\n🎉 Migration successful!")
        print("Next steps:")
        print("1. Restart the backend to load new database")
        print("2. Test with MCP tools")
        print("3. Verify in frontend")
    else:
        print("\n❌ Migration failed. Check logs for details.")
