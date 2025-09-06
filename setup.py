#!/usr/bin/env python3
# Quick Setup Script for HAK-GAL Hexagonal

import os
import subprocess
import sys

def main():
    print("HAK-GAL Hexagonal Setup")
    print("=" * 40)
    
    # 1. Check Python version
    if sys.version_info < (3, 11):
        print("ERROR: Python 3.11+ required!")
        sys.exit(1)
    print("✓ Python version OK")
    
    # 2. Create venv
    if not os.path.exists(".venv"):
        print("Creating virtual environment...")
        subprocess.run([sys.executable, "-m", "venv", ".venv"])
        print("✓ Virtual environment created")
    
    # 3. Install requirements
    pip_cmd = ".venv/Scripts/pip.exe" if os.name == 'nt' else ".venv/bin/pip"
    if os.path.exists(pip_cmd):
        print("Installing requirements...")
        subprocess.run([pip_cmd, "install", "-r", "requirements.txt"])
        print("✓ Requirements installed")
    
    # 4. Check for database
    if not os.path.exists("hexagonal_kb.db"):
        print("\nWARNING: Knowledge base not found!")
        print("Please run download_kb.bat or download_kb.sh")
        print("Or download from GitHub releases")
    else:
        print("✓ Knowledge base found")
    
    # 5. Frontend setup
    if os.path.exists("frontend/package.json"):
        print("\nSetting up frontend...")
        os.chdir("frontend")
        subprocess.run(["npm", "install"])
        os.chdir("..")
        print("✓ Frontend ready")
    
    print("\nSetup complete! Next steps:")
    print("1. Activate venv: .venv\Scripts\activate (Windows)")
    print("2. Start MCP: python ultimate_mcp/hakgal_mcp_ultimate.py")
    print("3. Start API: python src_hexagonal/hexagonal_api_enhanced_clean.py")
    print("4. Start Frontend: cd frontend && npm run dev")

if __name__ == "__main__":
    main()
