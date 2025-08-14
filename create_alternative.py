#!/usr/bin/env python
"""
ALTERNATIVE: Configure Backend to use k_assistant_dev.db directly
==================================================================
Instead of copying, point backend to the correct DB
"""

import os
from pathlib import Path

def create_config_override():
    """Create environment override to use k_assistant_dev.db"""
    
    print("="*60)
    print("🔧 ALTERNATIVE: Backend Configuration Override")
    print("="*60)
    
    # Create .env.local file for override
    env_content = """# Local Override - Use correct database
HAK_GAL_DB_PATH=D:\\MCP Mods\\HAK_GAL_HEXAGONAL\\k_assistant_dev.db
USE_LOCAL_DB=true
"""
    
    env_path = Path(r"D:\MCP Mods\HAK_GAL_HEXAGONAL\.env.local")
    with open(env_path, 'w') as f:
        f.write(env_content)
    
    print(f"✅ Created: {env_path}")
    
    # Create modified startup script
    startup_content = '''@echo off
echo ============================================================
echo HAK-GAL HEXAGONAL - Using k_assistant_dev.db (3079 facts)
echo ============================================================

REM Set database override
set HAK_GAL_DB_URI=sqlite:///D:/MCP Mods/HAK_GAL_HEXAGONAL/k_assistant_dev.db

REM Activate virtual environment
if exist .venv_hexa\\Scripts\\activate.bat (
    call .venv_hexa\\Scripts\\activate.bat
)

echo Starting with correct database...
python start_working_backend.py

pause
'''
    
    startup_path = Path(r"D:\MCP Mods\HAK_GAL_HEXAGONAL\start_with_dev_db.bat")
    with open(startup_path, 'w') as f:
        f.write(startup_content)
    
    print(f"✅ Created: {startup_path}")
    
    print("\n" + "="*60)
    print("📋 TWO OPTIONS AVAILABLE:")
    print("\n1. QUICK FIX (Recommended):")
    print("   python QUICK_FIX.py")
    print("   (Copies k_assistant_dev.db to HAK_GAL_SUITE)")
    print("\n2. CONFIGURATION OVERRIDE:")
    print("   .\\start_with_dev_db.bat")
    print("   (Uses k_assistant_dev.db directly)")
    print("="*60)

if __name__ == '__main__':
    create_config_override()
