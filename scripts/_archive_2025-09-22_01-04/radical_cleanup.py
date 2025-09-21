#!/usr/bin/env python3
"""
HAK-GAL Scripts Radikaler Cleanup
Datum: 2025-09-22
Zweck: Reduzierung von 410 auf ~10 Dateien
ACHTUNG: Erstellt Backup bevor es aufräumt!
"""

import os
import shutil
from datetime import datetime
from pathlib import Path

# Konfiguration
SCRIPTS_DIR = Path(r"D:\MCP Mods\HAK_GAL_HEXAGONAL\scripts")
BACKUP_DIR = SCRIPTS_DIR / f"_archive_{datetime.now().strftime('%Y-%m-%d_%H-%M')}"
ACTIVE_DIR = SCRIPTS_DIR / "active"
ENGINES_DIR = SCRIPTS_DIR / "engines"

# Die einzigen aktiven Dateien
ACTIVE_FILES = {
    "start_prometheus.py",
    "hakgal_dashboard_ultra.py"
}

# Engines die möglicherweise noch benötigt werden
ENGINE_FILES = {
    "aethelred_engine.py",
    "archimedes_engine.py", 
    "thesis_engine.py",
    "advanced_growth_engine_intelligent.py"  # Neueste Version
}

def cleanup_scripts(dry_run=True):
    """Führt radikalen Cleanup durch"""
    
    print(f"HAK-GAL Scripts Cleanup - {'DRY RUN' if dry_run else 'LIVE RUN'}")
    print("="*60)
    
    # Erstelle Verzeichnisse
    if not dry_run:
        BACKUP_DIR.mkdir(exist_ok=True)
        ACTIVE_DIR.mkdir(exist_ok=True)
        ENGINES_DIR.mkdir(exist_ok=True)
    
    stats = {
        'total': 0,
        'active': 0,
        'engines': 0,
        'archived': 0
    }
    
    # Durchlaufe alle Python-Dateien
    for file in SCRIPTS_DIR.glob("*.py"):
        if file.is_file():
            stats['total'] += 1
            filename = file.name
            
            if filename in ACTIVE_FILES:
                # Aktive Dateien
                stats['active'] += 1
                dest = ACTIVE_DIR / filename
                print(f"[ACTIVE] {filename}")
                if not dry_run:
                    shutil.copy2(file, dest)
                    
            elif filename in ENGINE_FILES:
                # Engine Dateien
                stats['engines'] += 1
                dest = ENGINES_DIR / filename
                print(f"[ENGINE] {filename}")
                if not dry_run:
                    shutil.copy2(file, dest)
                    
            else:
                # Alles andere -> Archiv
                stats['archived'] += 1
                if stats['archived'] <= 10:  # Zeige nur erste 10
                    print(f"[ARCHIV] {filename}")
                elif stats['archived'] == 11:
                    print(f"[ARCHIV] ... und {stats['total'] - stats['active'] - stats['engines'] - 10} weitere Dateien")
                
                if not dry_run:
                    dest = BACKUP_DIR / filename
                    shutil.move(file, dest)
    
    # Zusammenfassung
    print("\n" + "="*60)
    print("ZUSAMMENFASSUNG:")
    print(f"Gesamt:    {stats['total']} Dateien")
    print(f"Aktiv:     {stats['active']} Dateien -> active/")
    print(f"Engines:   {stats['engines']} Dateien -> engines/")
    print(f"Archiviert: {stats['archived']} Dateien -> {BACKUP_DIR.name}/")
    print(f"\nREDUKTION: {stats['total']} → {stats['active'] + stats['engines']} Dateien ({(stats['archived']/stats['total']*100):.0f}% Reduktion)")
    
    if dry_run:
        print("\n⚠️  Dies war ein DRY RUN - keine Dateien wurden verschoben!")
        print("Führen Sie cleanup_scripts(dry_run=False) aus für echten Cleanup")
    else:
        print("\n✅ Cleanup abgeschlossen!")
        print(f"Backup in: {BACKUP_DIR}")

if __name__ == "__main__":
    # Erst Dry Run
    cleanup_scripts(dry_run=True)
    
    print("\n" + "="*60)
    response = input("\nMöchten Sie den Cleanup wirklich durchführen? [j/N]: ")
    
    if response.lower() == 'j':
        print("\nStarte echten Cleanup...\n")
        cleanup_scripts(dry_run=False)
    else:
        print("\nCleanup abgebrochen.")
