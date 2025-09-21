#!/usr/bin/env python3
"""
Production Example: Using ClaudeDesktopAdapter
==============================================
Shows how to use the adapter in a real scenario
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src_hexagonal'))

from adapters.agent_adapters import ClaudeDesktopAdapter
import json

def delegate_to_claude_desktop(task, context=None):
    """Delegate a task to Claude Desktop"""
    
    adapter = ClaudeDesktopAdapter()
    
    print("=" * 60)
    print("DELEGATING TASK TO CLAUDE DESKTOP")
    print("=" * 60)
    print(f"\nTask: {task}")
    if context:
        print(f"Context: {json.dumps(context, indent=2)}")
    
    print("\nAttempting delegation...")
    result = adapter.dispatch(task, context or {})
    
    print(f"\nResult Status: {result['status']}")
    
    if result['status'] == 'completed':
        print("\n✅ TASK COMPLETED!")
        print("\nResponse:")
        print("-" * 60)
        print(result['result'])
        print("-" * 60)
    elif result['status'] == 'pending':
        print("\n⏳ TASK PENDING")
        print(f"Details: {result.get('message')}")
        if 'url_used' in result:
            print("\nClaude Desktop should have opened with your task.")
            print("Please provide the response manually if needed.")
    else:
        print(f"\n❌ ERROR: {result.get('message')}")
    
    return result

# Example usage
if __name__ == "__main__":
    # Example 1: Code Review
    print("\n### EXAMPLE 1: Code Review ###")
    delegate_to_claude_desktop(
        "Review this Python function and suggest improvements for error handling",
        context={
            "code": """
def divide(a, b):
    return a / b
""",
            "language": "python",
            "focus": "error handling"
        }
    )
    
    print("\n" + "="*60 + "\n")
    
    # Example 2: Architecture Analysis  
    print("### EXAMPLE 2: Architecture Analysis ###")
    delegate_to_claude_desktop(
        "Analyze the pros and cons of using hexagonal architecture for a microservices system",
        context={
            "current_architecture": "monolithic",
            "target_architecture": "microservices with hexagonal pattern",
            "team_size": 5,
            "timeline": "6 months"
        }
    )
    
    print("\nPress Enter to exit...")
    input()
