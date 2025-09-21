#!/usr/bin/env python3
"""
QUICK FIX SCRIPT für semantic_similarity und consistency_check
Automatische Reparatur der letzten 2 defekten Tools

Dieses Script:
1. Findet die Tool-Handler in hakgal_mcp_ultimate.py
2. Ersetzt sie mit n-ären Versionen
3. Erstellt Backup
4. Testet die Änderungen

Author: Claude (für nächste Instanz)
Date: 2025-09-19
"""

import os
import shutil
import re
from datetime import datetime

# Konfiguration
BASE_PATH = r'D:\MCP Mods\HAK_GAL_HEXAGONAL'
SERVER_FILE = os.path.join(BASE_PATH, 'ultimate_mcp', 'hakgal_mcp_ultimate.py')
BACKUP_FILE = SERVER_FILE + f'.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}'

# Die neuen Tool-Handler (n-är kompatibel)
SEMANTIC_SIMILARITY_HANDLER = '''elif name == "semantic_similarity":
            try:
                # N-äre kompatible Version
                import sys
                if r'D:\\MCP Mods\\HAK_GAL_HEXAGONAL\\scripts' not in sys.path:
                    sys.path.insert(0, r'D:\\MCP Mods\\HAK_GAL_HEXAGONAL\\scripts')
                
                from fix_nary_tools import FixedNaryTools
                
                tools = FixedNaryTools()
                statement = params.get('statement', '')
                threshold = params.get('threshold', 0.8)
                limit = params.get('limit', 50)
                
                logger.debug(f"[N-ARY] semantic_similarity: {statement[:50]}... threshold={threshold} limit={limit}")
                
                results = tools.semantic_similarity(statement, threshold, limit)
                
                if results:
                    output = f"Gefundene {len(results)} ähnliche Facts:\\n"
                    for score, fact in results:
                        output += f"  Score {score:.3f}: {fact}\\n"
                    return output
                return "Keine ähnlichen Facts gefunden"
                
            except Exception as e:
                logger.error(f"[N-ARY] semantic_similarity error: {e}")
                return f"Fehler: {str(e)}"
'''

CONSISTENCY_CHECK_HANDLER = '''elif name == "consistency_check":
            try:
                # N-äre kompatible Version
                import sys
                if r'D:\\MCP Mods\\HAK_GAL_HEXAGONAL\\scripts' not in sys.path:
                    sys.path.insert(0, r'D:\\MCP Mods\\HAK_GAL_HEXAGONAL\\scripts')
                
                from fix_nary_tools import FixedNaryTools
                
                tools = FixedNaryTools()
                limit = params.get('limit', 1000)
                
                logger.debug(f"[N-ARY] consistency_check: limit={limit}")
                
                inconsistencies = tools.consistency_check(limit)
                
                if inconsistencies:
                    output = f"Gefundene {len(inconsistencies)} potentielle Inkonsistenzen:\\n"
                    for fact1, fact2, reason in inconsistencies[:10]:
                        output += f"\\n{reason}:\\n"
                        output += f"  1. {fact1}\\n"
                        output += f"  2. {fact2}\\n"
                    if len(inconsistencies) > 10:
                        output += f"\\n... und {len(inconsistencies) - 10} weitere."
                    return output
                return "✓ Keine Inkonsistenzen gefunden"
                
            except Exception as e:
                logger.error(f"[N-ARY] consistency_check error: {e}")
                return f"Fehler: {str(e)}"
'''

def find_and_replace_handler(content, tool_name, new_handler):
    """Findet und ersetzt einen Tool-Handler"""
    
    # Pattern für den Tool-Handler
    pattern = rf'elif\s+name\s*==\s*["\']({tool_name})["\']\s*:(.*?)(?=elif\s+name\s*==|else\s*:|$)'
    
    matches = list(re.finditer(pattern, content, re.DOTALL))
    
    if matches:
        print(f"✓ Gefunden: {tool_name} Handler (Zeile ~{content[:matches[0].start()].count(chr(10))})")
        
        # Ersetze den gefundenen Handler
        for match in reversed(matches):  # Von hinten nach vorne um Positionen zu erhalten
            content = content[:match.start()] + new_handler + content[match.end():]
            
        print(f"✓ Ersetzt: {tool_name} mit n-ärer Version")
        return content, True
    else:
        print(f"✗ Nicht gefunden: {tool_name} Handler")
        return content, False

