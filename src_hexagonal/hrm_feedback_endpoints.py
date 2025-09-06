"""
HAK-GAL HRM Feedback Endpoints
===============================
Implements missing HRM feedback and verification endpoints
"""

from flask import jsonify, request
import json
import time
from pathlib import Path
from typing import Dict, Any, Optional

def register_hrm_feedback_endpoints(app, fact_repository, reasoning_engine):
    """Register HRM feedback and verification endpoints"""
    
    # Ensure feedback data directory exists
    feedback_path = Path(__file__).parent.parent / 'data'
    feedback_path.mkdir(exist_ok=True)
    feedback_file = feedback_path / 'hrm_feedback.json'
    
    def load_feedback_data() -> Dict[str, Any]:
        """Load feedback data from persistent storage"""
        if feedback_file.exists():
            try:
                with open(feedback_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"[ERROR] Loading feedback data: {e}")
        
        # Default structure
        return {
            'history': {},
            'adjustments': {},
            'statistics': {
                'total_feedback': 0,
                'positive_feedback': 0,
                'negative_feedback': 0
            }
        }
    
    def save_feedback_data(data: Dict[str, Any]):
        """Save feedback data to persistent storage"""
        try:
            with open(feedback_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"[ERROR] Saving feedback data: {e}")
    
    @app.route('/api/hrm/feedback', methods=['POST', 'OPTIONS'])
    def hrm_feedback():
        """POST /api/hrm/feedback - Provide feedback for HRM reasoning"""
        if request.method == 'OPTIONS':
            return ('', 204)
        
        try:
            data = request.get_json(silent=True) or {}
            query = data.get('query', '').strip()
            feedback_type = data.get('type', '').lower()  # 'positive' or 'negative'
            confidence_adjustment = data.get('confidence_adjustment', 0.0)
            
            if not query:
                return jsonify({'error': 'Missing query parameter'}), 400
            
            if feedback_type not in ['positive', 'negative']:
                return jsonify({'error': 'Invalid feedback type. Use "positive" or "negative"'}), 400
            
            # Load existing feedback data
            feedback_data = load_feedback_data()
            
            # Initialize query history if not exists
            if query not in feedback_data['history']:
                feedback_data['history'][query] = {
                    'positive_count': 0,
                    'negative_count': 0,
                    'last_feedback': None,
                    'confidence_adjustments': []
                }
            
            # Update feedback counts
            if feedback_type == 'positive':
                feedback_data['history'][query]['positive_count'] += 1
                feedback_data['statistics']['positive_feedback'] += 1
            else:
                feedback_data['history'][query]['negative_count'] += 1
                feedback_data['statistics']['negative_feedback'] += 1
            
            feedback_data['statistics']['total_feedback'] += 1
            feedback_data['history'][query]['last_feedback'] = time.time()
            
            # Calculate confidence adjustment based on feedback type
            if feedback_type == 'positive':
                # Positive feedback increases confidence by 6%
                confidence_adjustment = 0.06 if confidence_adjustment == 0.0 else confidence_adjustment
            else:
                # Negative feedback decreases confidence by 6%
                confidence_adjustment = -0.06 if confidence_adjustment == 0.0 else -abs(confidence_adjustment)
            
            # Record confidence adjustment
            feedback_data['history'][query]['confidence_adjustments'].append({
                'timestamp': time.time(),
                'adjustment': confidence_adjustment,
                'type': feedback_type
            })
            
            # ALWAYS update active adjustments (this was the bug!)
            if 'adjustments' not in feedback_data:
                feedback_data['adjustments'] = {}
            
            # Calculate feedback ratio
            positive = feedback_data['history'][query]['positive_count']
            negative = feedback_data['history'][query]['negative_count']
            total = positive + negative
            feedback_ratio = positive / max(1, total)
            
            # Save adjustment settings
            feedback_data['adjustments'][query] = {
                'base_adjustment': abs(confidence_adjustment),
                'feedback_ratio': feedback_ratio,
                'updated_at': time.time()
            }
            
            # Save updated feedback data
            save_feedback_data(feedback_data)
            
            # If using NativeReasoningEngine, apply feedback directly
            if hasattr(reasoning_engine, 'apply_feedback'):
                reasoning_engine.apply_feedback(query, feedback_type, abs(confidence_adjustment))
            
            return jsonify({
                'success': True,
                'message': f'Feedback recorded for query: {query}',
                'query': query,
                'feedback_type': feedback_type,
                'total_positive': feedback_data['history'][query]['positive_count'],
                'total_negative': feedback_data['history'][query]['negative_count']
            })
            
        except Exception as e:
            print(f"[ERROR] HRM feedback error: {e}")
            return jsonify({
                'error': 'Failed to process feedback',
                'details': str(e)
            }), 500
    
    @app.route('/api/feedback/verify', methods=['POST', 'OPTIONS'])
    def verify_query():
        """POST /api/feedback/verify - Verify a query and mark it as validated"""
        if request.method == 'OPTIONS':
            return ('', 204)
        
        try:
            data = request.get_json(silent=True) or {}
            query = data.get('query', '').strip()
            verified = data.get('verified', True)
            confidence_override = data.get('confidence_override', None)
            
            if not query:
                return jsonify({'error': 'Missing query parameter'}), 400
            
            # Load feedback data
            feedback_data = load_feedback_data()
            
            # Create verified queries section if not exists
            if 'verified_queries' not in feedback_data:
                feedback_data['verified_queries'] = {}
            
            # Record verification
            feedback_data['verified_queries'][query] = {
                'verified': verified,
                'confidence_override': confidence_override,
                'verified_at': time.time(),
                'verifier': data.get('verifier', 'system')
            }
            
            # If query has history, update it
            if query in feedback_data['history']:
                feedback_data['history'][query]['verified'] = verified
                feedback_data['history'][query]['verified_at'] = time.time()
            
            # Save updated data
            save_feedback_data(feedback_data)
            
            # Try to persist to database if available
            if hasattr(fact_repository, 'add_verified_query'):
                fact_repository.add_verified_query(query, verified, confidence_override)
            
            return jsonify({
                'success': True,
                'message': f'Query {"verified" if verified else "marked as invalid"}',
                'query': query,
                'verified': verified,
                'confidence_override': confidence_override
            })
            
        except Exception as e:
            print(f"[ERROR] Verify query error: {e}")
            return jsonify({
                'error': 'Failed to verify query',
                'details': str(e)
            }), 500
    
    @app.route('/api/hrm/feedback/history', methods=['GET', 'OPTIONS'])
    def get_feedback_history():
        """GET /api/hrm/feedback/history - Get feedback history for queries"""
        if request.method == 'OPTIONS':
            return ('', 204)
        
        try:
            query = request.args.get('query', '').strip()
            limit = request.args.get('limit', 100, type=int)
            
            feedback_data = load_feedback_data()
            
            if query:
                # Return history for specific query
                if query in feedback_data['history']:
                    return jsonify({
                        'query': query,
                        'history': feedback_data['history'][query],
                        'adjustment': feedback_data['adjustments'].get(query, None)
                    })
                else:
                    return jsonify({
                        'query': query,
                        'history': None,
                        'message': 'No feedback history for this query'
                    })
            else:
                # Return all history (limited)
                histories = sorted(
                    feedback_data['history'].items(),
                    key=lambda x: x[1].get('last_feedback', 0),
                    reverse=True
                )[:limit]
                
                return jsonify({
                    'histories': dict(histories),
                    'total': len(feedback_data['history']),
                    'statistics': feedback_data['statistics']
                })
                
        except Exception as e:
            print(f"[ERROR] Get feedback history error: {e}")
            return jsonify({
                'error': 'Failed to retrieve feedback history',
                'details': str(e)
            }), 500
    
    @app.route('/api/hrm/adjustments', methods=['GET', 'OPTIONS'])
    def get_confidence_adjustments():
        """GET /api/hrm/adjustments - Get active confidence adjustments"""
        if request.method == 'OPTIONS':
            return ('', 204)
        
        try:
            feedback_data = load_feedback_data()
            
            # Sort adjustments by update time
            adjustments = sorted(
                feedback_data['adjustments'].items(),
                key=lambda x: x[1].get('updated_at', 0),
                reverse=True
            )
            
            return jsonify({
                'adjustments': dict(adjustments),
                'total': len(adjustments)
            })
            
        except Exception as e:
            print(f"[ERROR] Get adjustments error: {e}")
            return jsonify({
                'error': 'Failed to retrieve adjustments',
                'details': str(e)
            }), 500
    
    print("[OK] HRM Feedback endpoints registered:")
    print("  - POST /api/hrm/feedback")
    print("  - POST /api/feedback/verify")
    print("  - GET /api/hrm/feedback/history")
    print("  - GET /api/hrm/adjustments")
