#!/usr/bin/env python3
"""
Debug-Skript: Simuliert den MultiLLM-Ablauf bei Offline-Betrieb
================================================================
Testet die Offline-Erkennung und Ollama-Fallback
"""

import os
import sys
import time

# Füge src_hexagonal zum Python-Path hinzu
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src_hexagonal'))

def test_offline_scenario():
    """Simuliert Offline-Szenario und testet Fallback"""
    print("=== HAK_GAL Offline Scenario Test ===\n")
    
    # Setze Offline-Modus
    os.environ['HAK_GAL_OFFLINE_MODE'] = 'true'
    
    # Importiere NACH dem Setzen der Umgebungsvariable
    from adapters.llm_providers import get_llm_provider
    
    print("1. Initialisiere LLM Provider...")
    start = time.time()
    provider = get_llm_provider()
    init_time = time.time() - start
    print(f"   Initialisierung dauerte: {init_time:.2f}s")
    print(f"   Provider-Typ: {provider.__class__.__name__}")
    print(f"   Anzahl Provider: {len(provider.providers) if hasattr(provider, 'providers') else 1}")
    
    # Liste Provider
    if hasattr(provider, 'providers'):
        print("\n   Verfügbare Provider:")
        for p in provider.providers:
            print(f"   - {p.__class__.__name__}")
    
    # Teste Antwort-Generierung
    print("\n2. Teste Antwort-Generierung...")
    test_prompt = "What is consciousness in one sentence?"
    
    start = time.time()
    response, provider_name = provider.generate_response(test_prompt)
    gen_time = time.time() - start
    
    print(f"\n   Antwortzeit: {gen_time:.2f}s")
    print(f"   Provider: {provider_name}")
    print(f"   Antwortlänge: {len(response)} Zeichen")
    print(f"\n   Antwort: '{response[:200]}{'...' if len(response) > 200 else ''}'")
    
    # Prüfe ob es ein Fehler ist
    if 'error' in response.lower() or 'failed' in response.lower():
        print("\n   ⚠️  WARNUNG: Antwort enthält Fehlermeldung!")
    
    # Cleanup
    if 'HAK_GAL_OFFLINE_MODE' in os.environ:
        del os.environ['HAK_GAL_OFFLINE_MODE']
    
    print("\n" + "="*50)
    print("ZUSAMMENFASSUNG:")
    print(f"- Initialisierung: {init_time:.2f}s")
    print(f"- Antwortzeit: {gen_time:.2f}s")
    print(f"- Gesamtzeit: {init_time + gen_time:.2f}s")
    print(f"- Erwartete Zeit: <5s")
    print(f"- Status: {'✓ OK' if (init_time + gen_time) < 5 else '✗ ZU LANGSAM'}")

def test_connection_timeout():
    """Testet die Connection-Timeouts"""
    print("\n\n=== Connection Timeout Test ===\n")
    
    import requests
    
    # Teste verschiedene Timeout-Werte
    test_urls = [
        ("https://api.groq.com", "Groq"),
        ("https://api.deepseek.com", "DeepSeek"),
        ("https://unreachable.example.com", "Unreachable")
    ]
    
    for url, name in test_urls:
        print(f"Teste {name} ({url})...")
        
        for timeout in [0.5, 1, 2, 5]:
            try:
                start = time.time()
                resp = requests.get(url, timeout=timeout)
                elapsed = time.time() - start
                print(f"  {timeout}s timeout: Erfolg in {elapsed:.2f}s")
                break
            except Exception as e:
                elapsed = time.time() - start
                print(f"  {timeout}s timeout: Fehler nach {elapsed:.2f}s - {type(e).__name__}")

if __name__ == "__main__":
    # Test 1: Offline-Szenario
    test_offline_scenario()
    
    # Test 2: Connection Timeouts
    test_connection_timeout()
