#!/usr/bin/env python3
"""
Emergency Fix: Force WRITE mode for HAK-GAL Backend
"""

import os
import sys
from pathlib import Path

def force_write_mode():
    """Force the backend to start in WRITE mode"""
    
    print("="*60)
    print("FORCING WRITE MODE FOR HAK-GAL BACKEND")
    print("="*60)
    
    # Set environment variables
    os.environ['HAKGAL_WRITE_ENABLED'] = 'true'
    os.environ['HAKGAL_WRITE_TOKEN'] = 'emergency_write_token'
    os.environ['HAKGAL_PORT'] = '5002'
    
    print("✅ Environment variables set:")
    print(f"   HAKGAL_WRITE_ENABLED = true")
    print(f"   HAKGAL_WRITE_TOKEN = (set)")
    print(f"   HAKGAL_PORT = 5002")
    
    # Check launch script
    launch_script = Path("scripts/launch_5002_WRITE.py")
    
    if launch_script.exists():
        print(f"\n✅ Launch script found: {launch_script}")
        
        # Read and verify it sets write mode
        with open(launch_script, 'r') as f:
            content = f.read()
            
        if 'HAKGAL_WRITE_ENABLED' not in content:
            print("⚠️ Launch script doesn't explicitly set WRITE mode")
            
            # Create fixed version
            fixed_content = '''#!/usr/bin/env python3
"""
Launch HAK-GAL HEXAGONAL on port 5002 in WRITE mode
"""
import os
import sys
from pathlib import Path

# FORCE WRITE MODE
os.environ['HAKGAL_WRITE_ENABLED'] = 'true'
os.environ['HAKGAL_WRITE_TOKEN'] = 'secure_token_here'
os.environ['HAKGAL_PORT'] = '5002'

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import and run the API
from src_hexagonal.api import create_app

if __name__ == "__main__":
    print("="*60)
    print("STARTING HAK-GAL HEXAGONAL - PORT 5002 - WRITE MODE")
    print("="*60)
    print(f"WRITE_ENABLED: {os.environ.get('HAKGAL_WRITE_ENABLED', 'false')}")
    print(f"PORT: {os.environ.get('HAKGAL_PORT', '5002')}")
    print("="*60)
    
    app = create_app()
    
    # Verify write mode is enabled
    with app.app_context():
        from src_hexagonal.core.config import get_config
        config = get_config()
        if not config.WRITE_ENABLED:
            print("⚠️ WARNING: Write mode not enabled in config!")
            print("Forcing write mode...")
            config.WRITE_ENABLED = True
            config.WRITE_TOKEN = os.environ.get('HAKGAL_WRITE_TOKEN')
    
    # Run the app
    app.run(
        host='127.0.0.1',
        port=5002,
        debug=False,  # Set to False for production
        use_reloader=False  # Prevent double loading
    )
'''
            
            # Save fixed version
            fixed_path = Path("scripts/launch_5002_WRITE_FIXED.py")
            with open(fixed_path, 'w') as f:
                f.write(fixed_content)
            
            print(f"✅ Created fixed launch script: {fixed_path}")
            print("   Use this to ensure WRITE mode")
    
    # Check config file
    config_paths = [
        Path("src_hexagonal/core/config.py"),
        Path("config/hexagonal_config.py"),
        Path(".env")
    ]
    
    print("\nChecking configuration files...")
    for config_path in config_paths:
        if config_path.exists():
            print(f"✅ Found: {config_path}")
            
            if config_path.suffix == '.py':
                with open(config_path, 'r') as f:
                    content = f.read()
                    if 'WRITE_ENABLED' in content and 'False' in content:
                        print(f"   ⚠️ May be hardcoded to READ_ONLY")
            elif config_path.name == '.env':
                with open(config_path, 'r') as f:
                    content = f.read()
                    if 'HAKGAL_WRITE_ENABLED' not in content:
                        print(f"   ⚠️ Missing HAKGAL_WRITE_ENABLED")
                        # Add to .env
                        with open(config_path, 'a') as f2:
                            f2.write('\n# Write mode configuration\n')
                            f2.write('HAKGAL_WRITE_ENABLED=true\n')
                            f2.write('HAKGAL_WRITE_TOKEN=secure_token_here\n')
                        print(f"   ✅ Added WRITE configuration to .env")
    
    print("\n" + "="*60)
    print("CONFIGURATION COMPLETE")
    print("="*60)
    print("\nTo start in WRITE mode:")
    print("1. python scripts/launch_5002_WRITE_FIXED.py")
    print("   OR")
    print("2. restart_write_mode.bat")
    
    return True

if __name__ == "__main__":
    force_write_mode()
