#!/usr/bin/env python3
"""
MANUELLER PATCH für n-äre Fact Tools
Sicherer Patch ohne Syntax-Fehler

Author: Claude
Date: 2025-09-19
"""

import os
import shutil
from datetime import datetime

def manual_patch_hakgal_mcp():
    """Patcht hakgal_mcp_ultimate.py manuell und sicher"""
    
    filepath = r'D:\MCP Mods\HAK_GAL_HEXAGONAL\ultimate_mcp\hakgal_mcp_ultimate.py'
    
    # Backup
    backup_path = filepath + f'.backup_{datetime.now().strftime("%H%M%S")}'
    shutil.copy2(filepath, backup_path)
    print(f"✓ Backup erstellt: {backup_path}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # 1. Füge Import am Anfang der Datei hinzu (nach den anderen Imports)
    import_added = False
    for i, line in enumerate(lines):
        if i < 50 and 'import ' in line and not import_added:
            # Nach den Standard-Imports
            if 'from ' in lines[i] or 'import ' in lines[i]:
                # Warte auf eine Leerzeile oder Ende der Import-Section
                if i+1 < len(lines) and (lines[i+1].strip() == '' or not lines[i+1].startswith(('import', 'from'))):
                    lines.insert(i+1, '\n# N-äre Fact Patches\ntry:\n    from scripts.mcp_nary_patches import patch_mcp_server_tools, NARY_TOOL_DEFINITIONS\n    NARY_PATCHES_AVAILABLE = True\nexcept ImportError:\n    NARY_PATCHES_AVAILABLE = False\n    print("Warning: N-ary patches not available")\n\n')
                    import_added = True
                    print(f"✓ Import hinzugefügt nach Zeile {i+1}")
                    break
    
    # 2. Füge Patch-Aktivierung hinzu (vor Server-Start)
    patch_added = False
    for i, line in enumerate(lines):
        if 'async def main()' in line and not patch_added:
            # Füge am Anfang der main() Funktion hinzu
            for j in range(i+1, min(i+20, len(lines))):
                if '"""' in lines[j] or "'''" in lines[j]:
                    # Nach dem Docstring
                    continue
                elif lines[j].strip() and not lines[j].strip().startswith('#'):
                    # Erste echte Code-Zeile
                    indent = len(lines[j]) - len(lines[j].lstrip())
                    patch_code = ' ' * indent + '# Apply n-ary patches if available\n'
                    patch_code += ' ' * indent + 'if NARY_PATCHES_AVAILABLE:\n'
                    patch_code += ' ' * (indent + 4) + 'global patched_tools\n'
                    patch_code += ' ' * (indent + 4) + 'patched_tools = patch_mcp_server_tools()\n'
                    patch_code += ' ' * (indent + 4) + 'print("✓ N-ary fact patches applied")\n\n'
                    lines.insert(j, patch_code)
                    patch_added = True
                    print(f"✓ Patch-Aktivierung hinzugefügt in main() bei Zeile {j+1}")
                    break
    
    # 3. Modifiziere semantic_similarity Handler
    for i, line in enumerate(lines):
        if 'name == "semantic_similarity"' in line:
            # Füge Check für gepatchte Version hinzu
            indent = len(lines[i]) - len(lines[i].lstrip())
            check_code = ' ' * (indent + 4) + '# Use n-ary compatible version if available\n'
            check_code += ' ' * (indent + 4) + 'if NARY_PATCHES_AVAILABLE and "semantic_similarity" in patched_tools:\n'
            check_code += ' ' * (indent + 8) + 'result = await patched_tools["semantic_similarity"](\n'
            check_code += ' ' * (indent + 12) + 'params.get("statement"),\n'
            check_code += ' ' * (indent + 12) + 'params.get("limit", 50),\n'
            check_code += ' ' * (indent + 12) + 'params.get("threshold", 0.8)\n'
            check_code += ' ' * (indent + 8) + ')\n'
            check_code += ' ' * (indent + 8) + 'return str(result)\n'
            check_code += ' ' * (indent + 4) + '# Otherwise use original implementation\n'
            
            # Füge nach der if-Zeile ein
            lines.insert(i+1, check_code)
            print(f"✓ semantic_similarity Handler modifiziert bei Zeile {i+1}")
            break
    
    # Speichere gepatchte Datei
    with open(filepath, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print("✓ Datei erfolgreich gepatcht")
    
    # Verifiziere Syntax
    import ast
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            ast.parse(f.read())
        print("✅ Syntax-Check bestanden!")
        return True
    except SyntaxError as e:
        print(f"❌ Syntax-Fehler: {e}")
        # Restore backup
        shutil.copy2(backup_path, filepath)
        print("✓ Backup wiederhergestellt")
        return False


def add_simple_wrapper():
    """Alternative: Erstellt einen einfachen Wrapper"""
    
    wrapper_content = '''#!/usr/bin/env python3
"""
Wrapper für HAK_GAL MCP mit n-ären Fact Patches
Startet den Original-Server mit gepatchten Tools
"""

import sys
import os

# Füge scripts zum Path hinzu
sys.path.insert(0, r'D:\\MCP Mods\\HAK_GAL_HEXAGONAL\\scripts')

# Importiere Patches
try:
    from mcp_nary_patches import patch_mcp_server_tools
    patched_tools = patch_mcp_server_tools()
    print("✓ N-ary patches loaded")
    
    # Monkey-patch die Tools global
    import builtins
    builtins.NARY_PATCHED_TOOLS = patched_tools
    builtins.NARY_PATCHES_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not load n-ary patches: {e}")
    builtins.NARY_PATCHES_AVAILABLE = False

# Starte Original Server
exec(open(r'D:\\MCP Mods\\HAK_GAL_HEXAGONAL\\ultimate_mcp\\hakgal_mcp_ultimate.py').read())
'''
    
    wrapper_path = r'D:\MCP Mods\HAK_GAL_HEXAGONAL\ultimate_mcp\hakgal_mcp_patched.py'
    with open(wrapper_path, 'w', encoding='utf-8') as f:
        f.write(wrapper_content)
    
    print(f"✓ Wrapper erstellt: {wrapper_path}")
    print("  Verwenden Sie: python ultimate_mcp\\hakgal_mcp_patched.py")
    return wrapper_path


if __name__ == "__main__":
    print("=" * 60)
    print("MANUELLER N-ÄRE FACT PATCH")
    print("=" * 60)
    
    choice = input("\nWählen Sie:\n1. Direkt patchen (modifiziert hakgal_mcp_ultimate.py)\n2. Wrapper erstellen (erstellt hakgal_mcp_patched.py)\n\nWahl (1 oder 2): ")
    
    if choice == '1':
        success = manual_patch_hakgal_mcp()
        if success:
            print("\n✅ Patch erfolgreich!")
            print("Starten Sie den Server neu:")
            print("  python ultimate_mcp\\hakgal_mcp_ultimate.py")
    else:
        wrapper = add_simple_wrapper()
        print("\n✅ Wrapper erstellt!")
        print("Starten Sie den gepatchten Server:")
        print(f"  python {wrapper}")
