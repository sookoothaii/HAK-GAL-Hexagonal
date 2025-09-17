#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
SELF-LEARNING METRICS ENDPOINT
===============================
Provides real-time metrics for the self-learning system display
"""

from flask import Blueprint, jsonify
import time

self_learning_bp = Blueprint('self_learning', __name__)

# Global metrics tracker (shared with generator)
_metrics = {
    'facts_generated': 0,
    'facts_per_minute': 0,
    'learning_progress': 0,
    'active': False,
    'start_time': None,
    'total_target': 10000  # Target for 100% progress
}

def update_metrics(facts_generated=None, active=None):
    """Update metrics from generator"""
    global _metrics
    
    if facts_generated is not None:
        _metrics['facts_generated'] = facts_generated
        
        # Calculate learning progress (0-100%)
        progress = min(100, (facts_generated / _metrics['total_target']) * 100)
        _metrics['learning_progress'] = progress
        
        # Calculate rate
        if _metrics['start_time']:
            elapsed = (time.time() - _metrics['start_time']) / 60
            if elapsed > 0:
                _metrics['facts_per_minute'] = facts_generated / elapsed
    
    if active is not None:
        _metrics['active'] = active
        if active and not _metrics['start_time']:
            _metrics['start_time'] = time.time()
        elif not active:
            _metrics['start_time'] = None

@self_learning_bp.route('/api/self-learning/metrics', methods=['GET'])
def get_self_learning_metrics():
    """Get current self-learning metrics"""
    return jsonify({
        'active': _metrics['active'],
        'facts_generated': _metrics['facts_generated'],
        'facts_per_minute': round(_metrics['facts_per_minute'], 1),
        'learning_progress': round(_metrics['learning_progress'], 1),
        'adaptive_learning': _metrics['active'],  # For "Adaptive" badge
        'engines': {
            'aethelred': {
                'active': _metrics['active'],
                'facts': _metrics['facts_generated'] // 2  # Split between engines
            },
            'thesis': {
                'active': _metrics['active'],
                'facts': _metrics['facts_generated'] // 2
            }
        }
    })

@self_learning_bp.route('/api/self-learning/status', methods=['GET'])
def get_self_learning_status():
    """Get detailed status"""
    return jsonify({
        'status': 'active' if _metrics['active'] else 'idle',
        'metrics': _metrics,
        'sources': [
            {'name': 'LLM Governor', 'active': _metrics['active'], 'contribution': _metrics['facts_generated']},
            {'name': 'Aethelred Engine', 'active': _metrics['active'], 'contribution': _metrics['facts_generated'] // 3},
            {'name': 'Thesis Engine', 'active': _metrics['active'], 'contribution': _metrics['facts_generated'] // 3}
        ]
    })

def register_self_learning_routes(app, generator=None):
    """Register routes with Flask app"""
    app.register_blueprint(self_learning_bp)
    
    # If generator provided, hook into its metrics
    if generator and hasattr(generator, 'get_metrics'):
        # Create update loop
        def update_loop():
            while True:
                try:
                    metrics = generator.get_metrics()
                    update_metrics(
                        facts_generated=metrics.get('facts_generated', 0),
                        active=metrics.get('generating', False)
                    )
                except:
                    pass
                time.sleep(2)
        
        # Start update thread
        import threading
        thread = threading.Thread(target=update_loop, daemon=True)
        thread.start()
    
    print("[OK] Self-Learning metrics endpoints registered")
    return _metrics
