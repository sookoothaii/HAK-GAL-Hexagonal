#!/usr/bin/env python3
"""Test LLM Chain directly"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment
env_path = Path('D:/MCP Mods/HAK_GAL_HEXAGONAL/.env')
load_dotenv(env_path)

# Add src_hexagonal to path
sys.path.insert(0, 'D:/MCP Mods/HAK_GAL_HEXAGONAL/src_hexagonal')

# Import and test
from adapters.llm_providers import get_llm_provider

print("=" * 60)
print("TESTING LLM CHAIN")
print("=" * 60)

# Check environment variables
print("\n1. Environment Variables:")
print(f"   GROQ_API_KEY: {'Set' if os.environ.get('GROQ_API_KEY') else 'NOT SET'}")
print(f"   DEEPSEEK_API_KEY: {'Set' if os.environ.get('DEEPSEEK_API_KEY') else 'NOT SET'}")
print(f"   GEMINI_API_KEY: {'Set' if os.environ.get('GEMINI_API_KEY') else 'NOT SET'}")
print(f"   GOOGLE_API_KEY: {'Set' if os.environ.get('GOOGLE_API_KEY') else 'NOT SET'}")
print(f"   ANTHROPIC_API_KEY: {'Set' if os.environ.get('ANTHROPIC_API_KEY') else 'NOT SET'}")

# Get provider
print("\n2. Initializing LLM Provider...")
provider = get_llm_provider()

# Test availability
print(f"\n3. Provider Available: {provider.is_available()}")

# Test with simple prompt
print("\n4. Testing with simple prompt...")
test_prompt = "What is 2+2? Answer in one sentence."

response, provider_name = provider.generate_response(test_prompt)

print(f"\n5. RESULT:")
print(f"   Provider Used: {provider_name}")
print(f"   Response Length: {len(response)} chars")
print(f"   Response: {response[:200]}...")

# Check if it's an error
error_indicators = ['timeout', 'failed', 'unauthorized', 'not found', 'invalid', 'api error', 'api key', 'not configured', 'error:', 'connectionerror', 'max retries exceeded']
is_error = any(err in response.lower() for err in error_indicators)
print(f"   Is Error: {is_error}")

print("\n" + "=" * 60)
