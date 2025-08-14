#!/usr/bin/env python3
"""
Frontend Cleanup Script
Entfernt alle Backup-Dateien und dokumentiert Duplicate-Implementierungen
Nach HAK/GAL Verfassung Artikel 6: Empirische Validierung
"""

import os
import shutil
from datetime import datetime
from pathlib import Path
import json

# Base directory
BASE_DIR = Path(r"D:\MCP Mods\HAK_GAL_HEXAGONAL\frontend")

# Backup files to remove (empirisch gefunden)
BACKUP_FILES_TO_REMOVE = [
    r"src\ProApp.backup_20250808_224804",
    r"src\ProApp.tsx.backup_20250812_075547",
    r"src\components\ProNavigation.backup_20250808_224804",
    r"src\components\ProNavigation.tsx.backup_20250812_075547",
    r"src\config\backends.ts.backup_20250812_074343",
    r"src\pages\ProDashboard.backup_20250808_224804",
    r"src\pages\ProDashboard.tsx.backup_20250812_075547",
    r"src\pages\ProQueryInterface_backup.tsx",
    r"src\services\websocket.ts.backup_20250812_074343",
]

# Duplicate implementations to analyze
DUPLICATES_TO_ANALYZE = {
    "KnowledgePage": [
        r"src\pages\KnowledgePage.tsx",
        r"src\pages\KnowledgePage_new.tsx",
        r"src\pages\KnowledgePage_original.tsx"
    ],
    "ProQueryInterface": [
        r"src\pages\ProQueryInterface.tsx",
        r"src\pages\ProQueryInterface_DualResponse.tsx",
        r"src\pages\ProQueryInterface_backup.tsx"
    ],
    "ProUnifiedQuery": [
        r"src\pages\ProUnifiedQuery.tsx",
        r"src\pages\ProUnifiedQuery_original.tsx"
    ],
    "ProSettings": [
        r"src\pages\ProSettings.tsx",
        r"src\pages\ProSettingsEnhanced.tsx"
    ]
}

def create_safety_backup():
    """Create a safety backup before cleanup"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = BASE_DIR / f"cleanup_backup_{timestamp}"
    
    print(f"Creating safety backup at: {backup_dir}")
    
    # Backup all files we're going to remove
    for file_path in BACKUP_FILES_TO_REMOVE:
        full_path = BASE_DIR / file_path
        if full_path.exists():
            backup_path = backup_dir / file_path
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(full_path, backup_path)
            print(f"  Backed up: {file_path}")
    
    return backup_dir

def analyze_duplicates():
    """Analyze duplicate implementations"""
    report = {}
    
    for component, files in DUPLICATES_TO_ANALYZE.items():
        report[component] = {
            "files": [],
            "recommendation": ""
        }
        
        for file_path in files:
            full_path = BASE_DIR / file_path
            if full_path.exists():
                size = full_path.stat().st_size
                modified = datetime.fromtimestamp(full_path.stat().st_mtime)
                
                report[component]["files"].append({
                    "path": file_path,
                    "size": size,
                    "modified": modified.isoformat(),
                    "exists": True
                })
            else:
                report[component]["files"].append({
                    "path": file_path,
                    "exists": False
                })
        
        # Recommendation logic
        if component == "KnowledgePage":
            report[component]["recommendation"] = "Keep KnowledgePage_new.tsx (likely most optimized), remove others"
        elif component == "ProQueryInterface":
            report[component]["recommendation"] = "Merge DualResponse features into main ProQueryInterface.tsx"
        elif component == "ProUnifiedQuery":
            report[component]["recommendation"] = "Keep ProUnifiedQuery.tsx (main version)"
        elif component == "ProSettings":
            report[component]["recommendation"] = "Merge Enhanced features into main ProSettings.tsx"
    
    return report

def remove_backup_files():
    """Remove all backup files"""
    removed = []
    errors = []
    
    for file_path in BACKUP_FILES_TO_REMOVE:
        full_path = BASE_DIR / file_path
        if full_path.exists():
            try:
                full_path.unlink()
                removed.append(file_path)
                print(f"✅ Removed: {file_path}")
            except Exception as e:
                errors.append({"file": file_path, "error": str(e)})
                print(f"❌ Error removing {file_path}: {e}")
        else:
            print(f"⏭️  Already gone: {file_path}")
    
    return removed, errors

def generate_report(backup_dir, removed_files, errors, duplicate_analysis):
    """Generate cleanup report"""
    report = {
        "timestamp": datetime.now().isoformat(),
        "backup_location": str(backup_dir),
        "files_removed": len(removed_files),
        "removed_list": removed_files,
        "errors": errors,
        "duplicate_analysis": duplicate_analysis,
        "recommendations": {
            "immediate": [
                "Test frontend after backup removal",
                "Consolidate duplicate implementations",
                "Update imports if needed"
            ],
            "next_steps": [
                "Implement unified store architecture",
                "Add virtual scrolling for large lists",
                "Fix TypeScript typing issues"
            ]
        }
    }
    
    report_path = BASE_DIR / f"cleanup_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📊 Report saved to: {report_path}")
    
    return report

def main():
    print("=" * 60)
    print("HAK-GAL Frontend Cleanup Script")
    print("Nach HAK/GAL Verfassung - Empirische Validierung")
    print("=" * 60)
    
    # Step 1: Create safety backup
    print("\n📦 Step 1: Creating safety backup...")
    backup_dir = create_safety_backup()
    
    # Step 2: Analyze duplicates
    print("\n🔍 Step 2: Analyzing duplicate implementations...")
    duplicate_analysis = analyze_duplicates()
    
    # Step 3: Remove backup files
    print("\n🗑️ Step 3: Removing backup files...")
    removed_files, errors = remove_backup_files()
    
    # Step 4: Generate report
    print("\n📝 Step 4: Generating report...")
    report = generate_report(backup_dir, removed_files, errors, duplicate_analysis)
    
    # Summary
    print("\n" + "=" * 60)
    print("CLEANUP SUMMARY")
    print("=" * 60)
    print(f"✅ Files removed: {len(removed_files)}")
    print(f"❌ Errors: {len(errors)}")
    print(f"📊 Duplicates found: {len(duplicate_analysis)}")
    print(f"💾 Backup location: {backup_dir}")
    
    print("\n🎯 Next Steps:")
    print("1. Test frontend functionality")
    print("2. Consolidate duplicate implementations")
    print("3. Update import statements if needed")
    print("4. Run: npm run dev (to verify)")
    
    return report

if __name__ == "__main__":
    main()
