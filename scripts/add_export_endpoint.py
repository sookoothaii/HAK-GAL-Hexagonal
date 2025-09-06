#!/usr/bin/env python3
"""
Add export endpoint to hexagonal API for v6_autopilot
"""

import sys
from pathlib import Path

api_file = Path("D:/MCP Mods/HAK_GAL_HEXAGONAL/src_hexagonal/hexagonal_api_enhanced_clean.py")
content = api_file.read_text(encoding='utf-8')

# Add export endpoint after the existing /api/facts endpoints
export_endpoint = '''
        @self.app.route('/api/facts/export', methods=['GET'])
        def export_facts():
            """Export facts for autopilot/boosting"""
            limit = request.args.get('limit', 100, type=int)
            format_type = request.args.get('format', 'json')
            
            facts = self.fact_service.get_all_facts(limit)
            
            if format_type == 'json':
                return jsonify({
                    'facts': [{'statement': f.statement} for f in facts],
                    'count': len(facts)
                })
            else:
                # Plain text format
                return '\\n'.join([f.statement for f in facts]), 200, {'Content-Type': 'text/plain'}
'''

# Find position after /api/facts/count endpoint
if '/api/facts/export' not in content:
    # Find the line with facts_count function
    marker = "return jsonify({'count': count_val, 'cached': False, 'ttl_sec': 30})"
    if marker in content:
        # Insert after the facts_count function
        pos = content.find(marker) + len(marker)
        # Find the next line break
        next_newline = content.find('\n', pos)
        if next_newline != -1:
            content = content[:next_newline+1] + export_endpoint + content[next_newline+1:]
            
            # Save with backup
            api_file.rename(api_file.with_suffix('.py.backup_export'))
            api_file.write_text(content, encoding='utf-8')
            print("✅ Export endpoint added to API")
            print("Restart backend to apply changes")
    else:
        print("⚠️ Could not find insertion point")
else:
    print("✅ Export endpoint already exists")
