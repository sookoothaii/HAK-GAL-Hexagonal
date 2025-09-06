#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HAK/GAL FIX 1: Add missing HRM feedback-stats route
"""

import os
import sys
from pathlib import Path
from datetime import datetime

def main():
    print("FIX 1: Adding missing HRM feedback-stats route...")
    
    api_file = Path(__file__).parent / 'src_hexagonal' / 'hexagonal_api_enhanced_clean.py'
    
    if not api_file.exists():
        print("ERROR: API file not found!")
        print(f"  Looking for: {api_file}")
        return False
    
    # Read file
    with open(api_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if route already exists
    if 'hrm_feedback_stats' in content:
        print("INFO: Route already exists!")
        return True
    
    # Find where to insert (after the last HRM route)
    search_marker = "return jsonify({'status': 'error', 'message': str(e)}), 500"
    
    # Find in hrm_model_info function
    start_pos = content.find('def hrm_model_info():')
    if start_pos == -1:
        print("ERROR: Could not find hrm_model_info function!")
        return False
        
    end_pos = content.find(search_marker, start_pos)
    if end_pos == -1:
        print("ERROR: Could not find insertion point!")
        return False
    
    # Find next empty line after the function
    insertion_point = content.find('\n\n', end_pos) + 1
    
    # The route to add
    new_route = '''
        @self.app.route('/api/hrm/feedback-stats', methods=['GET'])
        def hrm_feedback_stats():
            """Gets feedback statistics for the HRM model."""
            try:
                if hasattr(self.reasoning_engine, 'get_feedback_stats'):
                    stats = self.reasoning_engine.get_feedback_stats()
                else:
                    stats = {
                        'total_feedback': 0,
                        'positive_feedback': 0,
                        'negative_feedback': 0,
                        'accuracy_improvement': 0.0,
                        'last_training': None,
                        'model_version': getattr(self.reasoning_engine, 'version', '1.0')
                    }
                return jsonify(stats)
            except Exception as e:
                return jsonify({'status': 'error', 'message': str(e)}), 500
'''
    
    # Create backup
    backup_name = f'hexagonal_api_enhanced_clean.py.bak_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
    backup_file = api_file.parent / backup_name
    
    with open(backup_file, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"BACKUP: Created {backup_name}")
    
    # Insert new route
    new_content = content[:insertion_point] + new_route + content[insertion_point:]
    
    # Write updated file
    with open(api_file, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("SUCCESS: Route added!")
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
