#!/usr/bin/env python
"""
Governance V3 Integration Script for HAK_GAL_HEXAGONAL Backend
This script patches the existing hexagonal_api_enhanced_clean.py
"""

import os
import sys
import shutil
from datetime import datetime

def backup_file(filepath):
    """Create backup of file before modification"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{filepath}.backup_{timestamp}"
    shutil.copy2(filepath, backup_path)
    print(f"✅ Backup created: {backup_path}")
    return backup_path

def integrate_governance_v3():
    """Integrate Governance V3 into the backend"""
    
    # Target file
    api_file = r"D:\MCP Mods\HAK_GAL_HEXAGONAL\src_hexagonal\hexagonal_api_enhanced_clean.py"
    
    print("="*60)
    print("GOVERNANCE V3 INTEGRATION - OPTION A")
    print("="*60)
    
    # Create backup
    backup_path = backup_file(api_file)
    
    # Read the file
    with open(api_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    print("\n📝 Modifying backend code...")
    
    # Find positions for insertions
    import_position = None
    init_position = None
    route_start = None
    route_end = None
    
    for i, line in enumerate(lines):
        # Find where to add governance import (after eventlet patching)
        if 'eventlet.monkey_patch()' in line and import_position is None:
            import_position = i + 2  # After the print statement
        
        # Find where to add other imports (after other imports)
        if 'from src_hexagonal.llm_config_routes import' in line:
            other_imports_position = i + 1
        
        # Find where to initialize governance (in __init__)
        if 'self.reasoning_engine = NativeReasoningEngine()' in line:
            init_position = i + 1
        
        # Find the add_fact route to replace
        if '@self.app.route(\'/api/facts\', methods=[\'POST\'])' in line:
            route_start = i
        
        # Find the end of add_fact function
        if route_start and 'return jsonify' in line and 'status_code' in lines[i]:
            route_end = i + 1
    
    # Insert governance version setting after eventlet
    if import_position:
        lines.insert(import_position, "\n# Set Governance Version BEFORE other imports\n")
        lines.insert(import_position + 1, "import os\n")
        lines.insert(import_position + 2, "os.environ.setdefault('GOVERNANCE_VERSION', 'v3')\n")
        lines.insert(import_position + 3, "print(f\"[INFO] Governance Version: {os.environ.get('GOVERNANCE_VERSION')}\")\n")
        lines.insert(import_position + 4, "\n")
        print("✅ Added Governance version setting")
    
    # Insert governance imports
    if other_imports_position:
        # Adjust for previous insertions
        other_imports_position += 5
        lines.insert(other_imports_position, "from src_hexagonal.application.transactional_governance_engine import TransactionalGovernanceEngine\n")
        lines.insert(other_imports_position + 1, "from src_hexagonal.application.governance_monitor import probe_sqlite\n")
        lines.insert(other_imports_position + 2, "\n")
        print("✅ Added Governance imports")
    
    # Initialize governance engine
    if init_position:
        # Adjust for previous insertions
        init_position += 8
        lines.insert(init_position, "\n        # Initialize Governance V3\n")
        lines.insert(init_position + 1, "        self.governance_engine = TransactionalGovernanceEngine()\n")
        lines.insert(init_position + 2, "        print(f\"[OK] Governance {os.environ.get('GOVERNANCE_VERSION')} initialized\")\n")
        lines.insert(init_position + 3, "        print(f\"[OK] Policy enforcement: {os.environ.get('POLICY_ENFORCE', 'observe')}\")\n")
        lines.insert(init_position + 4, "        print(f\"[OK] Bypass mode: {os.environ.get('GOVERNANCE_BYPASS', 'false')}\")\n")
        print("✅ Added Governance initialization")
    
    # Replace add_fact route
    if route_start and route_end:
        # Adjust for previous insertions
        route_start += 13
        route_end += 13
        
        new_route = '''        @self.app.route('/api/facts', methods=['POST'])
        def add_fact():
            """POST /api/facts - Add new fact WITH GOVERNANCE V3"""
            data = request.get_json(silent=True) or {}
            statement = (data.get('statement') or data.get('query') or data.get('fact') or '').strip()
            
            if not statement:
                return jsonify({'error': 'Missing statement'}), 400
            
            if not statement.endswith('.'):
                statement = statement + '.'
            
            if not re.match(r"^[A-Za-z_][A-Za-z0-9_]*\([^,\)]+,\s*[^\)]+\)\.$", statement):
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
        del lines[route_start:route_end]
        lines.insert(route_start, new_route)
        print("✅ Replaced add_fact route with Governance V3 version")
    
    # Add governance status endpoint (find where other routes are)
    for i, line in enumerate(lines):
        if '@self.app.route(\'/api/facts/count\', methods=[\'' in line:
            # Insert governance status route before facts/count
            status_route = '''        @self.app.route('/api/governance/status', methods=['GET'])
        def governance_status():
            """Get current governance status and health"""
            try:
                db_health = probe_sqlite(self.governance_engine.db_path)
                return jsonify({
                    'governance': {
                        'version': os.environ.get('GOVERNANCE_VERSION', 'unknown'),
                        'mode': os.environ.get('POLICY_ENFORCE', 'observe'),
                        'bypass_active': os.environ.get('GOVERNANCE_BYPASS') == 'true'
                    },
                    'database': {
                        'healthy': db_health.get('ok', False),
                        'wal_mode': db_health.get('wal_mode'),
                        'latency_ms': db_health.get('latency_ms'),
                        'facts_count': db_health.get('facts_count')
                    },
                    'status': 'operational'
                })
            except Exception as e:
                return jsonify({'error': str(e)}), 500

'''
            lines.insert(i, status_route)
            print("✅ Added governance status endpoint")
            break
    
    # Write the modified file
    with open(api_file, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print("\n" + "="*60)
    print("✅ INTEGRATION COMPLETE!")
    print("="*60)
    print("\nNext steps:")
    print("1. Stop the current backend (Ctrl+C)")
    print("2. Restart: python src_hexagonal\\hexagonal_api_enhanced_clean.py")
    print("3. Test: curl -X GET http://localhost:5002/api/governance/status")
    print("\nBackup saved at:", backup_path)

if __name__ == "__main__":
    integrate_governance_v3()
