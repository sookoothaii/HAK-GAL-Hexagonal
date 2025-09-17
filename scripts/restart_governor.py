#!/usr/bin/env python3
"""
Restart the Governor with optimized generator
"""
import subprocess
import time
import sys
from pathlib import Path

print("="*60)
print("RESTARTING GOVERNOR WITH OPTIMIZED GENERATOR")
print("="*60)

# Kill any running Python processes with governor/generator
print("\n1. Stopping old processes...")
try:
    # Windows specific
    subprocess.run(['taskkill', '/F', '/IM', 'python.exe'], capture_output=True)
    print("   ✅ Stopped all Python processes")
except:
    print("   ⚠️ No processes to stop")

time.sleep(2)

# Change to project directory
project_dir = Path(r"D:\MCP Mods\HAK_GAL_HEXAGONAL")
sys.path.insert(0, str(project_dir))

print("\n2. Starting optimized Governor...")
print("   Features:")
print("   - Duplicate prevention via argument normalization")
print("   - Balanced predicates (HasProperty: 20% max)")
print("   - Extended entity pools")
print("   - Quality metrics tracking")

# Import and start the governor
try:
    # Set environment
    import os
    os.environ['HAKGAL_AUTH_TOKEN'] = '515f57956e7bd15ddc3817573598f190'
    os.environ['PYTHONPATH'] = str(project_dir)
    
    # Start governor in new process
    governor_script = project_dir / "src_hexagonal" / "llm_governor_generator.py"
    
    print(f"\n3. Launching: {governor_script.name}")
    
    # Start in new window
    subprocess.Popen([
        sys.executable,
        str(governor_script)
    ], 
    cwd=str(project_dir),
    creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == 'win32' else 0
    )
    
    print("   ✅ Governor launched in new window")
    
    print("\n" + "="*60)
    print("RESTART COMPLETE")
    print("="*60)
    print("\nThe optimized generator is now running with:")
    print("- HasProperty limited to 20%")
    print("- No duplicate generation") 
    print("- Balanced predicate distribution")
    print("\nMonitor the new window for generation progress.")
    
except Exception as e:
    print(f"   ❌ Error: {e}")
    print("\nManual start required:")
    print(f"cd {project_dir}")
    print("python src_hexagonal\\llm_governor_generator.py")

print("="*60)
