#!/usr/bin/env python
"""
Auto-Fix Engine Timeouts
========================
Automatisch alle Timeout-Werte in den Engines erhöhen
"""

import re
from pathlib import Path

def fix_engine_timeouts():
    """Fix timeouts in all engine files"""
    
    print("="*70)
    print("AUTO-FIXING ENGINE TIMEOUTS")
    print("="*70)
    
    # Find engine files
    engine_files = [
        Path("src_hexagonal/infrastructure/engines/aethelred_engine.py"),
        Path("src_hexagonal/infrastructure/engines/thesis_engine.py"),
    ]
    
    fixed_count = 0
    
    for engine_file in engine_files:
        if not engine_file.exists():
            print(f"⚠️ Not found: {engine_file}")
            continue
        
        print(f"\n[{engine_file.name}]")
        
        # Read content
        content = engine_file.read_text(encoding='utf-8')
        original = content
        
        # Fix various timeout patterns
        replacements = [
            # requests timeout
            (r'timeout=30\)', 'timeout=60)'),
            (r'timeout=30,', 'timeout=60,'),
            (r'timeout = 30', 'timeout = 60'),
            
            # Specific timeout values
            (r'"timeout":\s*30', '"timeout": 60'),
            (r"'timeout':\s*30", "'timeout': 60"),
            
            # Read timeout
            (r'read_timeout=30', 'read_timeout=60'),
            (r'read timeout=30', 'read timeout=60'),
        ]
        
        changes = 0
        for pattern, replacement in replacements:
            new_content, n = re.subn(pattern, replacement, content)
            if n > 0:
                content = new_content
                changes += n
                print(f"  ✅ Fixed {n} occurrence(s) of: {pattern}")
        
        if changes > 0:
            # Backup original
            backup_path = engine_file.with_suffix('.py.backup')
            if not backup_path.exists():
                backup_path.write_text(original, encoding='utf-8')
                print(f"  📁 Backup saved: {backup_path}")
            
            # Write fixed content
            engine_file.write_text(content, encoding='utf-8')
            print(f"  ✅ Updated {changes} timeout values to 60 seconds")
            fixed_count += 1
        else:
            print(f"  ℹ️ No timeout=30 found (might already be fixed)")
    
    # Also check API files
    print("\n[Checking API timeout settings...]")
    
    api_files = [
        Path("src_hexagonal/api_server.py"),
        Path("src_hexagonal/infrastructure/api_adapter.py"),
    ]
    
    for api_file in api_files:
        if api_file.exists():
            content = api_file.read_text(encoding='utf-8')
            
            # Check for SQLAlchemy settings
            if 'SQLALCHEMY' in content and 'timeout' not in content:
                print(f"  ⚠️ {api_file.name}: Consider adding timeout settings")
    
    print("\n" + "="*70)
    print("RESULTS:")
    print("="*70)
    
    if fixed_count > 0:
        print(f"✅ Fixed timeouts in {fixed_count} engine file(s)")
        print("   All timeouts increased from 30s to 60s")
        print("\n⚠️ IMPORTANT: Restart all processes for changes to take effect!")
    else:
        print("ℹ️ No changes needed (timeouts might already be fixed)")
    
    print("\nNext steps:")
    print("1. Run: python fix_websocket_stability.py")
    print("2. Restart all processes")
    print("3. Monitor dashboard for stability")

if __name__ == "__main__":
    fix_engine_timeouts()
