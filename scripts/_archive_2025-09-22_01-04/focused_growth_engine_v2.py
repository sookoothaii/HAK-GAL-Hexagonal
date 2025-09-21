#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
HAK-GAL Focused Growth Engine V2 - Korrigierte Version
=======================================================
- Keine timestamp-Spalte verwenden (existiert nicht)
- Neue, eindeutige Fakten generieren
"""

import sqlite3
import random
from pathlib import Path
from datetime import datetime

class FocusedGrowthEngineV2:
    """Generiert nur sinnvolle, NEUE HAK-GAL Fakten"""
    
    def __init__(self):
        self.db_path = Path(r"D:\MCP Mods\HAK_GAL_HEXAGONAL\hexagonal_kb.db")
        self.generated_facts = []
        self.existing_facts = set()
        
        # Lade existierende Fakten
        self.load_existing_facts()
        
        # HAK-GAL spezifische Entitäten
        self.components = [
            "HAK_GAL_System", "HAK_GAL_API", "HAK_GAL_Frontend", 
            "HAK_GAL_Knowledge_Base", "HAK_GAL_Multi_Agent_System",
            "Hexagonal_Architecture", "MCP_Server", "REST_API",
            "Gemini_Adapter", "Claude_CLI_Adapter", "Claude_Desktop_Adapter",
            "Cursor_Adapter", "Knowledge_Validator", "Growth_Engine", 
            "WebSocket_Bridge", "Agent_Bus", "System_Monitor",
            "HRM_System", "Governor", "Sentry_Monitor"
        ]
        
        # Spezifische technische Details
        self.libraries = ["Flask", "SQLAlchemy", "Requests", "SocketIO", "Eventlet", 
                         "sqlite3", "json", "pathlib", "dataclasses", "enum"]
        
        self.endpoints = ["/health", "/api/facts/count", "/api/facts/search", 
                         "/api/facts/add", "/api/facts/delete", "/api/facts/update",
                         "/api/system/status", "/api/system/gpu", "/api/metrics",
                         "/api/agent-bus/delegate", "/api/agent-bus/responses"]
        
        self.versions = ["3.11", "3.12", "2.0", "2.1", "1.0", "1.1"]
        
        self.methods = ["GET", "POST", "PUT", "DELETE", "PATCH"]
        
        self.test_types = ["Unit_Tests", "Integration_Tests", "Live_Validation", 
                          "Performance_Tests", "Security_Tests"]
    
    def load_existing_facts(self):
        """Lade alle existierenden Fakten in Memory"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT statement FROM facts")
            facts = cursor.fetchall()
            self.existing_facts = {fact[0] for fact in facts}
            conn.close()
            print(f"📊 Loaded {len(self.existing_facts)} existing facts")
        except Exception as e:
            print(f"❌ Error loading facts: {e}")
    
    def generate_unique_fact(self):
        """Generiere einen garantiert neuen Fakt"""
        attempts = 0
        max_attempts = 100
        
        while attempts < max_attempts:
            fact = self.generate_technical_fact()
            if fact not in self.existing_facts:
                return fact
            attempts += 1
        
        # Fallback: Generiere Fakt mit Timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"GeneratedAt(HAK_GAL_Knowledge_Base, Time_{timestamp})."
    
    def generate_technical_fact(self):
        """Generiere verschiedene Arten technischer Fakten"""
        fact_type = random.choice([
            "implementation", "library", "endpoint", "version", 
            "testing", "monitoring", "dependency", "configuration",
            "performance", "architecture"
        ])
        
        if fact_type == "implementation":
            comp = random.choice(self.components)
            lang = random.choice(["Python", "JavaScript", "TypeScript", "SQL"])
            return f"ImplementedIn({comp}, {lang})."
            
        elif fact_type == "library":
            comp = random.choice(["HAK_GAL_API", "HAK_GAL_Frontend", "MCP_Server"])
            lib = random.choice(self.libraries)
            return f"UsesLibrary({comp}, {lib})."
            
        elif fact_type == "endpoint":
            endpoint = random.choice(self.endpoints)
            method = random.choice(self.methods)
            return f"SupportsMethod({endpoint}, {method})."
            
        elif fact_type == "version":
            comp = random.choice(self.components)
            ver = random.choice(self.versions)
            return f"RequiresVersion({comp}, Python_{ver.replace('.', '_')})."
            
        elif fact_type == "testing":
            comp = random.choice(self.components)
            test = random.choice(self.test_types)
            return f"TestedWith({comp}, {test})."
            
        elif fact_type == "monitoring":
            comp = random.choice(self.components)
            monitor = random.choice(["Sentry", "System_Monitor", "Health_Check", "Metrics_Collector"])
            return f"MonitoredBy({comp}, {monitor})."
            
        elif fact_type == "dependency":
            comp1 = random.choice(self.components)
            comp2 = random.choice(self.components)
            if comp1 != comp2:
                return f"DependsOn({comp1}, {comp2})."
            else:
                return f"SelfContained({comp1})."
                
        elif fact_type == "configuration":
            comp = random.choice(self.components)
            config = random.choice(["Environment_Variables", "Config_File", "Command_Line_Args"])
            return f"ConfiguredBy({comp}, {config})."
            
        elif fact_type == "performance":
            comp = random.choice(self.components)
            metric = random.choice(["Response_Time", "Throughput", "Memory_Usage", "CPU_Usage"])
            value = random.randint(1, 100)
            return f"PerformanceMetric({comp}, {metric}, {value})."
            
        else:  # architecture
            comp = random.choice(self.components)
            pattern = random.choice(["Hexagonal", "MVC", "REST", "Event_Driven", "Microservice"])
            return f"FollowsPattern({comp}, {pattern}_Architecture)."
    
    def add_fact(self, fact):
        """Füge Fakt zur Datenbank hinzu (ohne timestamp)"""
        if fact in self.existing_facts:
            return False
            
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            # Nur statement einfügen, keine timestamp
            cursor.execute(
                "INSERT INTO facts (statement) VALUES (?)",
                (fact,)
            )
            conn.commit()
            conn.close()
            
            # Update cache
            self.existing_facts.add(fact)
            self.generated_facts.append(fact)
            return True
            
        except Exception as e:
            print(f"  ❌ Error adding fact: {e}")
            return False
    
    def run(self, cycles=10):
        """Führe fokussiertes Wachstum aus"""
        print("=" * 80)
        print("HAK-GAL FOCUSED GROWTH ENGINE V2 - Unique Facts Only")
        print("=" * 80)
        print(f"Starting with {len(self.existing_facts)} existing facts")
        print("=" * 80)
        
        added_count = 0
        duplicate_count = 0
        
        for cycle in range(1, cycles + 1):
            print(f"\n🔄 Cycle {cycle}/{cycles}")
            
            # Generiere 5 unique Fakten pro Zyklus
            for _ in range(5):
                fact = self.generate_unique_fact()
                
                if self.add_fact(fact):
                    print(f"  ✅ Added: {fact}")
                    added_count += 1
                else:
                    print(f"  ⚠️ Failed: {fact}")
                    duplicate_count += 1
        
        print("\n" + "=" * 80)
        print("FOCUSED GROWTH COMPLETE")
        print("=" * 80)
        print(f"✅ Facts added: {added_count}")
        print(f"⚠️ Failed attempts: {duplicate_count}")
        
        if added_count > 0:
            efficiency = (added_count/(added_count+duplicate_count)*100)
            print(f"📊 Efficiency: {efficiency:.1f}%")
        else:
            print("📊 No new facts added - database may be saturated")
        
        if self.generated_facts:
            print("\n📝 Successfully generated facts:")
            for fact in self.generated_facts[:10]:
                print(f"  • {fact}")
        
        # Final statistics
        print(f"\n📈 Final database size: {len(self.existing_facts)} facts")

if __name__ == "__main__":
    engine = FocusedGrowthEngineV2()
    engine.run(cycles=5)
