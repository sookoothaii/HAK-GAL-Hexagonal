"""
Clear Python Cache Script
=========================
Löscht alle __pycache__ Verzeichnisse vor Backend-Neustart
"""

import os
import shutil
from pathlib import Path

def clear_all_pycache():
    """Lösche alle __pycache__ Verzeichnisse rekursiv"""
    
    base_path = Path(r"D:\MCP Mods\HAK_GAL_HEXAGONAL")
    
    # Finde alle __pycache__ Verzeichnisse
    pycache_dirs = list(base_path.rglob("__pycache__"))
    
    if not pycache_dirs:
        print("ℹ️ Keine __pycache__ Verzeichnisse gefunden.")
        return
    
    print(f"🔍 Gefunden: {len(pycache_dirs)} __pycache__ Verzeichnisse")
    print("-" * 60)
    
    # Lösche jedes gefundene Verzeichnis
    for cache_dir in pycache_dirs:
        try:
            shutil.rmtree(cache_dir)
            print(f"✅ Gelöscht: {cache_dir}")
        except Exception as e:
            print(f"❌ Fehler bei {cache_dir}: {e}")
    
    print("-" * 60)
    print(f"✨ Alle Caches gelöscht! Backend kann neu gestartet werden.")

if __name__ == "__main__":
    clear_all_pycache()
