#!/usr/bin/env python3
"""
HAK_GAL Database Cleanup Tool
Removes corrupt, meaningless, and redundant facts from the knowledge base.
"""

import sqlite3
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Tuple

class HAKGALDatabaseCleaner:
    """Clean up corrupt and meaningless facts from HAK_GAL database"""
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = r"D:\MCP Mods\HAK_GAL_HEXAGONAL\hexagonal_kb.db"
        
        self.db_path = Path(db_path)
        self.backup_path = self.db_path.parent / f"hexagonal_kb_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        
        # Statistics tracking
        self.stats = {
            'initial_facts': 0,
            'initial_facts_v2': 0,
            'deleted_facts': 0,
            'deleted_facts_v2': 0,
            'deleted_by_category': {},
            'errors': 0
        }
        
        # Cleanup patterns - kategorisierte problematische Fakten
        self.cleanup_patterns = {
            'generic_nodes': {
                'pattern': "ConnectedTo(Node%",
                'description': "Generic meaningless node connections"
            },
            'entity_counts': {
                'pattern': "HasProperty(KnowledgeBase, EntityCount%",
                'description': "Historical entity count metrics"
            },
            'syntax_errors': {
                'pattern': "%'%",
                'description': "Facts with apostrophes (syntax issues)"
            },
            'regulator_facts': {
                'pattern': "Regulates(Regulator%, Target%, Mechanism%",
                'description': "Generic regulator facts with numbered entities"
            },
            'process_facts': {
                'pattern': "Process(input:Input%, operation:Operation%, output:Output%",
                'description': "Generic process facts with numbered entities"
            },
            'temporal_generic': {
                'pattern': "Temporal(fact:%, start:2025-%",
                'description': "Generic temporal facts with auto-generated timestamps"
            }
        }
        
        print(f"🔧 HAK_GAL Database Cleaner initialized")
        print(f"📁 Database: {self.db_path}")
        print(f"💾 Backup will be created: {self.backup_path.name}")
    
    def create_backup(self):
        """Create a backup of the database before cleaning"""
        try:
            print(f"\n💾 Creating backup...")
            shutil.copy2(self.db_path, self.backup_path)
            print(f"✅ Backup created: {self.backup_path}")
            return True
        except Exception as e:
            print(f"❌ Failed to create backup: {e}")
            return False
    
    def get_database_stats(self, conn: sqlite3.Connection) -> Dict[str, int]:
        """Get current database statistics"""
        stats = {}
        
        # Count facts in main table
        try:
            cursor = conn.execute("SELECT COUNT(*) FROM facts")
            stats['facts'] = cursor.fetchone()[0]
        except sqlite3.OperationalError:
            stats['facts'] = 0
        
        # Count facts in extended table
        try:
            cursor = conn.execute("SELECT COUNT(*) FROM facts_v2")
            stats['facts_v2'] = cursor.fetchone()[0]
        except sqlite3.OperationalError:
            stats['facts_v2'] = 0
        
        return stats
    
    def identify_problematic_facts(self, conn: sqlite3.Connection) -> Dict[str, List[str]]:
        """Identify facts that should be deleted"""
        problematic_facts = {}
        
        for table_name in ['facts', 'facts_v2']:
            print(f"\n🔍 Scanning table: {table_name}")
            
            # Check if table exists
            cursor = conn.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name=?
            """, (table_name,))
            
            if not cursor.fetchone():
                print(f"  ⚠️ Table {table_name} does not exist")
                continue
            
            for category, pattern_info in self.cleanup_patterns.items():
                pattern = pattern_info['pattern']
                description = pattern_info['description']
                
                try:
                    cursor = conn.execute(f"""
                        SELECT statement FROM {table_name} 
                        WHERE statement LIKE ?
                    """, (pattern,))
                    
                    facts_to_delete = [row[0] for row in cursor.fetchall()]
                    
                    if facts_to_delete:
                        key = f"{table_name}_{category}"
                        problematic_facts[key] = facts_to_delete
                        print(f"  🎯 {category}: {len(facts_to_delete)} facts ({description})")
                        
                        # Show samples
                        samples = facts_to_delete[:3]
                        for sample in samples:
                            sample_short = sample[:60] + "..." if len(sample) > 60 else sample
                            print(f"     • {sample_short}")
                        if len(facts_to_delete) > 3:
                            print(f"     ... and {len(facts_to_delete) - 3} more")
                    
                except sqlite3.Error as e:
                    print(f"  ❌ Error scanning {category}: {e}")
                    self.stats['errors'] += 1
        
        return problematic_facts
    
    def delete_problematic_facts(self, conn: sqlite3.Connection, 
                                problematic_facts: Dict[str, List[str]]) -> Dict[str, int]:
        """Delete identified problematic facts"""
        deletion_stats = {}
        
        for key, facts_list in problematic_facts.items():
            table_name, category = key.split('_', 1)
            
            print(f"\n🗑️ Deleting {category} facts from {table_name}...")
            
            deleted_count = 0
            errors = 0
            
            for fact in facts_list:
                try:
                    cursor = conn.execute(f"""
                        DELETE FROM {table_name} WHERE statement = ?
                    """, (fact,))
                    
                    if cursor.rowcount > 0:
                        deleted_count += 1
                    
                except sqlite3.Error as e:
                    print(f"  ⚠️ Error deleting fact: {e}")
                    errors += 1
            
            deletion_stats[key] = {
                'deleted': deleted_count,
                'errors': errors,
                'category': category,
                'table': table_name
            }
            
            print(f"  ✅ Deleted {deleted_count} facts")
            if errors > 0:
                print(f"  ⚠️ {errors} errors occurred")
        
        # Commit all deletions
        conn.commit()
        return deletion_stats
    
    def save_cleanup_log(self, problematic_facts: Dict[str, List[str]], 
                        deletion_stats: Dict[str, Dict]):
        """Save detailed cleanup log"""
        log_path = self.db_path.parent / f"cleanup_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        log_data = {
            'timestamp': datetime.now().isoformat(),
            'database': str(self.db_path),
            'backup': str(self.backup_path),
            'initial_stats': {
                'facts': self.stats['initial_facts'],
                'facts_v2': self.stats['initial_facts_v2']
            },
            'cleanup_patterns': self.cleanup_patterns,
            'problematic_facts_found': {
                key: len(facts) for key, facts in problematic_facts.items()
            },
            'deletion_results': deletion_stats,
            'deleted_facts_samples': {
                key: facts[:5] for key, facts in problematic_facts.items()
            }
        }
        
        try:
            with open(log_path, 'w', encoding='utf-8') as f:
                json.dump(log_data, f, indent=2, ensure_ascii=False)
            print(f"📝 Cleanup log saved: {log_path}")
        except Exception as e:
            print(f"⚠️ Failed to save log: {e}")
    
    def run_cleanup(self, dry_run: bool = False):
        """Run the complete database cleanup process"""
        print("="*70)
        print("🚀 HAK_GAL Database Cleanup Tool")
        print(f"🔍 Mode: {'DRY RUN' if dry_run else 'LIVE CLEANUP'}")
        print("="*70)
        
        # Step 1: Create backup (only for live run)
        if not dry_run:
            if not self.create_backup():
                print("❌ Backup failed. Cleanup aborted for safety.")
                return False
        
        # Step 2: Connect to database
        try:
            conn = sqlite3.connect(self.db_path)
            print(f"✅ Connected to database: {self.db_path}")
        except sqlite3.Error as e:
            print(f"❌ Failed to connect to database: {e}")
            return False
        
        try:
            # Step 3: Get initial statistics
            initial_stats = self.get_database_stats(conn)
            self.stats['initial_facts'] = initial_stats.get('facts', 0)
            self.stats['initial_facts_v2'] = initial_stats.get('facts_v2', 0)
            
            print(f"\n📊 Initial Database Statistics:")
            print(f"  facts table: {self.stats['initial_facts']} facts")
            print(f"  facts_v2 table: {self.stats['initial_facts_v2']} facts")
            print(f"  Total: {self.stats['initial_facts'] + self.stats['initial_facts_v2']} facts")
            
            # Step 4: Identify problematic facts
            problematic_facts = self.identify_problematic_facts(conn)
            
            total_problematic = sum(len(facts) for facts in problematic_facts.values())
            print(f"\n🎯 Total problematic facts identified: {total_problematic}")
            
            if total_problematic == 0:
                print("✅ No problematic facts found. Database is clean!")
                return True
            
            # Step 5: Delete problematic facts (if not dry run)
            if not dry_run:
                print(f"\n🗑️ Proceeding with deletion...")
                deletion_stats = self.delete_problematic_facts(conn, problematic_facts)
                
                # Step 6: Get final statistics
                final_stats = self.get_database_stats(conn)
                
                # Step 7: Calculate and display results
                final_facts = final_stats.get('facts', 0)
                final_facts_v2 = final_stats.get('facts_v2', 0)
                
                total_deleted = (self.stats['initial_facts'] - final_facts) + \
                               (self.stats['initial_facts_v2'] - final_facts_v2)
                
                print(f"\n📊 Final Database Statistics:")
                print(f"  facts table: {final_facts} facts (-{self.stats['initial_facts'] - final_facts})")
                print(f"  facts_v2 table: {final_facts_v2} facts (-{self.stats['initial_facts_v2'] - final_facts_v2})")
                print(f"  Total: {final_facts + final_facts_v2} facts (-{total_deleted})")
                
                # Step 8: Save cleanup log
                self.save_cleanup_log(problematic_facts, deletion_stats)
                
                print(f"\n✅ Cleanup completed successfully!")
                print(f"   Deleted: {total_deleted} problematic facts")
                print(f"   Backup: {self.backup_path}")
                
            else:
                print(f"\n🔍 DRY RUN - No facts were actually deleted")
                print(f"   Would delete: {total_problematic} problematic facts")
                print(f"   Run without --dry-run to perform actual cleanup")
        
        finally:
            conn.close()
        
        return True
    
    def show_cleanup_preview(self):
        """Show what would be cleaned without actually doing it"""
        print("\n📋 Cleanup Preview:")
        print("The following types of facts will be removed:")
        
        for category, pattern_info in self.cleanup_patterns.items():
            print(f"\n🎯 {category}:")
            print(f"   Pattern: {pattern_info['pattern']}")
            print(f"   Reason: {pattern_info['description']}")
        
        print(f"\n💡 To see actual facts that would be deleted, run: python {__file__} --dry-run")
        print(f"💡 To perform cleanup, run: python {__file__} --cleanup")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='HAK_GAL Database Cleanup Tool')
    parser.add_argument('--db', type=str, help='Database path (default: hexagonal_kb.db)')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be deleted without actually deleting')
    parser.add_argument('--cleanup', action='store_true', help='Perform actual cleanup')
    parser.add_argument('--preview', action='store_true', help='Show cleanup patterns')
    
    args = parser.parse_args()
    
    # Initialize cleaner
    cleaner = HAKGALDatabaseCleaner(args.db)
    
    if args.preview:
        cleaner.show_cleanup_preview()
    elif args.dry_run:
        cleaner.run_cleanup(dry_run=True)
    elif args.cleanup:
        # Confirm cleanup
        print("⚠️  This will permanently delete problematic facts from your database.")
        print("💾 A backup will be created automatically.")
        confirm = input("Do you want to proceed? (yes/no): ").lower().strip()
        
        if confirm in ['yes', 'y']:
            cleaner.run_cleanup(dry_run=False)
        else:
            print("❌ Cleanup cancelled.")
    else:
        print("🔧 HAK_GAL Database Cleanup Tool")
        print("\nUsage:")
        print("  --preview    Show what types of facts will be cleaned")
        print("  --dry-run    Show actual facts that would be deleted")
        print("  --cleanup    Perform actual cleanup (with backup)")
        print("\nExample:")
        print("  python database_cleanup.py --preview")
        print("  python database_cleanup.py --dry-run")
        print("  python database_cleanup.py --cleanup")


if __name__ == "__main__":
    main()
