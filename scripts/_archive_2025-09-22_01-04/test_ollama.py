#!/usr/bin/env python3
"""
Ollama Debug Script
==================
Testet direkt die Ollama-Verbindung
"""

import requests
import json
import time

def check_ollama_status():
    """Prüft Ollama-Status"""
    print("=== Ollama Status Check ===\n")
    
    base_url = "http://localhost:11434"
    
    # 1. Prüfe ob Ollama läuft
    try:
        response = requests.get(f"{base_url}/api/tags", timeout=2)
        if response.status_code == 200:
            print("✓ Ollama läuft auf localhost:11434")
            models = response.json()
            print(f"\nVerfügbare Modelle:")
            for model in models.get('models', []):
                print(f"  - {model['name']} ({model.get('size', 'unknown')})")
        else:
            print("✗ Ollama antwortet nicht korrekt")
            return False
    except Exception as e:
        print(f"✗ Ollama nicht erreichbar: {e}")
        return False
    
    return True

def test_model_generation(model_name="qwen2.5:7b"):
    """Testet Modell-Generierung"""
    print(f"\n=== Test Generierung mit {model_name} ===\n")
    
    base_url = "http://localhost:11434"
    prompt = "Say only 'Hello World'"
    
    try:
        print(f"Sende Prompt: '{prompt}'")
        start = time.time()
        
        response = requests.post(
            f"{base_url}/api/generate",
            json={
                "model": model_name,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "max_tokens": 100
                }
            },
            timeout=30  # 30 Sekunden Timeout
        )
        
        elapsed = time.time() - start
        
        if response.status_code == 200:
            result = response.json()
            generated_text = result.get('response', '')
            print(f"\n✓ Erfolg nach {elapsed:.1f}s")
            print(f"Antwort: '{generated_text}'")
            print(f"Antwortlänge: {len(generated_text)} Zeichen")
            
            # Zeige weitere Details
            if 'total_duration' in result:
                total_ms = result['total_duration'] / 1_000_000
                print(f"Ollama Duration: {total_ms:.0f}ms")
        else:
            print(f"\n✗ Fehler: Status {response.status_code}")
            print(f"Response: {response.text[:200]}")
            
    except requests.exceptions.Timeout:
        print(f"\n✗ Timeout nach {time.time() - start:.1f}s")
        print("  → Model lädt möglicherweise noch oder ist zu langsam")
    except Exception as e:
        print(f"\n✗ Fehler: {type(e).__name__}: {e}")

def test_all_models():
    """Testet alle verfügbaren Modelle"""
    models_to_test = ["qwen2.5:7b", "qwen2.5:14b"]
    
    for model in models_to_test:
        test_model_generation(model)
        print("\n" + "="*50 + "\n")

def main():
    print("Ollama Diagnose Tool")
    print("=" * 50 + "\n")
    
    if check_ollama_status():
        print("\nWelches Modell testen?")
        print("1. qwen2.5:7b (Standard)")
        print("2. qwen2.5:14b")
        print("3. Alle testen")
        
        choice = input("\nWahl (1-3): ").strip()
        
        if choice == "1":
            test_model_generation("qwen2.5:7b")
        elif choice == "2":
            test_model_generation("qwen2.5:14b")
        elif choice == "3":
            test_all_models()
        else:
            test_model_generation()  # Default
    else:
        print("\n⚠️  Bitte stelle sicher, dass Ollama läuft:")
        print("   ollama serve")

if __name__ == "__main__":
    main()
