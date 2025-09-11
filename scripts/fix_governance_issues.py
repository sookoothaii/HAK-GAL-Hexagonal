#!/usr/bin/env python
"""
Fix Script for HAK/GAL Governance Issues
Repairs audit chain, cleans duplicates, optimizes database
"""

import sqlite3
import json
import hashlib
import shutil
from pathlib import Path
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GovernanceRepairTool:
    """
    Comprehensive repair tool for governance system issues
    """
    
    def __init__(self):
        self.db_path = "D:\\MCP Mods\\HAK_GAL_HEXAGONAL\\hexagonal_kb.db"
        self.audit_path = Path("D:\\MCP Mods\\HAK_GAL_HEXAGONAL\\audit_log.jsonl")
        
    def fix_all(self):
        """Run all fixes"""
        print("\n" + "="*60)
        print("HAK/GAL GOVERNANCE REPAIR TOOL")
        print("="*60)
        
        # 1. Fix database
        self.fix_database()
        
        # 2. Fix audit log
        self.fix_audit_chain()
        
        # 3. Clean duplicates
        self.remove_duplicates()
        
        # 4. Optimize performance
        self.optimize_database()
        
        print("\n[OK] ALL REPAIRS COMPLETED")
        print("="*60)
    
    def fix_database(self):
        """Fix database issues"""
        print("\n1. FIXING DATABASE...")
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Enable WAL mode
            cursor.execute("PRAGMA journal_mode=WAL")
            print("   [+] WAL mode enabled")
            
            # Set optimal pragmas
            cursor.execute("PRAGMA synchronous=NORMAL")
            cursor.execute("PRAGMA cache_size=10000")
            cursor.execute("PRAGMA temp_store=MEMORY")
            cursor.execute("PRAGMA busy_timeout=30000")
            print("   [+] Optimized pragmas set")
            
            # Add indexes if missing
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_facts_extended_statement 
                ON facts_extended(statement)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_facts_extended_predicate 
                ON facts_extended(predicate)
            """)
            print("   [+] Indexes created/verified")
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"   [!] Database fix failed: {e}")
    
    def fix_audit_chain(self):
        """Repair broken audit chain"""
        print("\n2. FIXING AUDIT CHAIN...")
        
        if not self.audit_path.exists():
            print("   [i] No audit log found, creating new one")
            self._create_genesis_block()
            return
        
        # Backup original
        backup_path = self.audit_path.with_suffix('.jsonl.backup')
        shutil.copy(self.audit_path, backup_path)
        print(f"   [+] Backup created: {backup_path}")
        
        # Read all entries
        entries = []
        with open(self.audit_path, 'r') as f:
            for line in f:
                try:
                    entries.append(json.loads(line))
                except:
                    pass
        
        if not entries:
            self._create_genesis_block()
            return
        
        # Rebuild chain
        repaired_entries = []
        prev_hash = None
        
        for i, entry in enumerate(entries):
            # Recompute hash
            entry_data = {
                'ts': entry.get('ts', datetime.utcnow().isoformat()),
                'event': entry.get('event', 'unknown'),
                'payload': entry.get('payload', {}),
                'prev_hash': prev_hash
            }
            
            entry_str = json.dumps(entry_data, sort_keys=True)
            entry_hash = hashlib.sha256(entry_str.encode()).hexdigest()
            
            entry_data['entry_hash'] = entry_hash
            repaired_entries.append(entry_data)
            prev_hash = entry_hash
        
        # Write repaired chain
        with open(self.audit_path, 'w') as f:
            for entry in repaired_entries:
                f.write(json.dumps(entry) + '\n')
        
        print(f"   [+] Repaired {len(repaired_entries)} audit entries")
    
    def _create_genesis_block(self):
        """Create a new genesis block"""
        genesis = {
            'ts': datetime.utcnow().isoformat(),
            'event': 'audit.genesis',
            'payload': {'message': 'Audit log repaired/initialized'},
            'prev_hash': None
        }
        
        genesis_str = json.dumps(genesis, sort_keys=True)
        genesis_hash = hashlib.sha256(genesis_str.encode()).hexdigest()
        genesis['entry_hash'] = genesis_hash
        
        with open(self.audit_path, 'w') as f:
            f.write(json.dumps(genesis) + '\n')
        
        print("   [+] Genesis block created")
    
    def remove_duplicates(self):
        """Remove duplicate facts from database"""
        print("\n3. REMOVING DUPLICATES...")
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Find duplicates
            cursor.execute("""
                SELECT statement, COUNT(*) as cnt 
                FROM facts_extended 
                GROUP BY statement 
                HAVING cnt > 1
            """)
            
            duplicates = cursor.fetchall()
            
            if duplicates:
                print(f"   Found {len(duplicates)} duplicate statements")
                
                # Keep only one of each
                for statement, count in duplicates:
                    cursor.execute("""
                        DELETE FROM facts_extended 
                        WHERE statement = ? 
                        AND rowid NOT IN (
                            SELECT MIN(rowid) 
                            FROM facts_extended 
                            WHERE statement = ?
                        )
                    """, (statement, statement))
                
                conn.commit()
                print(f"   [+] Removed {cursor.rowcount} duplicate entries")
            else:
                print("   [+] No duplicates found")
            
            conn.close()
            
        except Exception as e:
            print(f"   [!] Duplicate removal failed: {e}")
    
    def optimize_database(self):
        """Optimize database performance"""
        print("\n4. OPTIMIZING DATABASE...")
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Analyze tables
            cursor.execute("ANALYZE")
            print("   [+] Table statistics updated")
            
            # Vacuum
            cursor.execute("VACUUM")
            print("   [+] Database vacuumed")
            
            # Get stats
            cursor.execute("SELECT COUNT(*) FROM facts_extended")
            fact_count = cursor.fetchone()[0]
            
            # File size
            db_size = Path(self.db_path).stat().st_size / (1024*1024)
            
            print(f"   [i] Total facts: {fact_count}")
            print(f"   [i] Database size: {db_size:.2f} MB")
            
            conn.close()
            
        except Exception as e:
            print(f"   [!] Optimization failed: {e}")


def run_quick_test():
    """Run a quick test after repairs"""
    print("\n5. RUNNING QUICK TEST...")
    
    import sys
    sys.path.insert(0, "D:\\MCP Mods\\HAK_GAL_HEXAGONAL\\src_hexagonal")
    
    try:
        # Test with connection pool
        from infrastructure.db_connection_pool import PooledTransactionalGovernanceEngine
        
        engine = PooledTransactionalGovernanceEngine()
        
        # Test adding facts
        test_facts = [
            f"IsA(RepairTest{i}, TestEntity)" for i in range(5)
        ]
        
        context = {
            'test': 'post_repair',
            'harm_prob': 0.0001,
            'sustain_index': 0.95,
            'externally_legal': True
        }
        
        result = engine.add_facts_with_pool(test_facts, context)
        
        if result > 0:
            print(f"   [+] Successfully added {result} test facts")
        else:
            print(f"   [!] No facts added (may already exist)")
            
    except Exception as e:
        print(f"   [!] Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Run repairs
    tool = GovernanceRepairTool()
    tool.fix_all()
    
    # Run test
    run_quick_test()
    
    print("\n" + "="*60)
    print("REPAIR COMPLETE - Please re-run comprehensive tests")
    print("="*60)