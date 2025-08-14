#!/usr/bin/env python3
"""
Start Hexagonal API with Original Environment
==============================================
Uses the original .venv with CUDA support
"""

import sys
import os
from pathlib import Path

# Use ORIGINAL environment with CUDA support
ORIGINAL_VENV = Path(r"D:\MCP Mods\HAK_GAL_SUITE\.venv")
if ORIGINAL_VENV.exists():
    # Adjust Python path to use original environment's packages
    site_packages = ORIGINAL_VENV / "Lib" / "site-packages"
    if site_packages.exists():
        sys.path.insert(0, str(site_packages))
        print(f"✅ Using Original Environment with CUDA: {site_packages}")

# Add current directory
sys.path.insert(0, str(Path(__file__).parent))

# Start Hexagonal API
from src_hexagonal.hexagonal_api import create_app

if __name__ == "__main__":
    use_legacy = "--sqlite" not in sys.argv
    
    print("="*60)
    print("Starting HAK-GAL Hexagonal API with CUDA Support")
    print("="*60)
    print(f"Mode: {'Legacy (Original HAK-GAL)' if use_legacy else 'SQLite (Direct)'}")
    
    # Check CUDA status
    import torch
    if torch.cuda.is_available():
        print(f"✅ CUDA Active: {torch.cuda.get_device_name(0)}")
    else:
        print("⚠️ CUDA Not Available")
    
    print("="*60)
    
    app = create_app(use_legacy=use_legacy)
    app.run(host='127.0.0.1', port=5001, debug=False)
