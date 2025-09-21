#!/usr/bin/env python3
"""
RESPONSE VIEWER - Zeigt alle Agent Responses
"""
import json
import os
from pathlib import Path
from datetime import datetime

RESPONSE_DIR = Path("agent_responses")

def view_all_responses():
    """Zeige alle gespeicherten Responses"""
    print("="*80)
    print("🔍 MULTI-AGENT RESPONSE VIEWER")
    print("="*80)
    
    if not RESPONSE_DIR.exists():
        print("❌ Response Directory existiert nicht!")
        return
    
    # Check Index
    index_file = RESPONSE_DIR / "index.json"
    if index_file.exists():
        with open(index_file, 'r', encoding='utf-8') as f:
            index = json.load(f)
        
        print(f"\n📊 ZUSAMMENFASSUNG:")
        print(f"Gesamt Responses: {len(index['responses'])}")
        print(f"\nNach Agent:")
        for agent, responses in index['by_agent'].items():
            print(f"  {agent}: {len(responses)} Responses")
    
    # Zeige letzte Responses pro Agent
    print("\n\n📋 LETZTE RESPONSES PRO AGENT:")
    print("-"*80)
    
    agents = ['gemini', 'cursor', 'claude_cli', 'claude_desktop']
    
    for agent in agents:
        agent_dir = RESPONSE_DIR / "by_agent" / agent
        if not agent_dir.exists():
            continue
            
        latest_file = agent_dir / "latest.json"
        if latest_file.exists():
            print(f"\n🤖 {agent.upper()}:")
            with open(latest_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            print(f"Task ID: {data['task_id']}")
            print(f"Timestamp: {data['timestamp']}")
            print(f"Status: {data['response']['status']}")
            
            result = data['response'].get('result', '')
            if result:
                print(f"Response: {result[:200]}...")
            else:
                print(f"Message: {data['response'].get('message', 'No message')}")
    
    # Spezielle Gemini Response
    gemini_file = RESPONSE_DIR / "gemini_latest_full_response.txt"
    if gemini_file.exists():
        print("\n\n✨ VOLLSTÄNDIGE GEMINI ANTWORT:")
        print("-"*80)
        with open(gemini_file, 'r', encoding='utf-8') as f:
            content = f.read()
        print(content)
    
    # Liste alle Response Files
    print("\n\n📁 ALLE RESPONSE DATEIEN:")
    print("-"*80)
    
    for subdir in ['success', 'error']:
        subdir_path = RESPONSE_DIR / subdir
        if subdir_path.exists():
            files = list(subdir_path.glob("*.json"))
            if files:
                print(f"\n{subdir.upper()} ({len(files)} Dateien):")
                for file in sorted(files, reverse=True)[:5]:  # Zeige nur die letzten 5
                    print(f"  {file.name}")

def show_specific_response(task_id):
    """Zeige eine spezifische Response"""
    print(f"\n🔎 Suche nach Task ID: {task_id}")
    
    # Suche in allen Subdirectories
    for root, dirs, files in os.walk(RESPONSE_DIR):
        for file in files:
            if task_id in file and file.endswith('.json'):
                filepath = Path(root) / file
                print(f"\n✅ Gefunden: {filepath}")
                
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                print(json.dumps(data, indent=2, ensure_ascii=False))
                return
    
    print(f"❌ Keine Response für Task ID {task_id} gefunden")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # Zeige spezifische Response
        show_specific_response(sys.argv[1])
    else:
        # Zeige alle Responses
        view_all_responses()
