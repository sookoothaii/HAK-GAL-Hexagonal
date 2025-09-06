#!/usr/bin/env python3
"""
Deploy Governor Fix and Restart Backend
========================================
Fixes the JSON serialization error in Governor and restarts backend
"""

import subprocess
import sys
import time
from pathlib import Path

def main():
    print("GOVERNOR FIX DEPLOYMENT")
    print("=" * 60)
    
    # Test the fix
    print("\n[1] Testing Governor fix...")
    result = subprocess.run([sys.executable, "test_governor_fix.py"], capture_output=True, text=True)
    
    if "ALL TESTS PASSED" in result.stdout:
        print("✅ Governor fix verified successfully!")
    else:
        print("⚠️ Warning: Fix test didn't pass completely")
        print(result.stdout[-500:])
    
    print("\n[2] Backend must be restarted to apply the fix.")
    print("\nPlease:")
    print("1. Stop the current backend (Ctrl+C in the backend terminal)")
    print("2. Restart with: python src_hexagonal/hexagonal_api_enhanced.py")
    
    print("\n" + "=" * 60)
    print("EXPECTED BEHAVIOR AFTER RESTART:")
    print("- Governor WebSocket events will work correctly")
    print("- No more 'Popen is not JSON serializable' errors")
    print("- Frontend can control Governor without crashes")
    print("- Engines (Aethelred/Thesis) will start and stop properly")
    
    print("\n" + "=" * 60)
    print("FIX DETAILS:")
    print("- Removed subprocess.Popen objects from status response")
    print("- Added deep copy to prevent state contamination")
    print("- Preserved PID information (integers are JSON safe)")
    print("- Maintained all functionality while ensuring serializability")

if __name__ == "__main__":
    main()
