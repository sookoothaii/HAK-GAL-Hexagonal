#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
LLM LIVE MONITOR - Real-time LLM Interaction Monitoring
======================================================
Shows live LLM requests, responses, and decision-making process
"""

import requests
import json
import time
import threading
from datetime import datetime
from typing import Dict, Any
import os

class LLMLiveMonitor:
    def __init__(self, backend_url="http://localhost:5002"):
        self.backend_url = backend_url
        self.running = False
        self.monitor_thread = None
        
    def start_monitoring(self):
        """Start live monitoring"""
        if self.running:
            print("❌ Monitor already running!")
            return
            
        self.running = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        print("🚀 LLM Live Monitor started!")
        
    def stop_monitoring(self):
        """Stop monitoring"""
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join()
        print("⏹️ LLM Live Monitor stopped!")
        
    def _monitor_loop(self):
        """Main monitoring loop"""
        print("\n" + "="*80)
        print("🧠 LLM LIVE MONITOR - Real-time LLM Interactions")
        print("="*80)
        
        last_fact_count = 0
        last_governor_status = {}
        
        while self.running:
            try:
                # Get current status
                status = self._get_status()
                if not status:
                    time.sleep(2)
                    continue
                    
                # Monitor fact generation
                current_fact_count = status.get('fact_count', 0)
                if current_fact_count > last_fact_count:
                    new_facts = current_fact_count - last_fact_count
                    print(f"\n🎉 NEW FACTS DETECTED: +{new_facts} (Total: {current_fact_count})")
                    self._show_recent_facts()
                    last_fact_count = current_fact_count
                
                # Monitor Governor decisions
                governor = status.get('governor', {})
                if governor != last_governor_status:
                    self._show_governor_changes(governor, last_governor_status)
                    last_governor_status = governor.copy()
                
                # Monitor LLM Governor
                llm_governor = status.get('llm_governor', {})
                if llm_governor.get('enabled'):
                    self._show_llm_governor_status(llm_governor)
                
                # Monitor engine activity
                self._show_engine_activity(governor)
                
                time.sleep(3)  # Check every 3 seconds
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"❌ Monitor error: {e}")
                time.sleep(5)
                
    def _get_status(self):
        """Get system status from backend"""
        try:
            response = requests.get(f"{self.backend_url}/api/status", timeout=5)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"❌ Failed to get status: {e}")
        return None
        
    def _show_recent_facts(self):
        """Show recently added facts"""
        try:
            response = requests.get(f"{self.backend_url}/api/facts?limit=5", timeout=5)
            if response.status_code == 200:
                facts = response.json().get('facts', [])
                if facts:
                    print("📝 Recent Facts:")
                    for i, fact in enumerate(facts[-3:], 1):  # Show last 3
                        statement = fact.get('statement', 'N/A')
                        source = fact.get('source', 'unknown')
                        print(f"   {i}. {statement} (Source: {source})")
        except Exception as e:
            print(f"❌ Failed to get recent facts: {e}")
            
    def _show_governor_changes(self, current, previous):
        """Show Governor status changes"""
        print(f"\n🎯 GOVERNOR UPDATE:")
        
        # Engine status changes
        current_engines = current.get('engines', {})
        previous_engines = previous.get('engines', {})
        
        for engine_name in ['aethelred', 'thesis']:
            current_engine = current_engines.get(engine_name, {})
            previous_engine = previous_engines.get(engine_name, {})
            
            current_running = current_engine.get('running', False)
            previous_running = previous_engine.get('running', False)
            
            if current_running != previous_running:
                status = "🟢 STARTED" if current_running else "🔴 STOPPED"
                print(f"   {engine_name.upper()}: {status}")
                
                if current_running:
                    pid = current_engine.get('pid', 'N/A')
                    runtime = current_engine.get('runtime', 0)
                    print(f"      PID: {pid}, Runtime: {runtime:.1f}s")
        
        # Decision count
        decisions = current.get('decisions_count', 0)
        if decisions > 0:
            print(f"   Decisions made: {decisions}")
            
    def _show_llm_governor_status(self, llm_governor):
        """Show LLM Governor status"""
        provider = llm_governor.get('provider', 'unknown')
        epsilon = llm_governor.get('epsilon', 0)
        
        print(f"\n🤖 LLM GOVERNOR: {provider.upper()} (ε={epsilon})")
        
        # Get LLM metrics
        try:
            response = requests.get(f"{self.backend_url}/api/llm-governor/metrics", timeout=5)
            if response.status_code == 200:
                metrics = response.json()
                print(f"   Status: {metrics}")
        except Exception as e:
            print(f"   ❌ Failed to get LLM metrics: {e}")
            
    def _show_engine_activity(self, governor):
        """Show current engine activity"""
        engines = governor.get('engines', {})
        running_engines = []
        
        for engine_name, engine_data in engines.items():
            if engine_data.get('running', False):
                pid = engine_data.get('pid', 'N/A')
                runtime = engine_data.get('runtime', 0)
                runs = engine_data.get('runs', 0)
                running_engines.append(f"{engine_name}(PID:{pid}, {runtime:.1f}s, {runs} runs)")
        
        if running_engines:
            print(f"\n⚙️ ACTIVE ENGINES: {', '.join(running_engines)}")
        else:
            print(f"\n⏸️ NO ENGINES RUNNING")
            
    def test_llm_evaluation(self, fact_statement="test_fact(test, data)"):
        """Test LLM evaluation with a sample fact"""
        print(f"\n🧪 TESTING LLM EVALUATION:")
        print(f"   Fact: {fact_statement}")
        
        try:
            response = requests.post(
                f"{self.backend_url}/api/llm-governor/evaluate",
                json={"statement": fact_statement},
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ LLM Response: {result}")
            else:
                print(f"   ❌ LLM Error: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"   ❌ Request failed: {e}")

def main():
    """Main function"""
    print("🚀 Starting LLM Live Monitor...")
    
    monitor = LLMLiveMonitor()
    
    try:
        # Test connection
        status = monitor._get_status()
        if not status:
            print("❌ Cannot connect to backend! Make sure it's running on port 5002")
            return
            
        print("✅ Connected to backend!")
        
        # Start monitoring
        monitor.start_monitoring()
        
        # Keep running until Ctrl+C
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n⏹️ Stopping monitor...")
        monitor.stop_monitoring()
        print("👋 Goodbye!")

if __name__ == "__main__":
    main()

