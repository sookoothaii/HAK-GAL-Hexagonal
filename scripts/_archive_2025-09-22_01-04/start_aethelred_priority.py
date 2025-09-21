#!/usr/bin/env python3
"""
Start Aethelred Engine with Priority Configuration
==================================================
Korrigiert die Thompson Sampling Parameter für Aethelred Priorität
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def main():
    print("🚀 Starting Aethelred Engine with PRIORITY Configuration")
    print("=" * 60)
    
    # Set environment variables for Aethelred priority
    os.environ['AETHELRED_PRIORITY'] = 'true'
    os.environ['THOMPSON_ALPHA_AETHELRED'] = '10'
    os.environ['THOMPSON_BETA_AETHELRED'] = '1'
    os.environ['THOMPSON_ALPHA_THESIS'] = '1'
    os.environ['THOMPSON_BETA_THESIS'] = '10'
    
    # Get paths
    hex_root = Path(__file__).parent
    governor_script = hex_root / 'src_hexagonal' / 'adapters' / 'governor_adapter.py'
    aethelred_script = hex_root / 'src_hexagonal' / 'infrastructure' / 'engines' / 'aethelred_extended_fixed.py'
    
    print(f"📁 Governor Script: {governor_script}")
    print(f"📁 Aethelred Script: {aethelred_script}")
    
    # Check if files exist
    if not governor_script.exists():
        print(f"❌ ERROR: Governor script not found: {governor_script}")
        return 1
    
    if not aethelred_script.exists():
        print(f"❌ ERROR: Aethelred script not found: {aethelred_script}")
        return 1
    
    print("\n🔧 Starting Governor with Aethelred Priority...")
    print("   - Aethelred: alpha=10, beta=1 (HIGH PRIORITY)")
    print("   - Thesis: alpha=1, beta=10 (LOW PRIORITY)")
    print("   - Aethelred will run for 30 minutes")
    print("   - Thesis will run for only 2 minutes")
    
    try:
        # Start the governor
        process = subprocess.Popen([
            sys.executable, str(governor_script)
        ], cwd=str(hex_root))
        
        print(f"\n✅ Governor started with PID: {process.pid}")
        print("📊 Monitoring fact generation...")
        
        # Monitor for 5 minutes
        for i in range(300):  # 5 minutes
            time.sleep(1)
            if i % 30 == 0:  # Every 30 seconds
                print(f"⏱️  {i//60}m {i%60}s - Governor running...")
        
        print("\n🎯 Governor monitoring complete!")
        print("Check the logs for fact generation activity.")
        
        return 0
        
    except KeyboardInterrupt:
        print("\n⏹️  Stopping Governor...")
        process.terminate()
        return 0
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
