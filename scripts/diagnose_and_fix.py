#!/usr/bin/env python3
"""
DNS vs Direct IP Test & Auto-Fix
Findet heraus ob DNS das Problem ist und behebt es automatisch
"""
import os
import sys
import socket
import requests
import time
from pathlib import Path

# Farben für Output
RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

print("=" * 70)
print(f"{BLUE}HAK_GAL LLM PROBLEM DIAGNOSE & AUTO-FIX{RESET}")
print("=" * 70)

# API Mappings
API_ENDPOINTS = {
    'groq': {
        'domain': 'api.groq.com',
        'ip': '104.18.40.98',
        'test_endpoint': '/openai/v1/models',
        'needs_auth': True
    },
    'deepseek': {
        'domain': 'api.deepseek.com', 
        'ip': '104.18.26.90',
        'test_endpoint': '/v1/chat/completions',
        'needs_auth': False  # Basic connectivity test
    },
    'google': {
        'domain': 'www.google.com',
        'ip': '142.250.185.100',
        'test_endpoint': '/',
        'needs_auth': False
    }
}

# Load .env
sys.path.insert(0, 'D:/MCP Mods/HAK_GAL_HEXAGONAL')
from dotenv import load_dotenv
env_path = Path('D:/MCP Mods/HAK_GAL_HEXAGONAL/.env')
load_dotenv(env_path, override=True)

results = {}

print(f"\n{YELLOW}1. DNS AUFLÖSUNG TEST{RESET}")
print("-" * 40)

dns_working = True
for service, config in API_ENDPOINTS.items():
    domain = config['domain']
    try:
        ip = socket.gethostbyname(domain)
        print(f"✅ {domain:30} → {ip}")
        results[f"{service}_dns"] = True
    except socket.gaierror as e:
        print(f"❌ {domain:30} → DNS FEHLER!")
        results[f"{service}_dns"] = False
        dns_working = False

print(f"\n{YELLOW}2. DIREKTE IP VERBINDUNG TEST{RESET}")
print("-" * 40)

for service, config in API_ENDPOINTS.items():
    ip = config['ip']
    try:
        # Test mit IP statt Domain
        url = f"https://{ip}{config['test_endpoint']}"
        headers = {'Host': config['domain']}
        
        # SSL verify=False für IP-Verbindungen
        response = requests.get(url, headers=headers, timeout=3, verify=False)
        print(f"✅ {ip:20} ({service:8}) → Status {response.status_code}")
        results[f"{service}_ip"] = True
    except Exception as e:
        error_type = type(e).__name__
        print(f"❌ {ip:20} ({service:8}) → {error_type}")
        results[f"{service}_ip"] = False

print(f"\n{YELLOW}3. TATSÄCHLICHER API TEST{RESET}")
print("-" * 40)

# Test Groq mit API Key
groq_key = os.environ.get('GROQ_API_KEY', '')
if groq_key:
    # Test 1: Mit Domain (wird wahrscheinlich fehlschlagen)
    try:
        headers = {"Authorization": f"Bearer {groq_key}"}
        response = requests.get("https://api.groq.com/openai/v1/models", 
                               headers=headers, timeout=5)
        print(f"✅ Groq via Domain: {response.status_code}")
        results['groq_domain_api'] = True
    except Exception as e:
        print(f"❌ Groq via Domain: {type(e).__name__}")
        results['groq_domain_api'] = False
    
    # Test 2: Mit IP (sollte funktionieren wenn DNS Problem)
    try:
        headers = {
            "Authorization": f"Bearer {groq_key}",
            "Host": "api.groq.com"
        }
        response = requests.get("https://104.18.40.98/openai/v1/models", 
                               headers=headers, timeout=5, verify=False)
        print(f"✅ Groq via IP: {response.status_code}")
        results['groq_ip_api'] = True
    except Exception as e:
        print(f"❌ Groq via IP: {type(e).__name__}")
        results['groq_ip_api'] = False

print(f"\n{YELLOW}4. DIAGNOSE{RESET}")
print("-" * 40)

# Analyse
dns_problem = not results.get('groq_dns', True) or not results.get('deepseek_dns', True)
ip_works = results.get('groq_ip', False) or results.get('deepseek_ip', False)
api_via_ip_works = results.get('groq_ip_api', False)

