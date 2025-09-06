#!/usr/bin/env python3
"""
launch_5002_REAL_MOJO.py - Alternative launcher from main directory
Place this in D:\MCP Mods\HAK_GAL_HEXAGONAL\ and run from there
"""
import sys
import os

# CRITICAL: Add compiled module path FIRST!
sys.path.insert(0, r"D:\MCP Mods\HAK_GAL_HEXAGONAL\native\mojo_kernels\build\Release")

# Rename the stub first if it exists
from pathlib import Path
stub = Path("src_hexagonal/mojo_kernels.py")
if stub.exists():
    disabled = stub.with_suffix('.py.DISABLED')
    if not disabled.exists():
        stub.rename(disabled)
        print(f"AUTO-DISABLED: {stub} -> {disabled}")

# Now import - will find the .pyd
from src_hexagonal.hexagonal_api_enhanced import create_app

if __name__ == "__main__":
    print("=" * 60)
    print("STARTING PORT 5002 WITH REAL MOJO MODULE")
    print("=" * 60)
    
    # Verify we have the real module
    import mojo_kernels
    print(f"Mojo loaded from: {mojo_kernels.__file__}")
    
    if ".pyd" in mojo_kernels.__file__:
        print("SUCCESS: Using compiled Mojo module!")
    else:
        print("WARNING: Still using Python version!")
    
    os.environ['HAKGAL_HEXAGONAL_DB'] = 'hexagonal_kb.db'
    os.environ['HAKGAL_PORT'] = '5002'
    os.environ['MOJO_ENABLED'] = 'true'
    
    app = create_app(
        db_name='hexagonal_kb.db',
        backend='mojo_kernels',
        use_legacy=False,
        enable_all=True
    )
    
    print("Server starting on port 5002")
    app.run(host='127.0.0.1', port=5002, debug=False)