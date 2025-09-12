#!/usr/bin/env python3
"""
Test-Skript für HAK_GAL Offline-Modus
=====================================
Testet die verbesserte Offline-Erkennung
"""

import os
import sys
import time
import socket

# Füge src_hexagonal zum Python-Path hinzu
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src_hexagonal'))

from adapters.llm_providers import get_llm_provider

def test_dns_check():
    """Testet die DNS-basierte Offline-Erkennung"""
    print("\n=== DNS-Check Test ===")
    start = time.time()
    
    try:
        socket.setdefaulttimeout(0.3)
        result = socket.gethostbyname("api.groq.com")
        socket.setdefaulttimeout(None)
        elapsed = time.time() - start
        print(f"✓ DNS resolution successful: {result}")
        print(f"  Zeit: {elapsed:.3f}s")
        return True
    except Exception as e:
        socket.setdefaulttimeout(None)
        elapsed = time.time() - start
        print(f"✗ DNS resolution failed: {e}")
        print(f"  Zeit: {elapsed:.3f}s")
        return False

def test_offline_mode():
    """Testet manuellen Offline-Modus"""
    print("\n=== Manueller Offline-Modus Test ===")
    
    # Aktiviere Offline-Modus
    os.environ['HAK_GAL_OFFLINE_MODE'] = 'true'
    
    start = time.time()
    provider = get_llm_provider()
    elapsed = time.time() - start
    
    print(f"Provider-Initialisierung: {elapsed:.3f}s")
    print(f"Provider-Typ: {provider.__class__.__name__}")
    
    # Cleanup
    del os.environ['HAK_GAL_OFFLINE_MODE']
    
    return elapsed < 1.0  # Sollte unter 1 Sekunde sein

def test_provider_response():
    """Testet Provider-Antwort mit kurzer Anfrage"""
    print("\n=== Provider Response Test ===")
    
    provider = get_llm_provider()
    print(f"Aktiver Provider: {provider.__class__.__name__}")
    
    start = time.time()
    response, provider_name = provider.generate_response("Sage nur 'Hallo'")
    elapsed = time.time() - start
    
    print(f"\nAntwort von {provider_name}:")
    print(f"'{response[:100]}...'")
    print(f"Antwortzeit: {elapsed:.2f}s")
    print(f"Antwortlänge: {len(response)} Zeichen")
    
    return len(response) > 0

def simulate_offline():
    """Simuliert Offline-Zustand durch ungültige DNS-Server"""
    print("\n=== Simuliere Offline-Zustand ===")
    print("(Dies könnte fehlschlagen wenn echter DNS-Cache vorhanden)")
    
    # Temporär ungültigen DNS setzen (funktioniert nicht immer)
    original_dns = socket.gethostbyname
    
    def fake_dns(hostname):
        raise socket.gaierror("Simulated offline")
    
    socket.gethostbyname = fake_dns
    
    try:
        provider = get_llm_provider()
        print(f"Provider im simulierten Offline: {provider.__class__.__name__}")
    finally:
        socket.gethostbyname = original_dns

def main():
    """Führt alle Tests aus"""
    print("HAK_GAL Offline-Modus Test Suite")
    print("=" * 40)
    
    tests = [
        ("DNS-Check", test_dns_check),
        ("Manueller Offline-Modus", test_offline_mode),
        ("Provider Response", test_provider_response),
        ("Offline-Simulation", simulate_offline)
    ]
    
    results = []
    
    for name, test_func in tests:
        try:
            success = test_func()
            results.append((name, success))
        except Exception as e:
            print(f"\n✗ Test '{name}' fehlgeschlagen: {e}")
            results.append((name, False))
    
    # Zusammenfassung
    print("\n" + "=" * 40)
    print("TEST-ZUSAMMENFASSUNG:")
    print("=" * 40)
    
    for name, success in results:
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"{status} - {name}")
    
    # Performance-Hinweise
    print("\nPERFORMANCE-TIPPS:")
    print("- DNS-Check sollte < 0.5s dauern")
    print("- Offline-Modus-Init sollte < 1s dauern")
    print("- Bei erkanntem Offline direkt Ollama verwenden")
    print("\nUmgebungsvariablen:")
    print(f"- HAK_GAL_OFFLINE_MODE: {os.environ.get('HAK_GAL_OFFLINE_MODE', 'nicht gesetzt')}")
    print(f"- OLLAMA_MODEL: {os.environ.get('OLLAMA_MODEL', 'qwen2.5:7b (default)')}")

if __name__ == "__main__":
    main()
