#!/usr/bin/env python3
"""
UPDATE LLM CONFIG - Neueste Claude-Modelle und bessere Fehlerbehandlung
"""

import json
import os

def update_llm_config():
    """
    Aktualisiert llm_config.json mit neuesten Claude-Modellen
    """
    
    config = {
        "version": "3.0",
        "updated": "2025-01-18",
        
        # Provider-Reihenfolge
        "provider_chain": [
            "gemini",     # Primär (schnell und günstig)
            "claude",     # Sekundär (beste Qualität)
            "deepseek",   # Tertiär (gut für Code)
            "groq",       # Quaternär (kostenlos)
            "ollama"      # Lokal (Fallback)
        ],
        
        # Claude-spezifische Konfiguration
        "claude": {
            "enabled": True,
            "models": [
                "claude-3-5-sonnet-20241022",   # NEUESTES Sonnet
                "claude-3-5-haiku-20241022",    # NEUESTES Haiku (schnell)
                "claude-3-opus-20240229"        # Opus (stärkstes)
            ],
            "default_model": "claude-3-5-sonnet-20241022",
            "api_version": "2023-06-01",
            "timeout": 45,
            "max_retries": 2,
            "temperature": 0.1,
            "max_tokens": 200,
            "system_message": "Generate scientifically accurate facts with 6-7 arguments. Include units. Be precise."
        },
        
        # Gemini (funktioniert gut)
        "gemini": {
            "enabled": True,
            "models": [
                "gemini-2.0-flash-exp",
                "gemini-1.5-flash",
                "gemini-1.5-pro"
            ],
            "default_model": "gemini-2.0-flash-exp",
            "timeout": 30,
            "temperature": 0.1
        },
        
        # DeepSeek
        "deepseek": {
            "enabled": True,
            "models": ["deepseek-chat", "deepseek-coder"],
            "default_model": "deepseek-chat",
            "timeout": 30,  # Erhöht von 15
            "temperature": 0.1
        },
        
        # Groq (Fallback)
        "groq": {
            "enabled": True,
            "models": [
                "mixtral-8x7b-32768",
                "llama-3.1-70b-versatile",
                "llama-3.1-8b-instant"
            ],
            "default_model": "mixtral-8x7b-32768",
            "timeout": 25,
            "temperature": 0.1
        },
        
        # Ollama (lokal)
        "ollama": {
            "enabled": True,
            "models": ["qwen2.5:7b", "mistral:7b"],
            "default_model": "qwen2.5:7b",
            "timeout": 60,
            "temperature": 0.1
        },
        
        # Global settings
        "global": {
            "retry_on_connection_error": True,
            "max_connection_retries": 2,
            "connection_timeout": 10,
            "verify_ssl": True,
            "use_proxy": False,
            "log_errors": True,
            "fallback_on_error": True,
            "scientific_mode": True,
            "min_arguments": 6,
            "max_arguments": 7,
            "validation_mode": "strict"
        }
    }
    
    # Speichere in mehreren Orten
    paths = [
        "D:\\MCP Mods\\HAK_GAL_HEXAGONAL\\llm_config.json",
        "D:\\MCP Mods\\HAK_GAL_HEXAGONAL\\src_hexagonal\\llm_config.json"
    ]
    
    for path in paths:
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, 'w') as f:
                json.dump(config, f, indent=2)
            print(f"✓ Config gespeichert: {path}")
        except Exception as e:
            print(f"✗ Fehler bei {path}: {e}")
    
    return config

def fix_claude_connection():
    """
    Debugging und Fix für Claude-Verbindungsprobleme
    """
    print("\nCLAUDE CONNECTION FIX")
    print("="*60)
    
    # 1. API Key prüfen
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if api_key:
        print(f"✓ API Key vorhanden: {api_key[:15]}...{api_key[-5:]}")
        
        # Prüfe Format
        if api_key.startswith("sk-ant-"):
            print("✓ API Key Format korrekt")
        else:
            print("⚠️ API Key Format ungewöhnlich (sollte mit 'sk-ant-' beginnen)")
    else:
        print("✗ ANTHROPIC_API_KEY nicht gesetzt!")
    
    # 2. Test-Request
    print("\n2. Teste Claude API...")
    
    import requests
    
    url = "https://api.anthropic.com/v1/messages"
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }
    
    data = {
        "model": "claude-3-5-sonnet-20241022",
        "messages": [{"role": "user", "content": "Say 'test'"}],
        "max_tokens": 10,
        "temperature": 0
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=10)
        if response.status_code == 200:
            print("✓ Claude API funktioniert!")
            result = response.json()
            print(f"  Response: {result.get('content', [{}])[0].get('text', 'No text')[:50]}")
        else:
            print(f"✗ API Error {response.status_code}: {response.text[:200]}")
            
            if response.status_code == 401:
                print("  → API Key ungültig oder abgelaufen")
            elif response.status_code == 429:
                print("  → Rate limit erreicht")
            elif response.status_code == 500:
                print("  → Claude Server-Problem")
    except requests.exceptions.ConnectionError:
        print("✗ Verbindung fehlgeschlagen - Firewall/Proxy Problem?")
    except requests.exceptions.Timeout:
        print("✗ Timeout - Netzwerk zu langsam oder Server überlastet")
    except Exception as e:
        print(f"✗ Unerwarteter Fehler: {e}")
    
    # 3. Empfehlungen
    print("\n" + "="*60)
    print("EMPFEHLUNGEN:")
    print("-"*40)
    print("1. Backend neu starten nach Config-Update")
    print("2. Falls Claude nicht funktioniert:")
    print("   - Gemini als primären Provider nutzen")
    print("   - Groq als kostenlosen Fallback")
    print("3. Im Frontend Provider-Reihenfolge anpassen")

if __name__ == "__main__":
    print("LLM CONFIG UPDATE")
    print("="*60)
    
    # Update Config
    config = update_llm_config()
    
    # Test Claude
    fix_claude_connection()
    
    print("\n✅ Konfiguration aktualisiert!")
    print("   Backend neu starten für Änderungen:")
    print("   python hexagonal_api_enhanced_clean.py")
