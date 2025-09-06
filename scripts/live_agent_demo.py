#!/usr/bin/env python3
"""
LIVE AGENT DEMONSTRATION - REAL-TIME INTERACTION
"""
import requests
import json
import time
from datetime import datetime

API_BASE = "http://127.0.0.1:5002"
API_KEY = "hg_sk_4f9a8e1b7d2c5f6a8b3d9e0c1a7b4f9d"

def send_to_agent(agent, message):
    """Send message to specific agent"""
    print(f"\n[SENDING TO {agent.upper()}]")
    print(f"Message: {message[:80]}...")
    
    try:
        response = requests.post(
            f"{API_BASE}/api/agent-bus/delegate",
            headers={"X-API-Key": API_KEY},
            json={
                "target_agent": agent,
                "task_description": message,
                "context": {
                    "demo": "live_interaction",
                    "timestamp": datetime.now().isoformat()
                }
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"[SUCCESS] Task ID: {data.get('task_id')}")
            print(f"Status: {data.get('status')}")
            if 'message' in data:
                print(f"Message: {data.get('message')}")
            return data
        else:
            print(f"[ERROR] Status Code: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"[EXCEPTION] {e}")
        return None

def main():
    print("="*80)
    print("LIVE MULTI-AGENT DEMONSTRATION")
    print("="*80)
    print("\nThis demo shows real agent communication capabilities!")
    
    # Test 1: Simple Echo Test
    print("\n" + "="*80)
    print("TEST 1: ECHO TEST - Each agent confirms presence")
    print("="*80)
    
    agents = ["gemini", "claude_cli", "cursor", "claude_desktop"]
    for agent in agents:
        send_to_agent(agent, f"ECHO TEST: Reply with 'Agent {agent} is ONLINE and ready!'")
        time.sleep(2)
    
    # Test 2: Collaborative Task
    print("\n" + "="*80)
    print("TEST 2: COLLABORATIVE CALCULATION")
    print("="*80)
    
    send_to_agent("gemini", "Calculate: What is 42 * 17?")
    time.sleep(3)
    send_to_agent("claude_cli", "If 42 * 17 = 714, what is 714 / 6?")
    time.sleep(3)
    send_to_agent("cursor", "Create a Python one-liner to calculate (42 * 17) / 6")
    time.sleep(3)
    
    # Test 3: Creative Collaboration
    print("\n" + "="*80)
    print("TEST 3: CREATIVE COLLABORATION")
    print("="*80)
    
    send_to_agent("gemini", "Start a story with: 'In the digital void, four agents met...'")
    time.sleep(5)
    send_to_agent("claude_cli", "Continue the story from Gemini about four agents meeting")
    time.sleep(5)
    send_to_agent("cursor", "Write a function called tell_agent_story() that prints a story")
    time.sleep(5)
    send_to_agent("claude_desktop", "Design a UI concept for displaying agent stories")
    
    # Test 4: System Analysis
    print("\n" + "="*80)
    print("TEST 4: SYSTEM ANALYSIS REQUESTS")
    print("="*80)
    
    send_to_agent("gemini", "What is the HAK-GAL system's main purpose?")
    send_to_agent("claude_cli", "How many facts are in the knowledge base?")
    send_to_agent("cursor", "List the main Python files in src_hexagonal")
    send_to_agent("claude_desktop", "Describe the frontend architecture")
    
    print("\n" + "="*80)
    print("DEMONSTRATION COMPLETE")
    print("="*80)
    print("\nAll tasks have been delegated to agents!")
    print("Check agent_responses directory for results")
    print("\nAgent capabilities demonstrated:")
    print("- Gemini: Analysis and creative tasks")
    print("- Claude CLI: Calculations and continuations")
    print("- Cursor: Code generation and file operations")
    print("- Claude Desktop: UI/UX concepts and visualization")

if __name__ == "__main__":
    main()