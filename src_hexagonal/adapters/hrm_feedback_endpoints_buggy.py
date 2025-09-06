"""
HRM Feedback Endpoints Extension
=================================
Adds learning capability to HRM through human feedback
"""

def register_hrm_feedback_routes(app, feedback_adapter, reasoning_service, websocket_adapter=None):
    """
    Register HRM feedback routes for learning system.
    
    Args:
        app: Flask app instance
        feedback_adapter: HRMFeedbackAdapter instance
        reasoning_service: ReasoningService instance
    """
    from flask import jsonify, request
    
    @app.route('/api/hrm/feedback', methods=['POST', 'OPTIONS'])
    def hrm_feedback():
        """Submit feedback for HRM confidence learning."""
        if request.method == 'OPTIONS':
            return ('', 204)
        
        data = request.get_json(silent=True) or {}
        
        # Extract required fields
        query = data.get('query', '').strip()
        verification_type = data.get('type', 'positive')  # 'positive' or 'negative'
        original_confidence = data.get('confidence', 0.5)
        user_id = data.get('user_id')
        
        if not query:
            return jsonify({'error': 'Missing query'}), 400
        
        if verification_type not in ['positive', 'negative']:
            return jsonify({'error': 'Invalid verification type'}), 400
        
        # Add feedback and get updated metrics
        result = feedback_adapter.add_feedback(
            query=query,
            verification_type=verification_type,
            original_confidence=original_confidence,
            user_id=user_id
        )
        
        # Send WebSocket update if available
        if websocket_adapter and hasattr(websocket_adapter, 'emit_hrm_feedback_update'):
            websocket_adapter.emit_hrm_feedback_update(
                query=query,
                new_confidence=result.get('new_confidence', original_confidence),
                adjustment=result.get('adjustment', 0.0),
                metadata={
                    'type': verification_type,
                    'total_feedback': result.get('total_feedback', 0),
                    'learning_rate': result.get('learning_rate', 0.1)
                }
            )
        
        return jsonify({
            'success': True,
            'feedback_accepted': True,
            **result
        })
    
    @app.route('/api/hrm/confidence-adjusted', methods=['POST', 'OPTIONS'])
    def hrm_confidence_adjusted():
        """Get HRM confidence with feedback adjustments."""
        if request.method == 'OPTIONS':
            return ('', 204)
        
        data = request.get_json(silent=True) or {}
        query = data.get('query', '').strip()
        
        if not query:
            return jsonify({'error': 'Missing query'}), 400
        
        # Get base confidence from HRM
        reasoning_result = reasoning_service.reason(query)
        base_confidence = reasoning_result.confidence
        
        # Get adjusted confidence based on feedback
        adjusted_confidence, metadata = feedback_adapter.get_adjusted_confidence(
            query, base_confidence
        )
        
        return jsonify({
            'query': query,
            'base_confidence': base_confidence,
            'adjusted_confidence': adjusted_confidence,
            'adjustment': metadata['adjustment'],
            'feedback_count': metadata['feedback_count'],
            'positive_feedback': metadata['positive_feedback'],
            'negative_feedback': metadata['negative_feedback'],
            'has_learning_history': metadata['has_history'],
            'reasoning_terms': reasoning_result.reasoning_terms,
            'success': reasoning_result.success
        })
    
    @app.route('/api/hrm/feedback-stats', methods=['GET'])
    def hrm_feedback_stats():
        """Get HRM feedback statistics."""
        stats = feedback_adapter.get_statistics()
        return jsonify(stats)
    
    @app.route('/api/hrm/feedback-history', methods=['GET'])
    def hrm_feedback_history():
        """Get feedback history for a specific query."""
        query = request.args.get('query', '').strip()
        
        if not query:
            # Return overall stats if no query specified
            return jsonify(feedback_adapter.get_statistics())
        
        # Get history for specific query
        query_key = feedback_adapter._normalize_query(query)
        history = feedback_adapter.feedback_history.get(query_key, [])
        adjustment = feedback_adapter.confidence_adjustments.get(query_key, 0.0)
        
        return jsonify({
            'query': query,
            'history': history,
            'current_adjustment': adjustment,
            'feedback_count': len(history)
        })
    
    @app.route('/api/hrm/clear-old-feedback', methods=['POST'])
    def clear_old_feedback():
        """Clear old feedback data."""
        data = request.get_json(silent=True) or {}
        days = data.get('days', 30)
        
        try:
            feedback_adapter.clear_old_feedback(days)
            return jsonify({
                'success': True,
                'message': f'Cleared feedback older than {days} days'
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

# Export the registration function
__all__ = ['register_hrm_feedback_routes']
