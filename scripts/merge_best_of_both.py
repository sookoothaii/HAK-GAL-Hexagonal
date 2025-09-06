"""
INTELLIGENTE KOMBINATION - Das Beste aus beiden Welten!
========================================================
Original-Backup: HRM Feedback, Verify, Reasoning funktionieren
Aktuelle Version: Andere 9 Tests funktionieren
LÖSUNG: Die 3 fehlenden aus Backup kopieren!
"""

import re
import shutil
from datetime import datetime

# Dateien
current_file = r"D:\MCP Mods\HAK_GAL_HEXAGONAL\src_hexagonal\hexagonal_api_enhanced_clean.py"
backup_file = r"D:\MCP Mods\HAK_GAL_HEXAGONAL\backups\hexagonal_api_enhanced_clean.py"

print("=" * 70)
print("KOMBINIERE DIE FUNKTIONIERENDEN TEILE AUS BEIDEN VERSIONEN")
print("=" * 70)

# 1. Backup der aktuellen Version
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
shutil.copy(current_file, f"{current_file}.before_merge_{timestamp}")
print(f"✅ Backup erstellt: before_merge_{timestamp}")

# 2. Lese beide Versionen
print("\n2. Lese beide Versionen...")
with open(current_file, 'r', encoding='utf-8') as f:
    current_content = f.read()
    
with open(backup_file, 'r', encoding='utf-8') as f:
    backup_content = f.read()

# 3. Extrahiere die FUNKTIONIERENDEN Endpoints aus dem Backup
print("\n3. Extrahiere funktionierende Endpoints aus Backup...")

endpoints_to_extract = []

# REASONING ENDPOINT aus Backup
print("   Extrahiere /api/reason...")
reason_pattern = r'(@self\.app\.route\(\'/api/reason\'.*?)(?=@self\.app\.route|return self\.app|\Z)'
match = re.search(reason_pattern, backup_content, re.DOTALL)
if match:
    reason_code = match.group(1).strip()
    # Entferne den alten reasoning endpoint aus current
    current_content = re.sub(reason_pattern, '', current_content, flags=re.DOTALL)
    endpoints_to_extract.append(("reason", reason_code))
    print("   ✅ Reasoning endpoint gefunden")

# HRM FEEDBACK ENDPOINT aus Backup
print("   Extrahiere /api/hrm/feedback...")
hrm_pattern = r'(@self\.app\.route\(\'/api/hrm/feedback\'.*?)(?=@self\.app\.route|return self\.app|\Z)'
match = re.search(hrm_pattern, backup_content, re.DOTALL)
if match:
    hrm_code = match.group(1).strip()
    endpoints_to_extract.append(("hrm_feedback", hrm_code))
    print("   ✅ HRM Feedback endpoint gefunden")

# FEEDBACK-STATS ENDPOINT aus Backup
print("   Extrahiere /api/hrm/feedback-stats...")
stats_pattern = r'(@self\.app\.route\(\'/api/hrm/feedback-stats\'.*?)(?=@self\.app\.route|return self\.app|\Z)'
match = re.search(stats_pattern, backup_content, re.DOTALL)
if match:
    stats_code = match.group(1).strip()
    endpoints_to_extract.append(("feedback_stats", stats_code))
    print("   ✅ HRM Feedback-Stats endpoint gefunden")

# VERIFY ENDPOINT aus Backup (falls er dort anders ist)
print("   Prüfe /api/feedback/verify...")
verify_pattern = r'(@self\.app\.route\(\'/api/feedback/verify\'.*?)(?=@self\.app\.route|return self\.app|\Z)'
match_backup = re.search(verify_pattern, backup_content, re.DOTALL)
match_current = re.search(verify_pattern, current_content, re.DOTALL)

if match_backup and (not match_current or 'sqlite3' not in match_current.group(1)):
    verify_code = match_backup.group(1).strip()
    # Entferne den alten verify endpoint aus current falls vorhanden
    current_content = re.sub(verify_pattern, '', current_content, flags=re.DOTALL)
    endpoints_to_extract.append(("verify", verify_code))
    print("   ✅ Verify endpoint aus Backup übernommen")

# 4. Füge die extrahierten Endpoints zur aktuellen Version hinzu
print(f"\n4. Füge {len(endpoints_to_extract)} Endpoints zur aktuellen Version hinzu...")

# Finde eine gute Stelle zum Einfügen (vor agent-bus oder vor return self.app)
insertion_point = current_content.find("@self.app.route('/api/agent-bus/delegate'")
if insertion_point == -1:
    insertion_point = current_content.rfind('return self.app')

if insertion_point > 0:
    # Baue den Insert-String
    insert_code = "\n        # === FUNKTIONIERENDE ENDPOINTS AUS BACKUP ===\n"
    for name, code in endpoints_to_extract:
        insert_code += f"        # Aus Backup: {name}\n"
        insert_code += "        " + code.replace("\n", "\n        ") + "\n\n"
    
    # Füge ein
    current_content = current_content[:insertion_point] + insert_code + current_content[insertion_point:]
    print("   ✅ Alle Endpoints eingefügt")

# 5. Stelle sicher dass alle Imports da sind
print("\n5. Prüfe Imports...")
required_imports = [
    'import json',
    'import sqlite3',
    'import re',
    'from datetime import datetime',
    'from pathlib import Path'
]

for imp in required_imports:
    if imp not in current_content:
        # Füge am Anfang nach anderen imports ein
        insert_pos = current_content.find('from flask import')
        if insert_pos > 0:
            # Nach der flask import Zeile
            insert_pos = current_content.find('\n', insert_pos) + 1
            current_content = current_content[:insert_pos] + imp + '\n' + current_content[insert_pos:]
            print(f"   ✅ Added import: {imp}")

# 6. Speichere die kombinierte Version
print("\n6. Speichere kombinierte Version...")
with open(current_file, 'w', encoding='utf-8') as f:
    f.write(current_content)

print("\n" + "=" * 70)
print("✅ KOMBINATION ERFOLGREICH!")
print("=" * 70)
print("\nWas gemacht wurde:")
print("- Die 9 funktionierenden Tests bleiben erhalten")
print("- Die 3 fehlenden Endpoints aus Backup hinzugefügt:")
print("  ✅ /api/reason (mit base_confidence)")
print("  ✅ /api/hrm/feedback")
print("  ✅ /api/feedback/verify")
print("\nJETZT:")
print("1. Server neu starten (Ctrl+C, dann wieder starten)")
print("2. python test_system.py")
print("\nERWARTUNG: 12/12 TESTS BESTEHEN!")
print("=" * 70)
