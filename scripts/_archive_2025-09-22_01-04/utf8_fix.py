#!/usr/bin/env python3
"""
UTF-8 Fix Patch für HAK_GAL MCP Server
Behebt alle Encoding-Probleme
"""

import sys
import os
import re

def fix_mcp_server_utf8():
    """Fixe alle UTF-8 Probleme im MCP-Server"""
    
    mcp_file = "D:\\MCP Mods\\HAK_GAL_HEXAGONAL\\ultimate_mcp\\hakgal_mcp_ultimate.py"
    backup_file = mcp_file + ".backup"
    
    print("1. Erstelle Backup...")
    import shutil
    shutil.copy2(mcp_file, backup_file)
    print(f"   Backup: {backup_file}")
    
    print("\n2. Lese Original-Datei...")
    with open(mcp_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("\n3. Wende Fixes an...")
    fixes_applied = 0
    
    # Fix 1: json.dumps ohne ensure_ascii
    pattern1 = r'json\.dumps\(([^)]+)\)(?!.*ensure_ascii)'
    matches1 = list(re.finditer(pattern1, content))
    
    # Liste von Stellen, die NICHT ensure_ascii=False haben sollen
    force_ascii_patterns = [
        'response_str = json.dumps',
        'result = {"content":',
        'info = {',
        'text = json.dumps(data)'
    ]
    
    for match in reversed(matches1):  # Rückwärts, um Positionen beizubehalten
        match_text = content[match.start():match.end()]
        
        # Prüfe ob diese Stelle ensure_ascii=True braucht
        should_force_ascii = False
        for pattern in force_ascii_patterns:
            # Suche 100 Zeichen vor dem Match
            context_start = max(0, match.start() - 100)
            context = content[context_start:match.end()]
            if pattern in context:
                should_force_ascii = True
                break
        
        if should_force_ascii:
            # Füge ensure_ascii=True hinzu
            args = match.group(1)
            if not 'ensure_ascii' in args:
                new_text = f'json.dumps({args}, ensure_ascii=True)'
                content = content[:match.start()] + new_text + content[match.end():]
                fixes_applied += 1
                print(f"   Fix {fixes_applied}: Added ensure_ascii=True at position {match.start()}")
    
    # Fix 2: Stelle sicher, dass stdout/stderr UTF-8 konfiguriert sind
    if "sys.stdout.reconfigure" not in content:
        # Füge UTF-8 Konfiguration hinzu nach den Imports
        import_end = content.find("class HAKGALMCPServer:")
        if import_end > 0:
            utf8_config = """
# UTF-8 Configuration for stdout/stderr
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

"""
            content = content[:import_end] + utf8_config + content[import_end:]
            fixes_applied += 1
            print(f"   Fix {fixes_applied}: Added UTF-8 stdout/stderr configuration")
    
    # Fix 3: Alle file operations sollten encoding='utf-8' haben
    file_patterns = [
        (r'open\(([^,)]+)\s*,\s*["\'']r["\'']\s*\)', 'open(\\1, \'r\', encoding=\'utf-8\')'),
        (r'open\(([^,)]+)\s*,\s*["\'']w["\'']\s*\)', 'open(\\1, \'w\', encoding=\'utf-8\')'),
        (r'open\(([^,)]+)\s*,\s*["\'']a["\'']\s*\)', 'open(\\1, \'a\', encoding=\'utf-8\')')
    ]
    
    for pattern, replacement in file_patterns:
        if 'encoding=' not in pattern:  # Nur wenn noch kein encoding gesetzt
            matches = list(re.finditer(pattern, content))
            for match in reversed(matches):
                if 'encoding=' not in match.group(0):
                    old_text = match.group(0)
                    new_text = re.sub(pattern, replacement, old_text)
                    content = content[:match.start()] + new_text + content[match.end():]
                    fixes_applied += 1
    
    print(f"\n4. Schreibe gefixte Datei...")
    with open(mcp_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"\n✅ FERTIG: {fixes_applied} Fixes angewendet")
    print(f"   Original gesichert als: {backup_file}")
    
    return fixes_applied

if __name__ == "__main__":
    fixes = fix_mcp_server_utf8()
    if fixes > 0:
        print("\n⚠️ WICHTIG: MCP-Server muss neu gestartet werden!")
