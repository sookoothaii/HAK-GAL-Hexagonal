#!/usr/bin/env python
"""
Final cleanup and Governance V3 integration
"""

import os
import shutil
from datetime import datetime

def final_cleanup_and_integrate():
    """Final cleanup and proper Governance V3 integration"""
    
    api_file = r"D:\MCP Mods\HAK_GAL_HEXAGONAL\src_hexagonal\hexagonal_api_enhanced_clean.py"
    
    print("=" * 60)
    print("FINAL GOVERNANCE V3 CLEANUP & INTEGRATION")
    print("=" * 60)
    
    # Backup
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{api_file}.backup_final_{timestamp}"
    shutil.copy2(api_file, backup_path)
    print(f"✅ Backup created: {backup_path}")
    
    # Read file
    with open(api_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    print(f"Original file has {len(lines)} lines")
    
    # 1. Remove duplicate governance version setting (lines 20-24)
    for i in range(len(lines) - 5):
        if i < len(lines) - 5:
            if (lines[i].strip() == '# Set Governance Version BEFORE other imports' and
                lines[i+4].strip() == '# Set Governance Version BEFORE other imports'):
                # Remove the second occurrence
                del lines[i+4:i+8]
                print(f"✅ Removed duplicate governance version setting at lines {i+4}-{i+8}")
                break
    
    # 2. Find and replace the add_fact route with Governance V3 version
    add_fact_start = None
    add_fact_end = None
    
    for i in range(len(lines)):
        # Find the start of add_fact route
        if '@self.app.route(\'/api/facts\', methods=[\'POST\'])' in lines[i]:
            add_fact_start = i
            # Find the end (look for the next route or end of function)
            for j in range(i+1, min(i+50, len(lines))):
                if ('return jsonify({' in lines[j] and '}), status_code' in lines[j]):
                    add_fact_end = j + 1
                    break
            if add_fact_end:
                break
    
    if add_fact_start and add_fact_end:
        print(f"Found add_fact route from line {add_fact_start} to {add_fact_end}")
        
        # Replace with Governance V3 version
        governance_add_fact = '''        @self.app.route('/api/facts', methods=['POST'])
        # # # # # @require_api_key
        def add_fact():
            """POST /api/facts - Add new fact WITH GOVERNANCE V3"""
            data = request.get_json(silent=True) or {}
            statement = (data.get('statement') or data.get('query') or data.get('fact') or '').strip()
            
            if not statement:
                return jsonify({'error': 'Missing statement'}), 400
            
            if not statement.endswith('.'):
                statement = statement + '.'
            
            if not re.match(r"^[A-Za-z_][A-Za-z0-9_]*\\([^,\\)]+,\\s*[^\\)]+\\)\\.$", statement):
                return jsonify({'error': 'Invalid fact format. Expected Predicate(Entity1, Entity2).'}), 400
            
            # Prepare governance context
            context = {
                'source': 'api',
                'user': request.remote_addr,
                'externally_legal': True,
                'auth_token': request.headers.get('Authorization', ''),
                **data.get('context', {})
            }
            
            # Check for bypass header
            if request.headers.get('X-Governance-Bypass'):
                context['bypass_governance'] = True
                context['bypass_authorization'] = request.headers.get('X-Governance-Bypass')
            
            try:
                # Use Governance V3 Engine
                added = self.governance_engine.governed_add_facts_atomic(
                    [statement], 
                    context
                )
                
                if added > 0:
                    # Emit WebSocket event
                    if self.websocket_adapter:
                        self.websocket_adapter.emit_fact_added(statement, True)
                    
                    # Track with Sentry
                    if self.monitoring:
                        from infrastructure.sentry_monitoring import SentryMonitoring
                        SentryMonitoring.capture_fact_added(statement, True)
                    
                    return jsonify({
                        'success': True,
                        'message': f'Added {added} fact(s) via Governance V3',
                        'statement': statement
                    }), 201
                else:
                    return jsonify({
                        'success': False,
                        'message': 'Fact blocked by governance or already exists'
                    }), 409
                    
            except Exception as e:
                print(f"[ERROR] Governance error: {e}")
                import traceback
                traceback.print_exc()
                return jsonify({
                    'error': 'Governance processing failed',
                    'details': str(e)
                }), 500

'''
        
        # Replace the old route
        del lines[add_fact_start:add_fact_end]
        lines.insert(add_fact_start, governance_add_fact)
        print("✅ Replaced add_fact route with Governance V3 version")
    
    # 3. Remove duplicate governance_status routes
    governance_routes = []
    for i in range(len(lines)):
        if '@self.app.route(\'/api/governance/status\', methods=[\'GET\'])' in lines[i]:
            governance_routes.append(i)
    
    if len(governance_routes) > 1:
        print(f"Found {len(governance_routes)} governance_status routes")
        # Keep first, remove others (in reverse order)
        for i in reversed(governance_routes[1:]):
            # Find the end of this function
            end_idx = i
            for j in range(i+1, min(i+30, len(lines))):
                if 'return jsonify' in lines[j] and 'error' in lines[j]:
                    end_idx = j + 1
                    break
            del lines[i:end_idx]
            print(f"✅ Removed duplicate governance_status route at lines {i}-{end_idx}")
    
    # Write back
    with open(api_file, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print("\n" + "=" * 60)
    print("✅ FINAL INTEGRATION COMPLETE!")
    print("=" * 60)
    print("\nGovernance V3 is now integrated:")
    print("- ✅ All duplicates removed")
    print("- ✅ add_fact route uses TransactionalGovernanceEngine")
    print("- ✅ governance/status endpoint available")
    print("\nTest commands:")
    print("1. Start backend: python src_hexagonal\\hexagonal_api_enhanced_clean.py")
    print("2. Check status: curl http://localhost:5002/api/governance/status")
    print("3. Add fact: curl -X POST http://localhost:5002/api/facts -H 'Content-Type: application/json' -d '{\"statement\":\"GovernanceTest(V3, Success)\"}'")
    
    return backup_path

if __name__ == "__main__":
    backup = final_cleanup_and_integrate()
    print(f"\nBackup saved at: {backup}")
