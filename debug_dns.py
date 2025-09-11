#!/usr/bin/env python3
"""DNS & Environment Debug Script"""
import os
import socket
import sys
from pathlib import Path
from dotenv import load_dotenv

print("=" * 60)
print("DNS & ENVIRONMENT DIAGNOSTICS")
print("=" * 60)

# 1. Check which .env is loaded
env_path = Path('D:/MCP Mods/HAK_GAL_HEXAGONAL/.env')
print(f"\n1. Loading .env from: {env_path}")
print(f"   File exists: {env_path.exists()}")
load_dotenv(env_path, override=True)

# 2. Check loaded environment variables
print("\n2. Environment Variables (after loading):")
print(f"   GROQ_API_KEY: {os.environ.get('GROQ_API_KEY', 'NOT SET')[:20]}...")
print(f"   DEEPSEEK_API_KEY: {os.environ.get('DEEPSEEK_API_KEY', 'NOT SET')[:20]}...")
print(f"   GEMINI_API_KEY: {os.environ.get('GEMINI_API_KEY', 'NOT SET')[:20]}...")

# 3. DNS Resolution Test
print("\n3. DNS Resolution Test:")

def test_dns(hostname):
    try:
        ip = socket.gethostbyname(hostname)
        print(f"   ✅ {hostname} -> {ip}")
        return ip
    except socket.gaierror as e:
        print(f"   ❌ {hostname} -> DNS Error: {e}")
        return None

test_dns('google.com')
test_dns('api.groq.com')
test_dns('api.deepseek.com')
test_dns('generativelanguage.googleapis.com')

# 4. Alternative DNS resolution using getaddrinfo
print("\n4. Alternative DNS Resolution (getaddrinfo):")
try:
    info = socket.getaddrinfo('api.groq.com', 443, socket.AF_INET, socket.SOCK_STREAM)
    if info:
        print(f"   ✅ api.groq.com via getaddrinfo: {info[0][4][0]}")
except Exception as e:
    print(f"   ❌ getaddrinfo failed: {e}")

# 5. Check system DNS servers
print("\n5. System DNS Configuration:")
try:
    import subprocess
    result = subprocess.run(['nslookup', 'api.groq.com'], capture_output=True, text=True, timeout=5)
    print("   nslookup output:")
    for line in result.stdout.split('\n')[:5]:
        if line.strip():
            print(f"   {line}")
except Exception as e:
    print(f"   Could not run nslookup: {e}")

# 6. Test with requests library
print("\n6. Testing with requests library:")
import requests
try:
    # Test basic connectivity
    response = requests.get('https://www.google.com', timeout=5)
    print(f"   ✅ Google.com reachable (status {response.status_code})")
except Exception as e:
    print(f"   ❌ Google.com error: {str(e)[:100]}")

try:
    # Test Groq specifically
    response = requests.get('https://api.groq.com', timeout=5)
    print(f"   ✅ api.groq.com reachable (status {response.status_code})")
except Exception as e:
    print(f"   ❌ api.groq.com error: {str(e)[:100]}")

print("\n" + "=" * 60)
print("DIAGNOSIS:")
if test_dns('api.groq.com') is None:
    print("❌ DNS resolution is failing. Possible causes:")
    print("   1. Corporate firewall/proxy blocking DNS")
    print("   2. DNS cache corruption")
    print("   3. IPv6/IPv4 conflict")
    print("\nSOLUTIONS TO TRY:")
    print("   1. Run as Admin: ipconfig /flushdns")
    print("   2. Add to hosts file: 104.18.40.98  api.groq.com")
    print("   3. Change DNS servers to 8.8.8.8 / 8.8.4.4")
else:
    print("✅ DNS is working. Check if requests library has proxy issues.")

print("=" * 60)
