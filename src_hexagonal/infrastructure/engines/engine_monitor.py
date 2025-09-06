#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Engine Activity Monitor - Echtzeit-Überwachung der Learning Engines
=====================================================================
"""

import os
import time
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

class EngineMonitor:
    """
    Überwacht und protokolliert Engine-Aktivitäten
    """
    
    def __init__(self):
        self.log_dir = Path("D:/MCP Mods/HAK_GAL_HEXAGONAL/engine_logs")
        self.log_dir.mkdir(exist_ok=True)
        
        # Separate Logs für jede Engine
        self.aethelred_log = self.log_dir / "aethelred_activity.jsonl"
        self.thesis_log = self.log_dir / "thesis_activity.jsonl"
        self.governor_log = self.log_dir / "governor_decisions.jsonl"
        
        # Live-Status-Datei
        self.status_file = self.log_dir / "engine_status.json"
        
    def log_activity(self, engine: str, event_type: str, data: Dict[str, Any]):
        """
        Protokolliert Engine-Aktivität
        """
        entry = {
            "timestamp": datetime.now().isoformat(),
            "engine": engine,
            "event": event_type,
            "data": data
        }
        
        # Wähle Log-Datei
        if engine == "aethelred":
            log_file = self.aethelred_log
        elif engine == "thesis":
            log_file = self.thesis_log
        else:
            log_file = self.governor_log
        
        # Append to JSONL
        with open(log_file, 'a') as f:
            f.write(json.dumps(entry) + '\n')
        
        # Update Status
        self.update_status(engine, event_type, data)
    
    def update_status(self, engine: str, event: str, data: Dict):
        """
        Aktualisiert Live-Status
        """
        try:
            if self.status_file.exists():
                with open(self.status_file, 'r') as f:
                    status = json.load(f)
            else:
                status = {
                    "aethelred": {"state": "idle", "facts_generated": 0, "last_activity": None},
                    "thesis": {"state": "idle", "facts_analyzed": 0, "last_activity": None},
                    "governor": {"decisions": 0, "last_decision": None}
                }
            
            # Update engine-specific status
            if engine in status:
                status[engine]["state"] = data.get("state", event)
                status[engine]["last_activity"] = datetime.now().isoformat()
                
                if engine == "aethelred" and "facts_added" in data:
                    status[engine]["facts_generated"] += data["facts_added"]
                elif engine == "thesis" and "facts_analyzed" in data:
                    status[engine]["facts_analyzed"] = data["facts_analyzed"]
                elif engine == "governor":
                    status[engine]["decisions"] += 1
                    status[engine]["last_decision"] = event
            
            # Save updated status
            with open(self.status_file, 'w') as f:
                json.dump(status, f, indent=2)
                
        except Exception as e:
            print(f"Error updating status: {e}")
    
    def get_recent_activities(self, engine: str = None, limit: int = 10) -> List[Dict]:
        """
        Holt die letzten Aktivitäten
        """
        activities = []
        
        # Wähle Log-Dateien
        if engine:
            log_files = [getattr(self, f"{engine}_log")]
        else:
            log_files = [self.aethelred_log, self.thesis_log, self.governor_log]
        
        for log_file in log_files:
            if log_file.exists():
                with open(log_file, 'r') as f:
                    lines = f.readlines()
                    for line in lines[-limit:]:
                        try:
                            activities.append(json.loads(line))
                        except:
                            pass
        
        # Sort by timestamp
        activities.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        return activities[:limit]
    
    def print_dashboard(self):
        """
        Zeigt ein Live-Dashboard
        """
        os.system('cls' if os.name == 'nt' else 'clear')
        
        print("=" * 80)
        print("HAK-GAL ENGINE MONITOR DASHBOARD")
        print("=" * 80)
        
        # Load status
        if self.status_file.exists():
            with open(self.status_file, 'r') as f:
                status = json.load(f)
            
            # Aethelred Status
            print(f"\n🔬 AETHELRED ENGINE")
            print(f"   State: {status['aethelred']['state']}")
            print(f"   Facts Generated: {status['aethelred']['facts_generated']}")
            print(f"   Last Activity: {status['aethelred']['last_activity']}")
            
            # Thesis Status
            print(f"\n🧠 THESIS ENGINE")
            print(f"   State: {status['thesis']['state']}")
            print(f"   Facts Analyzed: {status['thesis']['facts_analyzed']}")
            print(f"   Last Activity: {status['thesis']['last_activity']}")
            
            # Governor Status
            print(f"\n👑 GOVERNOR")
            print(f"   Decisions Made: {status['governor']['decisions']}")
            print(f"   Last Decision: {status['governor']['last_decision']}")
        
        # Recent Activities
        print(f"\n📋 RECENT ACTIVITIES:")
        print("-" * 80)
        
        activities = self.get_recent_activities(limit=5)
        for act in activities:
            timestamp = act.get('timestamp', 'unknown')[:19]
            engine = act.get('engine', 'unknown')
            event = act.get('event', 'unknown')
            print(f"  [{timestamp}] {engine:10} | {event}")
        
        print("=" * 80)


# Singleton
_monitor = None

def get_monitor() -> EngineMonitor:
    global _monitor
    if _monitor is None:
        _monitor = EngineMonitor()
    return _monitor


if __name__ == "__main__":
    # Live Dashboard Mode
    monitor = get_monitor()
    
    while True:
        monitor.print_dashboard()
        time.sleep(2)  # Update every 2 seconds
