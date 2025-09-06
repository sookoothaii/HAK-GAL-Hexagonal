#!/usr/bin/env python3
"""
MULTI-AGENT ORCHESTRA - LIVE DEMONSTRATION
Shows real-time agent interaction and coordination
"""
import requests
import json
import time
from datetime import datetime
from pathlib import Path
import threading
import sys

API_BASE = "http://127.0.0.1:5002"
API_KEY = "hg_sk_4f9a8e1b7d2c5f6a8b3d9e0c1a7b4f9d"
RESPONSE_DIR = Path("agent_responses")

class AgentOrchestra:
    def __init__(self):
        self.active_tasks = {}
        self.responses = {}
        self.monitoring = True
        
    def delegate_task(self, agent, task, context=None):
        """Delegate a task to a specific agent"""
        try:
            response = requests.post(
                f"{API_BASE}/api/agent-bus/delegate",
                headers={"X-API-Key": API_KEY},
                json={
                    "target_agent": agent,
                    "task_description": task,
                    "context": context or {"orchestra": "multi_agent_demo"}
                },
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                self.active_tasks[agent] = data.get('task_id')
                return data
            return None
        except Exception as e:
            print(f"[ERROR] Failed to delegate to {agent}: {e}")
            return None

    def monitor_responses(self):
        """Monitor responses in real-time"""
        while self.monitoring:
            for agent in self.active_tasks:
                response_file = RESPONSE_DIR / "by_agent" / agent / "latest.json"
                if response_file.exists():
                    try:
                        with open(response_file, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            if data.get('task_id') in self.active_tasks.values():
                                status = data.get('response', {}).get('status')
                                if status == 'completed':
                                    self.responses[agent] = data
                                    print(f"\n[RESPONSE] {agent.upper()} completed task!")
                    except:
                        pass
            time.sleep(1)

    def run_orchestra(self):
        """Run the full multi-agent orchestra"""
        print("="*80)
        print("MULTI-AGENT ORCHESTRA - LIVE DEMONSTRATION")
        print("="*80)
        
        # Start monitoring thread
        monitor_thread = threading.Thread(target=self.monitor_responses, daemon=True)
        monitor_thread.start()
        
        # PHASE 1: Parallel Information Gathering
        print("\n[PHASE 1] PARALLEL INFORMATION GATHERING")
        print("-"*60)
        
        tasks_phase1 = {
            "gemini": "Analyze the current system architecture and list the top 3 strengths",
            "claude_cli": "Identify the most critical performance bottleneck in the system",
            "cursor": "Count total lines of Python code in src_hexagonal directory",
            "claude_desktop": "Review the frontend components and suggest one improvement"
        }
        
        print("Delegating analysis tasks to all agents...")
        for agent, task in tasks_phase1.items():
            result = self.delegate_task(agent, task)
            if result:
                print(f"  [{agent}] Task ID: {result.get('task_id')}")
        
        # Wait for Phase 1 completion
        print("\nWaiting for responses (15 seconds)...")
        time.sleep(15)
        
        # PHASE 2: Collaborative Problem Solving
        print("\n[PHASE 2] COLLABORATIVE PROBLEM SOLVING")
        print("-"*60)
        
        # Create a collaborative task based on Phase 1 results
        collab_context = {
            "instruction": "Each agent should build on the previous agent's work",
            "phase": "collaborative"
        }
        
        print("Starting collaborative chain...")
        
        # Gemini starts
        result = self.delegate_task(
            "gemini", 
            "Create a haiku about artificial intelligence collaboration",
            collab_context
        )
        print(f"  [gemini] Started creative task")
        time.sleep(5)
        
        # Claude CLI continues
        result = self.delegate_task(
            "claude_cli",
            "Take Gemini's haiku and translate it to German, maintaining the poetic structure",
            collab_context
        )
        print(f"  [claude_cli] Building on Gemini's work")
        time.sleep(5)
        
        # Cursor adds code
        result = self.delegate_task(
            "cursor",
            "Create a Python function that prints a haiku with proper formatting",
            collab_context
        )
        print(f"  [cursor] Adding technical implementation")
        time.sleep(5)
        
        # Claude Desktop visualizes
        result = self.delegate_task(
            "claude_desktop",
            "Design a simple HTML page concept to display haikus beautifully",
            collab_context
        )
        print(f"  [claude_desktop] Creating visualization concept")
        
        # PHASE 3: Consensus Building
        print("\n[PHASE 3] CONSENSUS BUILDING")
        print("-"*60)
        
        consensus_task = "Vote YES or NO: Should we implement a real-time dashboard for agent communication?"
        
        print("Requesting consensus from all agents...")
        for agent in ["gemini", "claude_cli", "cursor", "claude_desktop"]:
            result = self.delegate_task(agent, consensus_task, {"type": "vote"})
            if result:
                print(f"  [{agent}] Vote submitted")
        
        # Wait for final responses
        print("\nCollecting final responses (10 seconds)...")
        time.sleep(10)
        
        # Stop monitoring
        self.monitoring = False
        
        # Display Results
        self.display_results()
        
    def display_results(self):
        """Display all collected results"""
        print("\n" + "="*80)
        print("ORCHESTRA RESULTS")
        print("="*80)
        
        # Check response files
        for agent in ["gemini", "claude_cli", "cursor", "claude_desktop"]:
            print(f"\n[{agent.upper()}]")
            print("-"*40)
            
            latest_file = RESPONSE_DIR / "by_agent" / agent / "latest.json"
            if latest_file.exists():
                try:
                    with open(latest_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        response = data.get('response', {})
                        status = response.get('status', 'unknown')
                        
                        print(f"Status: {status}")
                        
                        if status == 'completed':
                            result = response.get('result', '')
                            if result:
                                print(f"Response: {result[:200]}...")
                        else:
                            print(f"Message: {response.get('message', 'Pending...')}")
                except Exception as e:
                    print(f"Error reading response: {e}")
            else:
                print("No response file found")
        
        # Special: Show Gemini's full response if available
        gemini_full = RESPONSE_DIR / "gemini_latest_full_response.txt"
        if gemini_full.exists():
            print("\n" + "="*80)
            print("GEMINI FULL RESPONSE")
            print("="*80)
            with open(gemini_full, 'r', encoding='utf-8') as f:
                content = f.read()
                print(content[:500] + "..." if len(content) > 500 else content)

if __name__ == "__main__":
    print("[INIT] Starting Multi-Agent Orchestra...")
    orchestra = AgentOrchestra()
    
    try:
        orchestra.run_orchestra()
    except KeyboardInterrupt:
        print("\n[STOP] Orchestra stopped by user")
    
    print("\n[DONE] Multi-Agent Orchestra completed!")
    print(f"[INFO] Check {RESPONSE_DIR.absolute()} for all responses")