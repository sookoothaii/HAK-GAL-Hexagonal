#!/usr/bin/env python3
"""
HAK-GAL Scripts ULTRA-RADIKALER Cleanup
Datum: 2025-09-22
Zweck: Reduzierung von 411 auf NUR 2 Dateien!
Erkenntniss: Alle Engines sind in src_hexagonal/, nicht in scripts/
"""

import os
import shutil
from datetime import datetime
from pathlib import Path

# Konfiguration
SCRIPTS_DIR = Path(r"D:\MCP Mods\HAK_GAL_HEXAGONAL\scripts")
BACKUP_DIR = SCRIPTS_DIR / f"_archive_{datetime.now().strftime('%Y-%m-%d_%H-%M')}"

# Die EINZIGEN aktiven Dateien
ACTIVE_FILES = {
    "start_prometheus.py",
    "hakgal_dashboard_ultra.py",
    "RADICAL_CLEANUP.py",  # Dieses Skript selbst
    "ULTRA_RADICAL_CLEANUP.py"  # Dieses Skript selbst
}

def ultra_cleanup(dry_run=True):
    """Führt ultra-radikalen Cleanup durch - behält NUR 2 aktive Dateien!"""
    
    print(f"HAK-GAL Scripts ULTRA-Cleanup - {'DRY RUN' if dry_run else 'LIVE RUN'}")
    print("="*60)
    print("ERKENNTNISS: Alle Engines sind in src_hexagonal/")
    print("AKTION: Behalte NUR die 2 aktiven Skripte!")
    print("="*60)
    
    if not dry_run:
        BACKUP_DIR.mkdir(exist_ok=True)
    
    stats = {
        'total': 0,
        'active': 0,
        'archived': 0
    }
    
    # Durchlaufe alle Python-Dateien
    for file in SCRIPTS_DIR.glob("*.py"):
        if file.is_file():
            stats['total'] += 1
            filename = file.name
            
            if filename in ACTIVE_FILES:
                # Aktive Dateien - NICHT verschieben
                stats['active'] += 1
                print(f"[BEHALTEN] {filename}")
            else:
                # ALLES andere -> Archiv
                stats['archived'] += 1
                if stats['archived'] <= 20:  # Zeige erste 20
                    print(f"[ARCHIV]   {filename}")
                elif stats['archived'] == 21:
                    print(f"[ARCHIV]   ... und {stats['total'] - stats['active'] - 20} weitere Dateien")
                
                if not dry_run:
                    dest = BACKUP_DIR / filename
                    shutil.move(file, dest)
    
    # Zusammenfassung
    print("\n" + "="*60)
    print("ZUSAMMENFASSUNG:")
    print(f"Gesamt:     {stats['total']} Dateien")
    print(f"Behalten:   {stats['active']} Dateien (im scripts/ Ordner)")
    print(f"Archiviert: {stats['archived']} Dateien -> {BACKUP_DIR.name}/")
    print(f"\nREDUKTION: {stats['total']} → {stats['active']} Dateien ({(stats['archived']/stats['total']*100):.0f}% Reduktion)")
    
    print("\nHINWEIS: Die aktiven Komponenten befinden sich hier:")
    print("- Engines: src_hexagonal/infrastructure/engines/")
    print("- MCP Server: filesystem_mcp/ und ultimate_mcp/")
    print("- Backend: src_hexagonal/")
    
    if dry_run:
        print("\n⚠️  Dies war ein DRY RUN - keine Dateien wurden verschoben!")
        print("Führen Sie ultra_cleanup(dry_run=False) aus für echten Cleanup")
    else:
        print("\n✅ ULTRA-Cleanup abgeschlossen!")
        print(f"Backup in: {BACKUP_DIR}")
        print("\nDer scripts/ Ordner enthält jetzt NUR noch die 2 aktiven Skripte!")

if __name__ == "__main__":
    # Erst Dry Run
    ultra_cleanup(dry_run=True)
    
    print("\n" + "="*60)
    response = input("\n⚠️  WARNUNG: Dies wird 409 Dateien archivieren!\nMöchten Sie den ULTRA-Cleanup wirklich durchführen? [j/N]: ")
    
    if response.lower() == 'j':
        print("\nStarte ULTRA-Cleanup...\n")
        ultra_cleanup(dry_run=False)
    else:
        print("\nULTRA-Cleanup abgebrochen.")
