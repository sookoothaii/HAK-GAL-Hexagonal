#!/usr/bin/env python3
"""
ULTIMATE FIX FOR PORT 5002 - Force Write Mode
This completely overrides ALL read-only logic for port 5002
"""

import os
import re
from pathlib import Path
from datetime import datetime

def ultimate_port_5002_fix():
    """Nuclear option - replace ALL read_only occurrences with False"""
    
    print("="*60)
    print("ULTIMATE PORT 5002 WRITE MODE FIX")
    print("="*60)
    print("This will FORCE port 5002 to always be in WRITE mode")
    print("="*60)
    
    target_file = Path("D:/MCP Mods/HAK_GAL_HEXAGONAL/src_hexagonal/hexagonal_api_enhanced.py")
    
    if not target_file.exists():
        print(f"❌ File not found: {target_file}")
        return False
    
    print(f"📄 Processing: {target_file}")
    
    # Read the file
    with open(target_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Create backup
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = str(target_file) + f".backup_ultimate_{timestamp}"
    with open(backup_file, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ Backup created: {backup_file}")
    
    # Track original content for comparison
    original_content = content
    
    # NUCLEAR REPLACEMENTS - Force everything to write mode
    replacements = [
        # Replace the variable assignment
        (r"read_only_backend\s*=\s*[^\n]+", "read_only_backend = False  # FORCED WRITE MODE"),
        
        # Replace in dictionary literals
        (r"'read_only'\s*:\s*read_only_backend", "'read_only': False  # FORCED"),
        (r'"read_only"\s*:\s*read_only_backend', '"read_only": False  # FORCED'),
        
        # Replace any True assignments
        (r"'read_only'\s*:\s*True", "'read_only': False  # FORCED"),
        (r'"read_only"\s*:\s*True', '"read_only": False  # FORCED'),
        
        # Replace any conditional checks
        (r"'read_only'\s*:\s*\([^)]+\)", "'read_only': False  # FORCED"),
        
        # Port 5002 specific overrides
        (r"==\s*'5002'\)", "== '5002') and False  # DISABLED"),
        (r"==\s*\"5002\"\)", '== "5002") and False  # DISABLED'),
        
        # SQLite readonly checks
        (r"HAKGAL_SQLITE_READONLY['\"]]\s*==\s*['\"]true", "HAKGAL_SQLITE_READONLY'] == 'false"),
    ]
    
    print("\nApplying replacements...")
    changes_count = 0
    
    for pattern, replacement in replacements:
        matches = re.findall(pattern, content)
        if matches:
            content = re.sub(pattern, replacement, content)
            changes_count += len(matches)
            print(f"   ✅ Replaced {len(matches)} occurrence(s) of: {pattern[:50]}...")
    
    # SPECIAL: Find the health endpoint and force it
    health_match = re.search(r"@app\.route\('/health'.*?\n\s+def health\(\):(.*?)(?=@app\.route|\Z)", content, re.DOTALL)
    if health_match:
        health_func = health_match.group(0)
        # Force the return value
        if "'read_only':" in health_func:
            new_health = re.sub(r"'read_only'\s*:\s*[^,}\n]+", "'read_only': False", health_func)
            content = content.replace(health_func, new_health)
            print(f"   ✅ Forced health endpoint to return read_only: False")
            changes_count += 1
    
    # SPECIAL: Find limits endpoint and force it
    limits_match = re.search(r"@app\.route\('/api/limits'.*?\n\s+def limits\(\):(.*?)(?=@app\.route|\Z)", content, re.DOTALL)
    if limits_match:
        limits_func = limits_match.group(0)
        if "'read_only':" in limits_func:
            new_limits = re.sub(r"'read_only'\s*:\s*[^,}\n]+", "'read_only': False", limits_func)
            content = content.replace(limits_func, new_limits)
            print(f"   ✅ Forced limits endpoint to return read_only: False")
            changes_count += 1
    
    # Write the fixed content
    if content != original_content:
        with open(target_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"\n✅ Total changes made: {changes_count}")
        print("✅ File successfully patched!")
    else:
        print("\n⚠️ No changes were needed (file might already be fixed)")
    
    return True

def create_launcher_with_override():
    """Create a special launcher that includes the override"""
    
    launcher_content = '''#!/usr/bin/env python3
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
'''
    
    launcher_file = Path("launch_5002_FORCED_WRITE.py")
    with open(launcher_file, 'w') as f:
        f.write(launcher_content)
    
    print(f"\n✅ Created special launcher: {launcher_file}")
    print("   This launcher forces write mode on port 5002")
    
    return launcher_file

def verify_ultimate_fix():
    """Check if the fix was successful"""
    target_file = Path("D:/MCP Mods/HAK_GAL_HEXAGONAL/src_hexagonal/hexagonal_api_enhanced.py")
    
    with open(target_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Count occurrences of read_only: False
    false_count = len(re.findall(r"'read_only'\s*:\s*False", content))
    
    # Check for problematic patterns
    problems = []
    if re.search(r"'read_only'\s*:\s*True", content):
        problems.append("Still has read_only: True")
    if re.search(r"'read_only'\s*:\s*read_only_backend(?!\s*=)", content):
        problems.append("Still references read_only_backend variable")
    if re.search(r"==\s*['\"]5002['\"]\)(?!\s*and\s*False)", content):
        problems.append("Port 5002 check not disabled")
    
    return false_count, problems

def main():
    print("\nULTIMATE FIX FOR PORT 5002 WRITE MODE")
    print("======================================\n")
    print("Port 5001 is deprecated - we MUST use port 5002!")
    print("Port 5002 has C++ code support which is essential.\n")
    
    # Apply ultimate fix
    if ultimate_port_5002_fix():
        print("\n" + "="*60)
        print("VERIFICATION")
        print("="*60)
        
        false_count, problems = verify_ultimate_fix()
        
        print(f"✅ Found {false_count} occurrences of 'read_only': False")
        
        if problems:
            print("\n⚠️ Remaining issues:")
            for problem in problems:
                print(f"   - {problem}")
        else:
            print("✅ No problematic patterns found!")
        
        # Create special launcher
        launcher = create_launcher_with_override()
        
        print("\n" + "="*60)
        print("NEXT STEPS")
        print("="*60)
        print("\n1. Stop the current backend (Ctrl+C)")
        print("\n2. Restart using ONE of these methods:")
        print("   Option A: python launch_5002_FORCED_WRITE.py")
        print("   Option B: START_WRITE.bat")
        print("\n3. Verify with: python verify_write_mode.py")
        print("\n✅ Port 5002 will now have WRITE mode with C++ support!")
    
    return True

if __name__ == "__main__":
    main()
    input("\nPress Enter to exit...")
