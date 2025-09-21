"""
API ENDPOINT MONITOR
====================
Überwacht, dass NIEMALS Endpoints verloren gehen
"""

import re
import os
from datetime import datetime

# Minimale erwartete Endpoints (dürfen NIEMALS fehlen)
REQUIRED_ENDPOINTS = [
    '/health',
    '/api/status',
    '/api/facts',  # GET, POST, DELETE
    '/api/facts/count',
    '/api/facts/export',
    '/api/search',
    '/api/reason',
    '/api/llm/get-explanation',
    '/api/graph/generate',
    '/api/governor/status',
    '/api/governor/start', 
    '/api/governor/stop',
    '/api/hrm/retrain',
    '/api/hrm/model_info',
    '/api/hrm/feedback-stats',
    '/api/agent-bus/delegate',
    '/api/agent-bus/tasks/<task_id>',
    '/api/feedback/verify'
]

def check_api_completeness(file_path):
    """Prüft ob alle erforderlichen Endpoints vorhanden sind"""
    
    print("=" * 70)
    print("API ENDPOINT VOLLSTÄNDIGKEITS-CHECK")
    print("=" * 70)
    print(f"Datei: {file_path}")
    print(f"Größe: {os.path.getsize(file_path):,} Bytes")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Finde alle Endpoints
    pattern = r"@self\.app\.route\('([^']+)'.*?\)"
    found_endpoints = re.findall(pattern, content)
    found_set = set(found_endpoints)
    
    print(f"\n📊 Gefundene Endpoints: {len(found_set)}")
    
    # Prüfe auf fehlende Required Endpoints
    missing = []
    for endpoint in REQUIRED_ENDPOINTS:
        # Berücksichtige dass manche Endpoints mehrfach vorkommen (GET, POST)
        if not any(endpoint in e for e in found_endpoints):
            missing.append(endpoint)
    
    if missing:
        print("\n❌ WARNUNG: FEHLENDE KRITISCHE ENDPOINTS:")
        for ep in missing:
            print(f"   ❌ {ep}")
        print(f"\n⚠️ {len(missing)} kritische Endpoints fehlen!")
        print("Dies verstößt gegen das Prinzip: Niemals Funktionen reduzieren!")
        return False
    else:
        print("\n✅ ALLE kritischen Endpoints vorhanden!")
        
    # Liste alle gefundenen Endpoints
    print("\n📋 Vollständige Endpoint-Liste:")
    for ep in sorted(found_set):
        status = "✅" if any(req in ep for req in REQUIRED_ENDPOINTS) else "➕"
        print(f"   {status} {ep}")
    
    return True

def compare_versions(current_file, backup_file):
    """Vergleicht zwei Versionen und warnt bei Funktionsverlust"""
    
    print("\n" + "=" * 70)
    print("VERSIONS-VERGLEICH")
    print("=" * 70)
    
    current_size = os.path.getsize(current_file)
    backup_size = os.path.getsize(backup_file)
    
    print(f"Aktuelle Version: {current_size:,} Bytes")
    print(f"Backup Version:   {backup_size:,} Bytes")
    
    if current_size < backup_size:
        print(f"\n⚠️ WARNUNG: {backup_size - current_size:,} Bytes VERLOREN!")
        print("Die aktuelle Version ist KLEINER als das Backup.")
        print("Dies deutet auf FUNKTIONSVERLUST hin!")
        
        # Detaillierter Endpoint-Vergleich
        with open(current_file, 'r', encoding='utf-8') as f:
            current_content = f.read()
        with open(backup_file, 'r', encoding='utf-8') as f:
            backup_content = f.read()
            
        pattern = r"@self\.app\.route\('([^']+)'.*?\)"
        current_endpoints = set(re.findall(pattern, current_content))
        backup_endpoints = set(re.findall(pattern, backup_content))
        
        lost_endpoints = backup_endpoints - current_endpoints
        if lost_endpoints:
            print("\n❌ VERLORENE ENDPOINTS:")
            for ep in sorted(lost_endpoints):
                print(f"   ❌ {ep}")
                
        new_endpoints = current_endpoints - backup_endpoints
        if new_endpoints:
            print("\n➕ NEUE ENDPOINTS:")
            for ep in sorted(new_endpoints):
                print(f"   ➕ {ep}")
    
    elif current_size > backup_size:
        print(f"\n✅ GUT: {current_size - backup_size:,} Bytes HINZUGEFÜGT!")
        print("Die aktuelle Version wurde ERWEITERT.")
    else:
        print("\n➖ Beide Versionen sind identisch groß.")

if __name__ == "__main__":
    current = r"D:\MCP Mods\HAK_GAL_HEXAGONAL\src_hexagonal\hexagonal_api_enhanced_clean.py"
    backup = r"D:\MCP Mods\HAK_GAL_HEXAGONAL\backups\hexagonal_api_enhanced_clean.py"
    
    # Check aktuelle Version
    is_complete = check_api_completeness(current)
    
    # Vergleich mit Backup
    if os.path.exists(backup):
        compare_versions(current, backup)
    
    # Empfehlung
    if not is_complete:
        print("\n" + "=" * 70)
        print("🔧 EMPFEHLUNG:")
        print("Führen Sie 'python restore_full_api.py' aus,")
        print("um die vollständige Funktionalität wiederherzustellen!")
        print("=" * 70)
