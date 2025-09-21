#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
THESIS ENGINE ENHANCED - Vollständiges Thesen-System
===================================================
1. Generiert logische Thesen aus Aethelred-Fakten
2. Validiert Thesen mit LLM-Hilfe
3. Speichert bewiesene Thesen als neues Wissen
"""

import sys
import os
import sqlite3
import time
import random
import argparse
from typing import List, Dict
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from thesis_thesis_generator import ThesisGenerator
from thesis_llm_proof_validator import ThesisLLMProofValidator

class ThesisEngineEnhanced:
    """Vollständiges Thesen-System"""
    
    def __init__(self):
        self.db_path = r"D:\MCP Mods\HAK_GAL_HEXAGONAL\hexagonal_kb.db"
        self.generator = ThesisGenerator()
        self.validator = ThesisLLMProofValidator()
        
    def get_thesis_statistics(self) -> Dict:
        """Hole Statistiken über Thesen"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Thesen nach Status
            cursor.execute("SELECT status, COUNT(*) FROM theses GROUP BY status")
            status_counts = dict(cursor.fetchall())
            
            # Beweise nach Status
            cursor.execute("SELECT proof_status, COUNT(*) FROM thesis_proofs GROUP BY proof_status")
            proof_counts = dict(cursor.fetchall())
            
            # Gesamtstatistiken
            cursor.execute("SELECT COUNT(*) FROM theses")
            total_theses = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM thesis_proofs")
            total_proofs = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                'total_theses': total_theses,
                'total_proofs': total_proofs,
                'thesis_status': status_counts,
                'proof_status': proof_counts
            }
            
        except Exception as e:
            print(f"[ERROR] Failed to get statistics: {e}")
            return {}
    
    def promote_proven_theses_to_facts(self) -> int:
        """Promote bewiesene Thesen zu Fakten"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Hole bewiesene Thesen
            cursor.execute("""
                SELECT t.id, t.statement, tp.confidence, tp.proof_text
                FROM theses t
                JOIN thesis_proofs tp ON t.id = tp.thesis_id
                WHERE tp.proof_status = 'proven' AND t.status = 'proven'
            """)
            
            proven_theses = cursor.fetchall()
            promoted_count = 0
            
            for thesis_id, statement, confidence, proof_text in proven_theses:
                # Konvertiere These zu Fakt-Format
                fact_statement = self.convert_thesis_to_fact(statement, confidence)
                
                if fact_statement:
                    try:
                        # Füge als Fakt hinzu
                        cursor.execute("INSERT INTO facts (statement, created_at) VALUES (?, ?)", 
                                     (fact_statement, datetime.now().isoformat()))
                        promoted_count += 1
                        print(f"[PROMOTE] {fact_statement}")
                        
                    except sqlite3.IntegrityError:
                        continue  # Duplikat
            
            conn.commit()
            conn.close()
            
            print(f"[PROMOTE] Promoted {promoted_count} proven theses to facts")
            return promoted_count
            
        except Exception as e:
            print(f"[ERROR] Failed to promote theses: {e}")
            return 0
    
    def convert_thesis_to_fact(self, thesis_statement: str, confidence: float) -> str:
        """Konvertiere These zu Fakt-Format"""
        # Vereinfache These zu Fakt
        # Z.B. "Entities with X often also have Y" -> "Correlates(X, Y)"
        
        if "often also have" in thesis_statement.lower():
            # Extrahiere X und Y aus "Entities with X often also have Y"
            import re
            match = re.search(r'with (\w+) often also have (\w+)', thesis_statement.lower())
            if match:
                x, y = match.groups()
                return f"Correlates({x}, {y})."
        
        elif "most" in thesis_statement.lower() and "have" in thesis_statement.lower():
            # Extrahiere aus "Most X entities have Y"
            match = re.search(r'most (\w+) entities have (\w+)', thesis_statement.lower())
            if match:
                entity_type, property = match.groups()
                return f"HasProperty({entity_type}, {property})."
        
        elif "connected to" in thesis_statement.lower():
            # Extrahiere aus "Entities connected to X often have Y"
            match = re.search(r'connected to (\w+) often have (\w+)', thesis_statement.lower())
            if match:
                entity, property = match.groups()
                return f"NetworkProperty({entity}, {property})."
        
        # Fallback: Generiere allgemeinen Fakt
        if confidence > 0.7:
            return f"ValidatedThesis({thesis_statement[:50]}, HighConfidence)."
        else:
            return f"ValidatedThesis({thesis_statement[:50]}, ModerateConfidence)."
    
    def run_generation_phase(self, duration_minutes: float = 1.0):
        """Führe Thesen-Generierung durch"""
        print(f"[PHASE 1] Thesis Generation - {duration_minutes} minutes")
        self.generator.run(duration_minutes=duration_minutes)
    
    def run_validation_phase(self, duration_minutes: float = 2.0):
        """Führe Thesen-Validierung durch"""
        print(f"[PHASE 2] Thesis Validation - {duration_minutes} minutes")
        self.validator.run(duration_minutes=duration_minutes)
    
    def run_promotion_phase(self):
        """Führe Promotion bewiesener Thesen durch"""
        print("[PHASE 3] Promoting proven theses to facts")
        promoted_count = self.promote_proven_theses_to_facts()
        return promoted_count
    
    def run(self, duration_minutes: float = 3.0):
        """Vollständiger Thesen-Workflow"""
        print(f"[START] Thesis Engine Enhanced - {duration_minutes} minutes")
        print("[INFO] Complete thesis workflow: Generate -> Validate -> Promote")
        
        start_time = time.time()
        end_time = start_time + (duration_minutes * 60)
        
        # Zeige initiale Statistiken
        stats = self.get_thesis_statistics()
        print(f"[INITIAL] Theses: {stats.get('total_theses', 0)}, Proofs: {stats.get('total_proofs', 0)}")
        
        while time.time() < end_time:
            print(f"\n=== Thesis Workflow Cycle ===")
            
            # Phase 1: Thesen-Generierung (30% der Zeit)
            generation_time = (end_time - time.time()) * 0.3
            if generation_time > 30:  # Mindestens 30 Sekunden
                self.run_generation_phase(generation_time / 60)
            
            # Phase 2: Thesen-Validierung (50% der Zeit)
            validation_time = (end_time - time.time()) * 0.5
            if validation_time > 60:  # Mindestens 1 Minute
                self.run_validation_phase(validation_time / 60)
            
            # Phase 3: Promotion (20% der Zeit)
            self.run_promotion_phase()
            
            # Zeige aktuelle Statistiken
            stats = self.get_thesis_statistics()
            print(f"[STATS] Theses: {stats.get('total_theses', 0)}, Proofs: {stats.get('total_proofs', 0)}")
            print(f"[STATS] Thesis Status: {stats.get('thesis_status', {})}")
            print(f"[STATS] Proof Status: {stats.get('proof_status', {})}")
            
            # Pause zwischen Zyklen
            if time.time() < end_time:
                time.sleep(30)
        
        # Finale Statistiken
        final_stats = self.get_thesis_statistics()
        print(f"\n[FINAL] Theses: {final_stats.get('total_theses', 0)}")
        print(f"[FINAL] Proofs: {final_stats.get('total_proofs', 0)}")
        print(f"[FINAL] Proven: {final_stats.get('proof_status', {}).get('proven', 0)}")
        print(f"[FINAL] Disproven: {final_stats.get('proof_status', {}).get('disproven', 0)}")
        print("[INFO] Thesis workflow completed")

def main():
    parser = argparse.ArgumentParser(description="Enhanced Thesis Engine")
    parser.add_argument("-d", "--duration", type=float, default=0.1, help="Duration in minutes")
    parser.add_argument("-p", "--port", type=int, default=5002, help="Port (unused)")
    args = parser.parse_args()
    
    engine = ThesisEngineEnhanced()
    engine.run(duration_minutes=args.duration)

if __name__ == "__main__":
    main()







