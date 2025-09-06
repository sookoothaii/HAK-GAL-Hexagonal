"""
LLM Provider Configuration for HAK_GAL Backend

Add this to your multi_llm_adapter.py or similar file to prioritize DeepSeek
"""

import os

# LLM Provider Priority (fastest first)
LLM_PROVIDERS = [
    {
        "name": "deepseek",
        "enabled": bool(os.getenv("DEEPSEEK_API_KEY")),
        "timeout": int(os.getenv("DEEPSEEK_TIMEOUT", "15")),
        "models": ["deepseek-chat"],
        "speed": "very_fast"
    },
    {
        "name": "gemini", 
        "enabled": bool(os.getenv("GOOGLE_API_KEY")),
        "timeout": int(os.getenv("GEMINI_TIMEOUT", "20")),
        "models": ["gemini-2.0-flash-exp", "gemini-1.5-flash"],
        "speed": "fast"
    },
    {
        "name": "anthropic",
        "enabled": bool(os.getenv("ANTHROPIC_API_KEY")),
        "timeout": int(os.getenv("ANTHROPIC_TIMEOUT", "25")),
        "models": ["claude-3-5-sonnet-latest", "claude-3-haiku-latest"],
        "speed": "medium"
    }
]

def get_fastest_provider():
    """Return the fastest available LLM provider"""
    for provider in LLM_PROVIDERS:
        if provider["enabled"]:
            return provider["name"]
    return "gemini"  # fallback

def get_provider_config(name):
    """Get configuration for a specific provider"""
    for provider in LLM_PROVIDERS:
        if provider["name"] == name:
            return provider
    return None

# Usage example:
# provider = get_fastest_provider()  # Returns "deepseek" if API key is set
# config = get_provider_config(provider)
# timeout = config["timeout"]  # 15 seconds for DeepSeek

print(f"Primary LLM: {get_fastest_provider()}")
print(f"Available providers: {[p['name'] for p in LLM_PROVIDERS if p['enabled']]}")
