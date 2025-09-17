#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
LLM GOVERNOR INTEGRATION MODULE
================================
Integriert den LLM Governor in das HAK_GAL Backend
"""

import os
import sys
from flask import Flask, request, jsonify
from typing import Dict, Any, Optional

# Add paths
sys.path.insert(0, r"D:\MCP Mods\HAK_GAL_HEXAGONAL")
sys.path.insert(0, r"D:\MCP Mods\HAK_GAL_HEXAGONAL\src_hexagonal")

# Import LLM Governor components
try:
    from adapters.llm_governor_adapter import LLMGovernorAdapter
    from adapters.hybrid_llm_governor import HybridLLMGovernor
    LLM_GOVERNOR_AVAILABLE = True
except ImportError as e:
    print(f"[WARNING] LLM Governor not available: {e}")
    LLM_GOVERNOR_AVAILABLE = False
except Exception as e:
    print(f"[WARNING] LLM Governor import error: {e}")
    LLM_GOVERNOR_AVAILABLE = False

class LLMGovernorIntegration:
    """
    Integration layer for LLM Governor in Backend
    """
    
    def __init__(self, app: Flask = None):
        self.app = app
        self.llm_governor = None
        self.hybrid_governor = None
        self.enabled = False
        self.config = {
            'provider': 'hybrid',  # hybrid, groq, ollama, mock
            'epsilon': 0.2,
            'batch_size': 10,
            'cache_ttl': 3600
        }
        
        if LLM_GOVERNOR_AVAILABLE:
            self._initialize_governors()
    
    def _initialize_governors(self):
        """Initialize LLM Governors"""
        try:
            # Determine provider from environment
            if os.environ.get('GROQ_API_KEY'):
                provider = 'groq'
                print("[LLM Governor] Using Groq Cloud provider")
            elif os.path.exists(r"C:\Users\{}\ollama\models".format(os.environ['USERNAME'])):
                provider = 'ollama'
                print("[LLM Governor] Using Ollama local provider")
            else:
                provider = 'mock'
                print("[LLM Governor] Using Mock provider (no LLM available)")
            
            # Initialize LLM Governor
            self.llm_governor = LLMGovernorAdapter(provider=provider)
            
            # Initialize Hybrid Governor
            self.hybrid_governor = HybridLLMGovernor(
                llm_provider=provider,
                epsilon=self.config['epsilon']
            )
            
            print(f"[OK] LLM Governor initialized with {provider} provider")
            
        except Exception as e:
            print(f"[ERROR] Failed to initialize LLM Governor: {e}")
            self.llm_governor = None
            self.hybrid_governor = None
    
    def register_routes(self, app: Flask):
        """Register LLM Governor API routes"""
        self.app = app
        
        @app.route('/api/llm-governor/status', methods=['GET'])
        def llm_governor_status():
            """Get LLM Governor status"""
            return jsonify({
                'available': LLM_GOVERNOR_AVAILABLE,
                'enabled': self.enabled,
                'provider': self.config['provider'],
                'epsilon': self.config['epsilon'],
                'metrics': self.get_metrics() if self.llm_governor else {}
            })
        
        @app.route('/api/llm-governor/enable', methods=['POST'])
        def enable_llm_governor():
            """Enable LLM Governor"""
            if not LLM_GOVERNOR_AVAILABLE:
                return jsonify({'error': 'LLM Governor not available'}), 503
            
            data = request.json or {}
            
            # Update config
            if 'epsilon' in data:
                self.config['epsilon'] = float(data['epsilon'])
                if self.hybrid_governor:
                    self.hybrid_governor.epsilon = self.config['epsilon']
            
            if 'provider' in data:
                self.config['provider'] = data['provider']
                # Reinitialize with new provider
                self._initialize_governors()
            
            self.enabled = True
            
            return jsonify({
                'status': 'enabled',
                'config': self.config
            })
        
        @app.route('/api/llm-governor/disable', methods=['POST'])
        def disable_llm_governor():
            """Disable LLM Governor"""
            self.enabled = False
            return jsonify({'status': 'disabled'})
        
        @app.route('/api/llm-governor/evaluate', methods=['POST'])
        def evaluate_fact():
            """Evaluate a fact using LLM Governor"""
            if not self.enabled or not self.llm_governor:
                return jsonify({'error': 'LLM Governor not enabled'}), 503
            
            data = request.json
            if not data or 'fact' not in data:
                return jsonify({'error': 'Missing fact in request'}), 400
            
            fact = data['fact']
            domain = data.get('domain', 'general')
            
            # Use hybrid governor if available
            if self.config['provider'] == 'hybrid' and self.hybrid_governor:
                result = self.hybrid_governor.evaluate(fact, domain)
            else:
                accepted, evaluation = self.llm_governor.evaluate_fact(fact, domain)
                result = {
                    'accepted': accepted,
                    'score': evaluation.score,
                    'reasoning': evaluation.reasoning,
                    'provider': self.config['provider']
                }
            
            return jsonify(result)
        
        @app.route('/api/llm-governor/metrics', methods=['GET'])
        def get_llm_metrics():
            """Get LLM Governor metrics"""
            if not self.llm_governor:
                return jsonify({'error': 'LLM Governor not initialized'}), 503
            
            return jsonify(self.get_metrics())
        
        print("[OK] LLM Governor routes registered:")
        print("  - GET  /api/llm-governor/status")
        print("  - POST /api/llm-governor/enable")
        print("  - POST /api/llm-governor/disable")
        print("  - POST /api/llm-governor/evaluate")
        print("  - GET  /api/llm-governor/metrics")
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics"""
        if not self.llm_governor:
            return {}
        
        return self.llm_governor.get_metrics()
    
    def evaluate_batch(self, facts: list) -> list:
        """Evaluate multiple facts"""
        if not self.enabled or not self.llm_governor:
            # Fallback to accepting all
            return [True] * len(facts)
        
        if self.hybrid_governor and self.config['provider'] == 'hybrid':
            return [self.hybrid_governor.evaluate(f) for f in facts]
        else:
            results = self.llm_governor.batch_evaluate(facts)
            return [r[0] for r in results]  # Return only accepted/rejected


def integrate_llm_governor(app: Flask) -> LLMGovernorIntegration:
    """
    Main integration function to be called from hexagonal_api_enhanced_clean.py
    
    Usage:
        from llm_governor_integration import integrate_llm_governor
        
        # In create_app():
        llm_gov = integrate_llm_governor(app)
    """
    integration = LLMGovernorIntegration(app)
    integration.register_routes(app)
    return integration


if __name__ == "__main__":
    # Test integration
    from flask import Flask
    
    app = Flask(__name__)
    llm_gov = integrate_llm_governor(app)
    
    print("\n=== LLM Governor Integration Test ===")
    print(f"Available: {LLM_GOVERNOR_AVAILABLE}")
    print(f"Enabled: {llm_gov.enabled}")
    print(f"Provider: {llm_gov.config['provider']}")
    
    # Test evaluation (if available)
    if LLM_GOVERNOR_AVAILABLE:
        llm_gov.enabled = True
        test_fact = "Gravity(Earth, Acceleration, 9.81, m/s²)"
        result = llm_gov.evaluate_batch([test_fact])
        print(f"Test evaluation: {result}")
