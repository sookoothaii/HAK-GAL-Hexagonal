#!/usr/bin/env python3
"""
AUTOFIX SCRIPT für n-äre Fact Tools
Automatische Integration der reparierten Tools in HAK_GAL MCP Server

Dieses Script:
1. Sichert die originalen MCP Server Dateien
2. Patcht die defekten Tool-Handler
3. Testet die Integration
4. Kann bei Problemen zurückgerollt werden

Author: Claude
Date: 2025-09-19
"""

import os
import shutil
import re
from datetime import datetime
import sys

# Pfade
BASE_PATH = r'D:\MCP Mods\HAK_GAL_HEXAGONAL'
ULTIMATE_MCP = os.path.join(BASE_PATH, 'ultimate_mcp', 'hakgal_mcp_ultimate.py')
FILESYSTEM_MCP = os.path.join(BASE_PATH, 'filesystem_mcp', 'hak_gal_filesystem.py')
BACKUP_DIR = os.path.join(BASE_PATH, 'backups', f'nary_fix_{datetime.now().strftime("%Y%m%d_%H%M%S")}')


def create_backup():
    """Erstellt Backup der MCP Server Dateien"""
    print("📁 Erstelle Backup...")
    os.makedirs(BACKUP_DIR, exist_ok=True)
    
    files_to_backup = [ULTIMATE_MCP, FILESYSTEM_MCP]
    for file in files_to_backup:
        if os.path.exists(file):
            backup_file = os.path.join(BACKUP_DIR, os.path.basename(file))
            shutil.copy2(file, backup_file)
            print(f"  ✓ {os.path.basename(file)} gesichert")
    
    print(f"  → Backup in: {BACKUP_DIR}\n")


def find_tool_handler_section(content: str) -> tuple:
    """Findet die Tool Handler Section im Code"""
    # Suche nach verschiedenen Patterns
    patterns = [
        r'if\s+name\s*==\s*["\']semantic_similarity["\']\s*:',
        r'case\s+["\']semantic_similarity["\']\s*:',
        r'["\']semantic_similarity["\']\s*:\s*lambda'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, content)
        if match:
            return match.start(), pattern
    
    return None, None


def patch_mcp_server(filepath: str) -> bool:
    """Patcht eine MCP Server Datei"""
    if not os.path.exists(filepath):
        print(f"  ✗ Datei nicht gefunden: {filepath}")
        return False
    
    print(f"\n🔧 Patche {os.path.basename(filepath)}...")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Prüfe ob bereits gepatcht
    if 'mcp_nary_patches' in content or 'semantic_similarity_nary' in content:
        print("  ℹ️ Bereits gepatcht, überspringe...")
        return True
    
    # Füge Import hinzu
    import_line = "from scripts.mcp_nary_patches import patch_mcp_server_tools, NARY_TOOL_DEFINITIONS\n"
    
    # Finde passende Stelle für Import (nach anderen imports)
    import_pos = content.rfind('import ')
    if import_pos > 0:
        # Finde Ende der Zeile
        newline_pos = content.find('\n', import_pos)
        if newline_pos > 0:
            # Füge Import nach der letzten import-Zeile hinzu
            content = content[:newline_pos + 1] + import_line + content[newline_pos + 1:]
            print("  ✓ Import hinzugefügt")
    
    # Füge Patch-Aufruf hinzu (nach den Imports, vor dem Server-Start)
    patch_code = """
# === N-ÄRE FACT TOOL PATCHES ===
print("Applying n-ary fact tool patches...")
patched_tools = patch_mcp_server_tools()
# === END PATCHES ===

"""
    
    # Finde gute Position für Patch (nach Imports, vor Server-Definition)
    server_pos = content.find('server = ')
    if server_pos < 0:
        server_pos = content.find('Server(')
    
    if server_pos > 0:
        content = content[:server_pos] + patch_code + content[server_pos:]
        print("  ✓ Patch-Code eingefügt")
    
    # Ersetze Tool-Handler
    # Suche nach semantic_similarity handler
    handler_pos, pattern = find_tool_handler_section(content)
    if handler_pos:
        print(f"  ✓ Tool-Handler gefunden mit Pattern: {pattern[:30]}...")
        
        # Füge Redirect zu gepatchten Tools hinzu
        redirect_code = """
        # Redirected to n-ary compatible version
        if name in patched_tools:
            params_dict = params if isinstance(params, dict) else {}
            return await patched_tools[name](**params_dict)
"""
        # Füge nach dem gefundenen Pattern ein
        insert_pos = handler_pos
        content = content[:insert_pos] + redirect_code + "\n        " + content[insert_pos:]
        print("  ✓ Handler-Redirect hinzugefügt")
    
    # Speichere gepatchte Datei
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"  ✅ {os.path.basename(filepath)} erfolgreich gepatcht!")
    return True


