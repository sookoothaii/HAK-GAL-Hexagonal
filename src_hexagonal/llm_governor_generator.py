#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
LLM GOVERNOR WITH OPTIMIZED FACT GENERATOR
===========================================
Uses the optimized SimpleFactGenerator with duplicate prevention
"""

import threading
import time
import os
import sys
from typing import Dict, Any

# Import the optimized generator
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from infrastructure.engines.simple_fact_generator import SimpleFactGenerator

class LLMGovernorWithGenerator:
    """LLM Governor with optimized fact generation"""
    
    def __init__(self):
        self.enabled = False
        self.generating = False
        self.generator_thread = None
        self.start_time = None
        
        # Use the optimized SimpleFactGenerator
        self.generator = SimpleFactGenerator()
        
        self.config = {
            'provider': 'groq',
            'epsilon': 0.1,
            'rate_per_minute': 60  # Increased rate
        }
        
        self.metrics = {
            'facts_generated': 0,
            'facts_per_minute': 0.0,
            'last_generation': None,
            'duplicates_prevented': 0
        }
    
    def start(self):
        """Start LLM Governor and optimized Fact Generator"""
        if self.generating:
            return False
        
        self.enabled = True
        self.generating = True
        self.start_time = time.time()
        
        # Reset generator stats
        self.generator.stats = {
            'facts_added': 0,
            'duplicates_prevented': 0,
            'api_errors': 0,
            'predicate_counts': {}
        }
        
        # Start generator thread
        self.generator_thread = threading.Thread(target=self._generation_loop, daemon=True)
        self.generator_thread.start()
        
        print("[LLM Governor] Started with OPTIMIZED fact generation")
        print("[LLM Governor] Features: Duplicate prevention, Balanced predicates (HasProperty ≤20%)")
        return True
    
    def stop(self):
        """Stop LLM Governor and Generator"""
        self.enabled = False
        self.generating = False
        
        if self.generator_thread:
            time.sleep(0.5)
            self.generator_thread = None
        
        # Show final statistics
        print(f"\n[LLM Governor] Stopped")
        print(f"  Facts added: {self.generator.stats['facts_added']}")
        print(f"  Duplicates prevented: {self.generator.stats['duplicates_prevented']}")
        
        # Show predicate distribution
        if self.generator.stats['predicate_counts']:
            print("\n  Predicate distribution:")
            total = sum(self.generator.stats['predicate_counts'].values())
            for pred, count in sorted(self.generator.stats['predicate_counts'].items(), 
                                     key=lambda x: -x[1])[:5]:
                pct = (count / total) * 100 if total > 0 else 0
                print(f"    {pred:20s}: {count:4d} ({pct:5.1f}%)")
        
        return True
    
    def _generation_loop(self):
        """Main generation loop using optimized generator"""
        print("[LLM Governor] Optimized generation loop started")
        
        batch_count = 0
        
        while self.generating:
            # Generate batch of unique facts
            batch_size = 10
            batch_added = 0
            
            for _ in range(batch_size):
                if not self.generating:
                    break
                
                # Generate unique fact with balanced predicates
                fact, metadata = self.generator.generate_fact()
                
                if fact:
                    # Add to KB
                    if self.generator.add_fact(fact):
                        batch_added += 1
                    
                    # Small delay for rate limiting
                    delay = 60.0 / self.config['rate_per_minute'] / batch_size
                    time.sleep(delay)
            
            batch_count += 1
            
            # Update metrics
            self.metrics['facts_generated'] = self.generator.stats['facts_added']
            self.metrics['duplicates_prevented'] = self.generator.stats['duplicates_prevented']
            
            if self.start_time:
                elapsed = (time.time() - self.start_time) / 60
                if elapsed > 0:
                    self.metrics['facts_per_minute'] = self.metrics['facts_generated'] / elapsed
            
            # Show progress every 10 batches
            if batch_count % 10 == 0:
                print(f"[LLM Governor] Progress: {self.metrics['facts_generated']} facts, "
                      f"{self.metrics['duplicates_prevented']} duplicates prevented, "
                      f"{self.metrics['facts_per_minute']:.1f} facts/min")
                
                # Check HasProperty percentage
                if self.generator.stats['predicate_counts']:
                    total = sum(self.generator.stats['predicate_counts'].values())
                    has_prop = self.generator.stats['predicate_counts'].get('HasProperty', 0)
                    has_prop_pct = (has_prop / total) * 100 if total > 0 else 0
                    
                    if has_prop_pct > 25:
                        print(f"[WARNING] HasProperty at {has_prop_pct:.1f}% (target: ≤20%)")
            
            # Pause between batches
            if self.generating:
                time.sleep(1)
        
        print("[LLM Governor] Generation loop stopped")
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics"""
        learning_progress = min(100, (self.metrics['facts_generated'] / 10000) * 100) \
                          if self.metrics['facts_generated'] > 0 else 0
        
        # Calculate HasProperty percentage
        has_property_pct = 0
        if self.generator.stats['predicate_counts']:
            total = sum(self.generator.stats['predicate_counts'].values())
            has_prop = self.generator.stats['predicate_counts'].get('HasProperty', 0)
            has_property_pct = (has_prop / total) * 100 if total > 0 else 0
        
        return {
            'facts_generated': self.metrics['facts_generated'],
            'facts_per_minute': self.metrics['facts_per_minute'],
            'duplicates_prevented': self.metrics['duplicates_prevented'],
            'generating': self.generating,
            'enabled': self.enabled,
            'last_generation': self.metrics.get('last_generation'),
            'learning_progress': learning_progress,
            'has_property_percentage': has_property_pct,
            'predicate_diversity': len(self.generator.stats['predicate_counts'])
        }

