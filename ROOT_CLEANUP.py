#!/usr/bin/env python3
"""
HAK-GAL Root Directory Cleanup
Datum: 2025-09-22
Zweck: Aufräumen des Root-Verzeichnisses vor dem Push
"""

import os
import shutil
from pathlib import Path
from datetime import datetime

# Konfiguration
ROOT_DIR = Path(r"D:\MCP Mods\HAK_GAL_HEXAGONAL")
ARCHIVE_DIR = ROOT_DIR / f"_cleanup_archive_{datetime.now().strftime('%Y-%m-%d')}"

# Kritische Dateien die BLEIBEN müssen
KEEP_FILES = {
    # Wichtige Configs
    'requirements.txt',
    'package.json',
    'package-lock.json',
    '.gitignore',
    'README.md',
    'LICENSE',
    'docker-compose.yml',
    'Dockerfile',
    '.env',
    '.env.example',
    
    # Aktive Configs
    'combined-mcp.sse.config.json',  # Für MCP
    'llm_config.json',               # LLM Konfiguration
    'governor_extended_optimized.conf', # Governance
    
    # Datenbank
    'hexagonal_kb.db',
    'hexagonal_kb.db-shm',
    'hexagonal_kb.db-wal',
    
    # Start-Skripte
    'START_BACKEND_FIXED.bat',
    'START_CADDY.bat',
}

# Dateien zum Löschen/Archivieren
TO_ARCHIVE = {
    # Logs
    '*.log',
    '*.jsonl',
    
    # Test-Reports
    'test_*.json',
    '*_test.json',
    '*_results.json',
    'validation_*.json',
    
    # Node Kataloge
    'node_catalog*.json',
    'node_catalog*.csv',
    
    # Alte Configs
    '*_fixed.json',
    '*_old.*',
    '*.backup_*',
    
    # Temporäre Dateien
    '*_report.json',
    '*_stats.json',
    'rescue_report.json',
    'semantic_fix_stats.json',
}

# Verzeichnisse zum Archivieren
ARCHIVE_DIRS = {
    'PROJECT_HUB_BACKUP_20250915',
    'emergency_dumps',
    'cursor_exchange',
    'validation_batches',
    'validation_results', 
    'validation_samples',
    'agent_responses',
    '__pycache__',
    'batch',
    'reports',  # Falls keine wichtigen Reports drin sind
}

def cleanup_root(dry_run=True):
    """Räumt das Root-Verzeichnis auf"""
    
    print(f"HAK-GAL Root Cleanup - {'DRY RUN' if dry_run else 'LIVE RUN'}")
    print("="*60)
    
    if not dry_run:
        ARCHIVE_DIR.mkdir(exist_ok=True)
    
    stats = {
        'files_kept': 0,
        'files_archived': 0,
        'dirs_archived': 0,
        'space_freed_mb': 0
    }
    
    # 1. Dateien durchgehen
    print("\n📄 DATEIEN:")
    for pattern in TO_ARCHIVE:
        for file in ROOT_DIR.glob(pattern):
            if file.is_file() and file.name not in KEEP_FILES:
                size_mb = file.stat().st_size / (1024 * 1024)
                stats['space_freed_mb'] += size_mb
                stats['files_archived'] += 1
                
                print(f"[ARCHIV] {file.name} ({size_mb:.1f} MB)")
                
                if not dry_run:
                    dest = ARCHIVE_DIR / file.name
                    shutil.move(str(file), str(dest))
    
    # Beibehaltene Dateien zählen
    for file in ROOT_DIR.glob("*"):
        if file.is_file() and file.name in KEEP_FILES:
            stats['files_kept'] += 1
            if dry_run:
                print(f"[BEHALTEN] {file.name}")
    
    # 2. Verzeichnisse durchgehen
    print("\n📁 VERZEICHNISSE:")
    for dir_name in ARCHIVE_DIRS:
        dir_path = ROOT_DIR / dir_name
        if dir_path.exists() and dir_path.is_dir():
            # Größe berechnen
            size_mb = sum(f.stat().st_size for f in dir_path.rglob('*') if f.is_file()) / (1024 * 1024)
            stats['space_freed_mb'] += size_mb
            stats['dirs_archived'] += 1
            
            print(f"[ARCHIV] {dir_name}/ ({size_mb:.1f} MB)")
            
            if not dry_run:
                dest = ARCHIVE_DIR / dir_name
                shutil.move(str(dir_path), str(dest))
    
    # 3. Zusammenfassung
    print("\n" + "="*60)
    print("ZUSAMMENFASSUNG:")
    print(f"Dateien behalten:    {stats['files_kept']}")
    print(f"Dateien archiviert:  {stats['files_archived']}")
    print(f"Ordner archiviert:   {stats['dirs_archived']}")
    print(f"Speicher freigegeben: {stats['space_freed_mb']:.1f} MB")
    
    if dry_run:
        print("\n⚠️  Dies war ein DRY RUN - nichts wurde verschoben!")
        print("Führen Sie cleanup_root(dry_run=False) aus für echten Cleanup")
    else:
        print(f"\n✅ Cleanup abgeschlossen!")
        print(f"Archiv in: {ARCHIVE_DIR}")
        
    # Zeige finale Struktur
    print("\n📋 FINALE ROOT-STRUKTUR:")
    critical_items = [
        'filesystem_mcp/', 'ultimate_mcp/', 'src_hexagonal/', 
        'frontend/', 'PROJECT_HUB/', 'tests/', 'models/', 'docs/',
        'scripts/', 'snapshots/', '.git/'
    ]
    for item in critical_items:
        print(f"  ✅ {item}")

if __name__ == "__main__":
    cleanup_root(dry_run=True)
    
    print("\n" + "="*60)
    response = input("\nRoot-Cleanup durchführen? [j/N]: ")
    
    if response.lower() == 'j':
        print("\nStarte Root-Cleanup...\n")
        cleanup_root(dry_run=False)
    else:
        print("\nCleanup abgebrochen.")
