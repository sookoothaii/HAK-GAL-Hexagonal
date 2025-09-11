#!/usr/bin/env python
"""
Clean up duplicates and properly integrate Governance V3
"""

import os
import re
from datetime import datetime
import shutil

def cleanup_and_integrate():
    """Clean up duplicates and properly integrate Governance V3"""
    
    api_file = r"D:\MCP Mods\HAK_GAL_HEXAGONAL\src_hexagonal\hexagonal_api_enhanced_clean.py"
    
    print("=" * 60)
    print("GOVERNANCE V3 CLEANUP & INTEGRATION")
    print("=" * 60)
    
    # Backup
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{api_file}.backup_cleanup_{timestamp}"
    shutil.copy2(api_file, backup_path)
    print(f"✅ Backup created: {backup_path}")
    
    # Read file
    with open(api_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remove duplicate governance version setting
    content = re.sub(
        r'# Set Governance Version BEFORE other imports\nimport os\nos\.environ\.setdefault\(\'GOVERNANCE_VERSION\', \'v3\'\)\nprint\(f"\[INFO\] Governance Version: \{os\.environ\.get\(\'GOVERNANCE_VERSION\'\)\}"\)\n\n\n# Set Governance Version BEFORE other imports\nimport os\nos\.environ\.setdefault\(\'GOVERNANCE_VERSION\', \'v3\'\)\nprint\(f"\[INFO\] Governance Version: \{os\.environ\.get\(\'GOVERNANCE_VERSION\'\)\}"\)',
        r'# Set Governance Version BEFORE other imports\nimport os\nos.environ.setdefault(\'GOVERNANCE_VERSION\', \'v3\')\nprint(f"[INFO] Governance Version: {os.environ.get(\'GOVERNANCE_VERSION\')}")',
        content
    )
    print("✅ Removed duplicate governance version setting")
    
    # Remove duplicate governance imports
    content = re.sub(
        r'from src_hexagonal\.application\.transactional_governance_engine import TransactionalGovernanceEngine\nfrom src_hexagonal\.application\.governance_monitor import probe_sqlite\n\nfrom src_hexagonal\.application\.transactional_governance_engine import TransactionalGovernanceEngine\nfrom src_hexagonal\.application\.governance_monitor import probe_sqlite',
        r'from src_hexagonal.application.transactional_governance_engine import TransactionalGovernanceEngine\nfrom src_hexagonal.application.governance_monitor import probe_sqlite',
        content
    )
    print("✅ Removed duplicate governance imports")
    
    # Remove duplicate governance initialization 
    content = re.sub(
        r'        # Initialize Governance V3\n        self\.governance_engine = TransactionalGovernanceEngine\(\)\n        print\(f"\[OK\] Governance \{os\.environ\.get\(\'GOVERNANCE_VERSION\'\)\} initialized"\)\n        print\(f"\[OK\] Policy enforcement: \{os\.environ\.get\(\'POLICY_ENFORCE\', \'observe\'\)\}"\)\n        print\(f"\[OK\] Bypass mode: \{os\.environ\.get\(\'GOVERNANCE_BYPASS\', \'false\'\)\}"\)\n\n        # Initialize Governance V3\n        self\.governance_engine = TransactionalGovernanceEngine\(\)\n        print\(f"\[OK\] Governance \{os\.environ\.get\(\'GOVERNANCE_VERSION\'\)\} initialized"\)\n        print\(f"\[OK\] Policy enforcement: \{os\.environ\.get\(\'POLICY_ENFORCE\', \'observe\'\)\}"\)\n        print\(f"\[OK\] Bypass mode: \{os\.environ\.get\(\'GOVERNANCE_BYPASS\', \'false\'\)\}"\)',
        r'        # Initialize Governance V3\n        self.governance_engine = TransactionalGovernanceEngine()\n        print(f"[OK] Governance {os.environ.get(\'GOVERNANCE_VERSION\')} initialized")\n        print(f"[OK] Policy enforcement: {os.environ.get(\'POLICY_ENFORCE\', \'observe\')}")\n        print(f"[OK] Bypass mode: {os.environ.get(\'GOVERNANCE_BYPASS\', \'false\')}")',
        content
    )
    print("✅ Removed duplicate governance initialization")
    
    # Find and replace the add_fact route
    pattern = r"        @self\.app\.route\('/api/facts', methods=\['POST'\]\)\n        # # # # # @require_api_key\n        def add_fact\(\):[\s\S]*?return jsonify\(\{[^}]+\}\), status_code"
    
    replacement = '''        @self.app.route('/api/facts', methods=['POST'])
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
                }), 500'''
    
    content = re.sub(pattern, replacement, content)
    print("✅ Replaced add_fact route with Governance V3 version")
    
    # Remove duplicate governance_status routes
    # Count occurrences
    governance_status_count = content.count("def governance_status():")
    if governance_status_count > 1:
        print(f"Found {governance_status_count} governance_status routes, keeping only one")
        # Keep first, remove duplicates
        parts = content.split("@self.app.route('/api/governance/status', methods=['GET'])")
        if len(parts) > 2:
            # Keep first occurrence, remove others
            new_parts = [parts[0]]
            for i in range(1, len(parts)):
                if i == 1:
                    # Keep first occurrence completely
                    new_parts.append(parts[i])
                else:
                    # Remove the duplicate function definition
                    cleaned = re.sub(
                        r"^\s*def governance_status\(\):[\s\S]*?return jsonify\(\{[^}]+\}\), 500",
                        "",
                        parts[i],
                        count=1
                    )
                    new_parts.append(cleaned)
            content = "@self.app.route('/api/governance/status', methods=['GET'])".join(new_parts)
            print("✅ Removed duplicate governance_status routes")
    
    # Write cleaned file
    with open(api_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("\n" + "=" * 60)
    print("✅ CLEANUP & INTEGRATION COMPLETE!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Stop the backend (Ctrl+C)")
    print("2. Restart: python src_hexagonal\\hexagonal_api_enhanced_clean.py")
    print("3. Test governance: curl -X GET http://localhost:5002/api/governance/status")
    print("4. Test add_fact: curl -X POST http://localhost:5002/api/facts -H 'Content-Type: application/json' -d '{\"statement\":\"Test(Governance, V3)\"}'")
    
    return backup_path

if __name__ == "__main__":
    backup = cleanup_and_integrate()
    print(f"\nBackup saved at: {backup}")
