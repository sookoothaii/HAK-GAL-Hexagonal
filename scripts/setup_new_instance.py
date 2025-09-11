#!/usr/bin/env python3
"""
HAK/GAL Governance V3 - Complete Setup Script for New Instance
Run this to initialize a fresh installation
"""

import os
import sys
import sqlite3
import json
import shutil
from datetime import datetime
from pathlib import Path

print("="*60)
print("HAK/GAL GOVERNANCE V3 - SETUP SCRIPT")
print("="*60)

# Configuration
BASE_DIR = Path(r"D:\MCP Mods\HAK_GAL_HEXAGONAL")
DB_PATH = BASE_DIR / "hexagonal_kb.db"
BACKUP_DIR = BASE_DIR / "backups"
AUDIT_LOG = BASE_DIR / "audit_log.jsonl"

def check_environment():
    """Check Python version and dependencies"""
    print("\n1. Checking Environment...")
    
    # Python version
    if sys.version_info < (3, 8):
        print("  ERROR: Python 3.8+ required")
        return False
    print(f"  Python {sys.version.split()[0]} - OK")
    
    # Required packages
    required = ['sqlite3', 'json', 'hashlib', 'threading', 'uuid']
    for pkg in required:
        try:
            __import__(pkg)
            print(f"  {pkg} - OK")
        except ImportError:
            print(f"  ERROR: {pkg} not available")
            return False
    
    # Optional packages
    try:
        import z3
        print("  z3-solver - OK (but not required for V3)")
    except ImportError:
        print("  z3-solver - NOT INSTALLED (OK for V3)")
    
    return True

def setup_directories():
    """Create required directories"""
    print("\n2. Setting up directories...")
    
    dirs = [
        BASE_DIR,
        BASE_DIR / "src_hexagonal",
        BASE_DIR / "src_hexagonal" / "application",
        BASE_DIR / "src_hexagonal" / "infrastructure",
        BASE_DIR / "src_hexagonal" / "domain",
        BACKUP_DIR,
        BASE_DIR / "PROJECT_HUB"
    ]
    
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)
        print(f"  {d} - OK")
    
    return True

def setup_database():
    """Initialize database with proper schema"""
    print("\n3. Setting up database...")
    
    # Backup existing if present
    if DB_PATH.exists():
        backup_name = f"hexagonal_kb_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        backup_path = BACKUP_DIR / backup_name
        shutil.copy2(DB_PATH, backup_path)
        print(f"  Existing DB backed up to {backup_name}")
    
    # Connect and setup
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    # Enable WAL mode
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA synchronous=NORMAL")
    cursor.execute("PRAGMA wal_autocheckpoint=1000")
    cursor.execute("PRAGMA cache_size=-64000")  # 64MB cache
    print("  WAL mode enabled")
    
    # Create main table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS facts_extended (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            statement TEXT UNIQUE NOT NULL,
            predicate TEXT,
            arg_count INTEGER,
            arg1 TEXT,
            arg2 TEXT,
            arg3 TEXT,
            arg4 TEXT,
            arg5 TEXT,
            args_json TEXT,
            fact_type TEXT,
            domain TEXT,
            complexity INTEGER DEFAULT 1,
            confidence REAL DEFAULT 1.0,
            created_at TEXT DEFAULT (datetime('now')),
            source TEXT
        )
    """)
    print("  facts_extended table created")
    
    # Create indices
    indices = [
        "CREATE INDEX IF NOT EXISTS idx_predicate ON facts_extended(predicate)",
        "CREATE INDEX IF NOT EXISTS idx_fact_type ON facts_extended(fact_type)",
        "CREATE INDEX IF NOT EXISTS idx_domain ON facts_extended(domain)",
        "CREATE INDEX IF NOT EXISTS idx_created_at ON facts_extended(created_at)",
        "CREATE INDEX IF NOT EXISTS idx_source ON facts_extended(source)"
    ]
    
    for idx in indices:
        cursor.execute(idx)
    print("  Indices created")
    
    # Create audit table (optional)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT DEFAULT (datetime('now')),
            event TEXT,
            payload TEXT,
            hash TEXT
        )
    """)
    print("  audit_log table created")
    
    conn.commit()
    
    # Verify
    cursor.execute("PRAGMA integrity_check")
    if cursor.fetchone()[0] == 'ok':
        print("  Database integrity - OK")
    
    conn.close()
    return True

