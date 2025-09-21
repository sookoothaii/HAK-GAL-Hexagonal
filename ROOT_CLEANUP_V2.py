#!/usr/bin/env python3
"""
HAK-GAL Root Directory Cleanup Script v2
Organisiert alle Root-Dateien in entsprechende Verzeichnisse
"""

import os
import shutil
from pathlib import Path

def cleanup_root_directory():
    """Organisiert Root-Dateien in entsprechende Verzeichnisse"""
    
    # Verzeichnisse erstellen
    directories = {
        'logs': ['audit_log.jsonl', 'filesystem_mcp.log', 'mcp_server.jsonl', 'mcp_server.log', 'mcp_write_audit.log'],
        'config': ['claude_desktop_config.json', 'llm_config.json', 'llm_config.example.json', 'governance_monitor.html'],
        'reports': ['quality_check_batch.json', 'verification_report_detailed.json', 'mcp_tools_extracted.json'],
        'temp': ['nul', 'chemistry_schema.sql', 'cleanup_deepseek.sql']
    }
    
    # Verzeichnisse erstellen
    for dir_name in directories.keys():
        Path(dir_name).mkdir(exist_ok=True)
        print(f"✅ Verzeichnis {dir_name}/ erstellt")
    
    # Dateien verschieben
    moved_count = 0
    for target_dir, files in directories.items():
        for file_name in files:
            if Path(file_name).exists():
                target_path = Path(target_dir) / file_name
                shutil.move(file_name, target_path)
                print(f"📁 {file_name} → {target_path}")
                moved_count += 1
    
    # Archive-Ordner löschen (nach Bestätigung)
    archive_dir = Path("_cleanup_archive_2025-09-22")
    if archive_dir.exists():
        print(f"🗑️  Archive-Ordner gefunden: {archive_dir}")
        print("   (Löschen nach manueller Bestätigung)")
    
    print(f"\n🎉 Cleanup abgeschlossen: {moved_count} Dateien organisiert")

if __name__ == "__main__":
    cleanup_root_directory()