if dns_problem and ip_works:
    print(f"{RED}✓ DNS PROBLEM BESTÄTIGT!{RESET}")
    print("  - DNS Auflösung schlägt fehl")
    print("  - Direkte IP-Verbindungen funktionieren")
    
    if api_via_ip_works:
        print("  - API-Aufrufe über IP funktionieren!")
    
    print(f"\n{GREEN}5. AUTOMATISCHE LÖSUNG IMPLEMENTIEREN{RESET}")
    print("-" * 40)
    
    # Patch llm_providers.py mit DNS-Fallback
    patch_code = '''
# DNS-FALLBACK PATCH
import socket

# Original gethostbyname speichern
_original_gethostbyname = socket.gethostbyname

# DNS-Fallback Mapping
DNS_FALLBACK = {
    'api.groq.com': '104.18.40.98',
    'api.deepseek.com': '104.18.26.90',
    'generativelanguage.googleapis.com': '142.250.185.74'
}

def patched_gethostbyname(hostname):
    """DNS mit Fallback zu hardcoded IPs"""
    try:
        return _original_gethostbyname(hostname)
    except socket.gaierror:
        if hostname in DNS_FALLBACK:
            print(f"[DNS-Fallback] Using IP for {hostname}")
            return DNS_FALLBACK[hostname]
        raise

# Monkey-patch socket
socket.gethostbyname = patched_gethostbyname
'''
    
    # Füge Patch am Anfang von llm_providers.py ein
    llm_file = Path('D:/MCP Mods/HAK_GAL_HEXAGONAL/src_hexagonal/adapters/llm_providers.py')
    
    if llm_file.exists():
        content = llm_file.read_text(encoding='utf-8')
        
        # Check ob Patch schon drin ist
        if 'DNS-FALLBACK PATCH' not in content:
            # Füge nach den imports ein
            import_end = content.find('class LLMProvider')
            if import_end > 0:
                new_content = content[:import_end] + '\n' + patch_code + '\n' + content[import_end:]
                
                # Backup erstellen
                backup_file = llm_file.with_suffix('.py.backup')
                llm_file.rename(backup_file)
                print(f"✓ Backup erstellt: {backup_file}")
                
                # Patched version schreiben
                llm_file.write_text(new_content, encoding='utf-8')
                print(f"✓ DNS-Fallback Patch eingefügt!")
                print(f"✓ Backend muss neu gestartet werden!")
            else:
                print("❌ Konnte Patch-Position nicht finden")
        else:
            print("✓ DNS-Fallback Patch bereits vorhanden!")
    
    print(f"\n{GREEN}6. ALTERNATIVE: Hosts-Datei Update{RESET}")
    print("-" * 40)
    print("Falls der Patch nicht reicht, füge zu C:\\Windows\\System32\\drivers\\etc\\hosts hinzu:")
    print()
    print("104.18.40.98    api.groq.com")
    print("104.18.26.90    api.deepseek.com")
    print("142.250.185.74  generativelanguage.googleapis.com")
    
elif not dns_problem and not ip_works:
    print(f"{RED}✗ NETZWERK PROBLEM!{RESET}")
    print("  - Weder DNS noch direkte IPs funktionieren")
    print("  - Möglicherweise Firewall oder Proxy Problem")
    
elif not dns_problem:
    print(f"{GREEN}✓ DNS funktioniert einwandfrei!{RESET}")
    print(f"{YELLOW}  Problem liegt woanders (nicht DNS){RESET}")
    
    # Check API keys
    print(f"\n{YELLOW}API Keys Check:{RESET}")
    print(f"  GROQ_API_KEY: {'✓ Gesetzt' if os.environ.get('GROQ_API_KEY') else '✗ FEHLT'}")
    print(f"  DEEPSEEK_API_KEY: {'✓ Gesetzt' if os.environ.get('DEEPSEEK_API_KEY') else '✗ FEHLT'}")
    print(f"  GEMINI_API_KEY: {'✓ Gesetzt' if os.environ.get('GEMINI_API_KEY') else '✗ FEHLT'}")

print("\n" + "=" * 70)
print(f"{BLUE}TEST ABGESCHLOSSEN{RESET}")
print("=" * 70)
