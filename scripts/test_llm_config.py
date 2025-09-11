#!/usr/bin/env python
"""
Test-Skript für LLM-Konfiguration
=================================
Zeigt, wie die neue LLM-Konfiguration funktioniert
"""

import requests
import json
import time

# Base URL - passen Sie an Ihre Installation an
BASE_URL = "http://localhost:5001"  # oder 5002

def test_llm_config():
    """Test der LLM-Konfigurations-API"""
    
    print("=== LLM Konfigurations-Test ===\n")
    
    # 1. Aktuelle Konfiguration abrufen
    print("1. Lade aktuelle Konfiguration...")
    resp = requests.get(f"{BASE_URL}/api/llm/config")
    if resp.status_code == 200:
        config = resp.json()
        print(f"   Aktivierte Provider: {config.get('enabled_providers', [])}")
        print(f"   Provider-Reihenfolge: {config.get('provider_order', [])}")
    else:
        print(f"   FEHLER: {resp.status_code}")
    
    # 2. Prüfe welche Provider Environment-Keys haben
    print("\n2. Prüfe Environment-Keys...")
    resp = requests.get(f"{BASE_URL}/api/llm/check-env-keys")
    if resp.status_code == 200:
        env_keys = resp.json()
        for provider, has_key in env_keys.items():
            status = "✓ Gesetzt" if has_key else "✗ Fehlt"
            print(f"   {provider}: {status}")
    
    # 3. Neue Konfiguration setzen (nur Groq und DeepSeek aktiviert)
    print("\n3. Setze neue Konfiguration (nur Groq + DeepSeek)...")
    new_config = {
        "providers": [
            {
                "id": "groq",
                "enabled": True,
                "order": 0,
                "tempApiKey": None  # Nutzt .env
            },
            {
                "id": "deepseek", 
                "enabled": True,
                "order": 1,
                "tempApiKey": None  # Nutzt .env
            },
            {
                "id": "gemini",
                "enabled": False,  # Deaktiviert
                "order": 2
            },
            {
                "id": "claude",
                "enabled": False,  # Deaktiviert
                "order": 3
            },
            {
                "id": "ollama",
                "enabled": True,  # Als Fallback
                "order": 4
            }
        ]
    }
    
    resp = requests.post(f"{BASE_URL}/api/llm/config", json=new_config)
    if resp.status_code == 200:
        print("   ✓ Konfiguration gespeichert!")
    else:
        print(f"   ✗ Fehler: {resp.status_code}")
    
    # 4. Test Groq Provider
    print("\n4. Teste Groq Provider...")
    test_data = {
        "provider": "groq",
        "apiKey": None  # Nutzt .env
    }
    
    start_time = time.time()
    resp = requests.post(f"{BASE_URL}/api/llm/test", json=test_data)
    duration = (time.time() - start_time) * 1000
    
    if resp.status_code == 200:
        result = resp.json()
        if result.get('success'):
            print(f"   ✓ Groq funktioniert! (Response in {duration:.0f}ms)")
        else:
            print(f"   ✗ Groq Fehler: {result.get('error')}")
    
    # 5. Test LLM-Erklärung mit neuer Konfiguration
    print("\n5. Teste LLM-Erklärung mit optimierter Konfiguration...")
    
    test_query = {
        "topic": "What is artificial intelligence?",
        "context_facts": ["IsA(AI, Technology).", "UsedFor(AI, MachineLearning)."]
    }
    
    start_time = time.time()
    resp = requests.post(f"{BASE_URL}/api/llm/get-explanation", json=test_query)
    duration = (time.time() - start_time)
    
    if resp.status_code == 200:
        result = resp.json()
        print(f"   ✓ Erklärung erhalten!")
        print(f"   Provider: {result.get('llm_provider')}")
        print(f"   Response-Zeit: {duration:.2f}s")
        print(f"   Erklärung (Auszug): {result.get('explanation', '')[:100]}...")
    else:
        print(f"   ✗ Fehler: {resp.status_code}")
    
    # 6. Vergleiche Performance
    print("\n=== Performance-Vergleich ===")
    print(f"Mit optimierter Konfiguration: {duration:.2f}s")
    print(f"Erwartete Zeit mit Groq: ~1.5s")
    print(f"Verbesserung: {((10 - duration) / 10 * 100):.1f}%")

if __name__ == "__main__":
    test_llm_config()
    
    print("\n=== Hinweise ===")
    print("1. Stellen Sie sicher, dass der HAK-GAL Backend-Server läuft")
    print("2. Setzen Sie GROQ_API_KEY in Ihrer .env Datei")
    print("3. Öffnen Sie Settings → LLM im Frontend für die GUI")
