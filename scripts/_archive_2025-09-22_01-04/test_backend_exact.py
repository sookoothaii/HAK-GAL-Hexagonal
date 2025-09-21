#!/usr/bin/env python3
"""
Test EXAKT wie das Backend es macht
"""
import os
import sys
from pathlib import Path

# EXAKT wie im Backend
os.chdir('D:/MCP Mods/HAK_GAL_HEXAGONAL')
sys.path.insert(0, 'D:/MCP Mods/HAK_GAL_HEXAGONAL/src_hexagonal')

# Load .env EXAKT wie Backend
from dotenv import load_dotenv
env_path = Path('.env')
load_dotenv(env_path, override=True)

print("=" * 70)
print("BACKEND SIMULATION TEST")
print("=" * 70)

# Import EXAKT wie Backend
from adapters.llm_providers import get_llm_provider

print("\n1. Check environment:")
print(f"   Working dir: {os.getcwd()}")
print(f"   Python: {sys.executable}")
print(f"   GROQ_API_KEY: {'SET' if os.environ.get('GROQ_API_KEY') else 'NOT SET'}")

print("\n2. Initialize provider:")
provider = get_llm_provider()

print("\n3. Test simple prompt:")
test_prompt = "Say hello in 3 words"

try:
    response, provider_name = provider.generate_response(test_prompt)
    print(f"\n✅ SUCCESS with {provider_name}")
    print(f"   Response: {response[:100]}")
except Exception as e:
    print(f"\n❌ ERROR: {e}")

# Check requests version
import requests
import urllib3
print(f"\n4. Library versions:")
print(f"   requests: {requests.__version__}")
print(f"   urllib3: {urllib3.__version__}")

# Check SSL
import ssl
print(f"   SSL: {ssl.OPENSSL_VERSION}")

# Check proxy
print(f"\n5. Proxy settings:")
print(f"   HTTP_PROXY: {os.environ.get('HTTP_PROXY', 'Not set')}")
print(f"   HTTPS_PROXY: {os.environ.get('HTTPS_PROXY', 'Not set')}")
print(f"   NO_PROXY: {os.environ.get('NO_PROXY', 'Not set')}")

print("\n" + "=" * 70)