def setup_configuration():
    """Create configuration files"""
    print("\n4. Setting up configuration...")
    
    # HAK/GAL Constitution
    constitution = {
        "version": "2.2",
        "description": "HAK/GAL Machine-Readable Constitution",
        "rules": [
            {
                "rule_id": "DEFAULT_PASS",
                "description": "Default approval conditions",
                "conditions": {
                    "type": "ALL",
                    "clauses": [
                        {"metric": "ExternallyLegal", "operator": "EQUALS", "value": True},
                        {"metric": "Universalizable", "operator": "EQUALS", "value": True},
                        {"metric": "HarmHumanProb", "operator": "LESS_THAN_OR_EQUAL", "value": 0.001},
                        {"metric": "SustainIndex", "operator": "GREATER_THAN_OR_EQUAL", "value": 0.85}
                    ]
                }
            },
            {
                "rule_id": "OVERRIDE_GATE",
                "description": "Override conditions",
                "conditions": {
                    "type": "ALL",
                    "clauses": [
                        {"metric": "ExternallyLegal", "operator": "EQUALS", "value": True},
                        {"metric": "Override.Operator", "operator": "EQUALS", "value": True},
                        {"metric": "Override.PeerReview", "operator": "EQUALS", "value": True},
                        {"metric": "Override.Documentation", "operator": "EQUALS", "value": True},
                        {"metric": "Override.RiskExceptionJustified", "operator": "EQUALS", "value": True}
                    ]
                }
            }
        ]
    }
    
    const_path = BASE_DIR / "hak_gal_constitution_v2_2.json"
    with open(const_path, 'w') as f:
        json.dump(constitution, f, indent=2)
    print(f"  Constitution v2.2 written")
    
    # Environment file
    env_path = BASE_DIR / ".env"
    with open(env_path, 'w') as f:
        f.write("# HAK/GAL Governance V3 Configuration\n")
        f.write("GOVERNANCE_VERSION=v3\n")
        f.write("GOVERNANCE_BYPASS=false\n")
        f.write(f"DB_PATH={DB_PATH}\n")
        f.write("MAX_WORKERS=10\n")
        f.write("BATCH_SIZE=100\n")
        f.write("CONNECTION_POOL_SIZE=10\n")
    print("  .env file created")
    
    return True

def test_installation():
    """Test the installation"""
    print("\n5. Testing installation...")
    
    # Add paths
    sys.path.insert(0, str(BASE_DIR))
    sys.path.insert(0, str(BASE_DIR / "src_hexagonal"))
    
    # Set environment
    os.environ['GOVERNANCE_VERSION'] = 'v3'
    
    try:
        # Try to import
        from src_hexagonal.application.transactional_governance_engine import TransactionalGovernanceEngine
        print("  TransactionalGovernanceEngine - OK")
        
        # Try to initialize
        engine = TransactionalGovernanceEngine()
        print("  Engine initialization - OK")
        
        # Try to add a fact
        test_fact = ["IsA(SetupTest, Success)"]
        context = {"source": "setup_script", "externally_legal": True}
        result = engine.governed_add_facts_atomic(test_fact, context)
        
        if result > 0:
            print(f"  Test fact added - OK")
            
            # Clean up test fact
            conn = sqlite3.connect(str(DB_PATH))
            conn.execute("DELETE FROM facts_extended WHERE statement = 'IsA(SetupTest, Success)'")
            conn.commit()
            conn.close()
        else:
            print("  WARNING: Test fact not added (governance blocked)")
            
    except ImportError as e:
        print(f"  ERROR: Import failed - {e}")
        print("  NOTE: You need to copy governance_v3.py and other files")
        return False
    except Exception as e:
        print(f"  ERROR: {e}")
        return False
    
    return True

def print_next_steps():
    """Print what to do next"""
    print("\n" + "="*60)
    print("SETUP COMPLETE - NEXT STEPS")
    print("="*60)
    
    print("""
1. Copy these files from the source:
   - src_hexagonal/application/governance_v3.py
   - src_hexagonal/application/transactional_governance_engine.py
   - test_governance_v3_fixed.py

2. Set environment variables:
   export GOVERNANCE_VERSION=v3
   export GOVERNANCE_BYPASS=false

3. Run tests:
   python test_governance_v3_fixed.py

4. For production:
   - Implement proper auth token validation
   - Set up backup rotation
   - Configure monitoring
   - Review security settings

5. Emergency bypass (if needed):
   export GOVERNANCE_BYPASS=true
   
Documentation: PROJECT_HUB/GOVERNANCE_V3_IMPLEMENTATION_REPORT_20250910.md
""")

if __name__ == "__main__":
    steps = [
        ("Environment", check_environment),
        ("Directories", setup_directories),
        ("Database", setup_database),
        ("Configuration", setup_configuration),
        ("Installation Test", test_installation)
    ]
    
    success = True
    for name, func in steps:
        if not func():
            print(f"\n{name} setup failed!")
            success = False
            break
    
    if success:
        print_next_steps()
        print("\nSetup completed successfully!")
    else:
        print("\nSetup failed - please check errors above")
        sys.exit(1)
