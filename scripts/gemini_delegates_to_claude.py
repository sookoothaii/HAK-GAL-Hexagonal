#!/usr/bin/env python3
"""
Gemini delegates a real task to Claude Desktop
==============================================
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src_hexagonal'))

from adapters.agent_adapters import ClaudeDesktopAdapter
import json
import time

def gemini_delegates_to_claude():
    """Gemini (me) delegates an analysis task to Claude Desktop"""
    
    print("="*80)
    print("🤖 GEMINI → CLAUDE DESKTOP: MULTI-AGENT TASK DELEGATION")
    print("="*80)
    print("\nGemini speaking: I'm delegating a complex analysis task to Claude Desktop...")
    
    adapter = ClaudeDesktopAdapter()
    
    # The task I want Claude Desktop to do
    task = """Als Senior KI-Architekt, führe eine umfassende Analyse des HAK/GAL Multi-Agent Systems durch:

## 1. SWOT-Analyse

### Strengths (Stärken)
- Analysiere die Vorteile der hexagonalen Architektur
- Bewerte die Multi-Method-Kommunikation (URL Scheme, File Exchange, MCP)

### Weaknesses (Schwächen)  
- Identifiziere Sicherheitslücken in der Agent-Kommunikation
- Bewerte die Abhängigkeit von manuellen Prozessen

### Opportunities (Chancen)
- Potenzial für weitere AI-Agent-Integrationen (GPT-4, Bard, Mistral)
- Enterprise-Anwendungsfälle

### Threats (Risiken)
- Skalierungsprobleme bei 10+ Agenten
- Sicherheitsrisiken bei subprocess-Ausführung

## 2. Konkrete Verbesserungsvorschläge
Gib 5 spezifische technische Verbesserungen mit Implementierungsdetails.

## 3. Zukunftsvision
Beschreibe, wie das System in 12 Monaten aussehen könnte."""
    
    context = {
        "gemini_analysis": {
            "current_state": "3 Adapter implementiert, File-Exchange getestet",
            "performance": "2100 queries/min peak",
            "kb_size": "5832 facts",
            "test_date": "25. August 2025"
        },
        "technical_details": {
            "working_adapters": ["ClaudeCliAdapter", "ClaudeDesktopAdapter"],
            "communication_methods": ["subprocess", "url_scheme", "file_exchange"],
            "pending_features": ["MCP support in Claude Desktop", "Cursor IDE extension"]
        },
        "request_from": "Gemini AI via HAK/GAL System"
    }
    
    print(f"\n📋 TASK DETAILS:")
    print("-"*80)
    print(task[:500] + "...")
    print("-"*80)
    
    print(f"\n📦 CONTEXT PROVIDED:")
    print(json.dumps(context, indent=2))
    
    print("\n🚀 Delegating to Claude Desktop...\n")
    
    result = adapter.dispatch(task, context)
    
    print(f"\n📊 RESULT STATUS: {result['status']}")
    
    if result['status'] == 'pending':
        print("\n✅ Successfully opened in Claude Desktop!")
        print(f"Details: {result.get('message')}")
        print("\n💡 Next steps:")
        print("1. Claude Desktop should now be open with the analysis task")
        print("2. Copy Claude's response when ready")
        print("3. Use 'python scripts/claude_desktop_helper.py' to save the response")
        
        # Create a request file for tracking
        request_id = f"gemini_to_claude_{int(time.time())}"
        print(f"\n📁 Request ID for tracking: {request_id}")
        
    elif result['status'] == 'completed':
        print("\n✅ Task completed!")
        print("Response:", result.get('result', 'No result'))
        
    else:
        print(f"\n❌ Error: {result.get('message')}")
    
    return result

if __name__ == "__main__":
    print("🤖 Gemini here! I'm going to delegate a complex analysis task to Claude Desktop.\n")
    
    result = gemini_delegates_to_claude()
    
    print("\n" + "="*80)
    print("MULTI-AGENT COLLABORATION INITIATED")
    print("="*80)
    print("\nThis demonstrates the power of the HAK/GAL Multi-Agent System:")
    print("- Gemini (me) can delegate tasks to other AI agents")
    print("- Claude Desktop receives complex tasks with full context")
    print("- The system orchestrates communication between different AI systems")
    
    print("\nPress Enter to exit...")
    input()
