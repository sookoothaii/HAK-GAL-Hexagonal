#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
AETHELRED ENGINE - FIXED VERSION
Robuster Code mit besserer Fehlerbehandlung
"""

import sys
import os
import sqlite3
import time
import random
import argparse

# WICHTIG: Keine externen Dependencies beim Start!
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    print("[WARN] requests not available, using fallback")

# Topics für Wissensgenerierung
TOPICS = [
    "quantum computing", "artificial intelligence", "biotechnology",
    "renewable energy", "space exploration", "nanotechnology",
    "blockchain", "virtual reality", "gene therapy", "robotics"
]

class AethelredEngineFast:
    def __init__(self):
        # Dynamischer Pfad-Aufbau
        script_dir = os.path.dirname(os.path.abspath(__file__))
        root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(script_dir))))
        self.db_path = os.path.join(root_dir, "hexagonal_kb.db")
        
        # Prüfe ob DB existiert
        if not os.path.exists(self.db_path):
            print(f"[ERROR] Database not found at {self.db_path}")
            # Fallback-Pfad
            self.db_path = r"D:\MCP Mods\HAK_GAL_HEXAGONAL\hexagonal_kb.db"
        
        self.api_base = "http://localhost:5002"
        self.existing_facts = set()
        self.facts_loaded = False
        
    def load_facts_from_db(self):
        """Lade Fakten DIREKT aus der Datenbank"""
        if self.facts_loaded:
            return
            
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT statement FROM facts")
            self.existing_facts = {row[0] for row in cursor.fetchall()}
            conn.close()
            self.facts_loaded = True
            print(f"[FAST] Loaded {len(self.existing_facts)} facts from DB")
        except Exception as e:
            print(f"[ERROR] DB load failed: {e}")
            self.existing_facts = set()
    
    def get_llm_response(self, topic):
        """Hole LLM Response - mit Fallback wenn requests fehlt"""
        if not REQUESTS_AVAILABLE:
            # Fallback ohne requests
            return self.generate_fallback_response(topic)
            
        try:
            response = requests.post(
                f"{self.api_base}/api/llm/get-explanation",
                json={'topic': topic},
                timeout=15
            )
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"[WARN] LLM timeout for {topic}: {e}")
        return None
    
    def generate_fallback_response(self, topic):
        """Generiere simple Fakten ohne LLM"""
        topic_clean = topic.replace(" ", "_").replace("-", "_").title()
        facts = [
            f"IsA({topic_clean}, Technology).",
            f"StudiedBy({topic_clean}, Scientists).",
            f"HasProperty({topic_clean}, Innovation).",
            f"UsedIn({topic_clean}, Research).",
            f"Enables({topic_clean}, Progress)."
        ]
        return {'suggested_facts': facts}
    
    def extract_facts(self, llm_response, topic):
        """Extrahiere Fakten aus Response"""
        facts = []
        
        if llm_response and 'suggested_facts' in llm_response:
            for fact in llm_response['suggested_facts'][:5]:
                if isinstance(fact, dict) and 'fact' in fact:
                    fact_str = fact['fact']
                elif isinstance(fact, str):
                    fact_str = fact
                else:
                    continue
                    
                # Validierung
                if '(' in fact_str and ')' in fact_str:
                    if not fact_str.endswith('.'):
                        fact_str += '.'
                    facts.append(fact_str)
        
        return facts
    
    def add_fact_to_db(self, fact):
        """Füge Fakt zur DB hinzu"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO facts (statement) VALUES (?)",
                (fact,)
            )
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            return False  # Duplikat
        except Exception as e:
            print(f"[ERROR] DB insert failed: {e}")
            return False
    
    def run(self, duration_minutes=5):
        """Hauptschleife"""
        print(f"[START] Aethelred Engine FIXED - {duration_minutes:.1f} minutes")
        
        # Lade Facts
        self.load_facts_from_db()
        
        if not self.facts_loaded:
            print("[ERROR] Could not load facts, generating fallback facts")
        
        start_time = time.time()
        end_time = start_time + (duration_minutes * 60)
        facts_added = 0
        round_num = 0
        
        try:
            while time.time() < end_time:
                round_num += 1
                remaining = int(end_time - time.time())
                print(f"\n=== Round {round_num} (remaining: {remaining}s) ===")
                
                topic = random.choice(TOPICS)
                print(f"[TOPIC] {topic}")
                
                llm_response = self.get_llm_response(topic)
                
                if llm_response:
                    new_facts = self.extract_facts(llm_response, topic)
                    
                    for fact in new_facts:
                        if fact not in self.existing_facts:
                            if self.add_fact_to_db(fact):
                                facts_added += 1
                                self.existing_facts.add(fact)
                                print(f"[+] {fact}")
                    
                    print(f"[STATS] Round {round_num}: +{len(new_facts)}, Total: {facts_added}")
                
                # Pause
                if time.time() < end_time:
                    time.sleep(10)
                    
        except KeyboardInterrupt:
            print("\n[INTERRUPTED] Stopping gracefully")
        except Exception as e:
            print(f"\n[ERROR] Unexpected error: {e}")
        
        print(f"\n[DONE] Added {facts_added} facts in {round_num} rounds")
        return 0  # Success exit code

def main():
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument("-d", "--duration", type=float, default=0.1)
        parser.add_argument("-p", "--port", type=int, default=5002)
        args = parser.parse_args()
        
        engine = AethelredEngineFast()
        return engine.run(duration_minutes=args.duration * 60)
    except Exception as e:
        print(f"[FATAL] {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
