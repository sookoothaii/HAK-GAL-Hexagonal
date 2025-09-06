#!/usr/bin/env python3
"""
Launch HAK-GAL HEXAGONAL on port 5002 in FORCED WRITE mode
Emergency launch script to ensure write capabilities
"""
import os
import sys
from pathlib import Path

# FORCE WRITE MODE - Override all settings
print("="*60)
print("FORCING WRITE MODE - EMERGENCY OVERRIDE")
print("="*60)

os.environ['HAKGAL_WRITE_ENABLED'] = 'true'
os.environ['HAKGAL_WRITE_TOKEN'] = 'emergency_write_token_2025'
os.environ['HAKGAL_PORT'] = '5002'
os.environ['FORCE_WRITE_MODE'] = 'true'

print(f"✅ HAKGAL_WRITE_ENABLED = {os.environ['HAKGAL_WRITE_ENABLED']}")
print(f"✅ FORCE_WRITE_MODE = {os.environ['FORCE_WRITE_MODE']}")
print(f"✅ PORT = {os.environ['HAKGAL_PORT']}")
print("="*60)

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'src_hexagonal'))

print(f"Project root: {project_root}")

try:
    # Try to import the existing launch script first
    from scripts import launch_5002_WRITE
    print("Using existing launch_5002_WRITE module...")
    
except ImportError:
    print("Creating app directly...")
    
    # Direct import and launch
    try:
        from src_hexagonal.api import create_app
    except ImportError:
        # Try alternative import
        os.chdir(project_root)
        from src_hexagonal.api import create_app
    
    app = create_app()
    
    # Force write mode in the app config
    with app.app_context():
        try:
            from src_hexagonal.core.config import get_config
            config = get_config()
            
            # FORCE OVERRIDE
            config.WRITE_ENABLED = True
            config.WRITE_TOKEN = 'emergency_write_token_2025'
            config.READ_ONLY = False  # Explicitly set to False
            
            print(f"✅ Config Override: WRITE_ENABLED = {config.WRITE_ENABLED}")
            print(f"✅ Config Override: READ_ONLY = False")
            
        except Exception as e:
            print(f"⚠️ Could not override config directly: {e}")
            print("   Proceeding anyway with environment variables...")
    
    # Run the application
    print("\n" + "="*60)
    print("STARTING HAK-GAL HEXAGONAL SERVER")
    print("Port: 5002 | Mode: WRITE (FORCED)")
    print("="*60 + "\n")
    
    app.run(
        host='127.0.0.1',
        port=5002,
        debug=False,
        use_reloader=False
    )
