#!/usr/bin/env python
"""
FINAL STEP: Start HEXAGONAL without Legacy Dependencies
========================================================
Completely independent from HAK_GAL_SUITE!
"""

import sys
import os
from pathlib import Path

# Add src_hexagonal to path
sys.path.insert(0, str(Path(__file__).parent / 'src_hexagonal'))

def start_native_backend():
    """Start backend with native modules only"""
    
    print("="*60)
    print("🚀 HAK-GAL HEXAGONAL - NATIVE MODE")
    print("="*60)
    print("[INFO] NO dependency on HAK_GAL_SUITE")
    print("[INFO] Using native modules only")
    print("[INFO] Database: k_assistant_dev.db (3079 facts)")
    print("="*60)
    
    # Import the enhanced API
    from hexagonal_api_enhanced import HexagonalAPI
    
    # Override to use native adapters
    import adapters.native_adapters as native
    
    # Monkey-patch the imports
    import sys
    sys.modules['adapters.legacy_adapters'] = native
    
    # Create API with native adapters
    api = HexagonalAPI(
        use_legacy=False,  # Use native!
        enable_websocket=True,
        enable_governor=True,
        enable_sentry=False
    )
    
    # Run on port 5001
    print("\n[INFO] Starting on http://127.0.0.1:5001")
    print("[INFO] Fast startup - no legacy loading!")
    print("="*60)
    
    api.run(host='127.0.0.1', port=5001, debug=True)

if __name__ == '__main__':
    start_native_backend()
