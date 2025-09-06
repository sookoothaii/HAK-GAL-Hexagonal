#!/usr/bin/env python3
"""
PROJEKT HUB REORGANIZER - LÖSUNG FÜR GPT
=========================================
Dieses Script löst das move_file Problem durch sichere Batch-Operationen
"""

import os
import sys
import shutil
import json
from pathlib import Path
from datetime import datetime
import fnmatch # NEU: Import für fnmatch

class ProjectHubReorganizer:
    def __init__(self, hub_path="PROJECT_HUB"):
        self.hub_path = Path(hub_path)
        self.backup_path = Path(f"{hub_path}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        
        # Neue Struktur Definition
        self.structure = {
            "docs/technical_reports": [
                "*TECHNICAL_REPORT*.md",
                "*TECH_REPORT*.md", 
                "*_REPORT_*.md"
            ],
            "docs/handovers": [
                "*HANDOVER*.md",
                "*HANDOFF*.md",
                "TECHNICAL_TRANSFORMATION*.md"
            ],
            "docs/snapshots": [
                "SNAPSHOT_*.md",
                "snapshot_*.json",
                "*_snapshot_*.json"
            ],
            "docs/system": [
                "SYSTEM_*.md",
                "STATUS_*.md",
                "*DASHBOARD*.md"
            ],
            "docs/migration": [
                "MIGRATION_*.md",
                "*MIGRAT*.md",
                "PHASE1_*.md"
            ],
            "docs/mcp": [
                "MCP_*.md",
                "*_MCP_*.md"
            ],
            "docs/mojo": [
                "MOJO_*.md",
                "*MOJO*.md",
                "REPORT_MOJO*.md"
            ],
            "configs": [
                "*.yaml",
                "*.json",
                "*.txt"
            ],
            "archive/old_snapshots": [
                "snapshot_20*",  # Alte Snapshot-Ordner
                "SNAPSHOT_5*"    # Port-basierte Snapshots
            ]
        }
    
    def create_backup(self):
        """Erstelle komplettes Backup bevor Reorganisation"""
        print(f"Erstelle Backup: {self.backup_path}")
        shutil.copytree(self.hub_path, self.backup_path)
        return True
    
    def create_structure(self):
        """Erstelle neue Verzeichnisstruktur"""
        for path in self.structure.keys():
            full_path = self.hub_path / path
            full_path.mkdir(parents=True, exist_ok=True)
            print(f"Erstellt: {path}")
    
    def categorize_files(self):
        """Kategorisiere alle Dateien und Ordner nach Patterns"""
        categorized = {cat: [] for cat in self.structure.keys()}
        uncategorized = []
        
        for item in self.hub_path.iterdir(): # Iterate over all items (files and dirs)
            matched = False
            for category, patterns in self.structure.items():
                for pattern in patterns:
                    if fnmatch.fnmatch(item.name, pattern): # Match against item.name using fnmatch
                        categorized[category].append(item.name)
                        matched = True
                        break
                if matched:
                    break
            if not matched: # If no category matched, add to uncategorized
                uncategorized.append(item.name)
        
        return categorized, uncategorized
    
    def move_files_safely(self, categorized):
        """Verschiebe Dateien mit Verifikation"""
        moved_count = 0
        failed = []
        
        for category, files in categorized.items():
            dest_dir = self.hub_path / category
            for filename in files:
                source = self.hub_path / filename
                dest = dest_dir / filename
                
                try:
                    # WICHTIG: Verwende shutil.move statt os.rename
                    # für cross-filesystem moves
                    shutil.move(str(source), str(dest))
                    
                    # Verifikation
                    if dest.exists() and not source.exists():
                        moved_count += 1
                        print(f"{filename} -> {category}")
                    else:
                        failed.append(filename)
                        print(f"FAILED: {filename}")
                except Exception as e:
                    failed.append(filename)
                    print(f"ERROR moving {filename}: {e}")
        
        return moved_count, failed
    
    def generate_index(self):
        """Erstelle INDEX.md für schnellen Überblick"""
        index_content = f"""# PROJECT HUB INDEX
Generated: {datetime.now().isoformat()}

## STATISTIK
"""
        
        for category in self.structure.keys():
            path = self.hub_path / category
            if path.exists():
                count = len(list(path.glob("*")))
                index_content += f"- **{category}**: {count} Dateien\n"
        
        index_content += "\n## STRUKTUR\n\n```"
        
        # Tree-View generieren
        for root, dirs, files in os.walk(self.hub_path):
            level = root.replace(str(self.hub_path), '').count(os.sep)
            indent = ' ' * 2 * level
            folder = os.path.basename(root)
            if folder:
                index_content += f"\n{indent}{folder}/"
            subindent = ' ' * 2 * (level + 1)
            for file in files[:5]:  # Nur erste 5 Dateien pro Ordner
                index_content += f"\n{subindent}{file}"
            if len(files) > 5:
                index_content += f"\n{subindent}... +{len(files)-5} mehr"
        
        index_content += "\n```"
        
        # Speichere INDEX.md
        with open(self.hub_path / "INDEX.md", "w", encoding="utf-8") as f:
            f.write(index_content)
        
        print(f"INDEX.md erstellt")
        return index_content
    
    def run_reorganization(self):
        """Führe komplette Reorganisation durch"""
        print("STARTE PROJECT HUB REORGANISATION")
        print("=" * 50)
        
        # 1. Backup
        if not self.create_backup():
            print("Backup fehlgeschlagen - Abbruch!")
            return False
        
        # 2. Struktur erstellen
        self.create_structure()
        
        # 3. Dateien kategorisieren
        categorized, uncategorized = self.categorize_files()
        
        print(f"\nKategorisierung:")
        for cat, files in categorized.items():
            print(f"  {cat}: {len(files)} Dateien")
        print(f"  Unkategorisiert: {len(uncategorized)} Dateien")
        
        # 4. Dateien verschieben
        print(f"\nVerschiebe Dateien...")
        moved, failed = self.move_files_safely(categorized)
        
        print(f"\nErfolgreich verschoben: {moved}")
        if failed:
            print(f"Fehlgeschlagen: {len(failed)}")
            for f in failed[:5]:
                print(f"  - {f}")
        
        # 5. Index generieren
        self.generate_index()
        
        # 6. Zusammenfassung
        print("\n" + "=" * 50)
        print("REORGANISATION ABGESCHLOSSEN")
        print(f"{moved} Dateien reorganisiert")
        print(f"Backup unter: {self.backup_path}")
        print(f"INDEX.md für Schnellzugriff erstellt")
        
        return True

# FÜR GPT: VERWENDUNG
if __name__ == "__main__":
    reorganizer = ProjectHubReorganizer("D:/MCP Mods/HAK_GAL_HEXAGONAL/PROJECT_HUB")
    
    # Test-Modus (nur Analyse, keine Änderungen)
    if "--dry-run" in sys.argv:
        categorized, uncategorized = reorganizer.categorize_files()
        print("DRY RUN - Würde folgende Änderungen machen:")
        for cat, files in categorized.items():
            print(f"\n{cat}:")
            for f in files[:3]:
                print(f"  - {f}")
            if len(files) > 3:
                print(f"  ... +{len(files)-3} mehr")
    else:
        # LIVE RUN
        reorganizer.run_reorganization()