def integrate_llm_governor_with_generator(app):
    """
    Integration function for Flask app
    """
    llm_gov = LLMGovernorWithGenerator()
    
    # Add status endpoint
    @app.route('/api/llm-governor/status', methods=['GET'])
    def llm_governor_status():
        return {
            'available': True,
            'enabled': llm_gov.enabled,
            'generating': llm_gov.generating,
            'provider': llm_gov.config['provider'],
            'metrics': llm_gov.get_metrics(),
            'optimized': True,
            'features': [
                'Duplicate prevention',
                'Balanced predicates',
                'HasProperty ≤20%',
                'Extended entity pools'
            ]
        }
    
    # Extend the existing governor/start endpoint
    original_governor_start = None
    for rule in app.url_map.iter_rules():
        if rule.rule == '/api/governor/start':
            original_governor_start = app.view_functions[rule.endpoint]
            break
    
    def enhanced_governor_start():
        """Enhanced governor start with optimized generator"""
        from flask import request, jsonify
        
        data = request.get_json(silent=True) or {}
        use_llm = data.get('use_llm', False)
        
        if use_llm:
            # Start the LLM Governor with optimized generator
            success = llm_gov.start()
            if success:
                print("[API] Started LLM Governor with OPTIMIZED fact generation")
                return jsonify({
                    'success': True,
                    'mode': 'llm_governor_generator_optimized',
                    'provider': llm_gov.config['provider'],
                    'generating': True,
                    'optimized': True,
                    'message': 'LLM Governor started with optimized fact generation (HasProperty ≤20%, no duplicates)'
                })
        
        # Fallback to original implementation
        if original_governor_start:
            return original_governor_start()
        else:
            return jsonify({'success': False, 'error': 'Original governor not found'})
    
    # Replace the endpoint
    app.view_functions['governor_start'] = enhanced_governor_start
    
    # Add stop enhancement
    original_governor_stop = None
    for rule in app.url_map.iter_rules():
        if rule.rule == '/api/governor/stop':
            original_governor_stop = app.view_functions[rule.endpoint]
            break
    
    def enhanced_governor_stop():
        """Enhanced governor stop"""
        from flask import jsonify
        
        # Stop the generator
        llm_gov.stop()
        
        # Call original if exists
        if original_governor_stop:
            return original_governor_stop()
        else:
            return jsonify({'success': True})
    
    app.view_functions['governor_stop'] = enhanced_governor_stop
    
    print("[OK] OPTIMIZED LLM Governor with Generator integrated")
    print("[OK] Features: Duplicate prevention, Balanced predicates (HasProperty ≤20%)")
    return llm_gov

# Test function
if __name__ == "__main__":
    print("Testing OPTIMIZED LLM Governor with Generator...")
    gov = LLMGovernorWithGenerator()
    
    # Show configuration
    print(f"\nOptimized Generator Configuration:")
    print(f"  Predicates: {len(gov.generator.predicates)} balanced types")
    print(f"  HasProperty weight: {gov.generator.predicates['HasProperty']*100:.0f}% (was 80%)")
    print(f"  Duplicate prevention: Active")
    
    # Test generation
    for i in range(5):
        fact, metadata = gov.generator.generate_fact()
        if fact:
            print(f"\nTest fact {i+1}:")
            print(f"  {fact}")
            print(f"  Predicate: {metadata['predicate']}, Domain: {metadata['domain']}")
    
    print("\n" + "="*60)
    print("Starting 10-second generation test...")
    print("="*60)
    
    # Test start/stop
    gov.start()
    time.sleep(10)
    gov.stop()
    
    print(f"\nTest complete!")
