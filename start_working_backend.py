#!/usr/bin/env python
"""
Start Hexagonal API with Legacy (JSONL) - Working Configuration
================================================================
Back to the working state before database changes
"""

import sys
import os
from pathlib import Path

# Add src_hexagonal to path
sys.path.insert(0, str(Path(__file__).parent / 'src_hexagonal'))

from hexagonal_api_enhanced import HexagonalAPI

def start_working_backend():
    """Start the backend with working legacy configuration"""
    
    print("=" * 60)
    print("🔄 HAK-GAL HEXAGONAL - Legacy Mode (Working)")
    print("=" * 60)
    print("[INFO] Using Legacy Adapters (Original HAK-GAL)")
    print("[INFO] JSONL as primary, SQLite available")
    print("[INFO] Transformer models will be loaded")
    print("=" * 60)
    
    # Create API with Legacy mode (wie es vorher funktioniert hat)
    api = HexagonalAPI(
        use_legacy=True,  # Back to legacy/JSONL mode!
        enable_websocket=True,
        enable_governor=True,
        enable_sentry=bool(os.environ.get('SENTRY_DSN'))
    )
    
    # Run on port 5001
    api.run(host='127.0.0.1', port=5001, debug=True)

if __name__ == '__main__':
    start_working_backend()
