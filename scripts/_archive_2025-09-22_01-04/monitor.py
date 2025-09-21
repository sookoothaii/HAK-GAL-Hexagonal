#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Live Engine Monitor - Zeigt in Echtzeit was die Engines tun
"""

import requests
import time
import os
from datetime import datetime
from colorama import init, Fore, Back, Style

# Initialize colorama for Windows
init()

class LiveMonitor:
    def __init__(self):
        self.api_base = "http://localhost:5002"
        self.last_facts = 0
        self.start_time = time.time()
        
    def get_status(self):
        """Sammelt alle Status-Informationen"""
        status = {
            'governor': None,
            'facts': None,
            'health': None,
            'errors': []
        }
        
        try:
            # Governor Status
            resp = requests.get(f"{self.api_base}/api/governor/status", timeout=2)
            if resp.status_code == 200:
                status['governor'] = resp.json()
        except Exception as e:
            status['errors'].append(f"Governor: {e}")
            
        try:
            # Facts Count
            resp = requests.get(f"{self.api_base}/api/facts/count", timeout=2)
            if resp.status_code == 200:
                status['facts'] = resp.json()
        except Exception as e:
            status['errors'].append(f"Facts: {e}")
            
        try:
            # Health
            resp = requests.get(f"{self.api_base}/health", timeout=2)
            if resp.status_code == 200:
                status['health'] = resp.json()
        except Exception as e:
            status['errors'].append(f"Health: {e}")
            
        return status
    
    def display(self):
        """Zeigt Dashboard an"""
        os.system('cls' if os.name == 'nt' else 'clear')
        
        status = self.get_status()
        runtime = int(time.time() - self.start_time)
        
        # Header
        print(f"{Back.BLUE}{Fore.WHITE}{'=' * 80}{Style.RESET_ALL}")
        print(f"{Back.BLUE}{Fore.WHITE} HAK-GAL ENGINE MONITOR {' ' * 40} Runtime: {runtime}s {Style.RESET_ALL}")
        print(f"{Back.BLUE}{Fore.WHITE}{'=' * 80}{Style.RESET_ALL}")
        
        # System Health
        if status['health']:
            health = status['health']
            print(f"\n{Fore.GREEN}✓ SYSTEM HEALTH{Style.RESET_ALL}")
            print(f"  Status: {health.get('status', 'unknown')}")
            print(f"  Port: {health.get('port', 'unknown')}")
            print(f"  Backend: {health.get('backend', 'unknown')}")
        else:
            print(f"\n{Fore.RED}✗ SYSTEM OFFLINE{Style.RESET_ALL}")
        
        # Knowledge Base
        if status['facts']:
            facts = status['facts']
            count = facts.get('count', 0)
            diff = count - self.last_facts
            self.last_facts = count
            
            print(f"\n{Fore.CYAN}📚 KNOWLEDGE BASE{Style.RESET_ALL}")
            print(f"  Total Facts: {count}")
            if diff > 0:
                print(f"  {Fore.GREEN}↑ New Facts: +{diff}{Style.RESET_ALL}")
            elif diff < 0:
                print(f"  {Fore.RED}↓ Facts Removed: {diff}{Style.RESET_ALL}")
        
        # Governor Status
        if status['governor']:
            gov = status['governor']
            print(f"\n{Fore.YELLOW}👑 GOVERNOR{Style.RESET_ALL}")
            print(f"  Running: {gov.get('running', False)}")
            print(f"  Mode: {gov.get('mode', 'unknown')}")
            print(f"  Decisions: {gov.get('decisions_made', 0)}")
            
            # Engines
            engines = gov.get('engines', {})
            for engine_name, engine_info in engines.items():
                if engine_info.get('running'):
                    runtime = engine_info.get('runtime', 0)
                    print(f"  {Fore.GREEN}● {engine_name.upper()}: Running ({runtime:.0f}s){Style.RESET_ALL}")
                else:
                    runs = engine_info.get('runs', 0)
                    print(f"  {Fore.RED}○ {engine_name.upper()}: Stopped (runs: {runs}){Style.RESET_ALL}")
        
        # Errors
        if status['errors']:
            print(f"\n{Fore.RED}⚠ ERRORS:{Style.RESET_ALL}")
            for error in status['errors'][:3]:
                print(f"  {error}")
        
        # Footer
        print(f"\n{Back.BLUE}{Fore.WHITE}{'=' * 80}{Style.RESET_ALL}")
        print(f"Press Ctrl+C to exit. Refreshing every 2 seconds...")
    
    def run(self):
        """Main loop"""
        try:
            while True:
                self.display()
                time.sleep(2)
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}Monitor stopped.{Style.RESET_ALL}")


if __name__ == "__main__":
    monitor = LiveMonitor()
    monitor.run()
