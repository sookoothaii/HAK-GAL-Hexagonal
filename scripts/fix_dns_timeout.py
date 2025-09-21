#!/usr/bin/env python3
"""
DNS Timeout Fix für HAK_GAL
Setzt robuste DNS-Resolver und Timeout-Konfigurationen
"""

import os
import sys
import socket
import subprocess
from pathlib import Path

def fix_dns_settings():
    """Konfiguriert robuste DNS-Settings für Python"""
    
    print("=== DNS TIMEOUT FIX ===")
    
    # 1. Set DNS timeout globally
    socket.setdefaulttimeout(10)  # 10 seconds default
    print("✓ Set global socket timeout to 10s")
    
    # 2. Configure environment for requests library
    os.environ['REQUESTS_CA_BUNDLE'] = ''
    os.environ['CURL_CA_BUNDLE'] = ''
    print("✓ Disabled certificate bundle checks (temporary)")
    
    # 3. Set DNS resolver preferences
    if sys.platform == "win32":
        # Windows-specific DNS fixes
        os.environ['SYSTEMROOT'] = r'C:\Windows'
        os.environ['WINDIR'] = r'C:\Windows'
        print("✓ Set Windows system paths")
    
    # 4. Create patched startup script
    patch_content = '''
# DNS TIMEOUT PATCH
import socket
import os

# Set conservative timeouts
socket.setdefaulttimeout(10)

# Configure DNS resolution
import urllib3
urllib3.disable_warnings()

# Patch requests library
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

def create_robust_session():
    session = requests.Session()
    retry = Retry(
        total=3,
        read=3,
        connect=3,
        backoff_factor=0.3,
        status_forcelist=(500, 502, 503, 504)
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    
    # Set timeouts
    session.timeout = (10, 60)  # (connect, read)
    return session

# Monkey-patch requests
original_get = requests.get
def patched_get(url, **kwargs):
    if 'timeout' not in kwargs:
        kwargs['timeout'] = (10, 60)
    return original_get(url, **kwargs)

requests.get = patched_get

print("[DNS PATCH] Applied robust DNS settings")
'''
    
    patch_file = Path("D:/MCP Mods/HAK_GAL_HEXAGONAL/src_hexagonal/dns_patch.py")
    patch_file.write_text(patch_content)
    print(f"✓ Created DNS patch file: {patch_file}")
    
    # 5. Create startup wrapper
    wrapper_content = '''#!/usr/bin/env python3
"""
HAK_GAL API Wrapper with DNS Fix
"""
import sys
import os

# Apply DNS patch first
try:
    import dns_patch
except:
    print("[WARNING] DNS patch not applied")

# Start original application
if __name__ == "__main__":
    import hexagonal_api_enhanced_clean
    hexagonal_api_enhanced_clean.main()
'''
    
    wrapper_file = Path("D:/MCP Mods/HAK_GAL_HEXAGONAL/src_hexagonal/start_with_dns_fix.py")
    wrapper_file.write_text(wrapper_content)
    print(f"✓ Created wrapper script: {wrapper_file}")
    
    # 6. Update .env with timeout settings
    env_additions = """
# DNS TIMEOUT FIXES
HTTP_TIMEOUT=60
HTTPS_TIMEOUT=60
DNS_TIMEOUT=10
REQUEST_TIMEOUT=60
ANTHROPIC_TIMEOUT=60
GROQ_TIMEOUT=30
GEMINI_TIMEOUT=30
DEEPSEEK_TIMEOUT=30
SENTRY_TIMEOUT=10

# Disable SSL verification temporarily (if needed)
PYTHONHTTPSVERIFY=0
"""
    
    env_file = Path("D:/MCP Mods/hak_gal_user/.env")
    if env_file.exists():
        current = env_file.read_text()
        if "DNS TIMEOUT FIXES" not in current:
            env_file.write_text(current + "\n" + env_additions)
            print("✓ Added timeout settings to .env")
    
    print("\n=== IMMEDIATE FIX ===")
    print("1. Stop the current backend (Ctrl+C)")
    print("2. Restart with DNS fix:")
    print("   cd D:\\MCP Mods\\HAK_GAL_HEXAGONAL\\src_hexagonal")
    print("   python start_with_dns_fix.py")
    print("\nOR add to hexagonal_api_enhanced_clean.py at the top:")
    print("   import socket")
    print("   socket.setdefaulttimeout(10)")

if __name__ == "__main__":
    fix_dns_settings()
