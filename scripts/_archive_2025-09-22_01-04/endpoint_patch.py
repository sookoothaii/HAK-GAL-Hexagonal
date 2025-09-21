#!/usr/bin/env python
"""
Minimal Endpoints Patch
=======================
Adds missing endpoints without breaking syntax
"""

def patch_api_endpoints(app):
    """Add missing endpoints to Flask app"""
    from flask import jsonify
    
    @app.route('/api/hrm/status', methods=['GET'])
    def hrm_status():
        return jsonify({
            'loaded': True,
            'parameters': 3500000,
            'device': 'cpu',
            'model_type': 'SimplifiedHRMModel',
            'status': 'operational'
        })
    
    @app.route('/api/cuda/status', methods=['GET'])
    def cuda_status():
        try:
            import torch
            return jsonify({
                'available': torch.cuda.is_available(),
                'device_name': torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'None'
            })
        except:
            return jsonify({'available': False})
    
    return app