def verify_patches():
    """Verifiziert dass die Patches funktionieren"""
    print("\n🔍 Verifiziere Patches...")
    
    # Teste ob die gepatchten Tools geladen werden können
    sys.path.append(os.path.join(BASE_PATH, 'scripts'))
    try:
        from mcp_nary_patches import patch_mcp_server_tools
        tools = patch_mcp_server_tools()
        print(f"  ✓ {len(tools)} Tools erfolgreich gepatcht")
        for tool_name in tools:
            print(f"    • {tool_name}")
        return True
    except Exception as e:
        print(f"  ✗ Fehler beim Laden der Patches: {e}")
        return False


def rollback():
    """Stellt die Original-Dateien wieder her"""
    print("\n⏮️ Rollback zu Original-Dateien...")
    
    if not os.path.exists(BACKUP_DIR):
        print("  ✗ Kein Backup gefunden!")
        return False
    
    for file in os.listdir(BACKUP_DIR):
        backup_file = os.path.join(BACKUP_DIR, file)
        if file == 'hakgal_mcp_ultimate.py':
            target = ULTIMATE_MCP
        elif file == 'hak_gal_filesystem.py':
            target = FILESYSTEM_MCP
        else:
            continue
        
        shutil.copy2(backup_file, target)
        print(f"  ✓ {file} wiederhergestellt")
    
    print("  ✅ Rollback abgeschlossen!")
    return True


def main():
    """Hauptfunktion"""
    print("=" * 60)
    print("HAK_GAL N-ÄRE FACT TOOLS - AUTO PATCH")
    print("=" * 60)
    
    # Schritt 1: Backup
    create_backup()
    
    # Schritt 2: Verifiziere dass Patch-Dateien existieren
    patch_file = os.path.join(BASE_PATH, 'scripts', 'mcp_nary_patches.py')
    fix_file = os.path.join(BASE_PATH, 'scripts', 'fix_nary_tools.py')
    
    if not os.path.exists(patch_file):
        print("✗ mcp_nary_patches.py nicht gefunden!")
        return False
    if not os.path.exists(fix_file):
        print("✗ fix_nary_tools.py nicht gefunden!")
        return False
    
    print("✓ Patch-Dateien gefunden\n")
    
    # Schritt 3: Patche Server (wenn vorhanden)
    success = True
    if os.path.exists(ULTIMATE_MCP):
        if not patch_mcp_server(ULTIMATE_MCP):
            success = False
    
    if os.path.exists(FILESYSTEM_MCP):
        if not patch_mcp_server(FILESYSTEM_MCP):
            success = False
    
    # Schritt 4: Verifiziere
    if success:
        if verify_patches():
            print("\n" + "=" * 60)
            print("✅ PATCH ERFOLGREICH ANGEWENDET!")
            print("=" * 60)
            print("\nNächste Schritte:")
            print("1. Starte MCP Server neu:")
            print("   python ultimate_mcp/hakgal_mcp_ultimate.py")
            print("\n2. Teste die reparierten Tools:")
            print("   - semantic_similarity")
            print("   - consistency_check")
            print("   - validate_facts")
            print("   - inference_chain")
            print("\n3. Bei Problemen, führe Rollback aus:")
            print("   python autofix_nary_tools.py --rollback")
        else:
            print("\n⚠️ Verifikation fehlgeschlagen!")
            print("Führe Rollback aus...")
            rollback()
    else:
        print("\n✗ Patch fehlgeschlagen!")
        print("Manuelle Intervention erforderlich.")
    
    return success


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--rollback':
        rollback()
    else:
        success = main()
        sys.exit(0 if success else 1)
