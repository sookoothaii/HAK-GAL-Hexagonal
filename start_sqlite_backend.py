#!/usr/bin/env python
"""
Start Hexagonal API with SQLite as Primary Data Source
========================================================
Based on HAK/GAL Constitution: Use SQLite instead of JSONL
"""

import sys
from pathlib import Path

# Add src_hexagonal to path
sys.path.insert(0, str(Path(__file__).parent / 'src_hexagonal'))

from hexagonal_api_enhanced import HexagonalAPI
import os

def start_sqlite_backend():
    """Start the backend with SQLite as primary data source"""
    
    print("=" * 60)
    print("🔄 HAK-GAL HEXAGONAL - SQLite Mode")
    print("=" * 60)
    print("[INFO] Switching from JSONL to SQLite database")
    print("[INFO] Database: k_assistant.db")
    print("=" * 60)
    
    # Create API with SQLite (use_legacy=False)
    api = HexagonalAPI(
        use_legacy=False,  # This switches to SQLite!
        enable_websocket=True,
        enable_governor=True,
        enable_sentry=bool(os.environ.get('SENTRY_DSN'))
    )
    
    # Run on port 5001
    api.run(host='127.0.0.1', port=5001, debug=True)

if __name__ == '__main__':
    start_sqlite_backend()
