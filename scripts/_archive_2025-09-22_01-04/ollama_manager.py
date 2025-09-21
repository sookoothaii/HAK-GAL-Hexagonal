#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
HAK-GAL: Ollama Manager - Kontrolliere die Ollama-Nutzung
"""

import os
import sys
import requests
import json

def check_ollama_status():
    """Prüfe ob Ollama läuft"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        if response.status_code == 200:
            models = response.json()
            print("✅ Ollama is RUNNING")
            print(f"   Models: {len(models.get('models', []))} available")
            for model in models.get('models', [])[:5]:
                print(f"   - {model['name']}")
            return True
    except:
        print("❌ Ollama is NOT running")
        return False

def stop_ollama():
    """Stoppe Ollama Server"""
    print("\n🛑 Stopping Ollama...")
    os.system("taskkill /F /IM ollama.exe 2>nul")
    print("   Ollama stopped (if it was running)")

def start_ollama():
    """Starte Ollama Server"""
    print("\n🚀 Starting Ollama...")
    os.system("start /min ollama serve")
    print("   Ollama started in background")

def force_offline_mode():
    """Aktiviere Offline-Modus (nur Ollama)"""
    print("\n📴 Forcing OFFLINE mode...")
    os.environ['HAK_GAL_OFFLINE_MODE'] = 'true'
    
    # Schreibe in .env.local
    env_path = r"D:\MCP Mods\HAK_GAL_HEXAGONAL\.env.local"
    with open(env_path, 'a') as f:
        f.write("\n# Force offline mode\nHAK_GAL_OFFLINE_MODE=true\n")
    print("   Offline mode enabled (only Ollama will be used)")

def force_online_mode():
    """Aktiviere Online-Modus (Gemini first)"""
    print("\n🌐 Forcing ONLINE mode...")
    os.environ['HAK_GAL_OFFLINE_MODE'] = 'false'
    
    # Update .env.local
    env_path = r"D:\MCP Mods\HAK_GAL_HEXAGONAL\.env.local"
    try:
        with open(env_path, 'r') as f:
            lines = f.readlines()
        
        with open(env_path, 'w') as f:
            for line in lines:
                if 'HAK_GAL_OFFLINE_MODE' not in line:
                    f.write(line)
            f.write("HAK_GAL_OFFLINE_MODE=false\n")
    except:
        with open(env_path, 'w') as f:
            f.write("HAK_GAL_OFFLINE_MODE=false\n")
    
    print("   Online mode enabled (Gemini → Ollama → DeepSeek)")

def disable_ollama_in_providers():
    """Entferne Ollama aus der Provider-Liste"""
    print("\n🔧 Patching llm_providers.py to disable Ollama...")
    
    providers_path = r"D:\MCP Mods\HAK_GAL_HEXAGONAL\src_hexagonal\adapters\llm_providers.py"
    
    # Backup erstellen
    import shutil
    shutil.copy(providers_path, providers_path + ".backup_with_ollama")
    
    # Lese Datei
    with open(providers_path, 'r') as f:
        content = f.read()
    
    # Entferne OllamaProvider aus der Online-Provider-Liste
    old_providers = """providers = [
                    GeminiProvider(),     # Gemini first - uses 2.5 pro/flash models
                    OllamaProvider(),     # Ollama local as fallback (qwen2.5:14b)
                    DeepSeekProvider(),   # DeepSeek as last resort (slower but reliable)
                ]"""
    
    new_providers = """providers = [
                    GeminiProvider(),     # Gemini first - uses 1.5-flash (working)
                    DeepSeekProvider(),   # DeepSeek as fallback (no Ollama!)
                    # OllamaProvider(),   # DISABLED to prevent GPU usage
                ]"""
    
    content = content.replace(old_providers, new_providers)
    
    # Schreibe zurück
    with open(providers_path, 'w') as f:
        f.write(content)
    
    print("   ✅ Ollama disabled in provider chain")
    print("   Backup saved as llm_providers.py.backup_with_ollama")

def restore_ollama_in_providers():
    """Stelle Ollama in Provider-Liste wieder her"""
    print("\n🔧 Restoring Ollama in llm_providers.py...")
    
    providers_path = r"D:\MCP Mods\HAK_GAL_HEXAGONAL\src_hexagonal\adapters\llm_providers.py"
    backup_path = providers_path + ".backup_with_ollama"
    
    if os.path.exists(backup_path):
        import shutil
        shutil.copy(backup_path, providers_path)
        print("   ✅ Ollama restored in provider chain")
    else:
        print("   ❌ No backup found")

def main():
    print("="*60)
    print(" HAK-GAL OLLAMA MANAGER ")
    print("="*60)
    
    # Status
    is_running = check_ollama_status()
    
    print("\n" + "="*60)
    print("OPTIONS:")
    print("1. Stop Ollama (save GPU)")
    print("2. Start Ollama") 
    print("3. Force OFFLINE mode (only Ollama)")
    print("4. Force ONLINE mode (Gemini first)")
    print("5. Disable Ollama completely (patch providers)")
    print("6. Restore Ollama (unpatch providers)")
    print("0. Exit")
    print("="*60)
    
    choice = input("\nYour choice: ").strip()
    
    if choice == "1":
        stop_ollama()
    elif choice == "2":
        start_ollama()
    elif choice == "3":
        force_offline_mode()
    elif choice == "4":
        force_online_mode()
    elif choice == "5":
        disable_ollama_in_providers()
        print("\n⚠️  Restart the API server for changes to take effect!")
    elif choice == "6":
        restore_ollama_in_providers()
        print("\n⚠️  Restart the API server for changes to take effect!")
    elif choice == "0":
        sys.exit(0)
    else:
        print("Invalid choice")

if __name__ == "__main__":
    main()