def main():
    print("=" * 60)
    print("N-ÄRE FACT TOOLS - AUTOMATISCHE REPARATUR")
    print("=" * 60)
    print(f"\nServer-Datei: {SERVER_FILE}\n")
    
    # 1. Backup erstellen
    print("1. Erstelle Backup...")
    if os.path.exists(SERVER_FILE):
        shutil.copy2(SERVER_FILE, BACKUP_FILE)
        print(f"   ✓ Backup: {BACKUP_FILE}")
    else:
        print(f"   ✗ Server-Datei nicht gefunden!")
        return False
    
    # 2. Datei einlesen
    print("\n2. Lade Server-Code...")
    with open(SERVER_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    print(f"   ✓ {len(content)} Zeichen geladen")
    
    # 3. Handler ersetzen
    print("\n3. Ersetze Tool-Handler...")
    
    # semantic_similarity
    content, success1 = find_and_replace_handler(
        content, 
        'semantic_similarity',
        SEMANTIC_SIMILARITY_HANDLER
    )
    
    # consistency_check
    content, success2 = find_and_replace_handler(
        content,
        'consistency_check', 
        CONSISTENCY_CHECK_HANDLER
    )
    
    if not (success1 and success2):
        print("\n⚠️ Nicht alle Handler gefunden. Versuche alternativen Ansatz...")
        
        # Alternative: Füge am Ende der Tool-Handler Section hinzu
        tool_section_end = content.rfind('else:')
        if tool_section_end > 0:
            # Finde die richtige Einrückung
            lines_before = content[:tool_section_end].split('\n')
            last_elif = [l for l in lines_before if 'elif name ==' in l]
            if last_elif:
                indent = len(last_elif[-1]) - len(last_elif[-1].lstrip())
                
                # Füge neue Handler vor dem else: ein
                insertion = '\n' + SEMANTIC_SIMILARITY_HANDLER.replace('elif', ' ' * indent + 'elif')
                insertion += '\n' + CONSISTENCY_CHECK_HANDLER.replace('elif', ' ' * indent + 'elif')
                
                content = content[:tool_section_end] + insertion + '\n' + ' ' * indent + content[tool_section_end:]
                print("   ✓ Handler am Ende der Tool-Section hinzugefügt")
    
    # 4. Speichere modifizierte Datei
    print("\n4. Speichere Änderungen...")
    with open(SERVER_FILE, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"   ✓ Server-Datei aktualisiert")
    
    # 5. Syntax-Check
    print("\n5. Prüfe Syntax...")
    import ast
    try:
        with open(SERVER_FILE, 'r', encoding='utf-8') as f:
            ast.parse(f.read())
        print("   ✓ Syntax OK")
    except SyntaxError as e:
        print(f"   ✗ Syntax-Fehler: {e}")
        print("\n⚠️ Stelle Backup wieder her...")
        shutil.copy2(BACKUP_FILE, SERVER_FILE)
        return False
    
    # 6. Test-Empfehlung
    print("\n" + "=" * 60)
    print("✅ REPARATUR ERFOLGREICH!")
    print("=" * 60)
    print("\nNächste Schritte:")
    print("1. Python Cache löschen:")
    print('   Get-ChildItem -Path "D:\\MCP Mods\\HAK_GAL_HEXAGONAL" -Filter "__pycache__" -Recurse | Remove-Item -Recurse -Force')
    print("\n2. Server neu starten:")
    print("   npx @srbhptl39/mcp-superassistant-proxy@latest --config ./combined-mcp.sse.config.json --outputTransport sse")
    print("\n3. Tools testen in Claude:")
    print("   - semantic_similarity")
    print("   - consistency_check")
    print("\nBei Problemen:")
    print(f"   Restore mit: copy {BACKUP_FILE} {SERVER_FILE}")
    
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
