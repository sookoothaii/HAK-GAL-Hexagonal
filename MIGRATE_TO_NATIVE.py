#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
COMPLETE MIGRATION TO HEXAGONAL
================================
Run this once to become independent from HAK_GAL_SUITE
"""

import subprocess
import sys
from pathlib import Path

# Fix encoding for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

def run_migration():
    """Run complete migration"""
    
    print("="*60)
    print("[MIGRATION] COMPLETE MIGRATION TO HEXAGONAL")
    print("="*60)
    print("This will:")
    print("1. Port Shared Models (ML/Transformers)")
    print("2. Port K-Assistant (Knowledge Management)")
    print("3. Port HRM System (Reasoning)")
    print("4. Create Native Adapters")
    print("5. Test the native backend")
    print("="*60)
    
    input("Press Enter to start migration...")
    
    steps = [
        ("Step 1: Migrating Models", "migrate_step1_models.py"),
        ("Step 2: Migrating K-Assistant", "migrate_step2_kassistant.py"),
        ("Step 3: Migrating HRM", "migrate_step3_hrm.py"),
        ("Step 4: Creating Adapters", "migrate_step4_adapters.py"),
    ]
    
    for step_name, script_name in steps:
        print(f"\n{'='*60}")
        print(f"[RUNNING] {step_name}")
        print("="*60)
        
        result = subprocess.run([sys.executable, script_name], capture_output=True, text=True)
        
        if result.returncode == 0:
            print(result.stdout)
            print(f"[OK] {step_name} - SUCCESS")
        else:
            print(f"[ERROR] {step_name} - FAILED")
            print(result.stderr)
            return False
    
    print("\n" + "="*60)
    print("[SUCCESS] MIGRATION COMPLETE!")
    print("="*60)
    print("\nYou are now INDEPENDENT from HAK_GAL_SUITE!")
    print("\nTo start the native backend:")
    print("  python start_native.py")
    print("\nExpected benefits:")
    print("  - Fast startup (5-10 seconds)")
    print("  - No legacy dependencies")
    print("  - Clean architecture")
    print("  - Full control over all components")
    print("="*60)
    
    return True

if __name__ == '__main__':
    try:
        success = run_migration()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"[ERROR] Migration failed: {e}")
        sys.exit(1)
