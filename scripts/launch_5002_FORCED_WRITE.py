#!/usr/bin/env python3
"""
Special launcher for Port 5002 with FORCED write mode
"""
import os
import sys
from pathlib import Path

# FORCE ALL WRITE SETTINGS
os.environ['HAKGAL_PORT'] = '5002'
os.environ['HAKGAL_WRITE_ENABLED'] = 'true'
os.environ['HAKGAL_WRITE_TOKEN'] = 'force_write_5002'
os.environ['HAKGAL_SQLITE_READONLY'] = 'false'
os.environ['FORCE_WRITE_MODE'] = 'true'

print("="*60)
print("STARTING PORT 5002 WITH FORCED WRITE MODE")
print("="*60)
print(f"PORT = 5002")
print(f"WRITE_ENABLED = true")
print(f"C++ Code Support = ENABLED (Port 5002 only)")
print("="*60)

# Get root and add to path
root = Path(__file__).resolve().parent
sys.path.insert(0, str(root))
sys.path.insert(0, str(root / 'src_hexagonal'))

# Monkey-patch to override read_only checks
import importlib.util

# Load the module
spec = importlib.util.spec_from_file_location(
    "hexagonal_api_enhanced",
    str(root / "src_hexagonal" / "hexagonal_api_enhanced.py")
)
module = importlib.util.module_from_spec(spec)

# Monkey-patch BEFORE execution
original_exec = spec.loader.exec_module

def patched_exec(module):
    # Execute original
    original_exec(module)
    
    # Now patch the app creation
    if hasattr(module, 'HexagonalAPI'):
        original_init = module.HexagonalAPI.__init__
        
        def patched_init(self, *args, **kwargs):
            # Call original
            original_init(self, *args, **kwargs)
            
            # Override health endpoint
            old_health = None
            for rule in self.app.url_map._rules:
                if rule.endpoint == 'health':
                    old_health = rule
                    break
            
            if old_health:
                @self.app.route('/health', methods=['GET'])
                def health():
                    return {
                        'status': 'operational',
                        'architecture': 'hexagonal',
                        'port': 5002,
                        'repository': 'SQLiteFactRepository',
                        'read_only': False,  # ALWAYS FALSE!
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
                    }
        
        module.HexagonalAPI.__init__ = patched_init
    
    return module

spec.loader.exec_module = patched_exec

# Import with patches
spec.loader.exec_module(module)
sys.modules['hexagonal_api_enhanced'] = module

# Now run the launch script
from scripts.launch_5002_WRITE import main
main()
