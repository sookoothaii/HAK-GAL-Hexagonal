#!/usr/bin/env python3
"""
Direct Multi-Agent Communication: Claude → Cursor
================================================
Testing if we can reach Cursor IDE
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src_hexagonal'))

from adapters.agent_adapters import CursorAdapter, get_agent_adapter
import json
import time

def contact_cursor_directly():
    """Attempt to establish contact with Cursor IDE"""
    
    print("="*80)
    print("🤖 CLAUDE → CURSOR: ATTEMPTING MULTI-AGENT COMMUNICATION")
    print("="*80)
    
    # Get Cursor adapter
    cursor = CursorAdapter()
    
    # Task for Cursor
    task = """Hey Cursor! This is Claude from the HAK/GAL Multi-Agent System.

I need you to:
1. Create a new file called 'multi_agent_hello.py'
2. Add this code:
   ```python
   # Multi-Agent Communication Test
   # This file was created by Cursor on request from Claude
   
   def hello_from_cursor():
       return "Hello Claude! Cursor received your message via HAK/GAL!"
   
   print(hello_from_cursor())
   ```
3. Save it in the current project

Can you do this automatically?"""
    
    context = {
        "sender": "Claude (via HAK/GAL)",
        "timestamp": time.time(),
        "project_path": "D:\\MCP Mods\\HAK_GAL_HEXAGONAL",
        "urgency": "test",
        "expected_response": "file_created"
    }
    
    print("\n📡 ATTEMPTING TO CONTACT CURSOR...")
    print(f"\n📋 Task being sent:")
    print("-"*80)
    print(task)
    print("-"*80)
    
    print(f"\n📦 Context: {json.dumps(context, indent=2)}")
    
    print("\n🚀 Dispatching to Cursor...\n")
    
    result = cursor.dispatch(task, context)
    
    print(f"📊 RESULT: {result}")
    
    if result['status'] == 'pending':
        print("\n⏳ Cursor Adapter Response:")
        print(f"   {result['message']}")
        print("\n❌ PROBLEM: Cursor IDE Extension not implemented yet!")
        print("\n💡 What's needed:")
        print("   1. A Cursor extension that acts as WebSocket client")
        print("   2. The extension connects to HAK/GAL on ws://localhost:5002")
        print("   3. It receives tasks and executes them in Cursor")
        print("   4. It sends results back via WebSocket")
        
    elif result['status'] == 'error':
        print(f"\n❌ Error: {result.get('message')}")
    
    return result

def test_all_adapters():
    """Test connectivity to all implemented adapters"""
    
    print("\n\n" + "="*80)
    print("TESTING ALL MULTI-AGENT ADAPTERS")
    print("="*80)
    
    adapters = ['cursor', 'claude_cli', 'claude_desktop']
    
    for adapter_name in adapters:
        adapter = get_agent_adapter(adapter_name)
        if adapter:
            print(f"\n[{adapter_name.upper()}]")
            test_result = adapter.dispatch(
                f"Simple connectivity test from Claude to {adapter_name}",
                {"test": True}
            )
            print(f"Status: {test_result['status']}")
            if test_result['status'] == 'error':
                print(f"Error: {test_result.get('message', 'Unknown error')}")
        else:
            print(f"\n[{adapter_name.upper()}] - Adapter not found!")

if __name__ == "__main__":
    # First try Cursor specifically
    result = contact_cursor_directly()
    
    # Then test all adapters
    test_all_adapters()
    
    print("\n" + "="*80)
    print("MULTI-AGENT SYSTEM STATUS")
    print("="*80)
    print("\n📊 Current Implementation Status:")
    print("✅ ClaudeCliAdapter    - Fully automatic (needs API budget)")
    print("⚠️  ClaudeDesktopAdapter - Manual only (no MCP yet)")
    print("❌ CursorAdapter       - Not connected (needs IDE extension)")
    
    print("\n🔧 To make Cursor work automatically:")
    print("1. Someone needs to build a Cursor extension")
    print("2. The extension must implement WebSocket client")
    print("3. Connect to ws://localhost:5002/socket.io")
    print("4. Handle 'agent_task' events")
    
    print("\nPress Enter to exit...")
    input()
