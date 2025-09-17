#!/usr/bin/env python3
"""
INTELLIGENT LLM GOVERNOR WITH FACT GENERATOR
=============================================
Ersetzt den fehlerhaften SimpleFactGenerator mit dem IntelligentFactGenerator
Wird vom Frontend über "Start LLM Governor" Button aktiviert
"""

import threading
import time
import os
import sys
from typing import Dict, Any

# Import the INTELLIGENT generator statt SimpleFactGenerator
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from intelligent_fact_generator import IntelligentFactGenerator

class LLMGovernorWithGenerator:
    """LLM Governor mit intelligentem Faktengenerator"""
    
    def __init__(self):
        self.enabled = False
        self.generating = False
        self.generator_thread = None
        self.start_time = None
        
        # Verwende den INTELLIGENTEN Generator!
        self.generator = IntelligentFactGenerator()
        print("[LLM Governor] Initialisiert mit INTELLIGENTEM Faktengenerator")
        
        self.config = {
            'provider': 'intelligent',
            'epsilon': 0.1,
            'rate_per_minute': 30  # Reduziert für Qualität
        }
        
        self.metrics = {
            'facts_generated': 0,
            'facts_per_minute': 0.0,
            'last_generation': None,
            'rejected_invalid': 0,
            'duplicates': 0
        }
    
    def start(self):
        """Start LLM Governor mit intelligentem Generator"""
        if self.generating:
            return False
        
        self.enabled = True
        self.generating = True
        self.start_time = time.time()
        
        # Reset generator stats
        self.generator.stats = {
            'facts_added': 0,
            'duplicates': 0,
            'rejected_invalid': 0,
            'api_errors': 0
        }
        
        # Start generator thread
        self.generator_thread = threading.Thread(target=self._generation_loop, daemon=True)
        self.generator_thread.start()
        
        print("[LLM Governor] Gestartet mit INTELLIGENTEM Faktengenerator")
        print("[LLM Governor] Features:")
        print("  ✓ Wissenschaftliche Validierung")
        print("  ✓ Korrekte chemische Formeln")  
        print("  ✓ Ausgewogene Prädikate (NICHT 90% HasProperty)")
        print("  ✓ Sinnvolle Relationen")
        return True
    
    def stop(self):
        """Stop LLM Governor und Generator"""
        self.enabled = False
        self.generating = False
        
        if self.generator_thread:
            time.sleep(0.5)
            self.generator_thread = None
        
        # Zeige finale Statistik
        print(f"\n[LLM Governor] Gestoppt")
        print(f"  ✓ Fakten hinzugefügt: {self.generator.stats.get('facts_added', 0)}")
        print(f"  ✗ Ungültige abgelehnt: {self.generator.stats.get('rejected_invalid', 0)}")
        print(f"  ⚠ Duplikate: {self.generator.stats.get('duplicates', 0)}")
        
        return True
    
    def _generation_loop(self):
        """Hauptgenerierungsschleife mit intelligentem Generator"""
        print("[LLM Governor] Intelligente Generierung gestartet")
        
        batch_count = 0
        domains = ['chemistry', 'biology', 'physics', 'computer_science', 'mathematics']
        
        while self.generating:
            batch_count += 1
            batch_added = 0
            
            # Generiere Batch von wissenschaftlich korrekten Fakten
            for _ in range(5):
                if not self.generating:
                    break
                
                # 80% domänenspezifisch, 20% cross-domain
                if batch_count % 5 == 0:  # Jeder 5. Batch
                    fact = self.generator.generate_cross_domain_fact()
                else:
                    import random
                    domain = random.choice(domains)
                    fact = self.generator.generate_fact_from_knowledge(domain)
                
                if fact:
                    # Validiere und füge hinzu
                    if self.generator.validate_fact(fact):
                        if self.generator.add_fact_to_kb(fact):
                            batch_added += 1
                            print(f"  ✓ {fact}")
                    else:
                        self.generator.stats['rejected_invalid'] = \
                            self.generator.stats.get('rejected_invalid', 0) + 1
                    
                    # Rate limiting
                    delay = 60.0 / self.config['rate_per_minute']
                    time.sleep(delay)
            
            # Update Metriken
            self.metrics['facts_generated'] = self.generator.stats.get('facts_added', 0)
            self.metrics['rejected_invalid'] = self.generator.stats.get('rejected_invalid', 0)
            self.metrics['duplicates'] = self.generator.stats.get('duplicates', 0)
            
            if self.start_time:
                elapsed = (time.time() - self.start_time) / 60
                if elapsed > 0:
                    self.metrics['facts_per_minute'] = self.metrics['facts_generated'] / elapsed
            
            # Zeige Fortschritt alle 10 Batches
            if batch_count % 10 == 0:
                print(f"\n[LLM Governor] Fortschritt:")
                print(f"  ✓ {self.metrics['facts_generated']} Fakten hinzugefügt")
                print(f"  ✗ {self.metrics['rejected_invalid']} ungültige abgelehnt")
                print(f"  ⚠ {self.metrics['duplicates']} Duplikate")
                print(f"  📊 Rate: {self.metrics['facts_per_minute']:.1f} Fakten/Min")
            
            # Pause zwischen Batches
            if self.generating:
                time.sleep(2)
        
        print("[LLM Governor] Generierungsschleife gestoppt")
    
    def get_metrics(self) -> Dict[str, Any]:
        """Hole aktuelle Metriken"""
        learning_progress = min(100, (self.metrics['facts_generated'] / 1000) * 100) \
                          if self.metrics['facts_generated'] > 0 else 0
        
        return {
            'facts_generated': self.metrics['facts_generated'],
            'facts_per_minute': self.metrics['facts_per_minute'],
            'rejected_invalid': self.metrics['rejected_invalid'],
            'duplicates': self.metrics['duplicates'],
            'generating': self.generating,
            'enabled': self.enabled,
            'last_generation': self.metrics.get('last_generation'),
            'learning_progress': learning_progress,
            'quality_mode': 'intelligent',
            'validation_active': True
        }

def integrate_llm_governor_with_generator(app):
    """
    Integration für Flask App
    """
    llm_gov = LLMGovernorWithGenerator()
    
    # Add status endpoint
    @app.route('/api/llm-governor/status', methods=['GET'])
    def llm_governor_status():
        return {
            'available': True,
            'enabled': llm_gov.enabled,
            'generating': llm_gov.generating,
            'provider': 'intelligent',
            'metrics': llm_gov.get_metrics(),
            'features': [
                'Wissenschaftliche Validierung',
                'Korrekte Chemie/Biologie/Physik',
                'Ausgewogene Prädikate',
                'Keine HasProperty-Dominanz',
                'Cross-Domain-Verbindungen'
            ]
        }
    
    # Diese Funktion wird vom hexagonal_api_enhanced_clean.py aufgerufen
    return llm_gov

# Test
if __name__ == "__main__":
    print("="*80)
    print("TEST: INTELLIGENTER LLM GOVERNOR")
    print("="*80)
    
    gov = LLMGovernorWithGenerator()
    
    print("\nKonfiguration:")
    print(f"  Generator: IntelligentFactGenerator")
    print(f"  Validierung: Aktiv")
    print(f"  Domänen: Chemie, Biologie, Physik, Informatik, Mathematik")
    
    print("\nStarte 10-Sekunden-Test...")
    print("-"*40)
    
    gov.start()
    time.sleep(10)
    gov.stop()
    
    print("\nTest abgeschlossen!")
    print(f"Metriken: {gov.get_metrics()}")
