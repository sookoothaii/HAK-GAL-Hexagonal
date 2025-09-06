#!/usr/bin/env python3
"""
Zeigt ECHTE automatische Multi-Agent-Kommunikation
==================================================
Ohne manuellen Nachrichtentransport!
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src_hexagonal'))

from adapters.agent_adapters import ClaudeCliAdapter
import json

def automatic_multi_agent_demo():
    """Zeigt wie Multi-Agent WIRKLICH funktionieren sollte - vollautomatisch!"""
    
    print("="*60)
    print("AUTOMATISCHE MULTI-AGENT-KOMMUNIKATION")
    print("="*60)
    
    # ClaudeCliAdapter funktioniert vollautomatisch!
    adapter = ClaudeCliAdapter()
    
    task = "Erkläre in 2 Sätzen was MCP (Model Context Protocol) ist und warum es für Multi-Agent-Systeme wichtig ist."
    
    context = {
        "system": "HAK/GAL Multi-Agent",
        "automatic": True,
        "no_manual_steps": True
    }
    
    print(f"\n📋 Task: {task}")
    print(f"\n🚀 Sende automatisch an Claude CLI...\n")
    
    result = adapter.dispatch(task, context)
    
    print(f"Status: {result['status']}")
    
    if result['status'] == 'completed':
        print("\n✅ AUTOMATISCHE ANTWORT ERHALTEN:")
        print("-" * 60)
        print(result['result'])
        print("-" * 60)
        print("\n🎯 DAS ist wie Multi-Agent funktionieren sollte!")
        print("   Keine manuellen Schritte, alles automatisch!")
    else:
        print(f"\n❌ Fehler: {result.get('message')}")
        print("\nHinweis: Stellen Sie sicher, dass 'claude' CLI installiert ist")
        print("und ein gültiges API-Budget hat.")

if __name__ == "__main__":
    automatic_multi_agent_demo()
    print("\nPress Enter to exit...")
    input()
