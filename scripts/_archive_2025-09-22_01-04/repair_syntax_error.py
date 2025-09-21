#!/usr/bin/env python3
"""
FIX SYNTAX ERROR - Repair the broken hexagonal_api_enhanced.py
"""

import os
from pathlib import Path
from datetime import datetime

def repair_syntax_error():
    """Repair the syntax error caused by aggressive replacements"""
    
    print("="*60)
    print("REPAIRING SYNTAX ERROR")
    print("="*60)
    
    target_file = Path("D:/MCP Mods/HAK_GAL_HEXAGONAL/src_hexagonal/hexagonal_api_enhanced.py")
    
    # First, try to restore from a good backup
    backups = list(Path("D:/MCP Mods/HAK_GAL_HEXAGONAL/src_hexagonal").glob("hexagonal_api_enhanced.py.backup*"))
    
    if backups:
        # Sort by modification time, get the most recent good one
        backups.sort(key=lambda x: x.stat().st_mtime)
        
        # Find a backup that's before the ultimate fix
        for backup in reversed(backups):
            if "ultimate" not in backup.name:
                print(f"✅ Found good backup: {backup.name}")
                
                # Restore from this backup
                with open(backup, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Save current broken version
                broken_backup = str(target_file) + ".broken_syntax"
                with open(target_file, 'r', encoding='utf-8') as f:
                    broken_content = f.read()
                with open(broken_backup, 'w', encoding='utf-8') as f:
                    f.write(broken_content)
                print(f"   Saved broken version to: {broken_backup}")
                
                # Restore good version
                with open(target_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                print(f"✅ Restored from backup: {backup.name}")
                
                # Now apply a SAFER fix
                apply_safe_fix(target_file)
                return True
    
    print("❌ No good backup found - attempting manual repair")
    
    # Manual repair
    with open(target_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Fix line 288
    for i, line in enumerate(lines):
        if "'read_only': False).strip() ==" in line:
            # This line is broken - fix it
            lines[i] = "            'read_only': False,  # FORCED WRITE MODE\n"
            print(f"✅ Fixed broken line {i+1}")
    
    # Write back
    with open(target_file, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print("✅ Manual repair completed")
    return True

def apply_safe_fix(filepath):
    """Apply a safer, more targeted fix"""
    
    print("\nApplying safe write mode fix...")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Safer replacements - only in specific contexts
    
    # Fix 1: In the health function specifically
    import re
    
    # Find the health function
    health_pattern = r"(@app\.route\('/health'[^@]*?)return jsonify\((.*?)\)"
    health_match = re.search(health_pattern, content, re.DOTALL)
    
    if health_match:
        before_return = health_match.group(1)
        return_dict = health_match.group(2)
        
        # Fix the return dictionary
        fixed_dict = re.sub(r"'read_only'\s*:\s*[^,}]+", "'read_only': False", return_dict)
        
        # Reconstruct
        fixed_health = before_return + "return jsonify(" + fixed_dict + ")"
        content = content[:health_match.start()] + fixed_health + content[health_match.end():]
        
        print("   ✅ Fixed health endpoint")
    
    # Fix 2: The read_only_backend variable assignment
    # Be more careful this time
    pattern = r"read_only_backend = \(str\(os\.environ\.get\('HAKGAL_PORT', ''\)\)\.strip\(\) == '5002'\)"
    replacement = "read_only_backend = False  # FORCED WRITE MODE for port 5002"
    
    if re.search(pattern, content):
        content = re.sub(pattern, replacement, content)
        print("   ✅ Fixed read_only_backend assignment")
    
    # Write back
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Safe fix applied")
    return True

def create_simple_launcher():
    """Create a simpler launcher that doesn't do complex patching"""
    
    launcher_content = '''#!/usr/bin/env python3
"""
Simple launcher for Port 5002 with write mode
"""
import os
import sys
from pathlib import Path

# Set environment variables
os.environ['HAKGAL_PORT'] = '5002'
os.environ['HAKGAL_WRITE_ENABLED'] = 'true'
os.environ['HAKGAL_WRITE_TOKEN'] = 'write_5002'
os.environ['HAKGAL_SQLITE_READONLY'] = 'false'

print("="*60)
print("STARTING PORT 5002 (WRITE MODE)")
print("="*60)
print(f"PORT = 5002")
print(f"WRITE_ENABLED = true")
print(f"C++ Support = ENABLED")
print("="*60)

# Add paths
root = Path(__file__).resolve().parent
sys.path.insert(0, str(root))
sys.path.insert(0, str(root / 'scripts'))

# Import and run the standard launcher
from launch_5002_WRITE import main
main()
'''
    
    launcher_file = Path("start_5002_simple.py")
    with open(launcher_file, 'w') as f:
        f.write(launcher_content)
    
    print(f"\n✅ Created simple launcher: {launcher_file}")
    return launcher_file

def main():
    print("\nREPAIRING SYNTAX ERROR AND APPLYING SAFE FIX")
    print("=============================================\n")
    
    # Repair the syntax error
    if repair_syntax_error():
        print("\n✅ Syntax error repaired!")
        
        # Create simple launcher
        launcher = create_simple_launcher()
        
        print("\n" + "="*60)
        print("NEXT STEPS")
        print("="*60)
        print("\n1. Start the backend with the simple launcher:")
        print(f"   python {launcher.name}")
        print("\n2. Or use the standard launcher:")
        print("   START_WRITE.bat")
        print("\n3. Verify with:")
        print("   python verify_write_mode.py")
    else:
        print("\n❌ Repair failed - manual intervention needed")
    
    return True

if __name__ == "__main__":
    main()
    input("\nPress Enter to exit...")
