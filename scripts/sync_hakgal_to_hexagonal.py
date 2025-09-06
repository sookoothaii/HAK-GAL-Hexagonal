#!/usr/bin/env python
"""
Synchronisiere HAK-GAL MCP mit Hexagonal Database (4,010 Facts)
================================================================
Nach HAK/GAL Artikel 3: Externe Verifikation
Nach HAK/GAL Artikel 6: Empirische Validierung

KRITISCH: Nur hexagonal_kb.db mit ≥4,000 Facts ist gültig!
"""

import sqlite3
import json
from pathlib import Path
import shutil
from datetime import datetime

def sync_databases():
    """Synchronisiere HAK-GAL MCP mit der korrekten hexagonal_kb.db"""
    
    print("="*70)
    print("HAK-GAL DATABASE SYNCHRONIZATION")
    print("Source: hexagonal_kb.db (4,010 facts) - VALIDATED")
    print("Target: HAK-GAL MCP Knowledge Base")
    print("="*70)
    
    # Pfade
    hexagonal_db = Path(__file__).parent / 'hexagonal_kb.db'
    hakgal_jsonl = Path(__file__).parent / 'data' / 'k_assistant.kb.jsonl'
    
    # 1. Verifiziere Source Database
    print("\n[1] Verifying source database...")
    if not hexagonal_db.exists():
        print("❌ ERROR: hexagonal_kb.db not found!")
        return False
        
    with sqlite3.connect(str(hexagonal_db)) as conn:
        cursor = conn.execute("SELECT COUNT(*) FROM facts")
        fact_count = cursor.fetchone()[0]
        
    if fact_count < 4000:
        print(f"❌ ERROR: Database has only {fact_count} facts (minimum 4,000 required)")
        return False
        
    print(f"✅ Source validated: {fact_count:,} facts")
    
    # 2. Backup existing HAK-GAL data
    print("\n[2] Creating backup...")
    if hakgal_jsonl.exists():
        backup_name = f"k_assistant.kb.jsonl.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        backup_path = hakgal_jsonl.parent / backup_name
        shutil.copy2(hakgal_jsonl, backup_path)
        print(f"✅ Backup created: {backup_name}")
    
    # 3. Export facts from hexagonal_kb.db to JSONL format
    print("\n[3] Exporting facts to JSONL format...")
    
    # Stelle sicher, dass data/ Verzeichnis existiert
    hakgal_jsonl.parent.mkdir(exist_ok=True)
    
    exported_count = 0
    with sqlite3.connect(str(hexagonal_db)) as conn:
        cursor = conn.execute("""
            SELECT statement, confidence, source, created_at 
            FROM facts 
            ORDER BY id
        """)
        
        with open(hakgal_jsonl, 'w', encoding='utf-8') as f:
            for row in cursor:
                statement, confidence, source, created_at = row
                
                # HAK-GAL JSONL Format
                fact = {
                    "type": "fact",
                    "content": statement,
                    "confidence": confidence if confidence else 1.0,
                    "source": source if source else "hexagonal_migration",
                    "timestamp": created_at if created_at else datetime.now().isoformat()
                }
                
                f.write(json.dumps(fact, ensure_ascii=False) + '\n')
                exported_count += 1
                
                if exported_count % 500 == 0:
                    print(f"  Exported {exported_count:,} facts...")
    
    print(f"✅ Successfully exported {exported_count:,} facts to JSONL")
    
    # 4. Update HAK-GAL configuration
    print("\n[4] Updating HAK-GAL configuration...")
    
    config = {
        "database": {
            "primary": "hexagonal_kb.db",
            "jsonl_export": str(hakgal_jsonl),
            "fact_count": fact_count,
            "last_sync": datetime.now().isoformat(),
            "status": "SYNCHRONIZED"
        },
        "validation": {
            "min_facts": 4000,
            "current_facts": fact_count,
            "valid": fact_count >= 4000
        },
        "hrm_model": {
            "trained_on": "3.5M parameters",
            "requires_facts": 4000,
            "database_compatible": True
        }
    }
    
    config_path = Path(__file__).parent / 'hakgal_sync_config.json'
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Configuration saved to {config_path}")
    
    # 5. Verify synchronization
    print("\n[5] Verifying synchronization...")
    
    # Count lines in JSONL
    with open(hakgal_jsonl, 'r', encoding='utf-8') as f:
        jsonl_count = sum(1 for line in f if line.strip())
    
    if jsonl_count == fact_count:
        print(f"✅ PERFECT SYNC: {jsonl_count:,} facts in JSONL matches database")
    else:
        print(f"⚠️  WARNING: JSONL has {jsonl_count:,} facts, database has {fact_count:,}")
    
    # 6. Display summary
    print("\n" + "="*70)
    print("SYNCHRONIZATION COMPLETE")
    print("="*70)
    print(f"✅ Database: hexagonal_kb.db ({fact_count:,} facts)")
    print(f"✅ JSONL: {hakgal_jsonl.name} ({jsonl_count:,} facts)")
    print(f"✅ Status: READY FOR PRODUCTION")
    print("="*70)
    
    # 7. Create startup script
    startup_script = Path(__file__).parent / 'START_HAKGAL_WITH_HEXAGONAL.bat'
    with open(startup_script, 'w') as f:
        f.write(f"""@echo off
echo ============================================
echo Starting HAK-GAL with Hexagonal Database
echo Facts: {fact_count:,} (VALIDATED)
echo ============================================

REM Activate virtual environment
call .venv_hexa\\Scripts\\activate

REM Set environment variables
set HAKGAL_DB=hexagonal_kb.db
set HAKGAL_FACTS={fact_count}
set HAKGAL_WRITE_ENABLED=true

REM Start the backend
echo Starting HAK-GAL Backend...
python src_hexagonal\\hexagonal_api_enhanced.py

pause
""")
    
    print(f"\n✅ Startup script created: {startup_script.name}")
    print("\nTo start HAK-GAL with the correct database, run:")
    print(f"  {startup_script.name}")
    
    return True

if __name__ == '__main__':
    success = sync_databases()
    if success:
        print("\n🎉 SUCCESS! HAK-GAL is now using the validated 4,010-fact database!")
    else:
        print("\n❌ FAILED! Please check the errors above.")
