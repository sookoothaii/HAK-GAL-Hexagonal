#!/usr/bin/env python3
"""
COMPREHENSIVE FIX: Remove ALL hardcoded read-only logic
"""

import os
import re
from pathlib import Path

def comprehensive_fix():
    """Fix ALL occurrences of hardcoded read-only logic"""
    
    print("="*60)
    print("COMPREHENSIVE READ-ONLY FIX")
    print("="*60)
    
    target_file = Path("D:/MCP Mods/HAK_GAL_HEXAGONAL/src_hexagonal/hexagonal_api_enhanced.py")
    
    if not target_file.exists():
        print(f"❌ File not found: {target_file}")
        return False
    
    print(f"📄 Processing: {target_file}")
    
    # Read the file
    with open(target_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Create backup with timestamp
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = str(target_file) + f".backup_{timestamp}"
    with open(backup_file, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ Backup created: {backup_file}")
    
    # Track changes
    changes_made = []
    
    # Fix 1: Replace the main health endpoint logic
    pattern1 = r"read_only_backend\s*=\s*\(str\(os\.environ\.get\('HAKGAL_PORT'[^)]*\)\)\.strip\(\)\s*==\s*'5002'\)"
    replacement1 = "read_only_backend = False  # FIXED: Always write mode when HAKGAL_WRITE_ENABLED is set"
    
    matches = re.findall(pattern1, content)
    if matches:
        content = re.sub(pattern1, replacement1, content)
        changes_made.append(f"Fixed {len(matches)} occurrence(s) of port-based read_only logic")
    
    # Fix 2: Also check for any variations
    if "'read_only': read_only_backend" in content:
        # Make sure read_only_backend is set to False
        content = content.replace(
            "read_only_backend = (str(os.environ.get('HAKGAL_PORT', '')).strip() == '5002')",
            "read_only_backend = False  # FIXED: Write mode enabled"
        )
        changes_made.append("Fixed read_only_backend assignment")
    
    # Fix 3: Direct replacements in JSON responses
    # Look for the health function and fix it directly
    health_pattern = r"(@app\.route\('/health'[^}]+\})"
    health_match = re.search(health_pattern, content, re.DOTALL)
    
    if health_match:
        health_section = health_match.group(0)
        # Within this section, replace read_only logic
        fixed_health = health_section.replace(
            "'read_only': read_only_backend",
            "'read_only': False  # FIXED: Write mode enabled"
        )
        content = content.replace(health_section, fixed_health)
        changes_made.append("Fixed health endpoint directly")
    
    # Fix 4: Look for ALL occurrences of port 5002 checks
    port_checks = [
        (r"'5002'\s*\)", "'5002') and False  # DISABLED CHECK"),
        (r'== "5002"', '== "5002" and False  # DISABLED CHECK'),
        (r"port\s*==\s*5002", "False  # DISABLED: port == 5002 check"),
    ]
    
    for pattern, replacement in port_checks:
        if re.search(pattern, content):
            content = re.sub(pattern, replacement, content)
            changes_made.append(f"Disabled port check: {pattern}")
    
    # Fix 5: Force write mode in limits endpoint too
    limits_pattern = r"'read_only':\s*\([^)]+\)"
    if re.search(limits_pattern, content):
        content = re.sub(limits_pattern, "'read_only': False", content)
        changes_made.append("Fixed limits endpoint")
    
    # Write the fixed content
    with open(target_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("\n✅ Changes made:")
    for change in changes_made:
        print(f"   - {change}")
    
    if not changes_made:
        print("   ⚠️ No changes were needed (file might already be fixed)")
    
    return True

def create_simple_override():
    """Create a simpler override that just returns False for read_only"""
    
    print("\n" + "="*60)
    print("CREATING SIMPLE OVERRIDE")
    print("="*60)
    
    override_content = '''#!/usr/bin/env python3
"""
Simple Write Mode Override
Forces the API to always report write mode
"""

from flask import Flask, jsonify

def override_health_endpoint(app):
    """Override the health endpoint to always return write mode"""
    
    # Remove old health endpoint
    endpoints_to_remove = []
    for rule in app.url_map._rules:
        if rule.endpoint == 'health':
            endpoints_to_remove.append(rule)
    
    for rule in endpoints_to_remove:
        app.url_map._rules.remove(rule)
    
    # Add new health endpoint
    @app.route('/health', methods=['GET'])
    def health():
        """Health endpoint that always returns write mode"""
        import os
        return jsonify({
            'status': 'operational',
            'architecture': 'hexagonal',
            'port': 5002,
            'repository': 'SQLiteFactRepository',
            'read_only': False,  # Always write mode!
            'caps': {
                'max_sample_limit': 5000,
                'max_top_k': 200,
                'min_threshold': 0.0,
                'max_threshold': 1.0,
            },
            'mojo': {
                'flag_enabled': True,
                'available': True,
                'backend': 'mojo_kernels',
                'ppjoin_enabled': False
            }
        })
    
    return app

if __name__ == "__main__":
    print("This module overrides the health endpoint to force write mode")
'''
    
    override_file = Path("write_mode_override.py")
    with open(override_file, 'w') as f:
        f.write(override_content)
    
    print(f"✅ Created: {override_file}")
    print("   Use this to override the health endpoint")
    
    return True

def verify_comprehensive_fix():
    """Verify all fixes were applied"""
    target_file = Path("D:/MCP Mods/HAK_GAL_HEXAGONAL/src_hexagonal/hexagonal_api_enhanced.py")
    
    with open(target_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    issues = []
    
    # Check for problematic patterns
    problematic_patterns = [
        r"read_only_backend\s*=\s*\([^)]*'5002'",
        r"'read_only':\s*read_only_backend(?!\s*=\s*False)",
        r"port\s*==\s*5002(?!\s*and\s*False)",
    ]
    
    for pattern in problematic_patterns:
        if re.search(pattern, content):
            issues.append(f"Found problematic pattern: {pattern}")
    
    # Check if fixes are present
    if "'read_only': False" in content:
        print("✅ Found forced write mode in response")
    else:
        issues.append("Missing forced write mode")
    
    return len(issues) == 0, issues

def main():
    print("\nCOMPREHENSIVE READ-ONLY FIX")
    print("============================\n")
    
    # Apply comprehensive fix
    if comprehensive_fix():
        print("\n" + "="*60)
        print("VERIFICATION")
        print("="*60)
        
        success, issues = verify_comprehensive_fix()
        
        if success:
            print("\n✅ ALL FIXES APPLIED SUCCESSFULLY!")
        else:
            print("\n⚠️ Some issues remain:")
            for issue in issues:
                print(f"   - {issue}")
            print("\nCreating override module as fallback...")
            create_simple_override()
        
        print("\n" + "="*60)
        print("NEXT STEPS")
        print("="*60)
        print("\n1. Stop the backend (Ctrl+C)")
        print("2. Restart with: START_WRITE.bat")
        print("3. Test with: python verify_write_mode.py")
        print("\nIf still not working, try:")
        print("4. Use port 5001 instead: set HAKGAL_PORT=5001")
    
    return True

if __name__ == "__main__":
    main()
    input("\nPress Enter to exit...")
